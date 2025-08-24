import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/files': 'http://localhost:8000',
      '/folders': 'http://localhost:8000'
    },
    // ARMアーキテクチャでの互換性向上
    hmr: {
      port: 24678,
      host: 'localhost'
    }
  },
  // ARMアーキテクチャでの最適化
  optimizeDeps: {
    exclude: ['@vitejs/plugin-vue'],
    esbuildOptions: {
      target: 'es2015'
    }
  },
  build: {
    target: 'es2015',
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true
      }
    }
  },
  // メモリ使用量を制限
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false
  }
})
