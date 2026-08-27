import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://pii2pw.pages.dev',
  vite: {
    server: { fs: { allow: ['..'] } },
  },
});
