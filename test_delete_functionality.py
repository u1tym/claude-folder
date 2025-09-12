#!/usr/bin/env python3
"""
削除機能のテストスクリプト
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

async def test_delete_functionality():
    """削除機能のテスト"""
    print("削除機能のテストを開始します...")

    # テーブルを作成
    create_tables()

    # データベースセッションを取得
    db = next(get_db())

    try:
        # テストフォルダを作成
        print("1. テストフォルダを作成...")
        test_folder = FolderService.create_folder(db, "削除テストフォルダ")
        print(f"   フォルダ作成完了: ID={test_folder.id}, 名前={test_folder.name}")

        # テストファイルのコンテンツ
        test_content = "削除テスト用のファイル内容です。".encode('utf-8')

        # ファイルをアップロード
        print("2. テストファイルをアップロード...")
        file_version = await FileVersionService.save_file_version(
            db=db,
            filename="delete_test.txt",
            file_content=test_content,
            memo="削除テスト用ファイル",
            operation="create",
            folder_id=test_folder.id,
            mime_type="text/plain"
        )
        print(f"   ファイルアップロード完了: ID={file_version.id}, バージョン={file_version.version}")

        # ファイル一覧を確認（削除前）
        print("3. 削除前のファイル一覧を確認...")
        files_before = FileVersionService.get_all_files(db, test_folder.id)
        print(f"   削除前のファイル数: {len(files_before)}")
        for file_info in files_before:
            print(f"   - {file_info['filename']} (v{file_info['latest_version']}) - {file_info['latest_operation']}")

        # ファイルを削除
        print("4. ファイルを削除...")
        delete_version = await FileVersionService.save_file_version(
            db=db,
            filename="delete_test.txt",
            file_content=b"",  # 削除なので空
            memo="削除テスト",
            operation="delete",
            folder_id=test_folder.id
        )
        print(f"   削除完了: バージョン={delete_version.version}")

        # ファイル一覧を確認（削除後）
        print("5. 削除後のファイル一覧を確認...")
        files_after = FileVersionService.get_all_files(db, test_folder.id)
        print(f"   削除後のファイル数: {len(files_after)}")
        for file_info in files_after:
            print(f"   - {file_info['filename']} (v{file_info['latest_version']}) - {file_info['latest_operation']}")

        # バージョン履歴を確認
        print("6. バージョン履歴を確認...")
        versions = FileVersionService.get_file_versions(db, "delete_test.txt", test_folder.id)
        print(f"   バージョン数: {len(versions)}")
        for version in versions:
            print(f"   - バージョン {version.version}: {version.operation} ({version.created_at})")

        # 削除されたファイルが一覧に表示されないことを確認
        if len(files_after) == 0:
            print("\n✓ 削除されたファイルが一覧から正しく除外されました！")
            return True
        else:
            print(f"\n✗ 削除されたファイルが一覧に残っています: {len(files_after)} ファイル")
            return False

    except Exception as e:
        print(f"\n✗ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_delete_functionality())
    sys.exit(0 if success else 1)
