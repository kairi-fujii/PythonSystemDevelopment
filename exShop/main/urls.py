# main/urls.py (新規作成)

from django.urls import path
from .views import *

app_name = 'main' # アプリケーションの名前空間

urlpatterns = [
    # ここにviewを実行するURLを追加していく
    # 例: path('/', index_view.as_view(), name='index'),
    # 例: path('product_list/', product_list_view.as_view(), name='product_list'),
    path('', IndexView.as_view(), name='index'),  # トップページ用のURL

    # 商品関連
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/manage/', MyProductManageView.as_view(), name='my_product_manage'),

    # 取引関連
    # path('products/<int:pk>/purchase/confirm/', PurchaseConfirmView.as_view(), name='purchase_confirm'),
    path('products/<int:product_id>/purchase/confirm/', PurchaseConfirmView.as_view(), name='purchase_confirm'),

    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),

    # インタラクション関連
    path('favorites/', FavoriteListView.as_view(), name='favorite_list'),
    path('messages/<int:transaction_id>/', MessageExchangeView.as_view(), name='message_exchange'),
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
]
