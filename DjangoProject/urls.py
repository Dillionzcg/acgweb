from django.contrib import admin
from django.urls import path, include

urlpatterns = [
<<<<<<< HEAD
    path('admin/', admin.site.urls),
    path('', include('acg_core.urls')),
    path('chat/', include('chat.urls')),
=======
    # 修正后的正确路径
    path('admin/', admin.site.urls),

    # 确保这一行指向你的 app
    path('', include('acg_core.urls')),
>>>>>>> 4d04697ac3bdaf0b50168b1a496a436f7cff8b65
]