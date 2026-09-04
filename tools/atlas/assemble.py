#!/usr/bin/env python3
"""Assemble the Data Center Power Atlas into a single self-contained page.

Inputs  : parts/head.html, parts/body.html, parts/app.js, build/data.json
Output  : dist/index.html   (no external dependencies except Google Fonts)

The page is one file on purpose: it has to still render years from now with
nothing but a browser, so nothing is loaded from a CDN at runtime.
"""
import json, os, sys, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
def rd(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return f.read()

head = rd('parts/head.html')
body = rd('parts/body.html')
app  = rd('parts/app.js')
data = json.load(open(os.path.join(ROOT, 'build/data.json'), encoding='utf-8'))

built = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
data.setdefault('meta', {})['built'] = built

blob = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
# </script> inside a string would close the tag early
blob = blob.replace('</', '<\\/')

html = (
 '<!doctype html><html lang="en"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<meta name="description" content="Interactive map of global data centre capacity, '
 'electricity use and CO2 - every parameter anchored to measured national statistics.">'
 + head +
 '</head><body>' + body +
 '<script>window.__DCDATA__=' + blob + ';</script>'
 '<script>' + app + '</script>'
 '</body></html>'
)

out = os.path.join(ROOT, 'dist')
os.makedirs(out, exist_ok=True)
path = os.path.join(out, 'index.html')
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'wrote {path}  {len(html):,} bytes  (built {built})')
