from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_home, name='community_home'),
    path('topics/', views.topic_list, name='topic_list'),
    path('topics/create/', views.create_topic, name='create_topic'),
    path('topics/<int:pk>/', views.topic_detail, name='topic_detail'),
    path('topics/<int:pk>/comment/', views.add_topic_comment, name='add_topic_comment'),
    path('topics/comment/<int:pk>/delete/', views.delete_topic_comment, name='delete_topic_comment'),
    path('topics/<int:pk>/delete/', views.delete_topic, name='delete_topic'),
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.create_news, name='create_news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('news/<int:pk>/like/', views.like_news, name='like_news'),
    path('news/<int:pk>/comment/', views.add_news_comment, name='add_news_comment'),
    path('news/comment/<int:pk>/delete/', views.delete_news_comment, name='delete_news_comment'),
    path('news/<int:pk>/delete/', views.delete_news, name='delete_news'),
]