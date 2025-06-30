# main/admin.py

from django.contrib import admin
from .models import (
    Category, Condition, Status, TransactionStatus, NtfType,
    Product, ProductImage, Transaction, Comment, Favorite, Message, Review, Notification
)

# ===================================
# インラインモデル定義
# ===================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# ===================================
# モデルごとのAdminクラス定義
# ===================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'status', 'condition', 'created_at')
    list_filter = ('status', 'category', 'condition')
    search_fields = ('name', 'description', 'seller__username')
    inlines = [ProductImageInline]
    list_per_page = 20
    # 関連フィールドを自動でプルダウンではなく、検索ボックス形式にする（パフォーマンス向上）
    autocomplete_fields = ['seller', 'category', 'condition', 'status']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'buyer', 'status', 'purchase_price', 'created_at')
    list_filter = ('status',)
    search_fields = ('product__name', 'buyer__username')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['product', 'buyer', 'status', 'shipping_address']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'content_summary', 'created_at')
    search_fields = ('product__name', 'user__username', 'content')

    @admin.display(description='内容（抜粋）')
    def content_summary(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'created_at')
    search_fields = ('product__name', 'user__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'reviewer', 'reviewee', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('transaction__product__name', 'reviewer__username', 'reviewee__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('recipient__username', 'message')


# ===================================
# マスタテーブルの単純登録
# ===================================
# 基本的にはモデルのverbose_nameが使われるので、シンプルな登録で十分
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

# Messageは検索やフィルタが不要と判断した場合
admin.site.register(Message)