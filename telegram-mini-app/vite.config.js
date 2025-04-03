import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Доступ в локальной сети
    port: 3000,      
    strictPort: true,
    allowedHosts: [
      '8c60-115-37-139-49.ngrok-free.app', 
      'localhost',                         
      
    ]
  }
})