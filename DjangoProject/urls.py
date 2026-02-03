from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 修正后的正确路径
    path('admin/', admin.site.urls),

    # 确保这一行指向你的 app
    path('', include('acg_core.urls')),
]