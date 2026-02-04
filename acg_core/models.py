from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 增加 unique=True 确保手机号唯一
    phone = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name="手机号")
    email = models.EmailField(unique=True, verbose_name="邮箱")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    gender = models.CharField(max_length=20, default='female')
    birthday = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=200, blank=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'acg_user'