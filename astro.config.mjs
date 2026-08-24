import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeTableWrap from './src/lib/rehype-table-wrap.mjs';

export default defineConfig({
  // Change this when you attach a real domain.
  site: 'https://ashley-cho.github.io',

  markdown: {
    // Math ($...$ inline, $$...$$ block) + auto-scrolling wide tables.
    processor: unified({
      remarkPlugins: [remarkMath],
      rehypePlugins: [rehypeKatex, rehypeTableWrap],
    }),
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark' },
      wrap: true,
    },
  },
});
