from django.shortcuts import render
from django.views.generic import TemplateView

# ========================================
# メインダッシュボード画面（トップページ）
# ========================================

class IndexView(TemplateView):
    # 使用するテンプレートファイルのパスを指定
    # base.html を継承し、ダッシュボード用に構成された index.html を描画
    template_name = 'main/index.html'


# ================================
# 商品関連の画面ビュー
# ================================

class ProductListView(TemplateView):
    # 商品一覧を表示するためのテンプレートを描画
    # 今後は「検索」「カテゴリフィルター」「並び替え」などの機能も追加予定
    template_name = 'main/product_list.html'

class ProductDetailView(TemplateView):
    # 商品の詳細情報を表示するテンプレートを描画
    # 商品画像、説明、出品者情報に加えて、コメント（質問）も本画面に統合して表示する
    template_name = 'main/product_detail.html'

class ProductCreateView(TemplateView):
    # 新しい商品を出品（登録）するための画面
    # カテゴリ選択、状態、価格、説明、画像アップロード等の項目を含む予定
    template_name = 'main/product_create.html'

class MyProductManageView(TemplateView):
    # 自分が出品した商品の管理画面
    # 商品ごとの編集・削除・ステータス変更ボタンを用意予定
    template_name = 'main/my_product_manage.html'


# ================================
# 取引関連の画面ビュー
# ================================

class TransactionListView(TemplateView):
    # ユーザーが関わる取引（購入・販売）の一覧画面
    # 商品名、価格、相手ユーザー、取引ステータス、日付などを表示
    template_name = 'main/transaction_list.html'

class TransactionDetailView(TemplateView):
    # 特定の取引に関する詳細情報を表示する画面
    # 発送先、メッセージ履歴、レビュー投稿フォームなどを配置予定
    template_name = 'main/transaction_detail.html'


# ================================
# インタラクション関連の画面ビュー
# ================================

class FavoriteListView(TemplateView):
    # ユーザーがお気に入り登録した商品の一覧画面
    # 商品画像・名前・価格に加え、お気に入り解除操作なども搭載予定
    template_name = 'main/favorite_list.html'

class MessageExchangeView(TemplateView):
    # 取引中のユーザー間でメッセージをやり取りするチャット形式の画面
    # 発言者とメッセージ、送信日時を並べて表示
    template_name = 'main/message.html'

class NotificationListView(TemplateView):
    # ユーザーに対して送られた通知の一覧画面
    # 未読・既読の状態表示、通知リンクへのジャンプ機能なども含める予定
    template_name = 'main/notification_list.html'
