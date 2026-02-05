from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # 保持他可能已经存在的字段，并注入你下午开发的所有新字段
    phone = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name="手机号")
    email = models.EmailField(unique=True, verbose_name="邮箱")

    # 你完善用户信息功能所需的核心字段
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="头像")
    gender = models.CharField(max_length=20, default='female', verbose_name="性别")
    birthday = models.DateField(null=True, blank=True, verbose_name="生日")
    bio = models.TextField(max_length=200, blank=True, verbose_name="个人简介")
    tags = models.JSONField(default=list, blank=True, verbose_name="标签")

    class Meta:
        db_table = 'acg_user'  # 保持表名一致，防止迁移冲突

    def __str__(self):
        return self.username


class Friendship(models.Model):
    STATUS_CHOICES = (
        ('pending', '申请中'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
    )
    from_user = models.ForeignKey(User, related_name='friendship_sent', on_delete=models.CASCADE, verbose_name="申请人")
    to_user = models.ForeignKey(User, related_name='friendship_received', on_delete=models.CASCADE, verbose_name="接收人")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'acg_friendship'
        unique_together = ('from_user', 'to_user')
        verbose_name = "好友关系"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"