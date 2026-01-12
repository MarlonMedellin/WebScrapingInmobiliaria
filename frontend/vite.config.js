import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['csimedellin.link', 'localhost', '127.0.0.1'],
    host: true,
    port: 5173
  }
})
