from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from .forms import RegisterForm, LoginForm

User = get_user_model()


def register_view(request):
    """
    处理用户注册逻辑，并与看板娘小柚联动
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                # 1. 创建用户 (确保你的自定义User模型有phone字段)
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    phone=data['phone'],
                    password=data['password']
                )

                # 2. 注册成功：自动登录
                # 显式指定 backend 防止多个认证后端导致的 ValueError
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                # 3. 注册成功直接跳转首页
                return redirect('index')

            except Exception as e:
                # 捕获数据库级别的异常（如并发下的唯一键冲突）
                messages.error(request, f"FORM_INVALID:数据库有点小脾气：{str(e)}")
        else:
            # --- 核心修复：提取表单校验失败的具体原因 ---
            # 优先检查全局错误（如密码不一致），再检查具体字段错误
            error_msg = ""
            if form.non_field_errors():
                error_msg = form.non_field_errors()[0]
            else:
                for field in form:
                    if field.errors:
                        # 格式示例：“用户名：这个名字已经被占领啦！”
                        error_msg = f"{field.label}{field.errors[0]}"
                        break

            # 将错误格式化为前端脚本可识别的 FORM_INVALID:内容
            if error_msg:
                messages.error(request, f"FORM_INVALID:{error_msg}")
    else:
        form = RegisterForm()

    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    """
    处理登录逻辑
    """
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('index')
            else:
                error = "账号或密码不对的说..."
                # 同时也给登录页的小柚发信号
                messages.error(request, f"LOGIN_ERROR:{error}")
    else:
        form = LoginForm()

    return render(request, 'authentication/login.html', {'form': form, 'error': error})


def logout_view(request):
    """
    退出登录
    """
    logout(request)
    return redirect('/')