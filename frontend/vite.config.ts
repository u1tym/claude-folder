import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/files': 'http://127.0.0.1:8000',
      '/folders': 'http://127.0.0.1:8000'
    },
    // ARMアーキテクチャでの互換性向上
    hmr: {
      port: 24678
    }
  },
  // ARMアーキテクチャでの最適化
  optimizeDeps: {
    exclude: ['@vitejs/plugin-vue']
  },
  build: {
    target: 'es2015',
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
})