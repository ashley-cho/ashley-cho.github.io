#!/usr/bin/env python3
"""What the judgement path must refuse.

apply_judgement.py exists so a session that has done the judgement pass can land
it without a human pushing. That only stays defensible while the gate is real,
so every rule the gate claims to enforce is pinned here: the writable set, the
admission band, the date window, the edit ceiling, reference integrity, and the
file formatting that keeps diffs readable.

It runs against copies in a temp directory; the real build/ is never written.

    python3 tools/atlas/test_apply_judgement.py
"""
import datetime, importlib.util, json, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('aj', os.path.join(ROOT, 'apply_judgement.py'))
aj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aj)

TODAY = datetime.date(2026, 9, 20)
failures = []


def check(name, got, want):
    if got == want:
        print(f'  ok   {name}')
    else:
        print(f'  FAIL {name}\n       got  {got!r}\n       want {want!r}')
        failures.append(name)


def sandbox():
    d = tempfile.mkdtemp(prefix='atlas-judge-')
    for f in ('news.json', 'policy.json', 'regs.json', 'disputed.json', 'sites.py'):
        shutil.copy(os.path.join(ROOT, 'build', f), os.path.join(d, f))
    return d


def refuse(payload, today=TODAY):
    """Return the refusal message, or None if the payload was accepted."""
    try:
        aj.apply(payload, sandbox(), today)
        return None
    except aj.Refused as exc:
        return str(exc)


NEWS = {'date': '2026-09-20', 'kind': 'policy', 'title': 'A regulator did a thing',
        'detail': 'Enough detail to describe what the filing actually says and when.',
        'effect': 'No figure moved. Recorded in the regulatory set.',
        'moved': False, 'src': 'Some PUC', 'url': 'https://example.org/order'}

REG = {'k': 'testk', 'place': 'Nowhere', 'body': 'Some Commission', 'ref': 'Docket 1',
       'date': '1 Jan 2026', 'iso': 'USA', 'metros': [], 'national': False,
       'head': 'A headline of adequate length',
       'body_text': 'x' * 250, 'url': 'https://example.org/o', 'sites': []}

# --- the writable set: anything that moves a fitted number stays manual
check('refuses a section outside the four ledger files',
      'unknown sections' in (refuse({'calib': {'anchors': []}}) or ''), True)
check('refuses an operation the section does not define',
      'unknown operations' in (refuse({'news': {'remove': [0]}}) or ''), True)
check('calib, override, newload and sites are not writable',
      aj.WRITABLE, {'news.json', 'policy.json', 'regs.json', 'disputed.json'})

# --- Test 2 of the admission policy, enforced rather than trusted
china = {'place': 'China', 'body': 'NBS', 'fig': '260 TWh (2024)', 'lf': 0.93,
         'role': 'anchor', 'basis': 'metro basis', 'why': 'x' * 60}
check('refuses an anchor outside the load-factor band',
      'fails Test 2' in (refuse({'policy': {'admit': [china]}}) or ''), True)
check('the same figure is fine as a declared override',
      refuse({'policy': {'admit': [dict(china, role='override')]}}), None)
check('accepts an anchor inside the band',
      refuse({'policy': {'admit': [dict(china, place='Ireland', lf=0.698)]}}), None)

# --- the date window: items expire on their own, so nothing may be backdated
check('refuses a news item dated outside today or yesterday',
      'neither today nor yesterday' in
      (refuse({'news': {'add': [dict(NEWS, date='2026-09-10')]}}) or ''), True)
check('refuses a news item dated into the future',
      'neither today nor yesterday' in
      (refuse({'news': {'add': [dict(NEWS, date='2026-09-21')]}}) or ''), True)
check('accepts yesterday', refuse({'news': {'add': [dict(NEWS, date='2026-09-19')]}}), None)

# --- a moved figure has to name itself
check('refuses moved:true without figures in the effect',
      'before and after' in (refuse({'news': {'add': [dict(NEWS, moved=True)]}}) or ''), True)

# --- reference integrity: a filing may not point at a place the map lacks
check('refuses a regs entry naming an unmapped metro',
      'nothing on the map' in
      (refuse({'regs': {'add': [dict(REG, metros=['Atlantis'])]}}) or ''), True)
check('accepts a regs entry naming a real metro',
      refuse({'regs': {'add': [dict(REG, metros=['Dublin'])]}}), None)
check('refuses a duplicate regs key',
      'already exists' in (refuse({'regs': {'add': [dict(REG, k='cru')]}}) or ''), True)
check('refuses a regs update to a field that is not mutable here',
      'may not change' in
      (refuse({'regs': {'update': [{'k': 'cru', 'iso': 'GBR'}]}}) or ''), True)

# --- unknown and missing fields are errors, not silent passes
check('refuses an unknown field on a news item',
      'unknown' in (refuse({'news': {'add': [dict(NEWS, spin='upbeat')]}}) or ''), True)
check('refuses a stub body_text on a filing',
      'at least 200' in (refuse({'regs': {'add': [dict(REG, body_text='short')]}}) or ''), True)
check('refuses a rejection re-check for a place that is not rejected',
      'not in the rejected list' in
      (refuse({'policy': {'recheck': [{'place': 'Atlantis', 'why': 'x' * 60}]}}) or ''), True)
check('accepts a rejection re-check for one that is',
      refuse({'policy': {'recheck': [{'place': 'World', 'why': 'x' * 60}]}}), None)

# --- a dispute needs two sides
check('refuses a disputed entry with one figure',
      'not a dispute' in (refuse({'disputed': {'set': {'XXX': {
          'note': 'n' * 80, 'using': 'iea',
          'vals': [{'twh': 1, 'pct': 1, 'src': 'a', 'yr': '2026',
                    'url': 'https://example.org'}]}}}}) or ''), True)

# --- the ceiling, and the floor
check('refuses an empty payload', 'nothing to do' in (refuse({}) or ''), True)
check('refuses more edits than the ceiling',
      'ceiling is' in (refuse({'news': {'add': [NEWS] * (aj.MAX_OPS + 1)}}) or ''), True)

# --- formatting: a landed edit must not reflow the file, and must not touch
# --- the files it had nothing to say about
d = sandbox()
before = {f: open(os.path.join(d, f), encoding='utf-8').read() for f in aj.WRITABLE}
files, _ = aj.apply({'news': {'add': [NEWS]}}, d, TODAY)
for name, data in files.items():
    aj.save(d, name, data)
after = {f: open(os.path.join(d, f), encoding='utf-8').read() for f in aj.WRITABLE}
check('a news edit leaves the other three files byte-identical',
      sorted(f for f in aj.WRITABLE if before[f] != after[f]), ['news.json'])
check('regs.json stays on one line',
      open(os.path.join(d, 'regs.json'), encoding='utf-8').read().count('\n'), 0)
check('news.json keeps its two-space indent',
      open(os.path.join(d, 'news.json'), encoding='utf-8').read().splitlines()[1],
      '  "window_days": 14,')
check('the added item is there',
      json.load(open(os.path.join(d, 'news.json'), encoding='utf-8'))['items'][-1]['title'],
      NEWS['title'])
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    sys.exit(f'{len(failures)} failed: ' + ', '.join(failures))
print('all checks passed')
