import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  envDir: false,
  define: { 'import.meta.env.VITE_API_URL': JSON.stringify('http://127.0.0.1:8001') },
  build: { outDir: '../../.venv/p5a2-source-demo-web', emptyOutDir: true },
});
