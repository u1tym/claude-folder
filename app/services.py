import os
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from .database import FileVersion, Folder
from typing import Optional, List, Dict, Union
from io import BytesIO

class FolderService:
    @staticmethod
    def create_folder(
        db: Session,
        name: str,
        parent_id: Optional[int] = None
    ) -> Folder:
        # デバッグログ
        print(f"Creating folder: name={name}, parent_id={parent_id}")

        # フォルダが既に存在するかチェック
        existing_folder = db.query(Folder).filter(
            Folder.name == name,
            Folder.parent_id == parent_id
        ).first()

        if existing_folder:
            print(f"Folder {name} already exists")
            return existing_folder

        # フォルダはDBのみで管理するため、物理ディレクトリの作成は不要

        # データベースにフォルダを追加
        new_folder = Folder(
            name=name,
            parent_id=parent_id
        )

        db.add(new_folder)
        db.commit()
        db.refresh(new_folder)

        print(f"Folder {name} added to database with ID {new_folder.id}")

        return new_folder

    @staticmethod
    def get_folder_tree(db: Session) -> List[Folder]:
        # ツリー状のフォルダ構造を取得
        def build_tree(parent_id=None):
            folders = db.query(Folder).filter(Folder.parent_id == parent_id).all()
            for folder in folders:
                folder.children = build_tree(folder.id)
            return folders

        return build_tree()

class FileVersionService:
    @staticmethod
    async def save_file_version(
        db: Session,
        filename: str,
        file_content: bytes,
        memo: Optional[str],
        operation: str,
        folder_id: Optional[int] = None,
        mime_type: Optional[str] = None
    ) -> FileVersion:
        print(f"Saving file version: filename={filename}, folder_id={folder_id}, operation={operation}")

        # 現在の最大バージョン番号を取得
        max_version = db.query(func.max(FileVersion.version)).filter(
            FileVersion.filename == filename,
            FileVersion.folder_id == folder_id
        ).scalar() or 0

        new_version = max_version + 1

        # データベースに記録（ファイルコンテンツも含む）
        db_version = FileVersion(
            filename=filename,
            version=new_version,
            file_content=file_content,  # ファイルコンテンツをDBに保存
            folder_id=folder_id,
            memo=memo,
            operation=operation,
            file_size=len(file_content),
            mime_type=mime_type
        )

        db.add(db_version)
        db.commit()
        db.refresh(db_version)

        print(f"File version added to database: ID={db_version.id}, version={new_version}")

        # 古いバージョンをクリーンアップ
        await FileVersionService.cleanup_old_versions(db, filename, folder_id)

        return db_version

    @staticmethod
    async def cleanup_old_versions(db: Session, filename: str, folder_id: Optional[int] = None):
        # 4バージョンより古いレコードを取得
        query = db.query(FileVersion).filter(
            FileVersion.filename == filename
        )

        if folder_id is not None:
            query = query.filter(FileVersion.folder_id == folder_id)

        max_version = query.with_entities(func.max(FileVersion.version)).scalar() or 0
        old_versions = query.filter(
            FileVersion.version <= max_version - 3
        ).all()

        # データベースレコードを削除（ファイルコンテンツも一緒に削除される）
        for version in old_versions:
            db.delete(version)

        db.commit()
        print(f"Cleaned up {len(old_versions)} old versions for {filename}")

    @staticmethod
    def get_file_versions(
        db: Session,
        filename: str,
        folder_id: Optional[int] = None
    ) -> List[FileVersion]:
        query = db.query(FileVersion).filter(
            FileVersion.filename == filename
        )

        if folder_id is not None:
            query = query.filter(FileVersion.folder_id == folder_id)

        return query.order_by(desc(FileVersion.version)).all()

    @staticmethod
    def get_file_version(
        db: Session,
        filename: str,
        version: int,
        folder_id: Optional[int] = None
    ) -> Optional[FileVersion]:
        query = db.query(FileVersion).filter(
            FileVersion.filename == filename,
            FileVersion.version == version
        )

        if folder_id is not None:
            query = query.filter(FileVersion.folder_id == folder_id)

        return query.first()

    @staticmethod
    def get_all_files(db: Session, folder_id: Optional[int] = None) -> List[dict]:
        try:
            # デバッグのためのログ出力
            print(f"Starting get_all_files method with folder_id: {folder_id}")

            # サブクエリの変更: 各ファイルの最新バージョンを取得
            latest_version_query = db.query(
                FileVersion.filename,
                FileVersion.folder_id,
                func.max(FileVersion.id).label('max_version_id')
            ).group_by(FileVersion.filename, FileVersion.folder_id)

            # フォルダIDでフィルタリングする場合
            if folder_id is not None:
                latest_version_query = latest_version_query.filter(
                    FileVersion.folder_id == folder_id
                )

            latest_version_subquery = latest_version_query.subquery()

            print("Subquery created")

            # 最新バージョンのファイルを取得
            latest_versions_query = db.query(FileVersion, Folder).outerjoin(
                Folder,
                FileVersion.folder_id == Folder.id
            ).join(
                latest_version_subquery,
                FileVersion.id == latest_version_subquery.c.max_version_id
            )

            # フォルダIDでフィルタリングする場合
            if folder_id is not None:
                latest_versions_query = latest_versions_query.filter(
                    FileVersion.folder_id == folder_id
                )

            latest_versions = latest_versions_query.order_by(desc(FileVersion.created_at)).all()

            print(f"Found {len(latest_versions)} latest versions")

            # 削除されたファイルも含めて表示
            result = [
                {
                    "filename": version.filename,
                    "latest_version": version.version,
                    "latest_operation": version.operation,
                    "latest_update": version.created_at,
                    "file_size": version.file_size,
                    "mime_type": version.mime_type,
                    "folder_name": folder.name if folder else None,
                    "folder_id": folder.id if folder else None
                }
                for version, folder in latest_versions
                # 削除されたファイルも表示するように変更
            ]

            print(f"Returning {len(result)} files")
            return result

        except Exception as e:
            # エラーの詳細をログに出力
            print(f"Error in get_all_files: {str(e)}")
            import traceback
            traceback.print_exc()

            # エラーを再送出
            raise