#!/usr/bin/env python3
"""
既存のファイルシステムベースのファイルをデータベースに移行するスクリプト
"""
import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import get_db, create_tables, FileVersion, Folder, engine
from app.services import FileVersionService

def migrate_files_to_db():
    """既存のファイルをデータベースに移行"""
    print("ファイルシステムからデータベースへの移行を開始します...")

    # テーブルを作成
    create_tables()

    # データベースセッションを取得
    db = next(get_db())

    try:
        # 既存のFileVersionレコードを取得
        existing_versions = db.query(FileVersion).all()

        migrated_count = 0
        error_count = 0

        for version in existing_versions:
            try:
                # ファイルパスが存在するかチェック
                if hasattr(version, 'file_path') and version.file_path and os.path.exists(version.file_path):
                    print(f"移行中: {version.filename} v{version.version}")

                    # ファイルを読み込み
                    with open(version.file_path, 'rb') as f:
                        file_content = f.read()

                    # データベースのfile_contentフィールドを更新
                    version.file_content = file_content

                    # file_pathフィールドを削除（新しいスキーマでは不要）
                    if hasattr(version, 'file_path'):
                        delattr(version, 'file_path')

                    migrated_count += 1

                    # 物理ファイルを削除
                    try:
                        os.remove(version.file_path)
                        # 空のディレクトリも削除
                        version_dir = Path(version.file_path).parent
                        if version_dir.exists() and not any(version_dir.iterdir()):
                            version_dir.rmdir()
                    except Exception as e:
                        print(f"警告: 物理ファイルの削除に失敗しました {version.file_path}: {e}")

                else:
                    print(f"スキップ: ファイルが見つかりません {version.filename} v{version.version}")
                    error_count += 1

            except Exception as e:
                print(f"エラー: {version.filename} v{version.version} の移行に失敗: {e}")
                error_count += 1

        # 変更をコミット
        db.commit()

        print(f"\n移行完了:")
        print(f"  成功: {migrated_count} ファイル")
        print(f"  エラー: {error_count} ファイル")

        # uploadsディレクトリを削除
        uploads_dir = Path("uploads")
        if uploads_dir.exists():
            try:
                import shutil
                shutil.rmtree(uploads_dir)
                print(f"uploadsディレクトリを削除しました: {uploads_dir}")
            except Exception as e:
                print(f"警告: uploadsディレクトリの削除に失敗: {e}")

    except Exception as e:
        print(f"移行中にエラーが発生しました: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_files_to_db()
