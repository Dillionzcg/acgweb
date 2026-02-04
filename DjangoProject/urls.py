from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 修改为最简单的包含方式
    path('', include('acg_core.urls')),
    path('auth/', include('authentication.urls')),
    path('chat/', include('chat.urls')),
]