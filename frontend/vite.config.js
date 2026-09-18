import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Goi /api/... tu frontend se tu dong forward sang backend FastAPI
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Chuyen PDF/DOCX/PPTX/anh sang Markdown truoc khi doc
      '/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
