<template>
  <div class="space-y-2">
    <div
      @click="selectFolder(null)"
      :class="[
        'px-3 py-2 rounded-md cursor-pointer flex items-center transition-colors duration-150',
        selectedFolderId === null 
          ? 'bg-blue-100 text-blue-800' 
          : 'hover:bg-gray-100 text-gray-700'
      ]"
    >
      <FolderIcon class="h-5 w-5 mr-2" />
      すべてのファイル
    </div>

    <div v-for="folder in folders" :key="folder.id" class="pl-0">
      <FolderItem
        :folder="folder"
        :depth="0"
        :selected-folder-id="selectedFolderId"
        @select-folder="selectFolder"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { FolderIcon } from '@heroicons/vue/24/outline'
import type { Folder } from '../types'
import FolderItem from './FolderItem.vue'

const props = defineProps<{
  folders: Folder[]
  selectedFolderId: number | null
}>()

const emit = defineEmits<{
  'select-folder': [folderId: number | null]
}>()

const selectFolder = (folderId: number | null) => {
  emit('select-folder', folderId)
}
</script>