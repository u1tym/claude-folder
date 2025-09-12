#!/usr/bin/env python3
"""
APIエンドポイントでの削除されたファイルのダウンロード機能のテスト
"""
import requests
import json
import time

def test_api_download():
    """APIエンドポイントでのダウンロード機能テスト"""
    base_url = "http://localhost:8000"

    print("APIエンドポイントでの削除されたファイルのダウンロード機能テストを開始します...")

    try:
        # 1. フォルダを作成
        print("1. フォルダを作成...")
        folder_data = {"name": "APIテストフォルダ"}
        folder_response = requests.post(f"{base_url}/folders", data=folder_data)
        if folder_response.status_code == 200:
            folder = folder_response.json()
            folder_id = folder["id"]
            print(f"   フォルダ作成完了: ID={folder_id}")
        else:
            print(f"   フォルダ作成失敗: {folder_response.status_code}")
            return False

        # 2. ファイルをアップロード
        print("2. ファイルをアップロード...")
        test_content = "APIテスト用のファイル内容です。"
        files = {"file": ("api_test.txt", test_content, "text/plain")}
        data = {"memo": "APIテスト用ファイル", "folder_id": folder_id}
        upload_response = requests.post(f"{base_url}/files/upload", files=files, data=data)
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            print(f"   ファイルアップロード完了: {upload_result['filename']}")
        else:
            print(f"   ファイルアップロード失敗: {upload_response.status_code}")
            return False

        # 3. ファイルを削除
        print("3. ファイルを削除...")
        delete_data = {"memo": "APIテスト用削除", "folder_id": folder_id}
        delete_response = requests.delete(f"{base_url}/files/api_test.txt", params=delete_data)
        if delete_response.status_code == 200:
            delete_result = delete_response.json()
            print(f"   ファイル削除完了: バージョン={delete_result['version']}")
        else:
            print(f"   ファイル削除失敗: {delete_response.status_code}")
            return False

        # 4. バージョン履歴を取得
        print("4. バージョン履歴を取得...")
        versions_params = {"folder_id": folder_id}
        versions_response = requests.get(f"{base_url}/files/api_test.txt/versions", params=versions_params)
        if versions_response.status_code == 200:
            versions_result = versions_response.json()
            print(f"   バージョン数: {len(versions_result['versions'])}")
            for version in versions_result['versions']:
                print(f"   - バージョン {version['version']}: {version['operation']}")
        else:
            print(f"   バージョン履歴取得失敗: {versions_response.status_code}")
            return False

        # 5. 各バージョンのダウンロードをテスト
        print("5. 各バージョンのダウンロードをテスト...")

        # バージョン1（初回アップロード）のダウンロード
        download_params = {"version": 1, "folder_id": folder_id}
        download_response = requests.get(f"{base_url}/files/api_test.txt/download", params=download_params)
        if download_response.status_code == 200:
            print(f"   ✓ バージョン1のダウンロード成功: {len(download_response.content)} bytes")
        else:
            print(f"   ✗ バージョン1のダウンロード失敗: {download_response.status_code}")
            return False

        # バージョン2（削除版）のダウンロード
        download_params = {"version": 2, "folder_id": folder_id}
        download_response = requests.get(f"{base_url}/files/api_test.txt/download", params=download_params)
        if download_response.status_code == 200:
            print(f"   ✓ バージョン2（削除版）のダウンロード成功: {len(download_response.content)} bytes")
        else:
            print(f"   ✗ バージョン2（削除版）のダウンロード失敗: {download_response.status_code}")
            return False

        # 6. ファイル一覧を確認
        print("6. ファイル一覧を確認...")
        files_params = {"folder_id": folder_id}
        files_response = requests.get(f"{base_url}/files", params=files_params)
        if files_response.status_code == 200:
            files_result = files_response.json()
            print(f"   一覧に表示されるファイル数: {len(files_result['files'])}")
            for file_info in files_result['files']:
                print(f"   - {file_info['filename']} (v{file_info['latest_version']}) - {file_info['latest_operation']}")
        else:
            print(f"   ファイル一覧取得失敗: {files_response.status_code}")
            return False

        print("\n✓ APIエンドポイントでの削除されたファイルのダウンロード機能テストが成功しました！")
        return True

    except requests.exceptions.ConnectionError:
        print("✗ サーバーに接続できません。サーバーが起動していることを確認してください。")
        return False
    except Exception as e:
        print(f"✗ テスト中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    # サーバーの起動を待つ
    print("サーバーの起動を待っています...")
    time.sleep(3)

    success = test_api_download()
    sys.exit(0 if success else 1)
