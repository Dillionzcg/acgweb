from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, TopicCategory, News, NewsCategory
from .forms import TopicForm

def community_home(request):
    """社区主页，展示热门话题和最新资讯"""
    pinned_topics = Topic.objects.filter(is_pinned=True).order_by('-created_at')[:3]
    recent_topics = Topic.objects.filter(is_pinned=False).order_by('-created_at')[:5]
    hot_news = News.objects.all().order_by('-views')[:3]
    topic_categories = TopicCategory.objects.all()
    
    context = {
        'pinned_topics': pinned_topics,
        'recent_topics': recent_topics,
        'hot_news': hot_news,
        'topic_categories': topic_categories,
    }
    return render(request, 'community/index.html', context)

def topic_list(request):
    """话题列表页"""
    category_id = request.GET.get('category')
    topics = Topic.objects.all()
    
    if category_id:
        topics = topics.filter(category_id=category_id)
        
    categories = TopicCategory.objects.all()
    
    context = {
        'topics': topics,
        'categories': categories,
        'current_category': int(category_id) if category_id else None
    }
    return render(request, 'community/topic_list.html', context)

def topic_detail(request, pk):
    """话题详情页"""
    topic = get_object_or_404(Topic, pk=pk)
    topic.views += 1
    topic.save()
    
    context = {
        'topic': topic
    }
    return render(request, 'community/topic_detail.html', context)

@login_required
def create_topic(request):
    """发布新话题"""
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            return redirect('topic_detail', pk=topic.pk)
    else:
        form = TopicForm()
    
    return render(request, 'community/create_topic.html', {'form': form})

def news_list(request):
    """资讯列表页"""
    category_id = request.GET.get('category')
    news_items = News.objects.all()
    
    if category_id:
        news_items = news_items.filter(category_id=category_id)
        
    categories = NewsCategory.objects.all()
    
    context = {
        'news_items': news_items,
        'categories': categories,
        'current_category': int(category_id) if category_id else None
    }
    return render(request, 'community/news_list.html', context)

def news_detail(request, pk):
    """资讯详情页"""
    news = get_object_or_404(News, pk=pk)
    news.views += 1
    news.save()
    
    related_news = News.objects.filter(category=news.category).exclude(pk=pk)[:3]
    
    context = {
        'news': news,
        'related_news': related_news
    }
    return render(request, 'community/news_detail.html', context)
