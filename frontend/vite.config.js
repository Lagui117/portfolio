import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
    host: true, // Permet l'accès depuis l'extérieur (Codespaces)
    watch: {
      usePolling: true, // Meilleur support dans Docker/Codespaces
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  },
  build: {
    sourcemap: true,
  }
})
