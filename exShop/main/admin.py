# main/admin.py

# Django管理サイトにモデルを登録するためのモジュール
from django.contrib import admin

# このアプリケーションで使用しているモデル群をインポート
from .models import (
    Category, Condition, Status, TransactionStatus, NtfType,  # 各種マスタモデル
    Product, ProductImage, Transaction, Comment, Favorite,StatusTransition,     # メイン機能に関するモデル
    Message, Review, Notification                              # インタラクション系モデル
)

# ===============================================================
# 商品画像を商品管理画面に埋め込んで登録・編集できるようにする
# ===============================================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage      # インライン編集の対象モデルを指定
    extra = 1                 # 追加用フォームを1つ表示（空行）

# ===============================================================
# 商品モデルに対する管理画面のカスタマイズ
# ===============================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 一覧画面に表示するカラムを指定
    list_display = ('name', 'seller', 'price', 'status', 'condition', 'created_at')
    
    # 絞り込みフィルタとして使うフィールドを指定
    list_filter = ('status', 'category', 'condition')
    
    # 検索対象とするフィールドを指定（外部キーのフィールドも検索可能）
    search_fields = ('name', 'description', 'seller__username')
    
    # 商品画像をインラインで追加・編集できるようにする
    inlines = [ProductImageInline]

    # 1ページに表示する件数（ページング対応）
    list_per_page = 20

    # 外部キーの項目を検索ボックスに置き換える（選択肢が多い場合の対策）
    autocomplete_fields = ['seller', 'category', 'condition', 'status']

# ===============================================================
# 取引モデルに対する管理画面のカスタマイズ
# ===============================================================
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'buyer', 'status', 'purchase_price', 'created_at')
    list_filter = ('status',)
    search_fields = ('product__name', 'buyer__username')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')  # 作成日時・更新日時は編集不可にする
    autocomplete_fields = ['product', 'buyer', 'status', 'shipping_address']

# ===============================================================
# コメントモデルのカスタマイズ
# ===============================================================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'content_summary', 'created_at')
    search_fields = ('product__name', 'user__username', 'content')

    # 内容が長すぎると管理画面で見づらいので、抜粋表示
    @admin.display(description='内容（抜粋）')
    def content_summary(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content

# ===============================================================
# お気に入りモデルのカスタマイズ
# ===============================================================
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'created_at')
    search_fields = ('product__name', 'user__username')

# ===============================================================
# 評価（レビュー）モデルのカスタマイズ
# ===============================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'reviewer', 'reviewee', 'rating', 'created_at')
    list_filter = ('rating',)  # 評価点での絞り込み
    search_fields = ('transaction__product__name', 'reviewer__username', 'reviewee__username')

# ===============================================================
# 通知モデルのカスタマイズ
# ===============================================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('recipient__username', 'message')

# ===============================================================
# 販売状況遷移マスタの管理画面
# 各販売ステータスの「遷移元」→「遷移先」のルールを管理する
# ===============================================================
@admin.register(StatusTransition)
class StatusTransitionAdmin(admin.ModelAdmin):
    list_display = ('from_status', 'to_status')  # 一覧表示項目
    list_filter = ('from_status', 'to_status',)   # 絞り込み項目
    search_fields = ('from_status__display_name', 'to_status__display_name')  # 検索用項目
    autocomplete_fields = ['from_status', 'to_status']  # ステータスを検索型にする（選択肢多い時の対策）


# ===============================================================
# マスタモデルの管理画面（カテゴリ・状態など）
# ===============================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    search_fields = ('name', 'display_name')

@admin.register(TransactionStatus)
class TransactionStatusAdmin(admin.ModelAdmin):
    search_fields = ('name', 'display_name')

@admin.register(NtfType)
class NtfTypeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'display_name')


# ===============================================================
# メッセージモデルはデフォルトのまま登録（最低限の管理用途のみ想定）
# ===============================================================
admin.site.register(Message)
