import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";
import { visualizer } from "rollup-plugin-visualizer";
import { compression } from 'vite-plugin-compression2';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    mode === 'development' && componentTagger(),
    // Visualize bundle size in production
    mode === 'production' && visualizer({
      filename: './dist/bundle-stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
    // Compression for production
    mode === 'production' && compression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    mode === 'production' && compression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    // Optimizaciones para producción
    rollupOptions: {
      output: {
        // Enhanced manual chunks strategy
        manualChunks: (id) => {
          // Core React ecosystem
          if (id.includes('node_modules/react/') || 
              id.includes('node_modules/react-dom/') || 
              id.includes('node_modules/react-router')) {
            return 'react-core';
          }
          
          // UI Component libraries
          if (id.includes('@radix-ui') || id.includes('@headlessui')) {
            return 'ui-components';
          }
          
          // State management
          if (id.includes('zustand') || id.includes('immer')) {
            return 'state-management';
          }
          
          // Data fetching and API
          if (id.includes('@tanstack/react-query') || 
              id.includes('axios') || 
              id.includes('@supabase')) {
            return 'data-fetching';
          }
          
          // Form handling
          if (id.includes('react-hook-form') || 
              id.includes('@hookform') || 
              id.includes('zod')) {
            return 'forms';
          }
          
          // Charts and data visualization
          if (id.includes('recharts') || 
              id.includes('d3') || 
              id.includes('victory')) {
            return 'data-viz';
          }
          
          // Utilities
          if (id.includes('date-fns') || 
              id.includes('lodash') || 
              id.includes('clsx') || 
              id.includes('tailwind-merge')) {
            return 'utilities';
          }
          
          // Icons
          if (id.includes('lucide-react') || id.includes('@heroicons')) {
            return 'icons';
          }
          
          // Animation libraries
          if (id.includes('framer-motion') || id.includes('@react-spring')) {
            return 'animations';
          }
          
          // Media handling
          if (id.includes('react-player') || 
              id.includes('react-audio') || 
              id.includes('wavesurfer')) {
            return 'media';
          }
        },
        
        // Optimize chunk names
        chunkFileNames: (chunkInfo) => {
          const name = chunkInfo.name || 'chunk';
          // Use content hash for better caching
          return `assets/js/${name}.[hash].js`;
        },
        
        // Entry chunk naming
        entryFileNames: 'assets/js/[name].[hash].js',
        
        // Asset naming
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.');
          const ext = info?.[info.length - 1];
          
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext || '')) {
            return `assets/images/[name].[hash][extname]`;
          }
          
          if (/woff2?|ttf|otf|eot/i.test(ext || '')) {
            return `assets/fonts/[name].[hash][extname]`;
          }
          
          return `assets/[name].[hash][extname]`;
        },
      },
      
      // Preserve module structure for better tree shaking
      preserveModules: false,
      
      // External dependencies (if using CDN)
      external: mode === 'production' ? [] : [],
    },
    // Aumentar el límite de advertencia
    chunkSizeWarningLimit: 1000,
    // Minificar el código
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: mode === 'production',
        drop_debugger: mode === 'production',
      },
    },
    // Generar sourcemaps solo en desarrollo
    sourcemap: mode !== 'production',
  },
  // Advanced optimizations
  optimizeDeps: {
    // Pre-bundle heavy dependencies
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@tanstack/react-query',
      'zustand',
      'recharts',
      '@radix-ui/react-dialog',
      '@radix-ui/react-tabs',
    ],
    exclude: ['@vite/client', '@vite/env'],
    // Force optimize deps on start
    force: mode === 'development',
  },
  
  // CSS code splitting
  css: {
    modules: {
      localsConvention: 'camelCase',
    },
    postcss: {
      plugins: [
        // Add autoprefixer and other PostCSS plugins here if needed
      ],
    },
  },
  
  // Enable build optimizations
  esbuild: {
    // Remove console and debugger in production
    drop: mode === 'production' ? ['console', 'debugger'] : [],
    // Legal comments
    legalComments: 'none',
  },
}));
