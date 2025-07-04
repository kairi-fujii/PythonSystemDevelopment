import os

def get_next_sequence_number(directory_path, base_name):
    """
    指定されたディレクトリ内で、次の連番を取得する。
    """
    if not os.path.exists(directory_path):
        return 1
    
    max_num = 0
    for filename in os.listdir(directory_path):
        # ファイル名が (ベース名)_(数字).(拡張子) の形式かチェック
        if filename.startswith(base_name + '_'):
            try:
                # 連番部分を抽出
                num_part = os.path.splitext(filename)[0].split('_')[-1]
                if num_part.isdigit():
                    max_num = max(max_num, int(num_part))
            except (ValueError, IndexError):
                continue
    return max_num + 1

def rename_images_recursively():
    """
    ユーザーに対話形式で親ディレクトリのパスを尋ね、
    その中の各サブフォルダ内の画像ファイルを一括でリネームする。
    """
    print("--- 画像ファイル一括リネームツール ---")
    parent_dir = input("リネーム対象の画像が入っている親フォルダのパスを入力してください (例: media/images): ")

    if not os.path.isdir(parent_dir):
        print(f"エラー: 指定されたパスが見つからないか、フォルダではありません: {parent_dir}")
        return

    print("-" * 30)
    print(f"処理を開始します...")
    print(f"対象フォルダ: {parent_dir}")
    print("-" * 30)

    renamed_count = 0
    skipped_count = 0

    # 親ディレクトリ内の全ての要素をスキャン
    for category_name in os.listdir(parent_dir):
        category_path = os.path.join(parent_dir, category_name)
        
        # それがディレクトリ（フォルダ）である場合のみ処理
        if os.path.isdir(category_path):
            print(f"カテゴリフォルダ '{category_name}' を処理中...")
            
            # このカテゴリフォルダで使う次の連番を取得
            # これにより、後から画像を追加しても連番が継続される
            next_num = get_next_sequence_number(category_path, category_name)
            
            # フォルダ内のファイルを一時的にリスト化（リネーム中の競合を防ぐため）
            files_to_rename = []
            for filename in os.listdir(category_path):
                # 新しい名前の形式にまだなっていないファイルのみを対象にする
                # 例: "tops_lady_001.jpg" は既にリネーム済みなのでスキップ
                if not filename.startswith(f"{category_name}_"):
                    files_to_rename.append(filename)
                else:
                    skipped_count += 1
            
            # リネーム対象のファイルを処理
            for filename in files_to_rename:
                _, ext = os.path.splitext(filename)
                
                # 新しいファイル名を生成 (例: tops_lady_001.jpg)
                new_filename = f"{category_name}_{next_num:03d}{ext}" # 3桁ゼロ埋め
                
                old_path = os.path.join(category_path, filename)
                new_path = os.path.join(category_path, new_filename)
                
                # os.renameでファイル名を直接変更
                os.rename(old_path, new_path)
                print(f"  リネーム: {filename} -> {new_filename}")
                renamed_count += 1
                next_num += 1 # 次のファイルのために連番をインクリメント

    print("-" * 30)
    print("処理完了。")
    print(f"リネーム: {renamed_count}件, スキップ(リネーム済み等): {skipped_count}件")


if __name__ == '__main__':
    rename_images_recursively()