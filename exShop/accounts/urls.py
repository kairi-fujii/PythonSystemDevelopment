# main/urls.py (新規作成)

from django.urls import path
from . import views

app_name = 'accounts' # アプリケーションの名前空間

urlpatterns = [
    # ここにviewを実行するURLを追加していく
    # 例: path('signup/', views.signup_view, name='signup'),
    # 例: path('login/', views.login_view, name='login'),
]