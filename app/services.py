import os
import aiofiles
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from .database import FileVersion, Folder
import shutil
from typing import Optional, List, Dict, Union

UPLOAD_DIR = Path(os.path.abspath("uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
print(f"Upload directory: {UPLOAD_DIR}")

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
        
        # フォルダのパスを生成
        folder_path = UPLOAD_DIR
        
        # 親フォルダがある場合はパスを追加
        if parent_id is not None:
            parent_folders = []
            current_parent_id = parent_id
            
            while current_parent_id is not None:
                parent = db.query(Folder).get(current_parent_id)
                if not parent:
                    print(f"Parent folder with ID {current_parent_id} not found")
                    break
                parent_folders.insert(0, parent.name)
                current_parent_id = parent.parent_id
            
            # 親フォルダのパスを追加
            folder_path = folder_path.joinpath(*parent_folders)
        
        # フォルダディレクトリを作成
        full_folder_path = folder_path / name
        print(f"Creating directory: {full_folder_path}")
        
        try:
            full_folder_path.mkdir(parents=True, exist_ok=True)
            print(f"Directory created successfully: {full_folder_path}")
        except Exception as e:
            print(f"Failed to create directory: {full_folder_path}")
            print(f"Error: {e}")
            raise
        
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
            FileVersion.filename == filename
        ).scalar() or 0
        
        new_version = max_version + 1
        
        # ファイルパスを生成
        version_dir = UPLOAD_DIR
        folder_path = None
        
        # フォルダIDが指定されている場合
        if folder_id:
            folder = db.query(Folder).get(folder_id)
            if folder:
                # フォルダのパスを生成（再帰的に親フォルダのパスを追加）
                folder_path = [folder.name]
                current_folder = folder
                while current_folder.parent_id:
                    current_folder = db.query(Folder).get(current_folder.parent_id)
                    folder_path.insert(0, current_folder.name)
                
                # フォルダパスを追加
                version_dir = version_dir.joinpath(*folder_path)
        
        # バージョンディレクトリとファイルパスを生成
        version_dir = version_dir / filename / str(new_version)
        print(f"Creating version directory: {version_dir}")
        
        try:
            version_dir.mkdir(parents=True, exist_ok=True)
            print(f"Version directory created successfully: {version_dir}")
        except Exception as e:
            print(f"Failed to create version directory: {version_dir}")
            print(f"Error: {e}")
            raise
        
        file_path = version_dir / filename
        print(f"File path: {file_path}")
        
        # ファイルを保存
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            print(f"File saved successfully: {file_path}")
        except Exception as e:
            print(f"Failed to save file: {file_path}")
            print(f"Error: {e}")
            raise
        
        # データベースに記録
        db_version = FileVersion(
            filename=filename,
            version=new_version,
            file_path=str(file_path),
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
        await FileVersionService.cleanup_old_versions(db, filename)
        
        return db_version
    
    @staticmethod
    async def cleanup_old_versions(db: Session, filename: str):
        # 4バージョンより古いレコードを取得
        old_versions = db.query(FileVersion).filter(
            FileVersion.filename == filename,
            FileVersion.version <= db.query(func.max(FileVersion.version)).filter(
                FileVersion.filename == filename
            ).scalar() - 3
        ).all()
        
        # 物理ファイルを削除
        for version in old_versions:
            try:
                if os.path.exists(version.file_path):
                    os.remove(version.file_path)
                    # 空のディレクトリも削除
                    version_dir = Path(version.file_path).parent
                    if version_dir.exists() and not any(version_dir.iterdir()):
                        version_dir.rmdir()
            except Exception as e:
                print(f"Failed to delete file {version.file_path}: {e}")
        
        # データベースレコードを削除
        for version in old_versions:
            db.delete(version)
        
        db.commit()
    
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