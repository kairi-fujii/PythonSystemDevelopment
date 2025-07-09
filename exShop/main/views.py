from django.urls import reverse_lazy
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from main.utils.transaction import get_ordered_transaction_statuses
from .forms import *
from main.models import *
from accounts.models import *


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

# class ProductListView(TemplateView):
#     # 商品一覧を表示するためのテンプレートを描画
#     # 今後は「検索」「カテゴリフィルター」「並び替え」などの機能も追加予定
#     template_name = 'main/product_list.html'
    
class ProductListView(ListView):
    model = Product
    template_name = 'main/product_list.html'  # 使用するテンプレート
    context_object_name = 'products'          # テンプレート内の変数名
    paginate_by = 24                          # 1ページあたりの表示件数

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        query = self.request.GET.get('q', '')

        if query:
            # 商品名、説明、カテゴリ名に icontains でフィルタをかける
            # icontains：指定した文字列を含んでいる場合(大文字小文字を区別しない)
            # ここでは、商品名、説明、カテゴリ名のいずれかにクエリが含まれる商品を検索
            # 各条件を別々にフィルタしてから結合
            name_matches = Product.objects.filter(name__icontains=query)
            description_matches = Product.objects.filter(description__icontains=query)
            category_matches = Product.objects.filter(category__name__icontains=query)
            # 各クエリセットを結合し、重複を排除
            queryset = (name_matches | description_matches | category_matches).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        # 基本のコンテキストを取得
        context = super().get_context_data(**kwargs)
        # テンプレートに検索語を渡し、検索フォームに反映させる
        context['search_query'] = self.request.GET.get('q', '')

        return context

# class ProductDetailView(TemplateView):
#     # 商品の詳細情報を表示するテンプレートを描画
#     # 商品画像、説明、出品者情報に加えて、コメント（質問）も本画面に統合して表示する
#     template_name = 'main/product_detail.html'

# 商品の詳細を表示するビュークラス（CBV）
class ProductDetailView(DetailView):
    # 使用するモデルを指定（Product モデルの情報を表示する）
    model = Product
    # 使用するテンプレートファイルのパスを指定（templates/main/product_detail.html）
    template_name = 'main/product_detail.html'
    # テンプレート内で使うオブジェクトの変数名を定義（デフォルトは「object」だが、「product」として扱えるように変更）
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        # DetailViewのget_context_dataを呼び出し、既存のコンテキストを取得
        context = super().get_context_data(**kwargs)
        # 表示対象の商品（このビューで取得される Product オブジェクト）を取得
        product = self.object
        # クエリパラメータから検索語を取得。存在しなければ空文字列を設定。
        context['search_query'] = self.request.GET.get('q', '')
        # クエリパラメータからページ番号を取得。存在しなければ空文字列を設定。
        context['page'] = self.request.GET.get('page', '')
        # 商品に紐づくコメントを作成日時の降順で取得して渡す
        context['comments'] = self.object.comments.select_related('user').order_by('-created_at')


        # --- おすすめ商品の取得（同じ出品者による他の商品）---
        # 今表示している商品と同じ seller（出品者）による他の商品を最大4件取得
        # 現在表示中の商品は除外する（exclude）
        context['related_by_seller'] = Product.objects.filter(
            seller=product.seller
        ).exclude(id=product.id)

        # --- おすすめ商品の取得（同じカテゴリの商品）---
        # 今表示している商品と同じカテゴリに属する他の商品を最大4件取得
        # 現在の商品を除外し、カテゴリが設定されている場合のみフィルタする
        if product.category:  # カテゴリが null の可能性もあるためチェック
            context['related_by_category'] = Product.objects.filter(
                category=product.category
            ).exclude(id=product.id)
        else:
            context['related_by_category'] = Product.objects.none()  # カテゴリが無ければ空のクエリセット

        return context

# class ProductCreateView(TemplateView):
#     # 新しい商品を出品（登録）するための画面
#     # カテゴリ選択、状態、価格、説明、画像アップロード等の項目を含む予定
#     template_name = 'main/product_create.html'

# 商品の新規登録（出品）を行うビュー
class ProductCreateView(LoginRequiredMixin, CreateView):
    # 登録対象のモデル（Productモデル）
    model = Product

    # 使用するフォームクラス（ModelForm）
    form_class = ProductForm

    # 使用するテンプレートファイル
    template_name = 'main/product_create.html'

    # テンプレートに渡す追加のコンテキストを定義
    def get_context_data(self, **kwargs):
        # 親クラスのコンテキストを取得
        context = super().get_context_data(**kwargs)

        # POSTリクエスト時（フォーム送信時）は、ユーザーの送信データを含むフォームセットを作成
        if self.request.POST:
            context['formset'] = ProductImageFormSet(self.request.POST, self.request.FILES)
        else:
            # 初回表示時は空のフォームセットを表示（画像3枚分）
            context['formset'] = ProductImageFormSet()

        return context

    # 商品フォームがバリデーションを通過した場合の処理
    def form_valid(self, form):
        # 出品者を現在ログイン中のユーザーに設定
        form.instance.seller = self.request.user

        # 初期の販売状況を取得（例：購入可能なステータス）
        initial_status = Status.objects.filter(purchasable=True).first()

        # 初期状態が取得できたら、商品に設定する
        form.instance.status = initial_status

        # 商品情報を保存して、インスタンスを取得
        self.object = form.save()

        # 商品画像フォームセットを作成し、バリデーションチェック
        formset = ProductImageFormSet(self.request.POST, self.request.FILES, instance=self.object)

        if formset.is_valid():
            # 商品画像がすべて正しく入力されていれば保存
            formset.save()
            # 商品詳細画面へリダイレクト（仮にproduct_detailが存在する前提）
            return redirect('main:product_detail', pk=self.object.pk)
        else:
            # フォームセットにエラーがある場合はテンプレート再表示
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
        

# class MyProductManageView(TemplateView):
#     # 自分が出品した商品の管理画面
#     # 商品ごとの編集・削除・ステータス変更ボタンを用意予定
#     template_name = 'main/my_product_manage.html'

class MyProductManageView(LoginRequiredMixin, ListView):
    # ログイン中の出品者が登録した商品を一覧表示する管理画面用ビュー
    
    template_name = 'main/my_product_manage.html'  # 表示するテンプレート
    context_object_name = 'products'  # テンプレート側で使う変数名
    paginate_by = 10  # ページネーション件数

    def get_queryset(self):
        # ログインユーザーが出品した商品だけを取得
        return Product.objects.filter(seller=self.request.user).select_related('status', 'category').prefetch_related('images').order_by('-created_at')

class ProductEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # 商品の編集画面ビュー（ログイン＋出品者本人のみ編集可）

    model = Product
    form_class = ProductForm  # 編集に使うフォーム
    template_name = 'main/product_edit.html'

    def get_success_url(self):
        # 編集後は商品管理画面にリダイレクト
        return reverse_lazy('main:my_product_manage')

    def test_func(self):
        # ログインユーザーがこの商品を出品した本人かどうかを確認
        product = self.get_object()
        return self.request.user == product.seller

# 商品削除ビュー
class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    # 商品の削除確認画面と削除処理
    model = Product
    template_name = 'main/product_confirm_delete.html'
    success_url = reverse_lazy('main:my_product_manage')  # 削除成功時のリダイレクト先

    def test_func(self):
        # 出品者のみが削除可能
        product = self.get_object()
        return self.request.user == product.seller
    
# ================================
# 取引関連の画面ビュー
# ================================

# class PurchaseConfirmView(TemplateView):
#     # 購入を確定する前に、商品の詳細と購入条件を確認する画面
#     # 商品名、価格、出品者情報、購入ボタンなどを表示予定
#     # 「購入する」ボタン押下で、実際の購入処理が行われ、取引画面へ遷移する
#     template_name = 'main/purchase_confirm.html'

class PurchaseConfirmView(LoginRequiredMixin, TemplateView):
    # 使用するテンプレートファイルの指定
    template_name = 'main/purchase_confirm.html'

    def get_context_data(self, **kwargs):
        """
        GETリクエスト時にテンプレートに渡すコンテキストを準備。
        URLから商品IDを取得し、該当商品をDBから取得して渡す。
        商品がなければエラーメッセージをセット。
        """
        # 親クラスのコンテキストを取得
        context = super().get_context_data(**kwargs)

        # URLパラメータから product_id を取得
        product_id = self.kwargs.get('product_id')

        # 該当商品の取得。なければ None
        product = Product.objects.filter(pk=product_id).first()

        if not product:
            # 商品が見つからなければテンプレートでエラー表示が可能に
            context['error'] = '指定された商品が見つかりません。'
            return context

        # 商品情報をテンプレートに渡す
        context['product'] = product
        return context

    def post(self, request, *args, **kwargs):
        """
        POSTリクエスト時に購入処理を実行。
        ・URLから商品IDを取得して商品を取得
        ・商品が存在し購入可能なら取引を作成
        ・商品の販売状況は遷移ルールに従って更新
        ・購入者の配送先住所を取得し、なければ住所登録画面へ誘導
        ・取引詳細画面へリダイレクト
        """
        # URLパラメータから product_id を取得
        product_id = self.kwargs.get('product_id')

        # 商品をDBから取得
        product = Product.objects.filter(pk=product_id).first()
        if not product:
            # 商品がない場合は商品一覧に戻す
            return redirect('main:product_list')

        # 購入可能かどうかチェック（purchasable フラグを確認）
        if not product.status.purchasable:
            # 購入不可の場合は商品詳細画面に戻す
            return redirect('main:product_detail', pk=product.id)

        # 取引状況の初期状態を取得（例: "WAITING_FOR_SHIPPING" という名前で登録してあるもの）
        initial_transaction_status = TransactionStatus.objects.filter(name='WAITING_FOR_SHIPPING').first()

        # ログインユーザーの配送先住所を取得（複数ある場合は最初のものを利用）
        shipping_address = Address.objects.filter(user=request.user).first()
        if not shipping_address:
            # 配送先住所が未登録なら住所登録画面へリダイレクト
            return redirect('accounts:address_register')

        # 取引を新規作成
        transaction = Transaction.objects.create(
            product=product,               # 購入対象の商品
            buyer=request.user,            # 購入者は現在ログイン中のユーザー
            status=initial_transaction_status,  # 取引状況は初期状態に設定
            shipping_address=shipping_address,  # 配送先住所
            purchase_price=product.price,  # 購入価格は商品価格
            platform_fee=0,                # 手数料は一旦0（必要に応じて計算処理を追加）
            seller_income=product.price,  # 出品者利益は商品価格と同じ（必要に応じて調整）
        )

        # 販売状況遷移マスタから、現在の販売状況から遷移可能な次の販売状況を1件取得
        transition = StatusTransition.objects.filter(from_status=product.status).first()
        if transition:
            # 次のステータスに更新
            product.status = transition.to_status
            product.save()

        # 作成した取引の詳細画面へリダイレクト
        return redirect('main:transaction_detail', pk=transaction.pk)


# class TransactionListView(TemplateView):
#     # ユーザーが関わる取引（購入・販売）の一覧画面
#     # 商品名、価格、相手ユーザー、取引ステータス、日付などを表示予定
#     template_name = 'main/transaction_list.html'

class TransactionListView(LoginRequiredMixin, TemplateView):
    # 使用するテンプレートファイルの指定
    template_name = 'main/transaction_list.html'

    def get_context_data(self, **kwargs):
        # 親クラスから基本のコンテキストを取得
        context = super().get_context_data(**kwargs)

        # ログインユーザーが購入者または出品者として関わる取引を取得
        transactions = Transaction.objects.select_related(
            'product', 'buyer', 'status'
        ).filter(
            buyer=self.request.user
        ).order_by('-created_at')

        # コンテキストに取引一覧を追加
        context['transactions'] = transactions
        return context

# class TransactionDetailView(TemplateView):
#     # 特定の取引に関する詳細情報を表示する画面
#     # 発送先、メッセージ履歴、レビュー投稿フォームなどを配置予定
#     template_name = 'main/transaction_detail.html'

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction  # 操作対象のモデル
    template_name = 'main/transaction_detail.html'  # 使用テンプレート
    context_object_name = 'transaction'  # テンプレートで使うオブジェクト名

    def get_queryset(self):
        # 現在のログインユーザーの取引のみを対象とする
        return Transaction.objects.select_related(
            'product', 'buyer', 'status', 'shipping_address'
        ).filter(buyer=self.request.user)

    def get_context_data(self, **kwargs):
        # 親クラスのコンテキスト取得
        context = super().get_context_data(**kwargs)

        # 商品情報・画像を追加
        transaction = self.object
        context['product'] = transaction.product
        context['images'] = transaction.product.images.all()

        # ステータス表示用の情報を追加
        status_list = get_ordered_transaction_statuses()
        context['status_list'] = status_list
        context['current_status_id'] = transaction.status.id

        return context

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
