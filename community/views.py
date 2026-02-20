from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import Topic, TopicCategory, News, NewsCategory, NewsComment, TopicComment
from .forms import TopicForm, NewsForm, NewsCommentForm, TopicCommentForm

@user_passes_test(lambda u: u.is_superuser)
def create_news(request):
    """发布新资讯 (仅限超级用户)"""
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return redirect('news_detail', pk=news.pk)
    else:
        form = NewsForm()
    
    return render(request, 'community/create_news.html', {'form': form})

def community_home(request):
    """社区主页，展示热门话题和最新资讯"""
    pinned_topics = Topic.objects.filter(is_pinned=True).order_by('-created_at')[:3]
    recent_topics = Topic.objects.filter(is_pinned=False).order_by('-created_at')[:5]
    hot_news = News.objects.all().order_by('-views')[:3]
    
    # 实例化表单用于Modal
    topic_form = TopicForm()

    context = {
        'pinned_topics': pinned_topics,
        'recent_topics': recent_topics,
        'hot_news': hot_news,
        'topic_form': topic_form, # 添加到上下文
    }
    return render(request, 'community/index.html', context)

def topic_list(request):
    """话题列表页"""
    topics = Topic.objects.all().order_by('-created_at')
    
    # 实例化表单用于Modal
    topic_form = TopicForm()
    
    context = {
        'topics': topics,
        'topic_form': topic_form, # 添加到上下文
    }
    return render(request, 'community/topic_list.html', context)

def topic_detail(request, pk):
    """话题详情页"""
    topic = get_object_or_404(Topic, pk=pk)
    topic.views += 1
    topic.save()
    
    # 评论逻辑
    comment_form = TopicCommentForm()
    # 只获取顶级评论
    comments = topic.comments.filter(parent__isnull=True).select_related('author').order_by('created_at')
    
    context = {
        'topic': topic,
        'comment_form': comment_form,
        'comments': comments
    }
    return render(request, 'community/topic_detail.html', context)

@login_required
def add_topic_comment(request, pk):
    """提交话题评论"""
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == 'POST':
        form = TopicCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.topic = topic
            comment.author = request.user
            
            # 处理父评论
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = TopicComment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except TopicComment.DoesNotExist:
                    pass
            
            comment.save()

            # 如果是 AJAX 请求，返回 JSON 数据
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'username': comment.author.username,
                    'is_superuser': comment.author.is_superuser,
                    'avatar_url': comment.author.avatar.url if comment.author.avatar else '/static/images/default_head.png',
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'parent_id': parent_id,
                    'comment_id': comment.id
                })

    return redirect('topic_detail', pk=pk)

@login_required
def create_topic(request):
    """发布新话题 (处理Modal提交)"""
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            return redirect('topic_detail', pk=topic.pk)
    # 如果是GET请求或者表单无效，通常Modal会处理，
    # 但为了兼容性，保留渲染独立页面的逻辑，或者重定向回上一页
    else:
        form = TopicForm()
    
    return render(request, 'community/create_topic.html', {'form': form})

def news_list(request):
    """资讯列表页"""
    tag = request.GET.get('tag')
    news_items = News.objects.all()
    
    if tag:
        news_items = news_items.filter(tags__icontains=tag)
        
    # 获取常用的几个标签用于展示
    # 这里简单获取所有资讯的前 5 个不重复标签
    all_tags = []
    for n in News.objects.all():
        if n.tags:
            all_tags.extend(n.tags.split())
    unique_tags = list(set(all_tags))[:5]
    
    context = {
        'news_items': news_items,
        'tags': unique_tags,
        'current_tag': tag
    }
    return render(request, 'community/news_list.html', context)

def news_detail(request, pk):
    """资讯详情页"""
    news = get_object_or_404(News, pk=pk)
    news.views += 1
    news.save()

    # 检查当前用户是否已点赞
    user_liked = False
    if request.user.is_authenticated:
        user_liked = news.liked_by.filter(id=request.user.id).exists()

    # 根据第一个标签推荐相关资讯
    related_news = []
    if news.tags:
        first_tag = news.tags.split()[0]
        related_news = News.objects.filter(tags__icontains=first_tag).exclude(pk=pk)[:3]

    if not related_news:
        related_news = News.objects.exclude(pk=pk).order_by('-created_at')[:3]

    # 评论逻辑
    comment_form = NewsCommentForm()
    # 只获取顶级评论，子评论通过模板中的 comment.replies.all 获取
    comments = news.comments.filter(parent__isnull=True).select_related('author').order_by('-created_at')

    context = {
        'news': news,
        'related_news': related_news,
        'user_liked': user_liked,
        'comment_form': comment_form,
        'comments': comments
    }
    return render(request, 'community/news_detail.html', context)

@login_required
def add_news_comment(request, pk):
    """提交资讯评论"""
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        form = NewsCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news
            comment.author = request.user
            
            # 处理父评论
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = NewsComment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except NewsComment.DoesNotExist:
                    pass
            
            comment.save()

            # 如果是 AJAX 请求，返回 JSON 数据
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'username': comment.author.username,
                    'is_superuser': comment.author.is_superuser,
                    'avatar_url': comment.author.avatar.url if comment.author.avatar else '/static/images/default_head.png',
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'parent_id': parent_id,
                    'comment_id': comment.id
                })

    return redirect('news_detail', pk=pk)

@login_required
def delete_topic(request, pk):
    """删除话题 (仅限作者或超级用户)"""
    topic = get_object_or_404(Topic, pk=pk)
    if topic.author == request.user or request.user.is_superuser:
        topic.delete()
        return redirect('topic_list')
    return redirect('topic_detail', pk=pk)

@login_required
def delete_news(request, pk):
    """删除资讯 (仅限作者或超级用户)"""
    news = get_object_or_404(News, pk=pk)
    if news.author == request.user or request.user.is_superuser:
        news.delete()
        return redirect('news_list')
    return redirect('news_detail', pk=pk)

@login_required
def like_news(request, pk):

    """为资讯点赞/取消点赞 (AJAX)"""

    if request.method == 'POST':

        news = get_object_or_404(News, pk=pk)

        if news.liked_by.filter(id=request.user.id).exists():

            # 取消点赞

            news.liked_by.remove(request.user)

            news.likes = max(0, news.likes - 1)

            liked = False

        else:

            # 点赞

            news.liked_by.add(request.user)

            news.likes += 1

            liked = True

        news.save()

        return JsonResponse({'likes': news.likes, 'liked': liked})

    return JsonResponse({'error': 'Invalid request'}, status=400)




