from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from .forms import RegisterForm, LoginForm

User = get_user_model()


def login_view(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # authenticate 会根据你的 backends.py 配置检查账号
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('index')
            else:
                error = "账号或密码不对的说..."
                # 发送给小柚的信号
                messages.error(request, f"LOGIN_ERROR:{error}")
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form, 'error': error})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    phone=data['phone'],
                    password=data['password']
                )
                # 显式指定 backend 防止 ValueError
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('index')
            except Exception as e:
                messages.error(request, f"FORM_INVALID:数据库保存失败啦：{str(e)}")
        else:
            # 提取第一个错误发送给小柚
            error_msg = next((f"{f.label}{f.errors[0]}" for f in form if f.errors),
                             form.non_field_errors()[0] if form.non_field_errors() else "表单错误")
            messages.error(request, f"FORM_INVALID:{error_msg}")
    else:
        form = RegisterForm()
    return render(request, 'authentication/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')