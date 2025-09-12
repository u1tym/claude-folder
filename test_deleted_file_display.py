#!/usr/bin/env python3
"""
削除されたファイルの表示機能のテストスクリプト
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import get_db, create_tables, FileVersion, Folder
from app.services import FileVersionService, FolderService
import asyncio

async def test_deleted_file_display():
    """削除されたファイルの表示機能のテスト"""
    print("削除されたファイルの表示機能のテストを開始します...")

    # テーブルを作成
    create_tables()

    # データベースセッションを取得
    db = next(get_db())

    try:
        # テストフォルダを作成
        print("1. テストフォルダを作成...")
        test_folder = FolderService.create_folder(db, "削除表示テストフォルダ")
        print(f"   フォルダ作成完了: ID={test_folder.id}, 名前={test_folder.name}")

        # テストファイル1をアップロード
        print("2. テストファイル1をアップロード...")
        test_content_1 = "テストファイル1の内容です。".encode('utf-8')
        file_version_1 = await FileVersionService.save_file_version(
            db=db,
            filename="test1.txt",
            file_content=test_content_1,
            memo="テストファイル1",
            operation="create",
            folder_id=test_folder.id,
            mime_type="text/plain"
        )
        print(f"   ファイル1アップロード完了: バージョン={file_version_1.version}")

        # テストファイル2をアップロード
        print("3. テストファイル2をアップロード...")
        test_content_2 = "テストファイル2の内容です。".encode('utf-8')
        file_version_2 = await FileVersionService.save_file_version(
            db=db,
            filename="test2.txt",
            file_content=test_content_2,
            memo="テストファイル2",
            operation="create",
            folder_id=test_folder.id,
            mime_type="text/plain"
        )
        print(f"   ファイル2アップロード完了: バージョン={file_version_2.version}")

        # ファイル一覧を確認（削除前）
        print("4. 削除前のファイル一覧を確認...")
        files_before = FileVersionService.get_all_files(db, test_folder.id)
        print(f"   削除前のファイル数: {len(files_before)}")
        for file_info in files_before:
            print(f"   - {file_info['filename']} (v{file_info['latest_version']}) - {file_info['latest_operation']}")

        # ファイル1を削除
        print("5. ファイル1を削除...")
        delete_version = await FileVersionService.save_file_version(
            db=db,
            filename="test1.txt",
            file_content=b"",  # 削除なので空
            memo="ファイル1削除",
            operation="delete",
            folder_id=test_folder.id
        )
        print(f"   ファイル1削除完了: バージョン={delete_version.version}")

        # ファイル一覧を確認（削除後）
        print("6. 削除後のファイル一覧を確認...")
        files_after = FileVersionService.get_all_files(db, test_folder.id)
        print(f"   削除後のファイル数: {len(files_after)}")
        for file_info in files_after:
            print(f"   - {file_info['filename']} (v{file_info['latest_version']}) - {file_info['latest_operation']}")

        # 削除されたファイルが一覧に表示されることを確認
        deleted_files = [f for f in files_after if f['latest_operation'] == 'delete']
        active_files = [f for f in files_after if f['latest_operation'] != 'delete']

        if len(deleted_files) == 1 and len(active_files) == 1:
            print("   ✓ 削除されたファイルとアクティブなファイルが正しく表示されています")
            print(f"   - 削除されたファイル: {deleted_files[0]['filename']}")
            print(f"   - アクティブなファイル: {active_files[0]['filename']}")
        else:
            print(f"   ✗ ファイル表示が正しくありません: 削除={len(deleted_files)}, アクティブ={len(active_files)}")
            return False

        # 削除されたファイルのダウンロードをテスト
        print("7. 削除されたファイルのダウンロードをテスト...")
        deleted_version = FileVersionService.get_file_version(db, "test1.txt", delete_version.version, test_folder.id)
        if deleted_version and deleted_version.operation == "delete":
            print(f"   ✓ 削除されたファイルのダウンロード可能: {len(deleted_version.file_content)} bytes")
        else:
            print("   ✗ 削除されたファイルのダウンロードに失敗")
            return False

        print("\n✓ 削除されたファイルの表示機能テストが成功しました！")
        print("   - 削除されたファイルが一覧に表示される")
        print("   - 削除されたファイルもダウンロード可能")
        print("   - アクティブなファイルと削除されたファイルが区別される")
        return True

    except Exception as e:
        print(f"\n✗ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_deleted_file_display())
    sys.exit(0 if success else 1)
