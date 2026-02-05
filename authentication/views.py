from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from .forms import RegisterForm, LoginForm
import json

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


# --- Friend System Views ---
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Friendship

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)
    
    users = User.objects.filter(
        Q(username__icontains=query) | Q(id__icontains=query)
    ).exclude(id=request.user.id).values('id', 'username', 'avatar', 'bio')[:10]
    
    # Check friendship status for each user
    results = []
    for u in users:
        status = 'none'
        # Check if sent request
        if Friendship.objects.filter(from_user=request.user, to_user_id=u['id'], status='pending').exists():
            status = 'sent'
        # Check if received request
        elif Friendship.objects.filter(from_user_id=u['id'], to_user=request.user, status='pending').exists():
            status = 'received'
        # Check if already friends
        elif Friendship.objects.filter(
            (Q(from_user=request.user, to_user_id=u['id']) | Q(from_user_id=u['id'], to_user=request.user)),
            status='accepted'
        ).exists():
            status = 'friend'
            
        u['friend_status'] = status
        results.append(u)

    return JsonResponse(results, safe=False)

@login_required
def send_friend_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            target_id = data.get('target_id')
            target_user = User.objects.get(id=target_id)
            
            # Check if already exists
            if Friendship.objects.filter(
                (Q(from_user=request.user, to_user=target_user) | Q(from_user=target_user, to_user=request.user))
            ).exists():
                return JsonResponse({'status': 'error', 'message': '关系已存在'})
            
            Friendship.objects.create(from_user=request.user, to_user=target_user)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def handle_friend_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request_id = data.get('request_id')
            action = data.get('action') # accept, reject
            
            friendship = Friendship.objects.get(id=request_id, to_user=request.user)
            
            if action == 'accept':
                friendship.status = 'accepted'
                friendship.save()
            elif action == 'reject':
                friendship.status = 'rejected'
                friendship.save() # Or delete
                
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_friends_data(request):
    # Get all friends
    friends_rel = Friendship.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)),
        status='accepted'
    ).select_related('from_user', 'to_user')
    
    friends = []
    for rel in friends_rel:
        friend = rel.to_user if rel.from_user == request.user else rel.from_user
        friends.append({
            'id': friend.id,
            'username': friend.username,
            'avatar': friend.avatar.url if friend.avatar else None,
            'bio': friend.bio
        })
        
    # Get pending requests
    pending = Friendship.objects.filter(to_user=request.user, status='pending').select_related('from_user')
    requests = [{
        'id': req.id,
        'from_user': {
            'id': req.from_user.id,
            'username': req.from_user.username,
            'avatar': req.from_user.avatar.url if req.from_user.avatar else None
        },
        'created_at': req.created_at.strftime("%Y-%m-%d %H:%M")
    } for req in pending]
    
    return JsonResponse({'friends': friends, 'requests': requests})

def user_list_api(request):
    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)
    users = User.objects.exclude(id=request.user.id).values('id', 'username')
    return JsonResponse(list(users), safe=False)