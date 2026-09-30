import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // The map chunk is maplibre-gl alone (~1.06 MB, ~286 kB gzip) and cannot be split further; App loads it lazily.
    // The limit sits just above it, so the warning still fires if the entry chunk or the map chunk grows.
    chunkSizeWarningLimit: 1100,
  },
})
