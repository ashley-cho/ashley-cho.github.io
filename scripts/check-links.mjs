// Verifies every internal link in the built site points at a page that exists.
// No dependencies — reads dist/ directly. Run after `npm run build`.
import { readdir, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, posix } from 'node:path';

const DIST = 'dist';

async function htmlFiles(dir) {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...await htmlFiles(p));
    else if (e.name.endsWith('.html')) out.push(p);
  }
  return out;
}

// Does an internal URL path resolve to something in dist/?
function resolves(urlPath) {
  const clean = urlPath.split('#')[0].split('?')[0];
  if (!clean || clean === '/') return existsSync(join(DIST, 'index.html'));
  const rel = clean.replace(/^\//, '');
  return (
    existsSync(join(DIST, rel)) ||                  // /rss.xml, /img/x.png
    existsSync(join(DIST, rel, 'index.html')) ||    // /writing/foo/
    existsSync(join(DIST, `${rel}.html`))           // /about.html
  );
}

const broken = [];
const pages = await htmlFiles(DIST);

for (const file of pages) {
  const html = await readFile(file, 'utf8');
  const from = '/' + posix.relative(DIST, file).replace(/index\.html$/, '');
  for (const m of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const url = m[1];
    // Only internal, absolute-path links. Skip external, protocol-relative,
    // anchors, mailto:, data: URIs.
    if (!url.startsWith('/') || url.startsWith('//')) continue;
    if (!resolves(url)) broken.push({ from, url });
  }
}

if (broken.length) {
  console.error(`\n✗ ${broken.length} broken internal link(s):\n`);
  for (const b of broken) console.error(`  ${b.from}  →  ${b.url}`);
  console.error('');
  process.exit(1);
}
console.log(`✓ checked ${pages.length} page(s), all internal links resolve`);
