import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // 重要: 部署路径需根据仓库名调整
  // 例如: alice-homepage -> /personalpage/alice-homepage/
  base: '/personalpage/hengzihan-homepage/',  // ← 用户需要修改这里

  server: {
    port: 5173,
    proxy: {
      // 代理 API 请求到生产环境
      '/api': {
        target: 'https://apps.habby.com',
        changeOrigin: true,
        secure: false,
      },
    },
  },

  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
});
