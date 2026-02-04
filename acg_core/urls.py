from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # 这里必须对应 views.py 里的函数名 kanban_chat
    path('api/kanban/chat/', views.kanban_chat, name='kanban_chat'),
    path('user_center/', views.user_center, name='user_center'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)