#!/usr/bin/env python3
"""Emit the artifact form of the atlas.

Same page as dist/index.html, minus the <!doctype>/<html>/<head>/<body>
wrapper, because the artifact host supplies those itself. Run assemble.py
first so build/data.json is current.

    python3 tools/atlas/artifact.py   ->  dist/artifact.html
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
rd = lambda p: open(os.path.join(ROOT, p), encoding='utf-8').read()

head = rd('parts/head.html')
body = rd('parts/body.html')
app  = rd('parts/app.js')
data = json.load(open(os.path.join(ROOT, 'build/data.json'), encoding='utf-8'))
data.setdefault('meta', {})['built'] = datetime.datetime.now(
    datetime.timezone.utc).strftime('%Y-%m-%d')

blob = json.dumps(data, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
html = head + body + '<script>window.__DCDATA__=' + blob + ';</script>\n<script>' + app + '</script>\n'

out = os.path.join(ROOT, 'dist')
os.makedirs(out, exist_ok=True)
path = os.path.join(out, 'artifact.html')
open(path, 'w', encoding='utf-8').write(html)
print(f'wrote {path}  {len(html):,} chars')
