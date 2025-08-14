<template>
  <div>
    <div
      @click="toggleFolder"
      :class="[
        'flex items-center px-3 py-2 rounded-md cursor-pointer transition-colors duration-150 relative',
        isSelected 
          ? 'bg-blue-100 text-blue-800' 
          : 'hover:bg-gray-100 text-gray-700'
      ]"
      :style="{ paddingLeft: `${depth * 1}rem` }"
    >
      <div class="flex items-center w-full">
        <ChevronRightIcon
          v-if="folder.children && folder.children.length > 0"
          :class="[
            'h-4 w-4 mr-1 transition-transform duration-200',
            isExpanded ? 'rotate-90' : ''
          ]"
        />
        <FolderIcon class="h-5 w-5 mr-2" />
        <span class="flex-1 truncate">{{ folder.name }}</span>
      </div>
    </div>

    <div 
      v-if="folder.children && folder.children.length > 0 && isExpanded" 
      class="space-y-1 mt-1"
    >
      <FolderItem
        v-for="childFolder in folder.children"
        :key="childFolder.id"
        :folder="childFolder"
        :depth="depth + 1"
        :selected-folder-id="selectedFolderId"
        @select-folder="selectFolder"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { FolderIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import type { Folder } from '../types'

const props = defineProps<{
  folder: Folder
  depth: number
  selectedFolderId: number | null
}>()

const emit = defineEmits<{
  'select-folder': [folderId: number]
}>()

const isExpanded = ref(false)

const isSelected = computed(() => {
  return props.selectedFolderId === props.folder.id
})

const toggleFolder = () => {
  if (props.folder.children && props.folder.children.length > 0) {
    isExpanded.value = !isExpanded.value
  }
  selectFolder(props.folder.id)
}

const selectFolder = (folderId: number) => {
  emit('select-folder', folderId)
}
</script>