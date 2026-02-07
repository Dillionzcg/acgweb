from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_home, name='community_home'),
    path('topics/', views.topic_list, name='topic_list'),
    path('topics/create/', views.create_topic, name='create_topic'),  # 新增
    path('topics/<int:pk>/', views.topic_detail, name='topic_detail'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
]