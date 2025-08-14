<template>
  <div class="min-h-screen bg-gray-50">
    <!-- ヘッダー -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <DocumentIcon class="h-8 w-8 text-blue-600 mr-3" />
            <h1 class="text-xl font-semibold text-gray-900">
              File Version Manager
            </h1>
          </div>
          <div class="flex items-center space-x-4">
            <button
              @click="refreshFileList"
              class="inline-flex items-center px-3 py-2 border border-gray-300
                     text-sm font-medium rounded-md text-gray-700 bg-white
                     hover:bg-gray-50 focus:outline-none focus:ring-2
                     focus:ring-offset-2 focus:ring-blue-500"
            >
              <ArrowPathIcon class="h-4 w-4 mr-2" />
              更新
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- メインコンテンツ -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-12 gap-6">
        <!-- フォルダ管理 -->
        <div class="col-span-3">
          <FolderManager 
            ref="folderManagerRef"
            @select-folder="onFolderSelect"
          />
        </div>

        <div class="col-span-9 space-y-8">
          <!-- ファイルアップロード -->
          <FileUpload 
            :folder-id="selectedFolderId"
            @uploaded="onFileUploaded" 
          />

          <!-- ファイル一覧 -->
          <FileList
            ref="fileListRef"
            :initial-folder-id="selectedFolderId"
            @show-versions="showVersionHistory"
            @deleted="onFileDeleted"
          />
        </div>
      </div>
    </main>

    <!-- バージョン履歴モーダル -->
    <VersionHistory
      :show="versionHistory.show"
      :filename="versionHistory.filename"
      @close="closeVersionHistory"
    />

    <!-- 通知トースト -->
    <div
      v-if="notification.show"
      class="fixed top-4 right-4 bg-white border-l-4 p-4 rounded-md shadow-lg z-40 min-w-80"
      :class="[
        notification.type === 'success'
          ? 'border-green-400 bg-green-50'
          : notification.type === 'error'
          ? 'border-red-400 bg-red-50'
          : 'border-blue-400 bg-blue-50'
      ]"
    >
      <div class="flex">
        <div class="flex-shrink-0">
          <CheckCircleIcon
            v-if="notification.type === 'success'"
            class="h-5 w-5 text-green-400"
          />
          <ExclamationCircleIcon
            v-else-if="notification.type === 'error'"
            class="h-5 w-5 text-red-400"
          />
          <InformationCircleIcon
            v-else
            class="h-5 w-5 text-blue-400"
          />
        </div>
        <div class="ml-3">
          <p
            class="text-sm font-medium"
            :class="[
              notification.type === 'success'
                ? 'text-green-800'
                : notification.type === 'error'
                ? 'text-red-800'
                : 'text-blue-800'
            ]"
          >
            {{ notification.message }}
          </p>
        </div>
        <div class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button
              @click="hideNotification"
              class="inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2"
              :class="[
                notification.type === 'success'
                  ? 'text-green-500 hover:bg-green-100 focus:ring-green-600'
                  : notification.type === 'error'
                  ? 'text-red-500 hover:bg-red-100 focus:ring-red-600'
                  : 'text-blue-500 hover:bg-blue-100 focus:ring-blue-600'
              ]"
            >
              <XMarkIcon class="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  DocumentIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import FileUpload from './components/FileUpload.vue'
import FileList from './components/FileList.vue'
import VersionHistory from './components/VersionHistory.vue'
import FolderManager from './components/FolderManager.vue'

const fileListRef = ref<InstanceType<typeof FileList>>()
const folderManagerRef = ref<InstanceType<typeof FolderManager>>()

const versionHistory = ref({
  show: false,
  filename: ''
})

const selectedFolderId = ref<number | null>(null)

const notification = ref({
  show: false,
  message: '',
  type: 'info' as 'success' | 'error' | 'info'
})

let notificationTimeout: number | null = null

const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  notification.value = {
    show: true,
    message,
    type
  }

  // 3秒後に自動で隠す
  if (notificationTimeout) {
    clearTimeout(notificationTimeout)
  }
  notificationTimeout = setTimeout(() => {
    hideNotification()
  }, 3000)
}

const hideNotification = () => {
  notification.value.show = false
  if (notificationTimeout) {
    clearTimeout(notificationTimeout)
    notificationTimeout = null
  }
}

const showVersionHistory = (filename: string) => {
  versionHistory.value = {
    show: true,
    filename
  }
}

const closeVersionHistory = () => {
  versionHistory.value = {
    show: false,
    filename: ''
  }
}

const onFileUploaded = (filename: string) => {
  showNotification(`ファイル「${filename}」がアップロードされました`, 'success')
  refreshFileList()
}

const onFileDeleted = (filename: string) => {
  showNotification(`ファイル「${filename}」が削除されました`, 'success')
}

const refreshFileList = () => {
  fileListRef.value?.refresh()
  showNotification('ファイル一覧を更新しました', 'info')
}

const onFolderSelect = (folderId: number | null) => {
  console.log('Selected Folder ID:', folderId)
  selectedFolderId.value = folderId
}
</script>