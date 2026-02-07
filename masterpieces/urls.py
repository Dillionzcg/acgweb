from django.urls import path
from . import views

# 设置 app_name 方便在模板中引用
app_name = 'masterpieces'

urlpatterns = [

    path('works/', views.works_center, name='works_center'),
]