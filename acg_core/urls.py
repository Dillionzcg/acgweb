from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index'),
    # 小柚 AI 接口
    path('api/kanban/chat/', views.kanban_chat, name='kanban_chat'),
    # 个人资料中心
    path('user_center/', views.user_center, name='user_center'),
    # 羁绊系统 (独立页面)
    path('bond_system/', views.bond_system_view, name='bond_system'),
]

# 静态文件访问（仅需在主 App 或总路由配置一次即可）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)