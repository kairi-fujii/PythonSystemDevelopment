# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role, Address

# UserAdminを継承して、一覧表示などをカスタマイズ
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # 一覧画面に表示する項目を定義
    # フィールドのverbose_name（日本語名）が自動でヘッダーに使われます
    list_display = ('username', 'email', 'role', 'points', 'is_staff')
    # 役割やスタッフ権限で絞り込みができるようにする
    list_filter = ('role', 'is_staff', 'is_superuser')
    # ユーザー名とメールアドレスで検索できるようにする
    search_fields = ('username', 'email')
    
    # 編集画面の項目は、一旦UserAdminのデフォルトを使用
    # fieldsets = ... (ここではカスタマイズしない)

# Roleモデルの管理画面
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name')
    search_fields = ('name', 'display_name')

# Addressモデルの管理画面
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipient_name', 'prefecture', 'is_default')
    list_filter = ('prefecture', 'is_default')
    search_fields = ('user__username', 'recipient_name')