from django.contrib import admin
from django.urls import path
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # '' で始まるURLは main.urls.py を参照する
    path('', include('main.urls')),
    
    # '/accounts/' で始まるURLは accounts.urls.py を参照する
    path('accounts/', include('accounts.urls')),
]
