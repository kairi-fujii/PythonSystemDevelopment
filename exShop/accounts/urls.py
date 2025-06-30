# main/urls.py (新規作成)

from django.urls import path
from . import views

app_name = 'accounts' # アプリケーションの名前空間

urlpatterns = [
    # ここにviewを実行するURLを追加していく
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

]