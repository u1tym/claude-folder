# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

File Version Manager - ファイルの更新・削除時にメモを残し、3バージョン前までのファイルをダウンロードできるシステム

## Technology Stack

- **Backend**: Python 3 + FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **File Storage**: Local filesystem with version directories

## Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup PostgreSQL database:
```bash
createdb fileversions
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database connection details
```

4. Run development server:
```bash
python -m app.main
```

5. Run frontend (in another terminal):
```bash
cd frontend
npm install
npm run dev
```

## Architecture

### Database Schema
- `file_versions` table tracks all file versions with memo, operation type, timestamps
- Automatic cleanup keeps only 3 previous versions (4th and older are deleted)

### File Storage Structure
```
uploads/
  filename/
    1/filename  # version 1
    2/filename  # version 2
    3/filename  # version 3
```

### API Endpoints
- File upload/update with memo: `POST /files/upload`
- File deletion with memo: `DELETE /files/{filename}`
- Version history: `GET /files/{filename}/versions`
- Download specific version: `GET /files/{filename}/download?version=N`

## Key Features

1. **Memo Support**: All file operations (create/update/delete) support memo fields
2. **Version Limits**: Automatically keeps only 3 previous versions
3. **Download History**: Can download any of the kept versions
4. **Operation Tracking**: Tracks create/update/delete operations separately

## Frontend

- **Framework**: Vue 3 + TypeScript
- **Styling**: Tailwind CSS + Heroicons
- **Build Tool**: Vite
- **Features**: File upload with drag & drop, version history modal, download functionality
- **API Proxy**: Vite proxies `/files` to backend at `localhost:8000`

### Frontend Components
- `FileUpload.vue`: File upload with memo support and folder selection
- `FileList.vue`: File listing with actions (download, delete, version history)
- `VersionHistory.vue`: Modal showing version history with download links
- `FolderManager.vue`: Folder management with tree view and folder creation
- `FolderTree.vue`: Recursive folder tree component
- `FolderItem.vue`: Individual folder item with expand/collapse
- `App.vue`: Main application layout with notifications