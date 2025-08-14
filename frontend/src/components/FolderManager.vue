<template>
  <div class="bg-white rounded-lg shadow-md">
    <div class="p-4 border-b border-gray-200 flex justify-between items-center">
      <h3 class="text-lg font-semibold text-gray-900">フォルダ管理</h3>
      <button
        @click="showCreateFolderModal = true"
        class="inline-flex items-center px-3 py-2 border border-transparent
               text-sm font-medium rounded-md text-white bg-blue-600
               hover:bg-blue-700 focus:outline-none focus:ring-2
               focus:ring-offset-2 focus:ring-blue-500"
      >
        <PlusIcon class="h-5 w-5 mr-2" />
        フォルダ作成
      </button>
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

    <div v-else-if="folders.length === 0" class="p-6 text-center text-gray-500">
      フォルダがありません。フォルダを作成してください。
    </div>

    <div v-else class="p-4">
      <FolderTree 
        :folders="folders" 
        :selected-folder-id="selectedFolderId"
        @select-folder="selectFolder"
      />
    </div>

    <!-- フォルダ作成モーダル -->
    <div
      v-if="showCreateFolderModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="showCreateFolderModal = false"
    >
      <div
        class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
        @click.stop
      >
        <div class="mt-3 text-center">
          <h3 class="text-lg font-medium text-gray-900 mb-4">新規フォルダ作成</h3>
          
          <div class="mb-4">
            <label for="folderName" class="block text-sm font-medium text-gray-700 mb-2">
              フォルダ名
            </label>
            <input
              id="folderName"
              v-model="newFolderName"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="フォルダ名を入力"
              @keyup.enter="createFolder"
            />
          </div>

          <div class="mb-4">
            <label for="parentFolder" class="block text-sm font-medium text-gray-700 mb-2">
              親フォルダ（オプション）
            </label>
            <select
              id="parentFolder"
              v-model="newFolderParentId"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option :value="null">親フォルダなし</option>
              <option 
                v-for="folder in flattenFolders(folders)" 
                :key="folder.id" 
                :value="folder.id"
              >
                {{ folder.name }}
              </option>
            </select>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              @click="showCreateFolderModal = false"
              class="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium
                     rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2
                     focus:ring-gray-500"
            >
              キャンセル
            </button>
            <button
              @click="createFolder"
              :disabled="!newFolderName"
              class="px-4 py-2 bg-blue-600 text-white text-sm font-medium
                     rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2
                     focus:ring-blue-500 disabled:bg-blue-400"
            >
              作成
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import { folderApi } from '../api'
import type { Folder } from '../types'
import FolderTree from './FolderTree.vue'

const emit = defineEmits<{
  'select-folder': [folderId: number | null]
}>()

const folders = ref<Folder[]>([])
const loading = ref(false)
const showCreateFolderModal = ref(false)
const newFolderName = ref('')
const newFolderParentId = ref<number | null>(null)
const selectedFolderId = ref<number | null>(null)

const loadFolders = async () => {
  loading.value = true
  try {
    const response = await folderApi.getFolders()
    folders.value = response.folders
  } catch (error) {
    console.error('フォルダ一覧の取得に失敗:', error)
  } finally {
    loading.value = false
  }
}

const createFolder = async () => {
  if (!newFolderName.value) return

  try {
    const newFolder = await folderApi.createFolder(
      newFolderName.value,
      newFolderParentId.value || undefined
    )
    
    // フォルダリストを再読み込み
    await loadFolders()
    
    // モーダルをリセット
    showCreateFolderModal.value = false
    newFolderName.value = ''
    newFolderParentId.value = null
  } catch (error) {
    console.error('フォルダ作成に失敗:', error)
  }
}

const selectFolder = (folderId: number | null) => {
  selectedFolderId.value = folderId
  emit('select-folder', folderId)
}

const flattenFolders = (folderList: Folder[], depth = 0): Folder[] => {
  const result: Folder[] = []
  folderList.forEach(folder => {
    result.push({
      ...folder,
      name: '　'.repeat(depth) + folder.name
    })
    if (folder.children && folder.children.length > 0) {
      result.push(...flattenFolders(folder.children, depth + 1))
    }
  })
  return result
}

onMounted(() => {
  loadFolders()
})

defineExpose({
  refresh: loadFolders
})
</script>