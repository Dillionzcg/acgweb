from django.urls import path
from . import views

urlpatterns = [
    # 账号基础功能
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # 好友系统 API
    path('api/search/', views.search_users, name='search_users'),
    path('api/friend/request/', views.send_friend_request, name='send_friend_request'),
    path('api/friend/handle/', views.handle_friend_request, name='handle_friend_request'),
    path('api/friends/', views.get_friends_data, name='get_friends_data'),
    path('api/users/', views.user_list_api, name='user_list_api'),
]