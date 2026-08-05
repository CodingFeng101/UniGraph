import { fileURLToPath, URL } from 'node:url';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  base: '/unigraph/',
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          const moduleId = id.replaceAll('\\', '/');
          if (!moduleId.includes('/node_modules/')) return undefined;

          if (moduleId.includes('/node_modules/cytoscape-cose-bilkent/')) return 'graph-layout-cose';
          if (moduleId.includes('/node_modules/cytoscape-dagre/')) return 'graph-layout-dagre';
          if (moduleId.includes('/node_modules/cytoscape-fcose/')) return 'graph-layout-fcose';
          if (moduleId.includes('/node_modules/cytoscape/')) return 'graph-cytoscape';
          if (moduleId.includes('/node_modules/vis-network/')) return 'graph-vis-network';
          if (/\/node_modules\/(vis-data|vis-util)\//.test(moduleId)) return 'graph-vis-data';
          if (moduleId.includes('/node_modules/gsap/')) return 'motion';
          if (/\/node_modules\/(vue|vue-router|@vue)\//.test(moduleId)) return 'vue';
          if (/\/node_modules\/(markdown-it|dompurify)\//.test(moduleId)) return 'content';
          if (moduleId.includes('/node_modules/lucide/')) return 'icons';
          return undefined;
        },
      },
    },
  },
});
