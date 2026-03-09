from django.urls import path
from . import views

# 设置 app_name 方便在模板中引用
app_name = 'masterpieces'

urlpatterns = [

    path('', views.works_center, name='works_center'),
    path('recommend/', views.recommend_work, name='recommend_work'),
    path('work/<int:work_id>/', views.work_detail, name='work_detail'),
    path('work/<int:work_id>/delete/', views.delete_work, name='delete_work'),
    path('work/<int:work_id>/comment/', views.submit_comment, name='submit_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('work/<int:work_id>/upload_image/', views.upload_work_image, name='upload_work_image'),
    path('work/<int:work_id>/add_tag/', views.add_user_tag, name='add_user_tag'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('gallery/<int:image_id>/delete/', views.delete_gallery_image, name='delete_gallery_image'),
    path('gallery/<int:image_id>/toggle-featured/', views.toggle_gallery_featured, name='toggle_gallery_featured'),
    path('user-tag/<int:tag_id>/delete/', views.delete_user_tag, name='delete_user_tag'),
    path('check-exists/', views.check_work_exists, name='check_work_exists'),
    path('work/<int:work_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    path('all/', views.all_works_view, name='all_works'),
    path('illustrations/', views.illustration_center, name='illustration_center'),
    path('illustrations/post/', views.post_illustration, name='post_illustration'),
    path('illustration/<int:pk>/', views.illustration_detail, name='illustration_detail'),
    path('illustration/<int:pk>/delete/', views.delete_illustration, name='delete_illustration'),
    path('illustration/<int:pk>/comment/', views.submit_illust_comment, name='submit_illust_comment'),
    path('illust-comment/<int:comment_id>/like/', views.like_illust_comment, name='like_illust_comment'),
    path('illust-comment/<int:comment_id>/delete/', views.delete_illust_comment, name='delete_illust_comment'),
    path('illustration/<int:pk>/favorite/', views.toggle_illustration_favorite, name='toggle_illustration_favorite'),
    path('illustrations/my-favorites/', views.my_favorite_illustrations, name='my_favorite_illustrations'),
    path('illustrations/tag/<str:tag_name>/', views.illustration_by_tag, name='illustration_by_tag'),
    path('user/<int:user_id>/follow/', views.toggle_follow, name='toggle_follow'),
]