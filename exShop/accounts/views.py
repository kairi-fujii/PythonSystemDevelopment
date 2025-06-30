from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

# CustomUserモデルを取得
User = get_user_model()

# ログインビュー
class LoginView(LoginView):
    template_name = 'accounts/login.html'  # ログインページのテンプレート

    def get_success_url(self):
        # ログインしたユーザーがどのモデルに属しているかを確認
        user = self.request.user
        # それ以外（デフォルト）は管理者ページなど
        return reverse_lazy('main:index')  # mainアプリのIndexにリダイレクト

# ログアウトビュー
class LogoutView(LogoutView):
    next_page = '/'  # ログアウト後のリダイレクト先
