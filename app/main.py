from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
import os
from pathlib import Path
from io import BytesIO

from .database import get_db, create_tables, FileVersion, Folder
from .services import FileVersionService, FolderService
from .schemas import Folder as FolderSchema

app = FastAPI(title="File Version Manager", version="1.0.0")

# 起動時にテーブル作成
create_tables()

# 静的ファイルの配信設定
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "File Version Manager API"}

@app.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    memo: Optional[str] = Form(None),
    folder_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """ファイルをアップロード（新規作成または更新）"""
    try:
        content = await file.read()

        print(f"Received folder_id: {folder_id}")
        # フォルダが存在するかチェック
        if folder_id is not None:
            folder = db.query(Folder).get(folder_id)
            if not folder:
                print(f"Folder with ID {folder_id} not found")
                raise HTTPException(status_code=404, detail=f"フォルダID {folder_id} が見つかりません")

        # 既存ファイルかチェック
        existing = db.query(FileVersion).filter(
            FileVersion.filename == file.filename,
            FileVersion.folder_id == folder_id
        ).first()

        operation = "update" if existing else "create"

        version = await FileVersionService.save_file_version(
            db=db,
            filename=file.filename,
            file_content=content,
            memo=memo,
            operation=operation,
            folder_id=folder_id,
            mime_type=file.content_type
        )

        return {
            "message": f"ファイル '{file.filename}' が正常に{operation}されました",
            "filename": file.filename,
            "version": version.version,
            "memo": memo,
            "operation": operation,
            "folder_id": folder_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルアップロードエラー: {str(e)}")

@app.delete("/files/{filename}")
async def delete_file(
    filename: str,
    memo: Optional[str] = Query(None),
    folder_id: Optional[int] = Query(None, description="フォルダID"),
    db: Session = Depends(get_db)
):
    """ファイルを削除（論理削除）"""
    try:
        # 最新バージョンを取得
        query = db.query(FileVersion).filter(
            FileVersion.filename == filename
        )

        if folder_id is not None:
            query = query.filter(FileVersion.folder_id == folder_id)

        latest_version = query.order_by(FileVersion.version.desc()).first()

        if not latest_version:
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")

        # 削除記録を作成（空のファイルコンテンツで）
        version = await FileVersionService.save_file_version(
            db=db,
            filename=filename,
            file_content=b"",  # 削除なので空
            memo=memo or "ファイル削除",
            operation="delete",
            folder_id=folder_id
        )

        return {
            "message": f"ファイル '{filename}' が削除されました",
            "filename": filename,
            "version": version.version,
            "memo": memo,
            "folder_id": folder_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル削除エラー: {str(e)}")

@app.post("/folders", response_model=FolderSchema)
async def create_folder(
    name: str = Form(...),
    parent_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """フォルダを作成"""
    try:
        folder = FolderService.create_folder(db, name, parent_id)
        return FolderSchema.from_orm(folder)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"フォルダ作成に失敗: {str(e)}")

@app.get("/folders", response_model=List[FolderSchema])
async def list_folders(db: Session = Depends(get_db)):
    """フォルダのツリー構造を取得"""
    folders = FolderService.get_folder_tree(db)
    return folders  # from_attrを使用するため、変換は不要

@app.get("/files")
async def list_files(
    folder_id: Optional[int] = Query(None, description="フォルダID"),
    db: Session = Depends(get_db)
):
    """全ファイルのリストを取得"""
    try:
        # まず、フォルダが存在するかチェック
        if folder_id is not None:
            folder = db.query(Folder).get(folder_id)
            if not folder:
                raise HTTPException(status_code=404, detail=f"フォルダID {folder_id} が見つかりません")

        # フォルダIDを渡してファイルを取得
        files = FileVersionService.get_all_files(db, folder_id)

        return {"files": files}
    except Exception as e:
        # デバッグのためにエラーをログに出力
        print(f"ファイル一覧取得エラー: {str(e)}")
        import traceback
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=f"ファイル一覧の取得に失敗: {str(e)}")

@app.get("/files/{filename}/versions")
async def get_file_versions(
    filename: str,
    folder_id: Optional[int] = Query(None, description="フォルダID"),
    db: Session = Depends(get_db)
):
    """指定ファイルのバージョン履歴を取得"""
    versions = FileVersionService.get_file_versions(db, filename, folder_id)

    if not versions:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    return {
        "filename": filename,
        "versions": [
            {
                "version": v.version,
                "operation": v.operation,
                "memo": v.memo,
                "created_at": v.created_at,
                "file_size": v.file_size,
                "mime_type": v.mime_type,
                "folder_id": v.folder_id
            }
            for v in versions
        ]
    }

@app.get("/files/{filename}/download")
async def download_file(
    filename: str,
    version: Optional[int] = Query(None, description="バージョン番号（省略時は最新版）"),
    folder_id: Optional[int] = Query(None, description="フォルダID"),
    db: Session = Depends(get_db)
):
    """ファイルをダウンロード"""
    if version:
        file_version = FileVersionService.get_file_version(db, filename, version, folder_id)
    else:
        # 最新バージョンを取得
        versions = FileVersionService.get_file_versions(db, filename, folder_id)
        file_version = versions[0] if versions else None

    if not file_version:
        raise HTTPException(status_code=404, detail="ファイルまたはバージョンが見つかりません")

    # 削除されたファイルでもダウンロード可能（3世代以内であれば）
    if file_version.operation == "delete":
        # 削除されたファイルの場合は空のコンテンツを返す
        if not file_version.file_content:
            # 削除記録の場合は空のファイルを返す
            file_content = b""
        else:
            file_content = file_version.file_content
    else:
        if not file_version.file_content:
            raise HTTPException(status_code=404, detail="ファイルコンテンツが見つかりません")
        file_content = file_version.file_content

    # データベースからファイルコンテンツを取得してストリーミングレスポンスで返す
    file_stream = BytesIO(file_content)

    return StreamingResponse(
        file_stream,
        media_type=file_version.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)