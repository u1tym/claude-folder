# File Version Manager

ファイルの更新・削除時にメモを残し、3バージョン前までのファイルをダウンロードできるシステム。

## 機能

- ファイルアップロード（新規作成・更新）時のメモ機能
- ファイル削除時のメモ機能
- 最大3バージョン前まで遡ってダウンロード可能
- 4バージョンより前の自動削除
- PostgreSQL でのバージョン管理

## セットアップ

1. 依存関係のインストール:
```bash
pip install -r requirements.txt
```

2. PostgreSQL データベースの準備:
```bash
createdb fileversions
```

3. 環境変数の設定:
```bash
cp .env.example .env
# .env ファイルを編集してデータベース接続情報を設定
```

4. サーバー起動:
```bash
python -m app.main
```

## API エンドポイント

### フォルダ管理
- `POST /folders` - フォルダ作成（親フォルダオプション）
- `GET /folders` - フォルダツリー取得

### ファイル管理
- `POST /files/upload` - ファイルアップロード（メモ・フォルダ付き）
- `DELETE /files/{filename}` - ファイル削除（メモ付き）
- `GET /files` - 全ファイルリスト（フォルダでフィルタ可能）
- `GET /files/{filename}/versions` - ファイルのバージョン履歴
- `GET /files/{filename}/download?version=N&folder_id=M` - ファイルダウンロード

## 機能

- フォルダ階層管理
- フォルダごとのファイル整理
- ファイルのバージョン管理
- メモ付きファイル操作
- 3世代までのバージョン保持