import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://alustos.us',
  output: 'static',
  trailingSlash: 'never',
  outDir: './output',
  devToolbar: { enabled: false },
  build: { format: 'file' },
});
