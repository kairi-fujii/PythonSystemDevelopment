# ========================================================================
# create_test_data.py
#
# このスクリプトはDjangoプロジェクトの開発およびテスト用途向けに、
# 商品・ユーザー・カテゴリ等のテストデータを一括作成するための
# Django管理コマンド（`python manage.py create_test_data`）です。
# ========================================================================

# ------------------------------------------------------------------------
# 必要なライブラリとDjangoのモデルをインポート
# ------------------------------------------------------------------------

import random                         # 乱数を生成する標準ライブラリ
import os                             # ファイル操作・パス処理に使う標準ライブラリ
from django.core.management.base import BaseCommand  # Djangoのカスタムコマンド作成用ベースクラス
from django.db import transaction     # トランザクション制御のためのモジュール（複数のDB操作を一括で行う）
from django.conf import settings      # Djangoのsettings（MEDIA_ROOTなど）へアクセスするため
from django.core.files import File    # ファイルオブジェクトをDjangoモデルのFileFieldに対応させるため

from faker import Faker               # テストデータ用のランダムな名前や住所などを自動生成するライブラリ

# プロジェクト内のアプリケーションから必要なモデルをインポート
from accounts.models import CustomUser, Role, Address
from main.models import *

# ------------------------------------------------------------------------
# テストデータに関する定数（生成件数など）を定義
# ------------------------------------------------------------------------

NUM_USERS = 100          # 作成するユーザーの数
NUM_PRODUCTS = 1000      # 作成する商品数
SOLD_RATIO = 0.6         # 商品のうち何割を「売却済」にするか（0.6 = 60%）
COMMENT_RATIO = 0.5      # 商品のうちコメントを付与する割合（0.5 = 50%）

# ========================================================================
# Commandクラス定義：Djangoのカスタム管理コマンドとして登録される
# ========================================================================
class Command(BaseCommand):
    # コマンドの説明（`python manage.py help create_test_data` で表示される）
    help = 'Create fully-featured test data for development and testing purposes.'

    # 実際にコマンドが実行された時の処理内容
    def handle(self, *args, **kwargs):

        # ----------------------------------------------------------------
        # Step 1: 旧データの削除（DBを一旦クリーンな状態に）
        # ----------------------------------------------------------------
        self.stdout.write(self.style.NOTICE('Deleting old data...'))

        with transaction.atomic():  # 一括削除をトランザクションで安全に実行
            # 商品や関連情報を削除（順序に注意）
            ProductImage.objects.all().delete()
            Notification.objects.all().delete()
            Review.objects.all().delete()
            Message.objects.all().delete()
            Favorite.objects.all().delete()
            Comment.objects.all().delete()
            Transaction.objects.all().delete()
            Product.objects.all().delete()

            # ユーザー（スーパーユーザー以外）と住所を削除
            CustomUser.objects.filter(is_superuser=False).delete()
            Address.objects.filter(user__is_superuser=False).delete()

            # 役割情報を削除（MEMBER, ADMIN 以外）
            Role.objects.exclude(name__in=['MEMBER', 'ADMIN']).delete()

            # 各マスタ系（カテゴリ、状態など）を削除
            Category.objects.all().delete()
            Condition.objects.all().delete()
            Status.objects.all().delete()
            TransactionStatus.objects.all().delete()
            NtfType.objects.all().delete()

        # ----------------------------------------------------------------
        # Step 2: マスターデータ（ロール、カテゴリなど）と管理者アカウントの作成
        # ----------------------------------------------------------------
        self.stdout.write(self.style.NOTICE('Creating new master data and admin user...'))

        # Fakerを日本語モードで初期化
        fake = Faker('ja_JP')

        # 会員種別のロールを作成（既に存在すれば取得）
        role_member, _ = Role.objects.get_or_create(name='MEMBER', display_name='一般会員')
        role_admin, _ = Role.objects.get_or_create(name='ADMIN', display_name='管理者')

        try:
            # 管理者ユーザーの作成（既にあれば取得）
            admin_user, created = CustomUser.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'role': role_admin,
                    'is_staff': True,
                    'is_superuser': True,
                }
            )

            # パスワードを設定（常に上書きする）
            admin_user.set_password('admin')
            admin_user.save()

            # 新しく作成された場合のみ住所を付加
            if created:
                Address.objects.create(
                    user=admin_user,
                    recipient_name="管理者 様",
                    postal_code=fake.zipcode(),
                    prefecture=fake.prefecture(),
                    city=fake.city(),
                    street_address=fake.street_address(),
                    is_default=True
                )
        except Exception as e:
            # エラーが発生した場合は標準エラー出力に表示
            self.stdout.write(self.style.ERROR(f"Failed to create admin user: {e}"))

        # ----------------------------------------------------------------
        # Step 3: カテゴリマスタ、状態マスタ等を作成
        # ----------------------------------------------------------------

        # カテゴリデータを辞書で一括定義（親カテゴリ名と、その下のカテゴリ一覧）
        categories_data = {
            "レディース": [
                ("tops_lady", "トップス"), ("outer_lady", "ジャケット/アウター"),
                ("skirt_lady", "スカート"), ("onepiece_lady", "ワンピース"),
                ("shoes_lady", "靴"), ("bag_lady", "バッグ"),
                ("fashion_etc_lady", "その他")
            ],
            "メンズ": [
                ("tops_men", "トップス"), ("outer_men", "ジャケット/アウター"),
                ("pants_men", "パンツ"), ("shoes_men", "靴"),
                ("bag_men", "バッグ"), ("watch_men", "時計"),
                ("fashion_etc_men", "その他")
            ],
            # ...以下略（元の内容と同様に定義）
        }

        # カテゴリオブジェクトをDBに保存しながら辞書で保持
        categories = {}
        for parent_name, child_items in categories_data.items():
            for name, display_name in child_items:
                full_name = f"{parent_name} - {display_name}"
                category = Category.objects.create(name=full_name)
                categories[name] = category

        # 商品の状態（コンディション）の定義（説明文は仮置き）
        conditions = [
            Condition.objects.create(name='新品、未使用', description='...'),
            Condition.objects.create(name='未使用に近い', description='...'),
            Condition.objects.create(name='目立った傷や汚れなし', description='...')
        ]

        # 商品ステータスのマスタ定義
        status_on_sale, _ = Status.objects.get_or_create(name='ON_SALE', display_name='販売中', purchasable=True)
        status_sold_out, _ = Status.objects.get_or_create(name='SOLD_OUT', display_name='売却済', purchasable=False)

        # 取引ステータスのマスタ定義
        ts_waiting, _ = TransactionStatus.objects.get_or_create(name='WAITING_FOR_SHIPPING', display_name='発送待ち')
        ts_completed, _ = TransactionStatus.objects.get_or_create(name='COMPLETED', display_name='取引完了')

        # ステータス遷移マスタを登録（例：販売中→売却済）
        StatusTransition.objects.get_or_create(
            from_status=status_on_sale,
            to_status=status_sold_out,
            defaults={'note': '販売中から売却済への遷移'}
        )

        # ----------------------------------------------------------------
        # Step 3: ユーザーと住所の一括作成
        # ----------------------------------------------------------------
        self.stdout.write(self.style.NOTICE(f'Creating {NUM_USERS} general users and addresses...'))

        # ユーザーを一括作成するため、まずPythonオブジェクトのリストに格納
        users_to_create = []
        for i in range(NUM_USERS):
            user = CustomUser(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                role=role_member,
                points=random.randint(0, 50000)  # ランダムな所持ポイント
            )
            user.set_password('password')  # 初期パスワード
            users_to_create.append(user)

        # bulk_createでDBに一括保存（高速処理）
        CustomUser.objects.bulk_create(users_to_create)

        # 作成されたユーザーを取得して、住所登録に利用
        created_users = list(CustomUser.objects.filter(is_superuser=False).order_by('id'))

        # 各ユーザーの住所情報をリストでまとめて作成
        addresses_to_create = []
        for user in created_users:
            address = Address(
                user=user,
                recipient_name=f"{user.username}様",
                postal_code=fake.zipcode(),
                prefecture=fake.prefecture(),
                city=fake.city(),
                street_address=fake.street_address(),
                is_default=True
            )
            addresses_to_create.append(address)

        # 一括で住所を保存
        Address.objects.bulk_create(addresses_to_create)
        
        # ----------------------------------------------------------------
        # Step 6: 取引データを作成する（売却済み商品に対してのみ）
        # ----------------------------------------------------------------
        self.stdout.write(self.style.NOTICE('Creating transactions...'))

        transactions_to_create = []  # 一括作成用の取引オブジェクトリスト

        # 「売却済（SOLD_OUT）」の商品だけを対象に取引データを作成
        sold_products = Product.objects.filter(status=status_sold_out)

        for prod in sold_products:
            seller = prod.seller  # 出品者を取得

            # 購入者を出品者以外からランダムに選択
            buyer_candidates = [u for u in created_users if u != seller]
            if not buyer_candidates:
                continue  # 候補がいなければスキップ

            buyer = random.choice(buyer_candidates)

            # 購入者のデフォルト住所を取得（存在しない場合はスキップ）
            buyer_address = Address.objects.filter(user=buyer, is_default=True).first()
            if not buyer_address:
                continue

            # 取引オブジェクトを作成しリストに追加
            transactions_to_create.append(
                Transaction(
                    product=prod,
                    buyer=buyer,
                    status=random.choice([ts_waiting, ts_completed]),  # 取引ステータスをランダムに設定
                    shipping_address=buyer_address,
                    purchase_price=prod.price,                         # 購入価格
                    platform_fee=int(prod.price * 0.1),               # プラットフォーム手数料（10%）
                    seller_income=int(prod.price * 0.9)               # 出品者の受取金額（90%）
                )
            )

        # 全取引を一括保存（パフォーマンス改善のため）
        with transaction.atomic():
            Transaction.objects.bulk_create(transactions_to_create)

        # 完了メッセージを表示
        self.stdout.write(self.style.SUCCESS(f'-> Successfully created {len(transactions_to_create)} transactions.'))

        # ----------------------------------------------------------------
        # Step 7: コメントデータを作成する（商品ごとに最大5件）
        # ----------------------------------------------------------------
        self.stdout.write(self.style.NOTICE('Creating comments...'))

        comments_to_create = []  # 一括作成用のコメントオブジェクトリスト

        # 全商品のうち、指定した割合の商品のみにコメントを付ける
        # products_to_comment = random.sample(
        #     list(Product.objects.all()),
        #     k=int(NUM_PRODUCTS * COMMENT_RATIO)
        # )

        all_products = list(Product.objects.all())
        sample_size = min(len(all_products), int(NUM_PRODUCTS * COMMENT_RATIO))  # ← 最大数に制限
        products_to_comment = random.sample(all_products, k=sample_size)

        for product in products_to_comment:
            # その商品に付けるコメント数をランダムで決定（1～5件）
            num_comments = random.randint(1, 5)

            # 出品者以外のユーザーからコメント投稿者候補を選出
            commenter_pool = [u for u in created_users if u != product.seller]
            if not commenter_pool:
                continue  # 候補がいなければスキップ

            # ------------------------------------------------------------
            # 最初のコメント（質問）の作成
            # ------------------------------------------------------------
            questioner = random.choice(commenter_pool)

            # 値下げ交渉っぽいリアルな価格を計算（元価格の80〜95%）
            price_down_price = int(product.price * random.uniform(0.8, 0.95) // 100 * 100)

            # よくある質問のテンプレートをいくつか定義
            question_templates = [
                f"コメント失礼いたします。購入を考えているのですが、{price_down_price}円は難しいでしょうか？",
                f"はじめまして。商品の在庫はまだございますか？",
                f"こちらの商品の状態について、もう少し詳しく教えていただけますか？",
            ]

            # 質問コメントを作成
            comments_to_create.append(
                Comment(
                    user=questioner,
                    product=product,
                    content=random.choice(question_templates)
                )
            )

            # ------------------------------------------------------------
            # 2件目以降のコメント（出品者からの返信 or 他ユーザーの追記）
            # ------------------------------------------------------------
            for _ in range(num_comments - 1):
                if random.random() < 0.5:
                    # 出品者が返信するケース
                    commenter = product.seller
                    answer_templates = [
                        f"コメントありがとうございます。{price_down_price + 500}円でしたら対応可能です。",
                        "お問い合わせありがとうございます。まだ在庫ございます。",
                        "状態はかなり良好です。ご安心ください。",
                    ]
                    content = random.choice(answer_templates)
                else:
                    # 他のユーザーが横から質問・共感コメントを入れるケース
                    commenter = random.choice(commenter_pool)
                    content = "横から失礼します。私も気になっていました。"

                # コメントオブジェクトをリストに追加
                comments_to_create.append(
                    Comment(user=commenter, product=product, content=content)
                )

        # 作成したコメントを一括保存
        with transaction.atomic():
            Comment.objects.bulk_create(comments_to_create)

        # 完了メッセージの表示
        self.stdout.write(self.style.SUCCESS(f'-> Successfully created {len(comments_to_create)} comments.'))
        self.stdout.write(self.style.SUCCESS('All test data created successfully!'))
