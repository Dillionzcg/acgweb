import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Avg
from .models import Work, Tag, Comment, WorkGallery  # 确保导入了所有新模型
from django.db.models import Count, F, ExpressionWrapper, FloatField


# 1. 作品中心列表页
def works_center(request):
    all_works = Work.objects.prefetch_related('tags').annotate(
        calculated_hot=ExpressionWrapper(
            F('views') + Count('favorites', distinct=True) * 10 + Count('comments', distinct=True) * 5,
            output_field=FloatField()
        )
    )
    fav_tags = []
    user_fav_ids = []
    if request.user.is_authenticated:
        fav_tags = request.user.preferences.get('genres', [])
        user_fav_ids = request.user.favorite_works.values_list('id', flat=True)
    def get_zone_data(zone_name):
        zone_works = all_works.filter(zone=zone_name)
        # --- “为你推荐”核心过滤逻辑 ---
        if fav_tags:
            # 筛选作品标签名称在用户喜好列表中的作品
            # 使用 .distinct() 防止因匹配多个标签导致的重复数据
            recommend_queryset = zone_works.filter(
                tags__name__in=fav_tags
            ).exclude(id__in=user_fav_ids).distinct().order_by('-calculated_hot')

            # 2. 取前 6 部
            recommend_list = list(recommend_queryset[:6])

            # 3. 可选逻辑：如果未收藏的推荐作品不足 6 部，可以用已收藏但符合标签的作品补齐
            if len(recommend_list) < 6:
                needed = 6 - len(recommend_list)
                already_fav_recommend = zone_works.filter(
                    tags__name__in=fav_tags,
                    id__in=user_fav_ids
                ).distinct().order_by('-calculated_hot')[:needed]
                recommend_list.extend(list(already_fav_recommend))
        else:
            recommend_list = []
        return {
            'recommend': recommend_list,
            'list': zone_works.order_by('-created_at')[:6],
            # 2. 排行榜按计算出的热度排序，取前10名
            'ranks': zone_works.order_by('-calculated_hot')[:15],
            'hot': zone_works.order_by('-calculated_hot')[:6],
        }

    anime_data = get_zone_data('anime')
    galgame_data = get_zone_data('galgame')
    manga_data = get_zone_data('manga')
    context = {
        'anime_recommend': anime_data['recommend'],  # 确保传递了 recommend 变量
        'anime_list': anime_data['list'],
        'anime_ranks': anime_data['ranks'],
        'anime_hot': anime_data['hot'],

        'galgame_recommend': galgame_data['recommend'],
        'galgame_list': galgame_data['list'],
        'galgame_ranks': galgame_data['ranks'],
        'galgame_hot': galgame_data['hot'],

        'manga_recommend': manga_data['recommend'],
        'manga_list': manga_data['list'],
        'manga_ranks': manga_data['ranks'],
        'manga_hot': manga_data['hot'],
        'has_fav_tags': len(fav_tags) > 0
    }
    return render(request, 'masterpieces/works_center.html', context)


# 2. 作品详情页 (包含图集预加载)
def work_detail(request, work_id):
    # prefetch_related 预加载相关数据，减少数据库查询压力
    work = get_object_or_404(
        Work.objects.prefetch_related('tags', 'owner', 'gallery', 'comments__user', 'comments__likes'),
        id=work_id
    )

    # 增加热度
    work.views += 1
    work.save()

    comments = work.comments.all().order_by('-created_at')

    context = {
        'work': work,
        'comments': comments,
    }
    return render(request, 'masterpieces/work_detail.html', context)


# 3. 提交评论与评分 (二合一逻辑)
@login_required
@require_POST
def submit_comment(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    content = request.POST.get('content')
    score = request.POST.get('score')

    if content and score:
        # 创建评论
        Comment.objects.create(
            work=work,
            user=request.user,
            content=content,
            score=int(score)
        )
        # 自动计算该作品所有评论的平均分，更新到 Work 模型
        avg_score = work.comments.aggregate(Avg('score'))['score__avg']
        if avg_score:
            work.hot_score = round(avg_score, 1)
            work.save()

    return redirect('masterpieces:work_detail', work_id=work.id)


# 4. 评论点赞 (Ajax 接口)
@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'count': comment.likes.count()
    })


# 5. 我要安利 (发布作品)
@login_required
def recommend_work(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        zone = request.POST.get('zone')
        cover = request.FILES.get('cover')
        description = request.POST.get('description')
        release_date = request.POST.get('release_date') or None

        tags_json = request.POST.get('tags_data')
        tags_list = json.loads(tags_json) if tags_json else []
        hide_month = request.POST.get('hide_month') == 'on'
        hide_day = request.POST.get('hide_day') == 'on'

        work = Work.objects.create(
            title=title,
            zone=zone,
            cover=cover,
            description=description,
            release_date=release_date,
            hide_month=hide_month,
            hide_day=hide_day,
            owner=request.user
        )

        for tag_name in tags_list:
            tag_obj, _ = Tag.objects.get_or_create(name=tag_name.strip())
            work.tags.add(tag_obj)

        return redirect('masterpieces:works_center')

    return render(request, 'masterpieces/recommend_work.html')
# 在 masterpieces/views.py 中确保有这个函数
@login_required
@require_POST
def delete_work(request, work_id):
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '没有权限'}, status=403)
    work = get_object_or_404(Work, id=work_id)
    work.delete()
    return redirect('masterpieces:works_center')

# 增加上传图片的视图
@login_required
@require_POST
def upload_work_image(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    image = request.FILES.get('image')
    if image:
        WorkGallery.objects.create(work=work, image=image,uploader=request.user)
    return redirect('masterpieces:work_detail', work_id=work.id)

# views.py
from .models import Work, UserTag # 确保导入新模型


@login_required
@require_POST
def add_user_tag(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    tag_name = request.POST.get('tag_name', '').strip()

    # 1. 基础校验
    if not tag_name:
        return JsonResponse({'status': 'error', 'message': '标签内容不能为空~'}, status=400)

    if len(tag_name) > 10:
        return JsonResponse({'status': 'error', 'message': '标签太长了（最多10个字）'}, status=400)

    # 2. 检查查重（不区分大小写）
    # 检查官方标签
    if work.tags.filter(name__iexact=tag_name).exists():
        return JsonResponse({'status': 'error', 'message': '这已经是官方认证的标签啦！'}, status=400)

    # 检查用户标签
    if UserTag.objects.filter(work=work, name__iexact=tag_name).exists():
        return JsonResponse({'status': 'error', 'message': '已经有小伙伴想到这个标签了哦~'}, status=400)

    # 3. 创建
    try:
        UserTag.objects.create(
            work=work,
            name=tag_name,
            user=request.user
        )
        return JsonResponse({'status': 'success', 'message': '添加成功'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': '服务器开小差了，请重试'}, status=500)


# views.py

# views.py

# views.py

@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    work = comment.work

    # 权限校验
    if request.user.is_staff or work.owner == request.user or comment.user == request.user:
        comment.delete()

        # 重新计算平均分
        avg_score = work.comments.aggregate(Avg('score'))['score__avg']
        work.hot_score = round(avg_score, 1) if avg_score else 0.0
        work.save()

        # 返回最新的数据给前端
        return JsonResponse({
            'status': 'success',
            'new_score': work.hot_score,
            'new_count': work.comments.count()
        })

    return JsonResponse({'status': 'error', 'message': '无权删除'}, status=403)


# masterpieces/views.py

@login_required
@require_POST
def delete_gallery_image(request, image_id):
    """
    删除图集中的单张图片
    权限：管理员、作品所有者、图片上传者
    """
    image_item = get_object_or_404(WorkGallery, id=image_id)
    work = image_item.work

    # 权限判断逻辑
    # 1. 是否是管理员
    is_staff = request.user.is_staff
    # 2. 是否是作品的推荐者
    is_work_owner = (work.owner == request.user)
    # 3. 是否是该图片的上传者 (需配合下方模型修改，若无此字段则默认为作品推荐者上传)
    is_uploader = getattr(image_item, 'uploader', work.owner) == request.user

    if is_staff or is_work_owner or is_uploader:
        image_item.delete()
        return JsonResponse({'status': 'success', 'message': '图片已删除'})

    return JsonResponse({'status': 'error', 'message': '你没有权限删除这张图片哦~'}, status=403)


@login_required
@require_POST
def toggle_gallery_featured(request, image_id):
    image_item = get_object_or_404(WorkGallery, id=image_id)
    work = image_item.work

    # 权限校验
    if not (request.user.is_staff or work.owner == request.user):
        return JsonResponse({'status': 'error', 'message': '无权操作'}, status=403)

    # 如果是要设为精选，先检查数量
    if not image_item.is_featured:
        featured_count = work.gallery.filter(is_featured=True).count()
        if featured_count >= 4:
            return JsonResponse({'status': 'error', 'message': '精选图片数量已达上限'}, status=400)
        image_item.is_featured = True
    else:
        image_item.is_featured = False

    image_item.save()
    return JsonResponse({'status': 'success', 'is_featured': image_item.is_featured})


# views.py

@login_required
@require_POST
def delete_user_tag(request, tag_id):
    """
    删除用户上传的标签
    权限：管理员、作品推荐者可以删除所有；普通用户只能删除自己上传的
    """
    tag = get_object_or_404(UserTag, id=tag_id)
    work = tag.work

    is_staff = request.user.is_staff
    is_work_owner = (work.owner == request.user)
    is_tag_uploader = (tag.user == request.user)

    if is_staff or is_work_owner or is_tag_uploader:
        tag.delete()
        return JsonResponse({'status': 'success', 'message': '标签已移除'})

    return JsonResponse({'status': 'error', 'message': '你没有权限删除这个标签哦~'}, status=403)


# views.py
# views.py 完整函数
def check_work_exists(request):
    title = request.GET.get('title', '').strip()
    zone = request.GET.get('zone', 'anime')

    if not title:
        return JsonResponse({'exists': False, 'results': []})

    # 使用 icontains 进行不区分大小写的模糊搜索
    works = Work.objects.filter(zone=zone, title__icontains=title)[:5]

    results = []
    for w in works:
        results.append({
            'title': w.title,
            # 确保即使没有封面也不会报错
            'cover': w.cover.url if w.cover else '/static/images/default_cover.png',
            'id': w.id
        })

    return JsonResponse({
        'exists': len(results) > 0,
        'results': results
    })


# masterpieces/views.py

@login_required
@require_POST
def toggle_favorite(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    if request.user in work.favorites.all():
        work.favorites.remove(request.user)
        is_favorite = False
    else:
        work.favorites.add(request.user)
        is_favorite = True

    return JsonResponse({
        'status': 'success',
        'is_favorite': is_favorite,
        'count': work.favorites.count()
    })
# views.py

@login_required
def my_favorites(request):
    # 获取当前用户收藏的所有作品
    favorite_works = request.user.favorite_works.prefetch_related('tags').all()

    def get_favorite_zone_data(zone_name):
        zone_works = favorite_works.filter(zone=zone_name).order_by('-created_at')
        return zone_works

    context = {
        'anime_favs': get_favorite_zone_data('anime'),
        'galgame_favs': get_favorite_zone_data('galgame'),
        'manga_favs': get_favorite_zone_data('manga'),
    }
    # 使用一个新的模板，但逻辑复用 works_center
    return render(request, 'masterpieces/my_favorites.html', context)


# views.py 增加以下函数

def all_works_view(request):
    zone = request.GET.get('zone', 'anime')
    category = request.GET.get('category', 'hot')  # recommend, hot, latest

    # 基础查询集：预加载标签并计算热度
    all_works = Work.objects.prefetch_related('tags').annotate(
        calculated_hot=ExpressionWrapper(
            F('views') + Count('favorites', distinct=True) * 10 + Count('comments', distinct=True) * 5,
            output_field=FloatField()
        )
    ).filter(zone=zone)

    user_fav_ids = []
    fav_tags = []
    if request.user.is_authenticated:
        fav_tags = request.user.preferences.get('genres', [])
        user_fav_ids = list(request.user.favorite_works.values_list('id', flat=True))

    # 根据类别筛选
    if category == 'recommend':
        # 逻辑与 works_center 一致，但不设数量限制
        display_works = all_works.filter(tags__name__in=fav_tags).distinct().order_by('-calculated_hot')
        title_prefix = "为你推荐"
    elif category == 'latest':
        display_works = all_works.order_by('-created_at')
        title_prefix = "最新发布"
    else:  # hot
        display_works = all_works.order_by('-calculated_hot')
        title_prefix = "热门作品"

    # 映射分区中文名
    zone_map = {'anime': '番剧', 'galgame': 'Galgame', 'manga': '小说和漫画'}

    context = {
        'works': display_works,
        'page_title': f"{zone_map.get(zone, '')} - {title_prefix}",
        'zone': zone,
        'category': category,
        'user_fav_ids': user_fav_ids,
        'is_recommend': category == 'recommend'
    }
    return render(request, 'masterpieces/all_works.html', context)