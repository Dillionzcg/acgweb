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
    views = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    likes = models.PositiveIntegerField(default=0, verbose_name="点赞数")
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
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, verbose_name="分类")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="发布者")
    views = models.PositiveIntegerField(default=0, verbose_name="阅读量")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="发布时间")

    class Meta:
        verbose_name = "资讯新闻"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title