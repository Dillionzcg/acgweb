from django.db import models  # 修正这里：从 django.db 导入 models


class Work(models.Model):  # 修正这里：继承自 models.Model
    ZONE_CHOICES = [
        ('anime', '番剧'),
        ('galgame', 'Galgame'),
        ('manga', '小说/漫画'),
    ]

    title = models.CharField('标题', max_length=200)
    zone = models.CharField('专区', max_length=20, choices=ZONE_CHOICES)
    tag = models.CharField('标签', max_length=100, help_text='例如：热血/战斗')
    hot_score = models.FloatField('评分', default=0.0)
    views = models.IntegerField('点击量/热度', default=0)
    # 使用 ImageField 需要安装 Pillow 库：pip install Pillow
    cover = models.ImageField('封面图', upload_to='works/covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title