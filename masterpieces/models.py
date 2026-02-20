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
# models.py

class WorkGallery(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField('图集图片', upload_to='works/gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField('评论内容')
    score = models.IntegerField('评分', default=5) # 1-10分
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def like_count(self):
        return self.likes.count()

# models.py

# ... 保留原有的 Tag 和 Work 模型 ...

class UserTag(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='user_tags')
    name = models.CharField('标签名', max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 核心：确保同一部作品下，标签名不重复
        unique_together = ('work', 'name')

    def __str__(self):
        return f"{self.work.title} - {self.name}"