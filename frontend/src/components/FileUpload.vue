<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-xl font-semibold mb-4">ファイルアップロード</h2>
    
    <form @submit.prevent="handleUpload" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          ファイル選択
        </label>
        <input
          type="file"
          ref="fileInput"
          @change="onFileSelect"
          class="block w-full text-sm text-gray-500
                 file:mr-4 file:py-2 file:px-4
                 file:rounded-md file:border-0
                 file:text-sm file:font-medium
                 file:bg-blue-50 file:text-blue-700
                 hover:file:bg-blue-100"
          required
        />
      </div>

      <div>
        <label for="memo" class="block text-sm font-medium text-gray-700 mb-2">
          メモ（オプション）
        </label>
        <textarea
          id="memo"
          v-model="memo"
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="このファイルに関するメモを入力してください..."
        ></textarea>
      </div>

      <button
        type="submit"
        :disabled="!selectedFile || uploading"
        class="w-full flex justify-center py-2 px-4 border border-transparent
               rounded-md shadow-sm text-sm font-medium text-white
               bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2
               focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400
               disabled:cursor-not-allowed"
      >
        <svg
          v-if="uploading"
          class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
        {{ uploading ? 'アップロード中...' : 'アップロード' }}
      </button>
    </form>

    <!-- 成功/エラーメッセージ -->
    <div v-if="message" class="mt-4">
      <div
        :class="[
          'p-3 rounded-md text-sm',
          messageType === 'success' 
            ? 'bg-green-50 text-green-700 border border-green-200'
            : 'bg-red-50 text-red-700 border border-red-200'
        ]"
      >
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { fileApi } from '../api'

const props = defineProps<{
  folderId?: number
}>()

const emit = defineEmits<{
  uploaded: [filename: string]
}>()

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const memo = ref('')
const uploading = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

const onFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  selectedFile.value = target.files?.[0] || null
}

const handleUpload = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  message.value = ''

  try {
    console.log('Uploading file with folder ID:', props.folderId)
    
    const result = await fileApi.uploadFile(
      selectedFile.value,
      memo.value.trim() || undefined,
      props.folderId
    )
    
    console.log('Upload result:', result)
    
    message.value = result.message
    messageType.value = 'success'
    
    // フォームをリセット
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    selectedFile.value = null
    memo.value = ''
    
    // 親コンポーネントに通知
    emit('uploaded', result.filename)
    
  } catch (error: any) {
    console.error('Upload error:', error)
    message.value = error.response?.data?.detail || 'アップロードに失敗しました'
    messageType.value = 'error'
  } finally {
    uploading.value = false
  }
}
</script>