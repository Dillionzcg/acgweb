from django.db import models
from django.conf import settings
from django.utils import timezone

class TopicCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="板块名称")
    description = models.TextField(blank=True, verbose_name="板块描述")
    icon = models.CharField(max_length=50, default="fa-comments", verbose_name="图标类名(FontAwesome)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "社区板块"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Topic(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topics", verbose_name="作者")
    category = models.ForeignKey(TopicCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="板块")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="关键词", help_text="用逗号或空格分隔")
    views = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    likes = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_topics', blank=True, verbose_name="点赞用户")
    is_pinned = models.BooleanField(default=False, verbose_name="置顶")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "社区话题"
        verbose_name_plural = verbose_name
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title

class NewsCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    
    class Meta:
        verbose_name = "资讯分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    summary = models.TextField(max_length=500, blank=True, verbose_name="摘要")
    content = models.TextField(verbose_name="内容")
    cover_image = models.ImageField(upload_to='news_covers/', blank=True, null=True, verbose_name="封面图")
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="分类")
    tags = models.CharField(max_length=255, blank=True, verbose_name="标签", help_text="用逗号或空格分隔")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="发布者")
    views = models.PositiveIntegerField(default=0, verbose_name="阅读量")
    likes = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_news', blank=True, verbose_name="点赞用户")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="发布时间")

    class Meta:
        verbose_name = "资讯新闻"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class NewsComment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments', verbose_name="所属资讯")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="评论者")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="父评论")
    content = models.TextField(verbose_name="评论内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")

    class Meta:
        verbose_name = "资讯评论"
        verbose_name_plural = verbose_name
        ordering = ['created_at'] # 按时间正序排列，方便楼层展示

    def __str__(self):
        return f"{self.author.username} 对 {self.news.title} 的评论"

class TopicComment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='comments', verbose_name="所属话题")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="评论者")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="父评论")
    content = models.TextField(verbose_name="评论内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")

    class Meta:
        verbose_name = "话题评论"
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} 对 {self.topic.title} 的评论"
