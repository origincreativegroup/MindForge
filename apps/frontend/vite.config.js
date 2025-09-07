import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Basic Vite configuration for the process visualization frontend
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
});
