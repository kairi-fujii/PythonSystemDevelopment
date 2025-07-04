# main/management/commands/create_test_data.py

# =================================================================
# 1. 必要なライブラリやモジュールをインポートする
# =================================================================
import random
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.core.files import File
from faker import Faker
from accounts.models import CustomUser, Role, Address
from main.models import (
    Category, Condition, Status, TransactionStatus, NtfType,
    Product, ProductImage, Transaction, Comment, Favorite, Message, Review, Notification
)

# =================================================================
# 2. パラメータ定義
# =================================================================
NUM_USERS = 100
NUM_PRODUCTS = 1000
SOLD_RATIO = 0.6
COMMENT_RATIO = 0.5
# =================================================================


class Command(BaseCommand):
    help = 'Create fully-featured test data for development and testing purposes.'

    def handle(self, *args, **kwargs):
        
        # =================================================================
        # Step 1, 2, 3 (データ削除、マスタ作成、ユーザー作成)
        # =================================================================
        # ... (これらのセクションは変更なし) ...
        self.stdout.write(self.style.NOTICE('Deleting old data...'))
        with transaction.atomic():
            ProductImage.objects.all().delete(); Notification.objects.all().delete(); Review.objects.all().delete(); Message.objects.all().delete(); Favorite.objects.all().delete(); Comment.objects.all().delete(); Transaction.objects.all().delete(); Product.objects.all().delete()
            CustomUser.objects.filter(is_superuser=False).delete(); Address.objects.filter(user__is_superuser=False).delete(); Role.objects.exclude(name__in=['MEMBER', 'ADMIN']).delete()
            Category.objects.all().delete(); Condition.objects.all().delete(); Status.objects.all().delete(); TransactionStatus.objects.all().delete(); NtfType.objects.all().delete()
        self.stdout.write(self.style.NOTICE('Creating new master data and admin user...'))
        fake = Faker('ja_JP')
        role_member, _ = Role.objects.get_or_create(name='MEMBER', display_name='一般会員')
        role_admin, _ = Role.objects.get_or_create(name='ADMIN', display_name='管理者')
        try:
            admin_user, created = CustomUser.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'role': role_admin, 'is_staff': True, 'is_superuser': True,})
            admin_user.set_password('admin'); admin_user.save()
            if created: Address.objects.create(user=admin_user, recipient_name="管理者 様", postal_code=fake.zipcode(), prefecture=fake.prefecture(), city=fake.city(), street_address=fake.street_address(), is_default=True)
        except Exception as e: self.stdout.write(self.style.ERROR(f"Failed to create admin user: {e}"))
        categories_data = {"レディース": [("tops_lady", "トップス"), ("outer_lady", "ジャケット/アウター"), ("skirt_lady", "スカート"), ("onepiece_lady", "ワンピース"), ("shoes_lady", "靴"), ("bag_lady", "バッグ"), ("fashion_etc_lady", "その他")],"メンズ": [("tops_men", "トップス"), ("outer_men", "ジャケット/アウター"), ("pants_men", "パンツ"), ("shoes_men", "靴"), ("bag_men", "バッグ"), ("watch_men", "時計"), ("fashion_etc_men", "その他")],"ベビー・キッズ": [("baby_clothes", "ベビー服 (~95cm)"), ("kids_clothes", "キッズ服 (100cm~)"), ("stroller", "ベビーカー"), ("toy_baby", "知育玩具"), ("kids_etc", "その他")],"本": [("novel", "文学/小説"), ("manga_all", "漫画(全巻セット)"), ("manga_single", "漫画(単巻)"), ("business_book", "ビジネス/経済"), ("picture_book", "絵本"), ("book_etc", "その他")],"音楽": [("jpop_cd", "邦楽"), ("kpop_cd", "K-POP/アジア"), ("pop_cd", "洋楽"), ("anime_cd", "アニメ"), ("music_etc", "その他")],"ゲーム": [("console_body", "家庭用ゲーム本体"), ("console_soft", "家庭用ゲームソフト"), ("portable_body", "携帯用ゲーム本体"), ("portable_soft", "携帯用ゲームソフト"), ("pc_game", "PCゲーム"), ("game_etc", "その他")],"おもちゃ・ホビー・グッズ": [("figure", "フィギュア"), ("plamodel", "プラモデル"), ("trading_card", "トレーディングカード"), ("character_goods", "キャラクターグッズ"), ("hobby_etc", "その他")],"スマートフォン/携帯電話": [("smartphone_body", "スマートフォン本体"), ("smartphone_case", "スマホケース"), ("charger", "充電器"), ("film", "保護フィルム"), ("mobile_etc", "その他")],"PC/タブレット": [("laptop_pc", "ノートPC"), ("desktop_pc", "デスクトップ型PC"), ("tablet", "タブレット"), ("display", "ディスプレイ"), ("keyboard", "キーボード"), ("mouse", "マウス"), ("pc_parts", "PCパーツ"), ("pc_etc", "その他")],"カメラ": [("digital_camera", "デジタルカメラ"), ("video_camera", "ビデオカメラ"), ("lens", "レンズ(単焦点)"), ("lens_zoom", "レンズ(ズーム)"), ("tripod", "三脚"), ("camera_etc", "その他")],"生活家電": [("cleaner", "掃除機"), ("washing_machine", "洗濯機"), ("air_conditioner", "エアコン"), ("hair_dryer", "ヘアドライヤー"), ("appliance_etc", "その他")],"オーディオ機器": [("headphone", "ヘッドホン"), ("earphone", "イヤホン"), ("speaker", "スピーカー"), ("amplifier", "アンプ"), ("audio_etc", "その他")],"スポーツ": [("golf_club", "ゴルフ"), ("training_wear", "トレーニング/エクササイズ"), ("baseball_gear", "野球"), ("soccer_gear", "サッカー/フットサル"), ("sports_etc", "その他")],"レジャー": [("camping_tent", "テント/タープ"), ("camping_table", "テーブル/チェア"), ("fishing_rod", "ロッド"), ("fishing_reel", "リール"), ("leisure_etc", "その他")],"コスメ・香水・美容": [("base_makeup", "ベースメイク"), ("skin_care", "スキンケア/基礎化粧品"), ("perfume", "香水"), ("nail_care", "ネイルケア"), ("beauty_etc", "その他")],"インテリア・住まい・小物": [("sofa", "ソファ/ソファベッド"), ("table", "机/テーブル"), ("chair", "椅子"), ("storage", "収納家具"), ("lighting", "ライト/照明"), ("kitchenware", "キッチン/食器"), ("rug", "ラグ/カーペット/マット"), ("interior_etc", "その他")],}
        categories = {}
        for parent_name, child_items in categories_data.items():
            for name, display_name in child_items: categories[name] = Category.objects.create(name=f"{parent_name} - {display_name}")
        conditions = [Condition.objects.create(name=name, description=desc) for name, desc in [('新品、未使用', '...'), ('未使用に近い', '...'), ('目立った傷や汚れなし', '...')]]
        status_on_sale, _ = Status.objects.get_or_create(name='ON_SALE', display_name='販売中')
        status_sold_out, _ = Status.objects.get_or_create(name='SOLD_OUT', display_name='売却済')
        ts_waiting, _ = TransactionStatus.objects.get_or_create(name='WAITING_FOR_SHIPPING', display_name='発送待ち')
        ts_completed, _ = TransactionStatus.objects.get_or_create(name='COMPLETED', display_name='取引完了')
        self.stdout.write(self.style.NOTICE(f'Creating {NUM_USERS} general users and addresses...'))
        users_to_create = []
        for i in range(NUM_USERS):
            user = CustomUser(username=f'user{i+1}', email=f'user{i+1}@example.com', role=role_member, points=random.randint(0, 50000))
            user.set_password('password'); users_to_create.append(user)
        CustomUser.objects.bulk_create(users_to_create)
        created_users = list(CustomUser.objects.filter(is_superuser=False).order_by('id'))
        addresses_to_create = [Address(user=user, recipient_name=f"{user.username}様", postal_code=fake.zipcode(), prefecture=fake.prefecture(), city=fake.city(), street_address=fake.street_address(), is_default=True) for user in created_users]
        Address.objects.bulk_create(addresses_to_create)

        # =================================================================
        # Step 4: 商品データを作成する
        # =================================================================
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

        # =================================================================
        # Step 5: 商品に画像を紐付ける (一件ずつ保存する修正版)
        # =================================================================
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


        # =================================================================
        # Step 6: 取引データを作成する
        # =================================================================
        self.stdout.write(self.style.NOTICE('Creating transactions...'))
        transactions_to_create = []
        
        # ステータスが「売却済」の商品だけを対象に取引データを作成する
        sold_products = Product.objects.filter(status=status_sold_out)
        for prod in sold_products:
            # 出品者と購入者が同じにならないように、購入者をランダムに選ぶ
            seller = prod.seller
            buyer = random.choice([u for u in created_users if u != seller])
            
            # 購入者のデフォルト住所を取得
            buyer_address = Address.objects.filter(user=buyer, is_default=True).first()

            # 住所が見つかった場合のみ取引データを作成する（念のため）
            if buyer_address:
                transactions_to_create.append(
                    Transaction(
                        product=prod, 
                        buyer=buyer, 
                        status=random.choice([ts_waiting, ts_completed]), # 取引状況もランダムに
                        shipping_address=buyer_address, 
                        purchase_price=prod.price,
                        platform_fee=int(prod.price * 0.1), # 手数料は価格の10%とする
                        seller_income=int(prod.price * 0.9)
                    )
                )
        # 作成した取引オブジェクトをまとめてDBに保存
        with transaction.atomic():
            Transaction.objects.bulk_create(transactions_to_create)

        # =================================================================
        # Step 7: コメントデータを作成する
        # =================================================================
        self.stdout.write(self.style.NOTICE('Creating comments...'))
        
        comments_to_create = []
        # 全商品のうち、指定した割合の商品をコメント対象としてランダムに選ぶ
        # random.sampleはリストから重複なく要素を選ぶのに便利
        products_to_comment = random.sample(
            list(Product.objects.all()),
            k=int(NUM_PRODUCTS * COMMENT_RATIO)
        )
        
        for product in products_to_comment:
            # 1つの商品に1〜5件のコメントを付ける
            num_comments = random.randint(1, 5)
            
            # コメントするユーザーの候補（出品者以外）
            commenter_pool = [u for u in created_users if u != product.seller]
            if not commenter_pool: continue # 候補者がいなければスキップ

            # 最初のコメントは他のユーザーからの質問とする
            questioner = random.choice(commenter_pool)
            # 値下げ交渉用のリアルな価格を生成（価格の80-95%の範囲で、100円単位に丸める）
            price_down_price = int(product.price * random.uniform(0.8, 0.95) // 100 * 100)
            question_templates = [
                f"コメント失礼いたします。購入を考えているのですが、こちらの商品はお値下げ可能でしょうか？ {price_down_price}円は難しいでしょうか？",
                f"はじめまして。商品の在庫はまだございますか？",
                f"こちらの商品の状態について、もう少し詳しく教えていただけますか？",
            ]
            comments_to_create.append(
                Comment(user=questioner, product=product, content=random.choice(question_templates))
            )

            # 2件目以降のコメント（半分は出品者からの返信）
            for _ in range(num_comments - 1):
                # 50%の確率で出品者が返信する
                if random.random() < 0.5:
                    commenter = product.seller
                    answer_templates = [
                        f"コメントありがとうございます。ご提示の金額では難しいですが、{price_down_price + 500}円でしたら可能です。ご検討ください。",
                        "お問い合わせありがとうございます。まだ在庫ございますので、ご検討よろしくお願いいたします。",
                        "ご覧いただきありがとうございます。商品説明に記載の通り、目立った傷はございません。ご安心ください。",
                    ]
                    content = random.choice(answer_templates)
                else:
                    # 他のユーザーからの追加の質問や相づち
                    commenter = random.choice(commenter_pool)
                    content = "横から失礼します。私も気になっていました。"
                
                comments_to_create.append(
                    Comment(user=commenter, product=product, content=content)
                )

        # 全てのコメントを一括でデータベースに保存
        with transaction.atomic():
            Comment.objects.bulk_create(comments_to_create)

        self.stdout.write(self.style.SUCCESS(f'-> Successfully created {len(comments_to_create)} comments.'))
        self.stdout.write(self.style.SUCCESS('All test data created successfully!'))