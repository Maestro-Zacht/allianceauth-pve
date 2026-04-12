import { defineConfig, type PluginOption } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    visualizer({
      template: "treemap",
      gzipSize: true,
      brotliSize: true,
      filename: "analyse.html",
    }) as PluginOption,
  ],
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
    rolldownOptions: {
      output: {
        // strictExecutionOrder: true,
        // this is to make sure our static files are in the write place when we build
        assetFileNames: (assetInfo: { names: string[] }) => {
          let extType = assetInfo.names[0].split('.').pop() || '';
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            extType = 'img';
          }
          // fake the path, we copy them over properly later
          return `static/allianceauth_pve/react/static/${extType}/[name]-[hash][extname]`;
        },
        codeSplitting: {
          groups: [
            {
              name: '@react-libs',
              test: /[\\/]node_modules[\\/](react|react-dom|react-router-dom|react-router)[\\/]/,
              priority: 10,
            },
            {
              name: '@datatables-libs',
              test: /[\\/]node_modules[\\/]datatables/,
              priority: 9,
            },
            {
              name: '@app-libs',
              test: /[\\/]node_modules[\\/](react-timeago|react-hook-form|@hookform\/resolvers|zod|openapi-fetch|js-cookie|@tanstack)[\\/]/,
              priority: 8,
            },
            {
              name: '@bootstrap-libs',
              test: /[\\/]node_modules[\\/](bootstrap|react-bootstrap)[\\/]/,
              priority: 7,
            },
            {
              name: '@lang-libs',
              test: /[\\/]node_modules[\\/](i18next|react-i18next|i18next-http-backend|i18next-browser-languagedetector)[\\/]/,
              priority: 6,
            },
            {
              name: '@misc-libs',
              test: /node_modules/,
              priority: 1,
            }
          ]
        }
      },
    },
  }
})
