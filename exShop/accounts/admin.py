# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role, Address

# UserAdminを継承して、一覧表示などをカスタマイズ
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    # ① 一覧画面の表示項目
    list_display = ('username', 'email', 'role', 'points', 'is_staff')
    
    # ② 絞り込みフィルター
    list_filter = ('role', 'is_staff', 'is_superuser', 'groups')
    
    # ③ 検索ボックスの対象フィールド
    search_fields = ('username', 'email')
    
    # ④ 編集画面のセクションとフィールドのレイアウト
    fieldsets = (
        # セクション名, { 'fields': (フィールド名のタプル,) }
        (None, {'fields': ('username', 'password')}),
        ('個人情報', {'fields': ('first_name', 'last_name', 'email')}),
        
        # ★★★ ここでロールとポイントを編集可能にする ★★★
        ('カスタム情報', {'fields': ('role', 'points', 'profile_image', 'introduction')}),
        
        # ★★★ グループとパーミッションを削除し、is_active等のみに限定 ★★★
        ('権限', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        
        ('重要な日時', {'fields': ('last_login', 'date_joined')}),
    )

    # ⑤ 新規作成画面のフィールドレイアウト
    #   (fieldsetsと合わせておくと整合性が取れる)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'password2'),
        }),
    )

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