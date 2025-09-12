#!/usr/bin/env python3
"""
削除されたファイルのダウンロード機能のテストスクリプト
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

async def test_deleted_file_download():
    """削除されたファイルのダウンロード機能のテスト"""
    print("削除されたファイルのダウンロード機能のテストを開始します...")
    
    # テーブルを作成
    create_tables()
    
    # データベースセッションを取得
    db = next(get_db())
    
    try:
        # テストフォルダを作成
        print("1. テストフォルダを作成...")
        test_folder = FolderService.create_folder(db, "削除ダウンロードテストフォルダ")
        print(f"   フォルダ作成完了: ID={test_folder.id}, 名前={test_folder.name}")
        
        # テストファイルのコンテンツ
        test_content = "削除ダウンロードテスト用のファイル内容です。".encode('utf-8')
        
        # ファイルをアップロード（バージョン1）
        print("2. テストファイルをアップロード（バージョン1）...")
        file_version_1 = await FileVersionService.save_file_version(
            db=db,
            filename="download_test.txt",
            file_content=test_content,
            memo="初回アップロード",
            operation="create",
            folder_id=test_folder.id,
            mime_type="text/plain"
        )
        print(f"   ファイルアップロード完了: バージョン={file_version_1.version}")
        
        # ファイルを更新（バージョン2）
        print("3. ファイルを更新（バージョン2）...")
        updated_content = "更新されたファイル内容です。".encode('utf-8')
        file_version_2 = await FileVersionService.save_file_version(
            db=db,
            filename="download_test.txt",
            file_content=updated_content,
            memo="ファイル更新",
            operation="update",
            folder_id=test_folder.id,
            mime_type="text/plain"
        )
        print(f"   ファイル更新完了: バージョン={file_version_2.version}")
        
        # ファイルを削除（バージョン3）
        print("4. ファイルを削除（バージョン3）...")
        delete_version = await FileVersionService.save_file_version(
            db=db,
            filename="download_test.txt",
            file_content=b"",  # 削除なので空
            memo="ファイル削除",
            operation="delete",
            folder_id=test_folder.id
        )
        print(f"   ファイル削除完了: バージョン={delete_version.version}")
        
        # バージョン履歴を確認
        print("5. バージョン履歴を確認...")
        versions = FileVersionService.get_file_versions(db, "download_test.txt", test_folder.id)
        print(f"   バージョン数: {len(versions)}")
        for version in versions:
            print(f"   - バージョン {version.version}: {version.operation} ({version.created_at})")
        
        # 各バージョンのダウンロードをテスト
        print("6. 各バージョンのダウンロードをテスト...")
        
        # バージョン1（初回アップロード）のダウンロード
        version_1 = FileVersionService.get_file_version(db, "download_test.txt", 1, test_folder.id)
        if version_1 and version_1.file_content:
            print(f"   ✓ バージョン1のダウンロード可能: {len(version_1.file_content)} bytes")
        else:
            print("   ✗ バージョン1のダウンロードに失敗")
            return False
        
        # バージョン2（更新版）のダウンロード
        version_2 = FileVersionService.get_file_version(db, "download_test.txt", 2, test_folder.id)
        if version_2 and version_2.file_content:
            print(f"   ✓ バージョン2のダウンロード可能: {len(version_2.file_content)} bytes")
        else:
            print("   ✗ バージョン2のダウンロードに失敗")
            return False
        
        # バージョン3（削除版）のダウンロード
        version_3 = FileVersionService.get_file_version(db, "download_test.txt", 3, test_folder.id)
        if version_3:
            print(f"   ✓ バージョン3（削除版）のダウンロード可能: {len(version_3.file_content)} bytes")
        else:
            print("   ✗ バージョン3（削除版）のダウンロードに失敗")
            return False
        
        # ファイル一覧を確認（削除されたファイルは表示されない）
        print("7. ファイル一覧を確認...")
        files = FileVersionService.get_all_files(db, test_folder.id)
        print(f"   一覧に表示されるファイル数: {len(files)}")
        for file_info in files:
            print(f"   - {file_info['filename']} (v{file_info['latest_version']}) - {file_info['latest_operation']}")
        
        if len(files) == 0:
            print("   ✓ 削除されたファイルは一覧に表示されません")
        else:
            print("   ✗ 削除されたファイルが一覧に表示されています")
            return False
        
        print("\n✓ 削除されたファイルのダウンロード機能テストが成功しました！")
        print("   - 削除されたファイルは一覧に表示されない")
        print("   - 削除されたファイルもバージョン履歴からダウンロード可能")
        print("   - 3世代以内のファイルはすべてダウンロード可能")
        return True
        
    except Exception as e:
        print(f"\n✗ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_deleted_file_download())
    sys.exit(0 if success else 1)
