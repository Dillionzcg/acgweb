import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Avg
from .models import Work, Tag, Comment, WorkGallery  # 确保导入了所有新模型
from django.db.models import Count, F, ExpressionWrapper, FloatField
from django.db import models
from django.db.models import Count
from django.db.models import F, Count, ExpressionWrapper, FloatField
from .models import Illustration, Tag, UserProfile  # 确保导入了新模型
import random


def update_tag_score(user, tags, delta):
    """
    通用标签权重更新逻辑
    delta: 权重变化值 (查看+1, 收藏+10, 取消收藏-10)
    """
    if not user or not user.is_authenticated:
        return

    profile, _ = UserProfile.objects.get_or_create(user=user)
    # 确保 preferences 是字典格式
    prefs = profile.tag_preferences if isinstance(profile.tag_preferences, dict) else {}

    for tag in tags:
        tag_id = str(tag.id) # JSON 的 key 必须是字符串
        current_score = prefs.get(tag_id, 0)
        # 更新分数，最低保留为 0，避免出现负分导致逻辑混乱
        prefs[tag_id] = max(0, current_score + delta)

    profile.tag_preferences = prefs
    profile.save()

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


# masterpieces/views.py

# masterpieces/views.py

# masterpieces/views.py
from django.db.models import Count, F, ExpressionWrapper, FloatField
from .models import Tag, Illustration

from django.db.models import Count, F, ExpressionWrapper, FloatField
from .models import Tag, Illustration, UserProfile  # 确保导入 UserProfile

def get_recommendation_data(user, all_illusts, target_count=50, max_groups=10):
    """
    标签分组轮播推荐
    - all_illusts: 带有 calculated_hot 注解的 QuerySet
    - target_count: 目标推荐数量（默认50）
    - max_groups: 最多使用多少组（每组3个标签）
    """
    # 获取用户所有正权重的标签
    profile, _ = UserProfile.objects.get_or_create(user=user)
    prefs = profile.tag_preferences  # 格式 {"1": 12, "5": 2, ...}

    # 过滤出正权重标签ID（转换为整数）
    tag_weights = {}
    for tid_str, weight in prefs.items():
        try:
            tag_id = int(tid_str)
            if weight > 0:
                tag_weights[tag_id] = weight
        except (ValueError, TypeError):
            continue

    # 若无偏好标签，直接返回热门
    if not tag_weights:
        return list(all_illusts.exclude(favorites=user).order_by('-calculated_hot')[:target_count])

    # 按权重降序排序标签ID
    sorted_tags = sorted(tag_weights.keys(), key=lambda tid: tag_weights[tid], reverse=True)
    # 取前 max_groups*3 个标签（最多30个）
    top_tags = sorted_tags[:max_groups * 3]

    # 分成每组3个标签（最后一组可能不足3个）
    groups = [top_tags[i:i+3] for i in range(0, len(top_tags), 3)]

    recommendations = []
    seen_ids = set()  # 记录已推荐作品ID，避免重复

    # 按组顺序获取作品
    for group in groups:
        if len(recommendations) >= target_count:
            break

        need = target_count - len(recommendations)
        # 查询包含该组任意标签、未收藏、未推荐的作品，按热度排序
        qs = all_illusts.filter(
            tags__id__in=group
        ).exclude(
            favorites=user
        ).exclude(
            id__in=seen_ids
        ).distinct().order_by('-calculated_hot')[:need]

        for illust in qs:
            recommendations.append(illust)
            seen_ids.add(illust.id)

    # 若仍未达到目标，用热门补足（排除已推荐和已收藏）
    if len(recommendations) < target_count:
        need = target_count - len(recommendations)
        hot_qs = all_illusts.exclude(
            favorites=user
        ).exclude(
            id__in=seen_ids
        ).order_by('-calculated_hot')[:need]
        recommendations.extend(list(hot_qs))

    return recommendations

def illustration_center(request):
    # 基础 QuerySet
    all_illusts = Illustration.objects.annotate(
        comment_count=Count('comments', distinct=True),
        favorite_count=Count('favorites', distinct=True),
        calculated_hot=ExpressionWrapper(
            F('views') + F('favorite_count') * 10 + F('comment_count') * 5,
            output_field=FloatField()
        )
    ).prefetch_related('tags', 'owner')
    tags_queryset = list(Tag.objects.annotate(num=Count('illustration'))
                         .filter(num__gt=0)
                         .prefetch_related('illustration_set'))


    sample_size = min(len(tags_queryset), 30)
    selected_tags = random.sample(tags_queryset, sample_size)

    # 3. 封面图去重算法
    used_illust_ids = set()
    tag_data_list = []

    for tag in selected_tags:
        # 获取该标签下所有作品
        available_illusts = list(tag.illustration_set.all())
        # 尝试找一个还没被其他标签占用的封面
        chosen_illust = None
        for img in available_illusts:
            if img.id not in used_illust_ids:
                chosen_illust = img
                used_illust_ids.add(img.id)
                break

        # 如果所有作品都被占用了，保底选第一个（或设为 None）
        if not chosen_illust and available_illusts:
            chosen_illust = available_illusts[0]

        tag_data_list.append({
            'tag': tag,
            'cover_url': chosen_illust.image.url if chosen_illust else None
        })

    # 1. 最新作品
    latest_illusts = all_illusts.order_by('-created_at')
    # 2. 最热作品
    hot_illusts = all_illusts.order_by('-calculated_hot')
    # 3. 为你推荐 (调用优化后的算法)
    recommend_illusts = get_recommendation_data(request.user, all_illusts, target_count=50)

    context = {
        'tag_data_list': tag_data_list,
        'all_tags': Tag.objects.annotate(num=Count('illustration')).filter(num__gt=0),
        'illustrations_latest': latest_illusts[:20],
        'illustrations_new': latest_illusts,  # 最新作品（全量，可用于分页）
        'illustrations_hot': hot_illusts[:20],
        'illustrations_rec': recommend_illusts,  # 为你推荐数据
        'illustrations_follow': [],  # 我的关注（暂无功能，先置空）
    }
    return render(request, 'masterpieces/illustration_center.html', context)

# masterpieces/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Illustration, Tag  # 确保你已经根据下方说明创建了 Illustration 模型


@login_required
def post_illustration(request):
    # 预设标签（保持不变，用于前端展示）
    illust_tags = [
        "原创角色", "女孩子", "少女", "萝莉", "同人", "二次元", "场景",
        "唯美", "少年", "御姐", "白发", "OC", "Q版", "机甲", "私服",
        "背景", "壁纸", "泳装", "女仆装", "涂鸦", "练习", "过程", "光影",
        "氛围", "意境", "暗黑", "清新", "街头", "科幻"
    ]

    if request.method == 'POST':
        # 1. 获取表单基础数据
        title = request.POST.get('title')
        # 如果前端没传，默认设为 'repost' (搬运)
        work_type = request.POST.get('work_type', 'repost')
        description = request.POST.get('description')

        # 2. 获取上传的图片文件 (对应前端 <input name="illustration">)
        illustration_file = request.FILES.get('illustration')

        # 3. 获取并处理标签字符串 (前端 js 把数组 join(',') 后传给隐藏域 selected_tags)
        tag_string = request.POST.get('selected_tags', '')
        tag_names = [t.strip() for t in tag_string.split(',') if t.strip()]

        # 4. 创建并保存作品对象
        # 注意：这里移除了 author_bio，因为它在 UI 上已经去掉了
        instance = Illustration.objects.create(
            title=title,
            work_type=work_type,
            description=description,
            image=illustration_file,
            owner=request.user
        )

        # 5. 处理标签关联 (多对多关系)
        for name in tag_names:
            # 确保标签库中唯一，存在则获取，不存在则创建
            tag_obj, created = Tag.objects.get_or_create(name=name)
            instance.tags.add(tag_obj)

        # 6. 发布成功后跳转
        # 注意：这里需要确保你的 urls.py 中有一个 name='illustration_center' 的路由
        return redirect('masterpieces:illustration_center')

    # 如果是 GET 请求，显示发布页面
    return render(request, 'masterpieces/post_illustration.html', {
        'illust_tags': illust_tags
    })


from django.shortcuts import render, get_object_or_404
from .models import Illustration


def illustration_detail(request, pk):
    illustration = get_object_or_404(Illustration, pk=pk)
    illustration.views += 1
    illustration.save(update_fields=['views'])

    if request.user.is_authenticated:
        # 只要点击进入详情页，所有标签权重 +1
        update_tag_score(request.user, illustration.tags.all(), 1)

    return render(request, 'masterpieces/illustration_detail.html', {'illustration': illustration})


from django.contrib import messages
from django.http import HttpResponseForbidden


@login_required
@require_POST
def delete_illustration(request, pk):
    illustration = get_object_or_404(Illustration, pk=pk)

    # 安全检查：只有管理员或所有者可以删除
    if not (request.user.is_staff or request.user == illustration.owner):
        return HttpResponseForbidden("你没有权限删除此作品")

    # 执行删除
    illustration.delete()
    return JsonResponse({"status": "success"})


# masterpieces/views.py
from .models import IllustrationComment
@login_required
@require_POST
def submit_illust_comment(request, pk):
    illustration = get_object_or_404(Illustration, pk=pk)
    content = request.POST.get('content', '').strip()

    if content:
        IllustrationComment.objects.create(
            illustration=illustration,
            user=request.user,
            content=content
        )
    return redirect('masterpieces:illustration_detail', pk=pk)


# masterpieces/views.py

@login_required
@require_POST
def like_illust_comment(request, comment_id):
    comment = get_object_or_404(IllustrationComment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': comment.likes.count()})

@login_required
@require_POST
def delete_illust_comment(request, comment_id):
    comment = get_object_or_404(IllustrationComment, id=comment_id)
    # 权限检查：管理员、插画作者、评论者本人
    if request.user.is_staff or request.user == comment.user or request.user == comment.illustration.owner:
        comment.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=403)
# masterpieces/views.py

# masterpieces/views.py
@login_required
@require_POST
def toggle_illustration_favorite(request, pk):
    illustration = get_object_or_404(Illustration, pk=pk)
    user = request.user

    # 获取该作品关联的所有标签，用于后续权重计算
    # 使用 .all() 获取 QuerySet
    illust_tags = illustration.tags.all()

    if user in illustration.favorites.all():
        # --- 取消收藏逻辑 ---
        illustration.favorites.remove(user)
        is_favorite = False

        # 行为追踪：标签权重减 10
        update_tag_score(user, illust_tags, -10)
    else:
        # --- 添加收藏逻辑 ---
        illustration.favorites.add(user)
        is_favorite = True

        # 行为追踪：标签权重加 10
        update_tag_score(user, illust_tags, 10)

    return JsonResponse({'status': 'success', 'is_favorite': is_favorite})
# masterpieces/views.py

@login_required
def my_favorite_illustrations(request):
    # 获取当前用户收藏的所有插画
    # 使用 prefetch_related 优化查询，并计算热度以供卡片展示（如果有逻辑需要）
    favorite_illusts = request.user.favorite_illustrations.annotate(
        comment_count=Count('comments', distinct=True),
        favorite_count=Count('favorites', distinct=True),
        calculated_hot=ExpressionWrapper(
            F('views') + F('favorite_count') * 10 + F('comment_count') * 5,
            output_field=FloatField()
        )
    ).prefetch_related('tags', 'owner').order_by('-created_at')

    context = {
        'favorite_illusts': favorite_illusts,
    }
    return render(request, 'masterpieces/my_favorite_illustrations.html', context)


def illustration_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)

    # 获取该标签下的所有插画，并关联相关数据
    illustrations = Illustration.objects.filter(tags=tag).annotate(
        comment_count=Count('comments', distinct=True),
        favorite_count=Count('favorites', distinct=True),
        calculated_hot=ExpressionWrapper(
            F('views') + F('favorite_count') * 10 + F('comment_count') * 5,
            output_field=FloatField()
        )
    ).prefetch_related('tags', 'owner').order_by('-created_at')

    context = {
        'tag': tag,
        'illustrations': illustrations,
    }
    return render(request, 'masterpieces/illustration_tag_detail.html', context)