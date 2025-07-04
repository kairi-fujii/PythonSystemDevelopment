from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.conf import settings  
from django.conf.urls.static import static 


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # '' で始まるURLは main.urls.py を参照する
    path('', include('main.urls')),
    
    # '/accounts/' で始まるURLは accounts.urls.py を参照する
    path('accounts/', include('accounts.urls')),
]

# 開発環境（DEBUG=True）でのみメディアファイルにアクセスできるようにする設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)