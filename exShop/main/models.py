from django.db import models
from django.conf import settings # settings.AUTH_USER_MODEL を参照するため

# ===================================
# マスタテーブル
# ===================================
class Category(models.Model):
    """商品カテゴリマスタ"""
    name = models.CharField("カテゴリ名", max_length=100, unique=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリマスタ'

    def __str__(self):
        return self.name

class Condition(models.Model):
    """商品状態マスタ"""
    name = models.CharField("状態名", max_length=100, unique=True)
    description = models.TextField("説明", blank=True)

    class Meta:
        verbose_name = '商品状態'
        verbose_name_plural = '商品状態マスタ'

    def __str__(self):
        return self.name

class Status(models.Model):
    """販売状況マスタ"""
    name = models.CharField("状況名（内部用）", max_length=50, unique=True)
    display_name = models.CharField("状況名（表示用）", max_length=50)
    purchasable = models.BooleanField("購入可能フラグ", default=False)

    class Meta:
        verbose_name = '販売状況'
        verbose_name_plural = '販売状況マスタ'

    def __str__(self):
        return self.display_name

class TransactionStatus(models.Model):
    """取引状況マスタ"""
    name = models.CharField("状況名（内部用）", max_length=50, unique=True)
    display_name = models.CharField("状況名（表示用）", max_length=50)

    class Meta:
        verbose_name = '取引状況'
        verbose_name_plural = '取引状況マスタ'

    def __str__(self):
        return self.display_name

class NtfType(models.Model):
    """通知種別マスタ"""
    name = models.CharField("種別名（内部用）", max_length=50, unique=True)
    display_name = models.CharField("種別名（表示用）", max_length=50)

    class Meta:
        verbose_name = '通知種別'
        verbose_name_plural = '通知種別マスタ'

    def __str__(self):
        return self.display_name

class StatusTransition(models.Model):
    """販売状況遷移マスタ"""
    from_status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name='transitions_from',
        verbose_name="遷移元ステータス"
    )
    to_status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name='transitions_to',
        verbose_name="遷移先ステータス"
    )
    note = models.CharField("備考", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = '販売状況遷移'
        verbose_name_plural = '販売状況遷移マスタ'
        unique_together = ('from_status', 'to_status')

    def __str__(self):
        return f"{self.from_status.display_name} → {self.to_status.display_name}"


# ===================================
# メインモデル
# ===================================
class Product(models.Model):
    """商品モデル"""
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products', verbose_name="出品者")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="カテゴリ")
    condition = models.ForeignKey(Condition, on_delete=models.PROTECT, verbose_name="商品状態")
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="販売状況")
    name = models.CharField("商品名", max_length=200)
    description = models.TextField("商品説明")
    price = models.PositiveIntegerField("価格")
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品一覧'

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    """商品画像モデル"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="商品")
    image = models.ImageField("画像", upload_to='products/')

    class Meta:
        verbose_name = '商品画像'
        verbose_name_plural = '商品画像一覧'

    def __str__(self):
        return f"{self.product.name} の画像"

class Transaction(models.Model):
    """取引モデル"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name="商品")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='transactions', verbose_name="購入者")
    status = models.ForeignKey(TransactionStatus, on_delete=models.PROTECT, verbose_name="取引状況")
    shipping_address = models.ForeignKey('accounts.Address', on_delete=models.PROTECT, verbose_name="配送先住所")
    purchase_price = models.PositiveIntegerField("購入価格")
    platform_fee = models.PositiveIntegerField("手数料", default=0)
    seller_income = models.PositiveIntegerField("出品者利益", default=0)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = '取引'
        verbose_name_plural = '取引一覧'

    def __str__(self):
        return f"{self.product.name} の取引"

# ===================================
# インタラクションモデル
# ===================================
class Comment(models.Model):
    """コメントモデル"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="投稿者")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name="商品")
    content = models.TextField("内容")
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = 'コメント'
        verbose_name_plural = 'コメント一覧'

class Favorite(models.Model):
    """お気に入りモデル"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites', verbose_name="ユーザー")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="商品")
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = 'お気に入り'
        verbose_name_plural = 'お気に入り一覧'
        unique_together = ('user', 'product')

class Message(models.Model):
    """取引メッセージモデル"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='messages', verbose_name="取引")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="送信者")
    content = models.TextField("内容")
    is_read = models.BooleanField("既読フラグ", default=False)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = '取引メッセージ'
        verbose_name_plural = '取引メッセージ一覧'

class Review(models.Model):
    """評価モデル"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='reviews', verbose_name="取引")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews', verbose_name="評価者")
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews', verbose_name="被評価者")
    rating = models.PositiveSmallIntegerField("評価点", choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField("コメント", blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = '評価'
        verbose_name_plural = '評価一覧'

class Notification(models.Model):
    """通知モデル"""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name="受信者")
    notification_type = models.ForeignKey(NtfType, on_delete=models.PROTECT, verbose_name="通知種別")
    message = models.CharField("内容", max_length=255)
    related_url = models.URLField("関連URL", blank=True, null=True)
    is_read = models.BooleanField("既読フラグ", default=False)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知一覧'