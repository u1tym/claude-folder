import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/files': 'http://localhost:8000',
      '/folders': 'http://localhost:8000'
    }
  }
})