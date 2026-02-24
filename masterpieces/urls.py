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
]