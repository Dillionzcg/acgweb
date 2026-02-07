from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # 修改为最简单的包含方式
    path('', include('acg_core.urls')),
    path('auth/', include('authentication.urls')),
    path('chat/', include('chat.urls')),
    path('works/', include('masterpieces.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)