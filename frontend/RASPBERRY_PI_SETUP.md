# Raspberry Pi OS Lite でのセットアップガイド

## 前提条件

1. **Node.js のバージョン確認**
   ```bash
   node --version  # 推奨: v18.x 以上
   npm --version   # 推奨: v9.x 以上
   ```

2. **Node.js の更新が必要な場合**
   ```bash
   # NodeSource リポジトリを追加
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

## インストール

```bash
cd frontend
npm install
```

## 開発サーバーの起動

### 方法1: ARM最適化版（推奨）
```bash
npm run dev:arm
```

### 方法2: レガシーモード
```bash
npm run dev:legacy
```

### 方法3: 通常版（問題が解決した場合）
```bash
npm run dev
```

## トラブルシューティング

### "Illegal instruction" エラーが発生する場合

1. **Node.js のバージョンを確認**
   ```bash
   chmod +x check-env.sh
   ./check-env.sh
   ```

2. **メモリ不足の場合**
   ```bash
   # スワップファイルを追加
   sudo fallocate -l 1G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

3. **依存関係の再インストール**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Vite のバージョンを下げる**
   ```bash
   npm install vite@4.5.0 --save-dev
   ```

### その他の問題

- **ポートが使用中**: `lsof -i :3000` で確認
- **権限エラー**: `sudo chown -R $USER:$USER .`
- **ネットワークエラー**: ファイアウォール設定を確認

## 本番ビルド

```bash
npm run build:arm
```

## アクセス

開発サーバー起動後、以下のURLでアクセス可能：
- ローカル: `http://localhost:3000`
- ネットワーク: `http://[Raspberry PiのIP]:3000`
