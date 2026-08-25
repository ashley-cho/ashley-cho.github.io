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

3. Commit and push to `main`. The GitHub Actions workflow in
   `.github/workflows/deploy.yml` builds the site and publishes it to GitHub
   Pages. Takes about a minute; watch it under the repo's Actions tab.

## What you can use in a post

- Normal Markdown: headings, lists, links, **bold**, tables, quotes.
- Math: `$E = mc^2$` inline, or `$$ ... $$` on its own lines for a centered block.
- Code blocks with syntax highlighting (triple backticks).
- Wide tables scroll sideways on phones automatically — you don't need to do anything.
- Callout boxes, for an aside you want set apart from the body text:

  ```html
  <div class="note">
    <span class="note-label">Caveat</span>
    The debris flux here rests on measurements that stopped in 2011.
  </div>
  ```

## Running it locally

```
npm install
npm run dev      # http://localhost:4321
npm run build    # writes dist/
npm test         # build + check every internal link resolves
```

`npm test` is what CI runs on every pull request. Run it before you push and
you'll almost never see a red build.

How the repo is wired up — CI, branch rules, deploys — is written down in
[`docs/repo-setup.md`](docs/repo-setup.md).

## Changing things

- Styling and colors: `src/styles/global.css` (all colors are variables at the top).
- Nav links, site title, footer: `src/layouts/Base.astro`.
- Home page intro text: `src/pages/index.astro`.
- About page: `src/pages/about.astro`.
- Your domain: `site:` in `astro.config.mjs` (only affects RSS links).

## Attaching a custom domain later

1. Buy the domain.
2. Point it at GitHub Pages with your registrar's DNS: an `ALIAS`/`ANAME` record
   for the apex domain to `ashley-cho.github.io`, or a `CNAME` record for a
   `www.` subdomain to the same.
3. Add it under the repo's Settings → Pages → Custom domain, and tick "Enforce
   HTTPS" once the certificate is issued.
4. Update `site:` in `astro.config.mjs` to the new URL.

Nothing else changes and old links keep working.
