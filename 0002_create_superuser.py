from django.db import migrations

def create_superuser(apps, schema_editor):
    """マイグレーション実行時にスーパーユーザーを自動作成する"""
    # マイグレーション実行時点でのモデルを取得する
    CustomUser = apps.get_model('accounts', 'CustomUser')
    
    # 既に同名のユーザーが存在しないか確認（再実行時のエラーを防ぐ）
    if not CustomUser.objects.filter(username='admin').exists():
        CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin' # 本番環境ではもっと複雑なパスワードを推奨
        )
        print("Superuser 'admin' created.")

def remove_superuser(apps, schema_editor):
    """マイグレーションを巻き戻す際にユーザーを削除する（任意）"""
    CustomUser = apps.get_model('accounts', 'CustomUser')
    CustomUser.objects.filter(username='admin').delete()
    print("Superuser 'admin' deleted.")


class Migration(migrations.Migration):

    dependencies = [
        # このマイグレーションは、accountsアプリの最初のマイグレーションに依存する
        ('accounts', '0001_initial'),
    ]

    operations = [
        # create_superuser関数を実行し、巻き戻し時にはremove_superuser関数を実行する
        migrations.RunPython(create_superuser, remove_superuser),
    ]