import { resolve } from 'path'
import { defineConfig } from 'electron-vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  main: {},
  preload: {},
  renderer: {
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8420',
          changeOrigin: true
        },
        '/ws': {
          target: 'ws://127.0.0.1:8420',
          ws: true
        },
        '/thumbnails': {
          target: 'http://127.0.0.1:8420',
          changeOrigin: true
        },
        '/cache': {
          target: 'http://127.0.0.1:8420',
          changeOrigin: true
        }
      }
    },
    resolve: {
      alias: {
        '@renderer': resolve('src/renderer/src')
      }
    },
    plugins: [tailwindcss(), react()]
  }
})
