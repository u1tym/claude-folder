import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

load_dotenv()

from app.database import Base, DATABASE_URL, create_tables
from app.database import Folder, FileVersion
from pathlib import Path

def init_db():
    """データベースを初期化し、全テーブルを作成"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # 既存のテーブルを全て削除
        Base.metadata.drop_all(bind=engine)
        
        # 全てのモデルのテーブルを作成
        Base.metadata.create_all(bind=engine)
        
        # セッションを作成
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # サンプルフォルダを作成
            documents_folder = Folder(name="Documents")
            images_folder = Folder(name="Images")
            session.add_all([documents_folder, images_folder])
            session.commit()

            # サンプルファイルを作成
            uploads_dir = Path("uploads")
            uploads_dir.mkdir(exist_ok=True)

            # サンプルドキュメントファイル
            doc_file_path = uploads_dir / "Documents" / "sample.txt"
            doc_file_path.parent.mkdir(parents=True, exist_ok=True)
            doc_file_path.write_text("これはサンプルドキュメントです。")

            doc_version = FileVersion(
                filename="sample.txt",
                version=1,
                file_path=str(doc_file_path),
                folder_id=documents_folder.id,
                memo="初期サンプルドキュメント",
                operation="create",
                file_size=len("これはサンプルドキュメントです。"),
                mime_type="text/plain"
            )
            session.add(doc_version)

            # サンプル画像ファイル
            image_file_path = uploads_dir / "Images" / "sample.txt"
            image_file_path.parent.mkdir(parents=True, exist_ok=True)
            image_file_path.write_bytes("これはサンプル画像の説明です。".encode('utf-8'))

            image_version = FileVersion(
                filename="sample.txt",
                version=1,
                file_path=str(image_file_path),
                folder_id=images_folder.id,
                memo="初期サンプル画像の説明",
                operation="create",
                file_size=len("これはサンプル画像の説明です。"),
                mime_type="text/plain"
            )
            session.add(image_version)

            session.commit()
            print("データベースとテーブルを再作成し、サンプルデータを追加しました。")

        except Exception as e:
            session.rollback()
            print(f"サンプルデータの追加中にエラーが発生しました: {e}")
        finally:
            session.close()

    except Exception as e:
        print(f"データベース初期化中にエラーが発生しました: {e}")

if __name__ == "__main__":
    init_db()