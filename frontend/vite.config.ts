import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      "/static": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/pve/api/": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    sourcemap: true,
    manifest: true,
    rollupOptions: {
      output: {
        // this is to make sure our static files are in the write place when we build
        assetFileNames: (assetInfo) => {
          let extType = assetInfo.names[0].split('.').pop() || '';
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            extType = 'img';
          }
          // fake the path, we copy them over properly later
          return `static/allianceauth_pve/react/static/${extType}/[name]-[hash][extname]`;
        },
        manualChunks(id) {
          // creating a chunk to react routes deps. Reducing the vendor chunk size
          if (
            id.includes('react-router') ||
            id.includes('react-select') ||
            id.includes('react-slider') ||
            id.includes('react-data-table-component') ||
            id.includes('react-awesome-styled-grid') ||
            id.includes('react-markdown')
          ) {
            return '@react-libs';
          }
          if (
            id.includes('datatables')
          ) {
            return '@datatables-libs';
          }
          if (
            id.includes('buffer') ||
            id.includes('chart.js') ||
            id.includes('react-chartjs-2') ||
            id.includes('@nivo/core') ||
            id.includes('lodash') ||
            id.includes('remark-gfm') ||
            id.includes('styled-components') ||
            id.includes('varint')
          ) {
            return '@app-libs';
          }
          if (id.includes('react-bootstrap') || id.includes('bootstrap')) {
            return '@bootstrap-libs'; // Not Yet Used, want to
          }
          if (
            id.includes('i18next') ||
            id.includes('i18next-http-backend') ||
            id.includes('i18next-browser-languagedetector') ||
            id.includes('react-i18next')
          ) {
            return '@lang-libs'; // Translations
          }
          if (
            id.includes('fontawesome-svg-core') ||
            id.includes('free-brands-svg-icons') ||
            id.includes('free-solid-svg-icons') ||
            id.includes('react-fontawesome')
          ) {
            return '@fontawesome-libs'; // Graphics
          }
        },
      },
    },
  }
})
