<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    @click="close"
  >
    <div
      class="relative top-8 mx-auto p-6 border max-w-4xl shadow-lg rounded-md bg-white"
      @click.stop
    >
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-xl font-semibold text-gray-900">
          {{ filename }} - バージョン履歴
        </h3>
        <button
          @click="close"
          class="text-gray-400 hover:text-gray-600 focus:outline-none"
        >
          <XMarkIcon class="h-6 w-6" />
        </button>
      </div>

      <div v-if="loading" class="text-center py-8">
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
        <p class="mt-2 text-gray-600">バージョン履歴を読み込み中...</p>
      </div>

      <div v-else-if="versions.length === 0" class="text-center py-8 text-gray-500">
        バージョン履歴がありません
      </div>

      <div v-else class="space-y-4 max-h-96 overflow-y-auto">
        <div
          v-for="(version, index) in versions"
          :key="version.version"
          class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-2">
                <span class="text-lg font-medium text-gray-900">
                  バージョン {{ version.version }}
                </span>
                <span
                  v-if="index === 0"
                  class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full"
                >
                  最新
                </span>
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    version.operation === 'delete'
                      ? 'bg-red-100 text-red-800'
                      : version.operation === 'create'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-blue-100 text-blue-800'
                  ]"
                >
                  {{ getOperationLabel(version.operation) }}
                </span>
              </div>

              <div class="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                <span class="flex items-center">
                  <CalendarDaysIcon class="h-4 w-4 mr-1" />
                  {{ formatDate(version.created_at) }}
                </span>
                <span v-if="version.file_size > 0" class="flex items-center">
                  <DocumentIcon class="h-4 w-4 mr-1" />
                  {{ formatFileSize(version.file_size) }}
                </span>
                <span v-if="version.mime_type" class="flex items-center">
                  <DocumentIcon class="h-4 w-4 mr-1" />
                  {{ version.mime_type }}
                </span>
              </div>

              <div v-if="version.memo" class="bg-gray-50 p-3 rounded-md">
                <p class="text-sm font-medium text-gray-700 mb-1">メモ:</p>
                <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ version.memo }}</p>
              </div>
            </div>

            <div v-if="version.operation !== 'delete'" class="ml-4 flex-shrink-0">
              <button
                @click="downloadVersion(version.version)"
                class="inline-flex items-center px-3 py-1.5 border border-transparent
                       text-sm font-medium rounded-md text-white bg-blue-600
                       hover:bg-blue-700 focus:outline-none focus:ring-2
                       focus:ring-offset-2 focus:ring-blue-500"
              >
                <ArrowDownTrayIcon class="h-4 w-4 mr-1.5" />
                ダウンロード
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="flex justify-end mt-6">
        <button
          @click="close"
          class="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium
                 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2
                 focus:ring-gray-500"
        >
          閉じる
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  XMarkIcon,
  ArrowDownTrayIcon,
  CalendarDaysIcon,
  DocumentIcon
} from '@heroicons/vue/24/outline'
import { fileApi } from '../api'
import type { FileVersion } from '../types'

interface Props {
  show: boolean
  filename: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const versions = ref<FileVersion[]>([])
const loading = ref(false)

const loadVersions = async () => {
  if (!props.filename) return

  loading.value = true
  try {
    const response = await fileApi.getFileVersions(props.filename)
    versions.value = response.versions
  } catch (error) {
    console.error('バージョン履歴の取得に失敗:', error)
    versions.value = []
  } finally {
    loading.value = false
  }
}

const downloadVersion = async (version: number) => {
  try {
    await fileApi.downloadFile(props.filename, version)
  } catch (error) {
    console.error('ダウンロードに失敗:', error)
    alert('ダウンロードに失敗しました')
  }
}

const close = () => {
  emit('close')
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString('ja-JP')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const getOperationLabel = (operation: string): string => {
  switch (operation) {
    case 'create':
      return '新規作成'
    case 'update':
      return '更新'
    case 'delete':
      return '削除'
    default:
      return operation
  }
}

// ファイル名が変更されたらバージョン履歴を読み込む
watch(() => props.filename, loadVersions, { immediate: true })

// モーダルが表示されたらバージョン履歴を読み込む
watch(() => props.show, (show) => {
  if (show && props.filename) {
    loadVersions()
  }
})
</script>