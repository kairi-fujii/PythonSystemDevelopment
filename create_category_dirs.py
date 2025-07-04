import os

# === カテゴリ定義（create_test_data.pyからコピー） ===
# このリストをメンテナンスすれば、生成されるフォルダも追従します
CATEGORIES_DATA = {
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

def create_folders():
    """
    ユーザーに親ディレクトリのパスを尋ね、カテゴリフォルダを一括作成する。
    """
    print("カテゴリフォルダを作成します。")
    # 親ディレクトリのパスをユーザーに入力させる
    parent_dir = input("作成先の親ディレクトリのパスを入力してください（例: C:\\Users\\Taro\\Pictures\\DummyImages）: ")

    # パスが存在するかチェック
    if not os.path.isdir(parent_dir):
        print(f"エラー: 指定されたパス '{parent_dir}' は存在しないか、ディレクトリではありません。")
        return

    print("-" * 30)
    created_count = 0
    skipped_count = 0

    # カテゴリ辞書から内部名（フォルダ名）を取得してループ
    for child_items in CATEGORIES_DATA.values():
        for internal_name, _ in child_items:
            # 作成するフォルダのフルパスを生成
            folder_path = os.path.join(parent_dir, internal_name)
            
            # フォルダが既に存在するかチェック
            if not os.path.exists(folder_path):
                # 存在しない場合のみ作成
                os.makedirs(folder_path)
                print(f"作成しました: {folder_path}")
                created_count += 1
            else:
                # 存在する場合はスキップ
                print(f"スキップしました（既に存在）: {folder_path}")
                skipped_count += 1

    print("-" * 30)
    print(f"処理完了。")
    print(f"新規作成: {created_count} 件, スキップ: {skipped_count} 件")


if __name__ == "__main__":
    create_folders()