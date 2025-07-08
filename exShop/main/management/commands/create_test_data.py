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
from main.models import (
    Category, Condition, Status, TransactionStatus, NtfType,
    Product, ProductImage, Transaction, Comment, Favorite, Message, Review, Notification
)

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
            "レディース": [("tops_lady", "トップス"), ("outer_lady", "ジャケット/アウター"), ("skirt_lady", "スカート"), ("onepiece_lady", "ワンピース"), ("shoes_lady", "靴"), ("bag_lady", "バッグ"), ("fashion_etc_lady", "その他")],
            "メンズ": [("tops_men", "トップス"), ("outer_men", "ジャケット/アウター"), ("pants_men", "パンツ"), ("shoes_men", "靴"), ("bag_men", "バッグ"), ("watch_men", "時計"), ("fashion_etc_men", "その他")],
            "ベビー・キッズ": [("baby_clothes", "ベビー服 (~95cm)"), ("kids_clothes", "キッズ服 (100cm~)"), ("stroller", "ベビーカー"), ("toy_baby", "知育玩具"), ("kids_etc", "その他")],
            "本": [("novel", "文学/小説"), ("manga_all", "漫画(全巻セット)"), ("manga_single", "漫画(単巻)"), ("business_book", "ビジネス/経済"), ("picture_book", "絵本"), ("book_etc", "その他")],
            "音楽": [("jpop_cd", "邦楽"), ("kpop_cd", "K-POP/アジア"), ("pop_cd", "洋楽"), ("anime_cd", "アニメ"), ("music_etc", "その他")],
            "ゲーム": [("console_body", "家庭用ゲーム本体"), ("console_soft", "家庭用ゲームソフト"), ("portable_body", "携帯用ゲーム本体"), ("portable_soft", "携帯用ゲームソフト"), ("pc_game", "PCゲーム"), ("game_etc", "その他")],
            "おもちゃ・ホビー・グッズ": [("figure", "フィギュア"), ("plamodel", "プラモデル"), ("trading_card", "トレーディングカード"), ("character_goods", "キャラクターグッズ"), ("hobby_etc", "その他")],
            "スマートフォン/携帯電話": [("smartphone_body", "スマートフォン本体"), ("smartphone_case", "スマホケース"), ("charger", "充電器"), ("film", "保護フィルム"), ("mobile_etc", "その他")],
            "PC/タブレット": [("laptop_pc", "ノートPC"), ("desktop_pc", "デスクトップ型PC"), ("tablet", "タブレット"), ("display", "ディスプレイ"), ("keyboard", "キーボード"), ("mouse", "マウス"), ("pc_parts", "PCパーツ"), ("pc_etc", "その他")],
            "カメラ": [("digital_camera", "デジタルカメラ"), ("video_camera", "ビデオカメラ"), ("lens", "レンズ(単焦点)"), ("lens_zoom", "レンズ(ズーム)"), ("tripod", "三脚"), ("camera_etc", "その他")],
            "生活家電": [("cleaner", "掃除機"), ("washing_machine", "洗濯機"), ("air_conditioner", "エアコン"), ("hair_dryer", "ヘアドライヤー"), ("appliance_etc", "その他")],
            "オーディオ機器": [("headphone", "ヘッドホン"), ("earphone", "イヤホン"), ("speaker", "スピーカー"), ("amplifier", "アンプ"), ("audio_etc", "その他")],
            "スポーツ": [("golf_club", "ゴルフ"), ("training_wear", "トレーニング/エクササイズ"), ("baseball_gear", "野球"), ("soccer_gear", "サッカー/フットサル"), ("sports_etc", "その他")],
            "レジャー": [("camping_tent", "テント/タープ"), ("camping_table", "テーブル/チェア"), ("fishing_rod", "ロッド"), ("fishing_reel", "リール"), ("leisure_etc", "その他")],
            "コスメ・香水・美容": [("base_makeup", "ベースメイク"), ("skin_care", "スキンケア/基礎化粧品"), ("perfume", "香水"), ("nail_care", "ネイルケア"), ("beauty_etc", "その他")],
            "インテリア・住まい・小物": [("sofa", "ソファ/ソファベッド"), ("table", "机/テーブル"), ("chair", "椅子"), ("storage", "収納家具"), ("lighting", "ライト/照明"), ("kitchenware", "キッチン/食器"), ("rug", "ラグ/カーペット/マット"), ("interior_etc", "その他")],
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
        status_on_sale, _ = Status.objects.get_or_create(name='ON_SALE', display_name='販売中')
        status_sold_out, _ = Status.objects.get_or_create(name='SOLD_OUT', display_name='売却済')

        # 取引ステータスのマスタ定義
        ts_waiting, _ = TransactionStatus.objects.get_or_create(name='WAITING_SHIPPING', display_name='発送待ち')
        ts_shipped, _ = TransactionStatus.objects.get_or_create(name='SHIPPED', display_name='発送済み')
        ts_transit, _ = TransactionStatus.objects.get_or_create(name='IN_TRANSIT', display_name='輸送中')
        ts_deliver, _ = TransactionStatus.objects.get_or_create(name='OUT_FOR_DELIVERY', display_name='配達中')
        ts_delivered, _ = TransactionStatus.objects.get_or_create(name='DELIVERED', display_name='配達済み')
        ts_completed, _ = TransactionStatus.objects.get_or_create(name='COMPLETED', display_name='取引完了')

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
        # Step 4: 商品データを作成する
        # ----------------------------------------------------------------
        self.stdout.write(self.style.NOTICE(f'Creating {NUM_PRODUCTS} products...'))
        
        # まずはPythonのリストにProductオブジェクトをためていく。
        # 一件ずつDBに保存すると、1000回のDBアクセスが発生して非常に遅くなるため。
        products_to_create = []
        
        # 商品の出品者やカテゴリをランダムに選ぶための「母集団」をあらかじめ用意しておく。
        # ループの中で毎回DBに問い合わせるのを防ぎ、パフォーマンスを向上させる。
        user_pool = list(created_users)
        category_keys = list(categories.keys())
        condition_pool = list(Condition.objects.all())

        for i in range(NUM_PRODUCTS):
            # 母集団からランダムに一つ選ぶ
            seller = random.choice(user_pool)
            category_key = random.choice(category_keys)
            category_obj = categories[category_key] # キーを使って、対応するCategoryオブジェクトを取得
            
            # Fakerを使って、それらしい商品名や説明文を生成する
            product_name = f"【美品】{category_obj.name.split(' - ')[-1]} {fake.word()}"
            description = fake.text(max_nb_chars=400)
            
            # Productモデルのインスタンス（Pythonオブジェクト）を作成する。まだDBには保存されない。
            product = Product(
                seller=seller, 
                category=category_obj, 
                condition=random.choice(condition_pool),
                name=product_name, 
                description=description, 
                price=random.randint(1000, 30000)
            )
            
            # 定義した割合に基づいて、商品を「売却済」か「販売中」に振り分ける
            if i < NUM_PRODUCTS * SOLD_RATIO:
                product.status = status_sold_out
            else:
                product.status = status_on_sale
            
            # 作成したProductオブジェクトをリストに追加
            products_to_create.append(product)
        
        # ループでためた1000件の商品オブジェクトを、1回のDBアクセスでまとめて作成する。
        # これが `bulk_create` の最も重要な使い方。
        with transaction.atomic():
            Product.objects.bulk_create(products_to_create)

        # ----------------------------------------------------------------
        # Step 5: 商品に画像を紐付ける (一件ずつ保存する修正版)
        # ----------------------------------------------------------------
        self.stdout.write(self.style.NOTICE('Attaching images to products...'))

        from pathlib import Path

        all_products = list(Product.objects.select_related('category'))
        image_base_dir = Path(settings.MEDIA_ROOT) / 'images'
        default_image_path = image_base_dir / 'no-image.png'
        product_image_base_dir = Path(settings.MEDIA_ROOT) / 'products'

        # カテゴリごとの画像ファイル一覧を作成
        category_image_map = {}
        for category_key in categories.keys():
            category_dir = image_base_dir / category_key
            if category_dir.exists() and category_dir.is_dir():
                image_files = list(category_dir.glob(f'{category_key}_*.jpg'))
                if image_files:
                    category_image_map[category_key] = image_files

        # デフォルト画像が存在するか確認
        if not default_image_path.exists():
            self.stdout.write(self.style.ERROR(f"'no-image.png' not found in {image_base_dir}. Aborting."))
            return

        image_count = 0
        with transaction.atomic():
            for product in all_products:
                # カテゴリキーを特定
                category_key = next((key for key, val in categories.items() if val == product.category), None)

                # 対象カテゴリに画像があれば使う
                image_paths = category_image_map.get(category_key, [default_image_path])
                selected_images = random.sample(image_paths, k=min(len(image_paths), random.randint(1, 3)))

                # 保存先ディレクトリ
                save_dir = product_image_base_dir / category_key
                save_dir.mkdir(parents=True, exist_ok=True)

                for i, image_path in enumerate(selected_images, start=1):
                    image_obj = ProductImage(product=product)

                    # ファイル名生成（例: 123_1.jpg）
                    _, ext = os.path.splitext(image_path.name)
                    new_filename = f"{product.id}_{i}{ext}"
                    new_save_path = save_dir / new_filename

                    # 画像ファイルを読み取り、保存
                    with open(image_path, 'rb') as f:
                        django_file = File(f)
                        # save=True でDBとファイル両方に保存
                        image_obj.image.save(str(Path(category_key) / new_filename), django_file, save=True)

                    image_count += 1

        self.stdout.write(self.style.SUCCESS(f'-> Successfully created and attached {image_count} images.'))


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
                    status=random.choice([ts_waiting,ts_shipped,ts_transit,ts_deliver,ts_delivered,ts_completed]),  # 取引ステータスをランダムに設定
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
        products_to_comment = random.sample(
            list(Product.objects.all()),
            k=int(NUM_PRODUCTS * COMMENT_RATIO)
        )

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
