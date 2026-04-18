import { fileURLToPath } from 'node:url';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.API_PROXY_TARGET ?? 'http://localhost:8000',
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/auth': {
        target: process.env.AUTH_PROXY_TARGET ?? 'http://127.0.0.1:8001',
        rewrite: (path) => path.replace(/^\/auth/, ''),
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    exclude: ['**/node_modules/**', '**/dist/**', 'e2e/**'],
    env: { VITE_API_BASE_URL: 'http://localhost/api', VITE_AUTH_BASE_URL: 'http://localhost/auth' },
    coverage: {
      provider: 'v8',
      include: ['src/**'],
      exclude: [
        'src/**/*.css',
        'src/api/schema.ts',
        'src/api/index.ts',
        'src/auth/schema.ts',
        'src/main.tsx',
        'src/App.tsx',
        'src/components/ui/**',
        'src/hooks/use-toast.ts',
        'src/test/**',
        'src/**/*.test.*',
        'src/vite-env.d.ts',
      ],
      reporter: ['text', 'html', 'json-summary'],
      thresholds: {
        lines: 80,
      },
    },
  },
});
