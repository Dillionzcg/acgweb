from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authentication.models import User  # 导入你自定义的 User 模型


@admin.register(User)
class MyUserAdmin(UserAdmin):
    # 在后台列表页显示的字段
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_phone_real', 'is_email_real')

    # 编辑页面分栏显示（包含你新增的手机号、头像等字段）
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('phone', 'avatar', 'gender', 'bio', 'is_phone_real', 'is_email_real')}),
    )

    # 允许在创建用户时填写的字段
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('扩展信息', {'fields': ('phone', 'email')}),
    )