export interface Folder {
  id: number
  name: string
  parent_id?: number
  children?: Folder[]
}

export interface FileVersion {
  version: number
  operation: 'create' | 'update' | 'delete'
  memo?: string
  created_at: string
  file_size: number
  mime_type?: string
  folder_id?: number
}

export interface FileInfo {
  filename: string
  latest_version: number
  latest_operation: string
  latest_update: string
  file_size: number
  mime_type?: string
  folder_name?: string
  folder_id?: number
}

export interface ApiResponse<T> {
  data?: T
  message?: string
  error?: string
}

export interface UploadResponse {
  message: string
  filename: string
  version: number
  memo?: string
  operation: string
  folder_id?: number
}

export interface FileVersionsResponse {
  filename: string
  versions: FileVersion[]
}

export interface FilesListResponse {
  files: FileInfo[]
}

export interface FolderListResponse {
  folders: Folder[]
}