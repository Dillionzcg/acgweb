from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=11, unique=True, null=False, blank=False, verbose_name="手机号")
    # 邮箱保持唯一
    email = models.EmailField(unique=True, verbose_name="邮箱")

    # 新增：真实性自证字段
    # True 代表用户在弹窗中确认是真实的；False 代表用户承认是填写的非真实信息
    is_phone_real = models.BooleanField(default=True, verbose_name="手机号是否真实")
    is_email_real = models.BooleanField(default=True, verbose_name="邮箱是否真实")

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
    
    RELATIONSHIP_TYPES = (
        ('normal', '普通好友'),
        ('bestie', '基友/死党'),
        ('lover', '情侣/CP'),
        ('family', '家人'),
    )
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES, default='normal', verbose_name="关系类型")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'acg_friendship'
        unique_together = ('from_user', 'to_user')
        verbose_name = "好友关系"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"