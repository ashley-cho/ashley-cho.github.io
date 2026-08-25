# Stream of Random Thoughts

Personal site. Astro, static, no database, no CMS.

## Writing a new post

1. Add a Markdown file to `src/content/writing/`. The filename becomes the URL:
   `my-post.md` → `/writing/my-post/`
2. Give it frontmatter:

```markdown
---
title: "The title"
description: "One sentence. Shows on the index and in link previews."
date: 2026-09-01
series: "Data centers in orbit"   # optional
seriesPart: 2                      # optional
draft: false                       # set true to hide it
---

Body goes here.
```

3. Commit and push. Vercel rebuilds automatically.

## What you can use in a post

- Normal Markdown: headings, lists, links, **bold**, tables, quotes.
- Math: `$E = mc^2$` inline, or `$$ ... $$` on its own lines for a centered block.
- Code blocks with syntax highlighting (triple backticks).
- Wide tables scroll sideways on phones automatically — you don't need to do anything.

## Running it locally

```
npm install
npm run dev      # http://localhost:4321
npm run build    # writes dist/
```

## Changing things

- Styling and colors: `src/styles/global.css` (all colors are variables at the top).
- Nav links, site title, footer: `src/layouts/Base.astro`.
- Home page intro text: `src/pages/index.astro`.
- About page: `src/pages/about.astro`.
- Your domain: `site:` in `astro.config.mjs` (only affects RSS links).

## Attaching a custom domain later

Buy the domain, add it in the Vercel project settings under Domains, update
`site:` in `astro.config.mjs`. Nothing else changes and old links keep working.
