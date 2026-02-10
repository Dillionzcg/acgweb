from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse

class LoginRequiredMiddleware:
    """
    Middleware that redirects all unauthenticated users to the login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 排除路径
        path = request.path_info
        
        # 1. 如果用户已登录，正常放行
        if request.user.is_authenticated:
            return self.get_response(request)

        # 2. 定义豁免列表
        exempt_urls = [
            reverse('index'),
            reverse('login'),
            reverse('register'),
            reverse('logout'),
            reverse('kanban_chat'),
        ]
        
        # 3. 检查是否在豁免列表中，或者是后台、静态文件、媒体文件
        is_exempt = any(path == url for url in exempt_urls) or \
                    path.startswith('/admin/') or \
                    path.startswith(settings.STATIC_URL) or \
                    (settings.MEDIA_URL and path.startswith(settings.MEDIA_URL))

        if is_exempt:
            return self.get_response(request)

        # 4. 否则对于普通请求跳转到登录页，对于 AJAX 请求返回 403
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or \
           request.content_type == 'application/json':
            return JsonResponse({'error': 'Login required'}, status=403)

        return redirect(f"{reverse('login')}?next={path}")

        