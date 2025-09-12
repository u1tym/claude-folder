<template>
  <div class="bg-white rounded-lg shadow-md">
    <div class="px-6 py-4 border-b border-gray-200">
      <h2 class="text-xl font-semibold">ファイル一覧</h2>
    </div>

    <div v-if="loading" class="p-6 text-center">
      <svg
        class="animate-spin mx-auto h-8 w-8 text-blue-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      <p class="mt-2 text-gray-600">読み込み中...</p>
    </div>

    <div v-else-if="files.length === 0" class="p-6 text-center text-gray-500">
      アップロードされたファイルがありません
    </div>

    <div v-else class="divide-y divide-gray-200">
      <div
        v-for="file in files"
        :key="file.filename"
        class="p-6 hover:bg-gray-50 transition-colors duration-150"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <DocumentIcon v-if="file.latest_operation !== 'delete'" class="h-8 w-8 text-gray-400" />
                <TrashIcon v-else class="h-8 w-8 text-red-400" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-lg font-medium truncate" :class="file.latest_operation === 'delete' ? 'text-red-600 line-through' : 'text-gray-900'">
                  {{ file.filename }}
                  <span v-if="file.latest_operation === 'delete'" class="ml-2 text-sm text-red-500">(削除済み)</span>
                </p>
                <div class="flex items-center space-x-4 text-sm text-gray-500">
                  <span>v{{ file.latest_version }}</span>
                  <span>{{ formatFileSize(file.file_size) }}</span>
                  <span>{{ formatDate(file.latest_update) }}</span>
                  <span
                    :class="[
                      'px-2 py-1 rounded-full text-xs font-medium',
                      file.latest_operation === 'delete'
                        ? 'bg-red-100 text-red-800'
                        : file.latest_operation === 'create'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-blue-100 text-blue-800'
                    ]"
                  >
                    {{ getOperationLabel(file.latest_operation) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center space-x-2 ml-4">
            <button
              @click="$emit('showVersions', file.filename, file.folder_id)"
              class="inline-flex items-center px-3 py-1.5 border border-gray-300
                     text-sm font-medium rounded-md text-gray-700 bg-white
                     hover:bg-gray-50 focus:outline-none focus:ring-2
                     focus:ring-offset-2 focus:ring-blue-500"
            >
              <ClockIcon class="h-4 w-4 mr-1.5" />
              履歴
            </button>

            <button
              @click="downloadFile(file.filename)"
              :class="[
                'inline-flex items-center px-3 py-1.5 border border-transparent',
                'text-sm font-medium rounded-md focus:outline-none focus:ring-2',
                'focus:ring-offset-2',
                file.latest_operation === 'delete'
                  ? 'text-white bg-red-600 hover:bg-red-700 focus:ring-red-500'
                  : 'text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
              ]"
            >
              <ArrowDownTrayIcon class="h-4 w-4 mr-1.5" />
              {{ file.latest_operation === 'delete' ? '削除版をダウンロード' : 'ダウンロード' }}
            </button>

            <button
              v-if="file.latest_operation !== 'delete'"
              @click="showDeleteModal(file.filename)"
              class="inline-flex items-center px-3 py-1.5 border border-transparent
                     text-sm font-medium rounded-md text-white bg-red-600
                     hover:bg-red-700 focus:outline-none focus:ring-2
                     focus:ring-offset-2 focus:ring-red-500"
            >
              <TrashIcon class="h-4 w-4 mr-1.5" />
              削除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 削除確認モーダル -->
    <div
      v-if="deleteModal.show"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="closeDeleteModal"
    >
      <div
        class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
        @click.stop
      >
        <div class="mt-3">
          <div class="flex items-center">
            <ExclamationTriangleIcon class="h-6 w-6 text-red-600 mr-3" />
            <h3 class="text-lg font-medium text-gray-900">ファイルを削除</h3>
          </div>
          <div class="mt-4">
            <p class="text-sm text-gray-500 mb-4">
              「{{ deleteModal.filename }}」を削除しますか？<br>
              この操作は元に戻せません。
            </p>
            <textarea
              v-model="deleteModal.memo"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                     focus:ring-2 focus:ring-red-500 focus:border-red-500"
              placeholder="削除理由をメモしてください（オプション）"
            ></textarea>
          </div>
          <div class="flex justify-end space-x-3 mt-5">
            <button
              @click="closeDeleteModal"
              class="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium
                     rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2
                     focus:ring-gray-500"
            >
              キャンセル
            </button>
            <button
              @click="confirmDelete"
              :disabled="deleting"
              class="px-4 py-2 bg-red-600 text-white text-sm font-medium
                     rounded-md hover:bg-red-700 focus:outline-none focus:ring-2
                     focus:ring-red-500 disabled:bg-red-400"
            >
              {{ deleting ? '削除中...' : '削除' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import {
  DocumentIcon,
  ClockIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import { fileApi } from '../api'
import type { FileInfo } from '../types'

const emit = defineEmits<{
  showVersions: [filename: string, folderId?: number]
  deleted: [filename: string]
}>()

const props = defineProps<{
  initialFolderId?: number | null
}>()

const files = ref<FileInfo[]>([])
const loading = ref(false)
const deleting = ref(false)

const deleteModal = ref({
  show: false,
  filename: '',
  memo: ''
})

const loadFiles = async () => {
  loading.value = true
  try {
    const response = await fileApi.getFiles(props.initialFolderId || undefined)
    files.value = response.files
  } catch (error) {
    console.error('ファイル一覧の取得に失敗:', error)
  } finally {
    loading.value = false
  }
}

// initialFolderIdが変更されたら再読み込み
watch(() => props.initialFolderId, () => {
  loadFiles()
}, { immediate: true })

const downloadFile = async (filename: string) => {
  try {
    await fileApi.downloadFile(filename, undefined, props.initialFolderId || undefined)
  } catch (error) {
    console.error('ダウンロードに失敗:', error)
  }
}

const showDeleteModal = (filename: string) => {
  deleteModal.value = {
    show: true,
    filename,
    memo: ''
  }
}

const closeDeleteModal = () => {
  deleteModal.value = {
    show: false,
    filename: '',
    memo: ''
  }
}

const confirmDelete = async () => {
  if (!deleteModal.value.filename) return

  deleting.value = true
  try {
    await fileApi.deleteFile(
      deleteModal.value.filename,
      deleteModal.value.memo.trim() || undefined,
      props.initialFolderId || undefined
    )

    emit('deleted', deleteModal.value.filename)
    closeDeleteModal()
    await loadFiles() // リストを更新
  } catch (error: any) {
    console.error('削除に失敗:', error)
    alert(error.response?.data?.detail || '削除に失敗しました')
  } finally {
    deleting.value = false
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString('ja-JP')
}

const getOperationLabel = (operation: string): string => {
  switch (operation) {
    case 'create':
      return '新規作成'
    case 'update':
      return '更新'
    case 'delete':
      return '削除済み'
    default:
      return operation
  }
}

// 外部から呼び出せるようにする
const refresh = () => {
  loadFiles()
}

defineExpose({
  refresh
})

onMounted(() => {
  loadFiles()
})
</script>