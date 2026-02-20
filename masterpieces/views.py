import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Avg
from .models import Work, Tag, Comment, WorkGallery  # 确保导入了所有新模型


# 1. 作品中心列表页
def works_center(request):
    all_works = Work.objects.prefetch_related('tags').all()

    def get_zone_data(zone_name):
        zone_works = all_works.filter(zone=zone_name)
        return {
            'list': zone_works.order_by('-created_at')[:6],
            'ranks': zone_works.order_by('-views')[:10],
            'hot': zone_works.order_by('-views')[:6],
        }

    context = {
        'anime_list': get_zone_data('anime')['list'],
        'anime_ranks': get_zone_data('anime')['ranks'],
        'anime_hot': get_zone_data('anime')['hot'],
        'galgame_list': get_zone_data('galgame')['list'],
        'galgame_ranks': get_zone_data('galgame')['ranks'],
        'galgame_hot': get_zone_data('galgame')['hot'],
        'manga_list': get_zone_data('manga')['list'],
        'manga_ranks': get_zone_data('manga')['ranks'],
        'manga_hot': get_zone_data('manga')['hot'],
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

        work = Work.objects.create(
            title=title,
            zone=zone,
            cover=cover,
            description=description,
            release_date=release_date,
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
        WorkGallery.objects.create(work=work, image=image)
    return redirect('masterpieces:work_detail', work_id=work.id)

# views.py
from .models import Work, UserTag # 确保导入新模型

@login_required
@require_POST
def add_user_tag(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    tag_name = request.POST.get('tag_name', '').strip()

    if not tag_name:
        return JsonResponse({'status': 'error', 'message': '标签内容不能为空'}, status=400)

    # 1. 检查是否与官方标签重复
    if work.tags.filter(name__iexact=tag_name).exists():
        return JsonResponse({'status': 'error', 'message': '该标签已存在于官方标签中'}, status=400)

    # 2. 检查是否与其他用户添加的标签重复
    if UserTag.objects.filter(work=work, name__iexact=tag_name).exists():
        return JsonResponse({'status': 'error', 'message': '该标签已被其他用户添加过了'}, status=400)

    # 3. 创建新标签
    UserTag.objects.create(
        work=work,
        name=tag_name,
        user=request.user
    )

    return JsonResponse({'status': 'success', 'message': '添加成功'})