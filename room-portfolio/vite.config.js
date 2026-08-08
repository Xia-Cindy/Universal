import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import glsl from 'vite-plugin-glsl';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react(), glsl()],
    server: {
        port: 5180,
        proxy: {
            '/api': 'http://127.0.0.1:8000'
        }
    }
});
