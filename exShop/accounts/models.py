from django.db import models
from django.contrib.auth.models import AbstractUser

# ===================================
# マスタテーブル
# ===================================
class Role(models.Model):
    """役割マスタ"""
    name = models.CharField("役割名（内部用）", max_length=20, unique=True)
    display_name = models.CharField("役割名（表示用）", max_length=50)

    # モデルの表示名を定義
    class Meta:
        verbose_name = '役割'
        verbose_name_plural = '役割マスタ'

    def __str__(self):
        return self.display_name

class Address(models.Model):
    """住所モデル"""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='addresses', verbose_name="ユーザー")
    recipient_name = models.CharField("宛名", max_length=100)
    postal_code = models.CharField("郵便番号", max_length=8)
    prefecture = models.CharField("都道府県", max_length=10)
    city = models.CharField("市区町村", max_length=100)
    street_address = models.CharField("番地・ビル名", max_length=255)
    phone_number = models.CharField("電話番号", max_length=15, blank=True, null=True)
    is_default = models.BooleanField("デフォルト設定", default=False)

    # モデルの表示名を定義
    class Meta:
        verbose_name = '住所'
        verbose_name_plural = '住所一覧'

    def __str__(self):
        return f"{self.user.username} - {self.recipient_name}"

# ===================================
# メインのユーザーモデル
# ===================================
class CustomUser(AbstractUser):
    """カスタムユーザーモデル"""
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name="役割", null=True, blank=True)
    points = models.PositiveIntegerField("保有ポイント", default=0)
    profile_image = models.ImageField("プロフィール画像", upload_to='profiles/', null=True, blank=True)
    introduction = models.TextField("自己紹介文", max_length=1000, blank=True)

    # モデルの表示名を定義
    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー一覧'

    def __str__(self):
        return self.username