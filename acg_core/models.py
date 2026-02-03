from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 增加 unique=True 确保手机号唯一
    phone = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name="手机号")
    email = models.EmailField(unique=True, verbose_name="邮箱")

    class Meta:
        db_table = 'acg_user'