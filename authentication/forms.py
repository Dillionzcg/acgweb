from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class RegisterForm(forms.Form):
    username = forms.CharField(min_length=3, max_length=20, label="用户名")
    email = forms.EmailField(label="邮箱")
    phone = forms.CharField(min_length=11, max_length=11, label="手机号")
    password = forms.CharField(min_length=6, widget=forms.PasswordInput, label="密码")
    confirm_password = forms.CharField(min_length=6, widget=forms.PasswordInput, label="确认密码")

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^1[3-9]\d{9}$', phone):
            raise ValidationError("手机号格式不正确")
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("该手机号已被注册")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("该邮箱已被注册")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        cpwd = cleaned_data.get("confirm_password")
        if pwd and cpwd and pwd != cpwd:
            raise ValidationError("两次输入的密码不一致")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(label="账号")
    password = forms.CharField(widget=forms.PasswordInput, label="密码")
