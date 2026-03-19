import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Обязательно для GitHub Pages:
  base: '/my-city/',
  server: {
    proxy: {
      '/api': {
        // Это будет работать ТОЛЬКО локально (npm run dev)
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    // Убеждаемся, что билд идет в папку dist (стандарт для gh-pages)
    outDir: 'dist',
  }
})