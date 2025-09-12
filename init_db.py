#!/usr/bin/env python3
"""
データベースを初期化し、新しいスキーマを適用するスクリプト
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import create_tables, engine, Base
from sqlalchemy import text

def init_database():
    """データベースを初期化"""
    print("データベースを初期化しています...")

    try:
        # 既存のテーブルを削除して新しく作成
        print("既存のテーブルを削除しています...")
        Base.metadata.drop_all(bind=engine)

        print("新しいテーブルを作成しています...")
        create_tables()

        print("データベースの初期化が完了しました。")

    except Exception as e:
        print(f"データベース初期化中にエラーが発生しました: {e}")
        raise

if __name__ == "__main__":
    init_database()
