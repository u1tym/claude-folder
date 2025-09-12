import axios from 'axios'
import type { UploadResponse, FilesListResponse, FileVersionsResponse } from './types'

const fileApiClient = axios.create({
  baseURL: '/files'
})

const folderApiClient = axios.create({
  baseURL: ''  // ルートパスに変更
})

export const folderApi = {
  // フォルダ一覧取得
  async getFolders(): Promise<FolderListResponse> {
    const response = await folderApiClient.get<Folder[]>('/folders')
    return { folders: response.data }
  },

  // フォルダ作成
  async createFolder(name: string, parentId?: number): Promise<Folder> {
    const formData = new FormData()
    formData.append('name', name)
    if (parentId !== undefined) {
      formData.append('parent_id', parentId.toString())
    }

    const response = await folderApiClient.post<Folder>('/folders', formData)
    return response.data
  }
}

export const fileApi = {
  // ファイル一覧取得
  async getFiles(folderId?: number): Promise<FilesListResponse> {
    const params = folderId !== undefined ? { folder_id: folderId } : {}
    const response = await fileApiClient.get<FilesListResponse>('', { params })
    return response.data
  },

  // ファイルアップロード
  async uploadFile(file: File, memo?: string, folderId?: number): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (memo) {
      formData.append('memo', memo)
    }
    if (folderId !== undefined) {
      formData.append('folder_id', folderId.toString())
    }

    const response = await fileApiClient.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // ファイル削除
  async deleteFile(filename: string, memo?: string, folderId?: number): Promise<UploadResponse> {
    const params: any = {}
    if (memo) params.memo = memo
    if (folderId !== undefined) params.folder_id = folderId
    const response = await fileApiClient.delete<UploadResponse>(`/${filename}`, { params })
    return response.data
  },

  // ファイルバージョン履歴取得
  async getFileVersions(filename: string, folderId?: number): Promise<FileVersionsResponse> {
    const params = folderId !== undefined ? { folder_id: folderId } : {}
    const response = await fileApiClient.get<FileVersionsResponse>(`/${filename}/versions`, { params })
    return response.data
  },

  // ファイルダウンロードURL取得
  getDownloadUrl(filename: string, version?: number, folderId?: number): string {
    const params = new URLSearchParams()
    if (version !== undefined) {
      params.append('version', version.toString())
    }
    if (folderId !== undefined) {
      params.append('folder_id', folderId.toString())
    }
    return `/files/${filename}/download?${params.toString()}`
  },

  // ファイルダウンロード
  async downloadFile(filename: string, version?: number, folderId?: number): Promise<void> {
    const url = this.getDownloadUrl(filename, version, folderId)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}