# main/urls.py (新規作成)

from django.urls import path
from .views import *

app_name = 'accounts' # アプリケーションの名前空間

urlpatterns = [
    # ここにviewを実行するURLを追加していく
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    # プロフィール編集
    path('profile/edit/', EditProfileView.as_view(), name='profile_edit'),

    # ユーザー情報（マイページ的な画面）
    path('profile/', ProfileView.as_view(), name='profile'),

    # 住所管理（登録／編集）
    path('addresses/create/', AddressCreateView.as_view(), name='address_create'),
    path('addresses/edit/', AddressEditView.as_view(), name='address_edit'),

]