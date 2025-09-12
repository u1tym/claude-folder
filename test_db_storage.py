#!/usr/bin/env python3
"""
データベースストレージのテストスクリプト
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

async def test_db_storage():
    """データベースストレージのテスト"""
    print("データベースストレージのテストを開始します...")

    # テーブルを作成
    create_tables()

    # データベースセッションを取得
    db = next(get_db())

    try:
        # テストフォルダを作成
        print("1. テストフォルダを作成...")
        test_folder = FolderService.create_folder(db, "テストフォルダ")
        print(f"   フォルダ作成完了: ID={test_folder.id}, 名前={test_folder.name}")

        # テストファイルのコンテンツ
        test_content = "これはテストファイルの内容です。\nHello, World!".encode('utf-8')

        # ファイルをアップロード
        print("2. テストファイルをアップロード...")
        file_version = await FileVersionService.save_file_version(
            db=db,
            filename="test.txt",
            file_content=test_content,
            memo="テストファイル",
            operation="create",
            folder_id=test_folder.id,
            mime_type="text/plain"
        )
        print(f"   ファイルアップロード完了: ID={file_version.id}, バージョン={file_version.version}")

        # ファイルを取得して検証
        print("3. ファイルを取得して検証...")
        retrieved_version = FileVersionService.get_file_version(
            db, "test.txt", file_version.version, test_folder.id
        )

        if retrieved_version and retrieved_version.file_content == test_content:
            print("   ✓ ファイルコンテンツが正しく保存・取得されました")
        else:
            print("   ✗ ファイルコンテンツの保存・取得に失敗しました")
            return False

        # ファイル一覧を取得
        print("4. ファイル一覧を取得...")
        files = FileVersionService.get_all_files(db, test_folder.id)
        print(f"   取得されたファイル数: {len(files)}")
        for file_info in files:
            print(f"   - {file_info['filename']} (v{file_info['latest_version']})")

        # ファイルバージョン履歴を取得
        print("5. ファイルバージョン履歴を取得...")
        versions = FileVersionService.get_file_versions(db, "test.txt", test_folder.id)
        print(f"   取得されたバージョン数: {len(versions)}")
        for version in versions:
            print(f"   - バージョン {version.version}: {version.operation} ({version.created_at})")

        print("\n✓ すべてのテストが成功しました！")
        return True

    except Exception as e:
        print(f"\n✗ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_db_storage())
    sys.exit(0 if success else 1)
