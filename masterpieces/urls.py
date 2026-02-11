from django.urls import path
from . import views

# 设置 app_name 方便在模板中引用
app_name = 'masterpieces'

urlpatterns = [

    path('', views.works_center, name='works_center'),
    path('recommend/', views.recommend_work, name='recommend_work'),
    path('work/<int:work_id>/', views.work_detail, name='work_detail'),
    path('work/<int:work_id>/delete/', views.delete_work, name='delete_work'),
]