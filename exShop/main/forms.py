from django import forms
from .models import Product, ProductImage

# 商品登録用のフォーム（1商品分）
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # 入力対象のフィールドを指定（出品者やステータスはビュー側で設定）
        fields = ['name', 'description', 'price', 'category', 'condition']

# 商品画像のフォームセット（1つの商品に対して複数画像をアップロード可能にする）
ProductImageFormSet = forms.inlineformset_factory(
    parent_model=Product,                 # 親モデルは Product（1対多の「1」側）
    model=ProductImage,                  # 子モデルは ProductImage（「多」側）
    fields=['image'],                    # 入力対象のフィールド
    extra=3,                             # 最大で追加できる画像数
    can_delete=True                      # 画像削除機能を有効にする
)
