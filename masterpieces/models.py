from django.db import models
from django.conf import settings  # 添加这行
from django.contrib.auth.models import User  # 这行可以删除或保留

class Tag(models.Model):
    name = models.CharField('标签名称', max_length=20, unique=True)
    def __str__(self):
        return self.name

class Work(models.Model):
    ZONE_CHOICES = [
        ('anime', '番剧'),
        ('galgame', 'Galgame'),
        ('manga', '小说/漫画'),
    ]

    title = models.CharField('标题', max_length=200)
    zone = models.CharField('专区', max_length=20, choices=ZONE_CHOICES)
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)

    # 修改这里：使用 settings.AUTH_USER_MODEL
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 修改这里
        on_delete=models.SET_NULL,
        verbose_name='推荐者',
        null=True,
        blank=True
    )
    description = models.TextField('作品简介', help_text='简单介绍下这部作品吧...')
    release_date = models.DateField('作品官方发布日期')

    hot_score = models.FloatField('评分', default=0.0)
    views = models.IntegerField('点击量/热度', default=0)
    cover = models.ImageField('封面图', upload_to='works/covers/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='comments')
    # 修改这里：同样使用 settings.AUTH_USER_MODEL
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField('评论内容')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '作品评论'
        verbose_name_plural = verbose_name