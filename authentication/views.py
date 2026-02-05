from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages  # 必须导入
from .forms import RegisterForm, LoginForm

User = get_user_model()


def register_view(request):
    """
    处理用户注册逻辑
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                # 1. 创建用户
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    phone=data['phone'],
                    password=data['password']
                )

                # 2. 注册成功：自动登录
                # 指定 backend 解决 "multiple authentication backends" 的报错
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                # 3. 注册成功直接跳转首页
                return redirect('index')
            except Exception as e:
                # 捕获可能的数据库异常并告知小柚
                messages.error(request, f"FORM_INVALID:数据库保存失败啦：{str(e)}")
        else:
            # --- 核心逻辑：提取表单校验失败的具体原因并传给小柚 ---
            error_msg = ""
            # 优先获取全局错误（如两个密码不一致）
            if form.non_field_errors():
                error_msg = form.non_field_errors()[0]
            else:
                # 否则获取第一个字段的错误（如手机号重复、用户名重复）
                for field in form:
                    if field.errors:
                        error_msg = f"{field.label}{field.errors[0]}"
                        break

            # 发送格式化的错误消息，前端脚本会解析冒号后的部分
            if error_msg:
                messages.error(request, f"FORM_INVALID:{error_msg}")
    else:
        form = RegisterForm()

    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    """
    处理登录逻辑，包含小柚联动
    """
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Django 的 authenticate 会检查用户名、邮箱或手机号（取决于你的 backends 配置）
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('index')
            else:
                error = "账号或密码不对的说..."
                # 核心修复：通过 messages 发送信号给前端脚本
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