from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

# ユーザーモデル（CustomUser）を取得
User = get_user_model()


# ========================================
# 認証ビュー
# ========================================

# ログインビュー
class LoginView(DjangoLoginView):
    # 使用するテンプレートファイル
    template_name = 'accounts/login.html'

    def get_success_url(self):
        # ログイン成功時の遷移先を指定（今回はトップページ）
        return reverse_lazy('main:index')


# ログアウトビュー
class LogoutView(DjangoLogoutView):
    # ログアウト後に遷移するページのURL
    next_page = '/'


# ========================================
# アカウント関連ビュー
# ========================================

# 新規ユーザー登録画面
class RegisterView(TemplateView):
    # ユーザー登録フォーム画面のテンプレート
    template_name = 'accounts/register.html'


# ユーザープロフィール表示画面
class ProfileView(TemplateView):
    # ユーザーのプロフィール詳細を表示する画面
    # 基本情報、プロフィール画像、紹介文、住所一覧などを含める予定
    template_name = 'accounts/profile.html'


# プロフィール編集画面
class EditProfileView(TemplateView):
    # 名前、アイコン、自己紹介文などの編集を行う画面
    # 複数住所が存在する場合、ここで削除ボタンも表示予定
    template_name = 'accounts/profile_edit.html'


# ========================================
# 住所管理ビュー（登録・編集は別画面、削除は編集画面から）
# ========================================

# 住所新規登録画面
class AddressCreateView(TemplateView):
    # ユーザーが新しい住所を追加する画面
    # 宛名、郵便番号、都道府県などを入力
    template_name = 'accounts/address_create.html'


# 住所編集画面
class AddressEditView(TemplateView):
    # 既存の住所を編集する画面（対象住所はURL引数などで特定）
    # 内容変更後、プロフィール編集画面などへリダイレクトする設計
    template_name = 'accounts/address_edit.html'
    