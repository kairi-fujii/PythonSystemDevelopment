# main/urls.py (新規作成)

from django.urls import path
from . import views

app_name = 'main' # アプリケーションの名前空間

urlpatterns = [
    # ここにviewを実行するURLを追加していく
    # 例: path('/', views.index_view, name='index'),
    # 例: path('product_list/', views.product_list_view, name='product_list'),
]