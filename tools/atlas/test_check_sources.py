#!/usr/bin/env python3
"""What the mechanical half must never do again.

On 18 Sep 2026 the daily refresh proposed 100 edits and every one was wrong:
the OWID reader took the last CSV column, which is a provenance year, and wrote
2024 into the carbon intensity of 93 countries; the Epoch reader used a
line-anchored regex that Epoch's multi-line quoted Sources column defeats, and
invented power figures for two campuses. Neither was caught, because the anchor
residual check constrains the energy factors and says nothing about these.

Plain stdlib, no packages, same as the rest of the pipeline:

    python3 tools/atlas/test_check_sources.py
"""
import importlib.util, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('cs', os.path.join(ROOT, 'check_sources.py'))
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)

failures = []


def check(name, got, want):
    if got == want:
        print(f'  ok   {name}')
    else:
        print(f'  FAIL {name}\n       got  {got!r}\n       want {want!r}')
        failures.append(name)


# --- Epoch: quoted fields spanning several lines, the shape that broke the regex
cs.escalations.clear()
check('epoch reads the power column across multi-line quoted fields',
      cs.parse_epoch('''Name,Total power (kW),Current power (MW),Ratio,Owner,Selected Sources,Country
Google New Albany,550783.2238504295,453,17.160546,Google #confident,"- [permit](https://x/1)
- 2025 Environmental Report

",United States
Meta Aiken,161697.82718544718,142,5.379244,Meta #confident,"- [intro](https://y/2)

",United States
'''),
      {'Google New Albany': 453.0, 'Meta Aiken': 142.0})

# --- Epoch: the column is found by name, so a layout change cannot shift it
cs.escalations.clear()
check('epoch finds the power column by header, not position',
      cs.parse_epoch('Current power (MW),Name\n453,Google New Albany\n'),
      {'Google New Albany': 453.0})

# --- Epoch: two rows claiming the same campus is a question, not an average
cs.escalations.clear()
got = cs.parse_epoch('Name,Current power (MW)\nGoogle New Albany,453\nGoogle New Albany,333\n')
check('epoch withholds a campus that appears twice', got, {})
check('epoch escalates the duplicate', any('more than once' in e for e in cs.escalations), True)

# --- Epoch: an unreadable header is refused rather than guessed at
cs.escalations.clear()
check('epoch refuses a CSV with no recognisable columns',
      cs.parse_epoch('a,b,c\n1,2,3\n'), {})

# --- OWID: the value column, not the trailing provenance year
cs.escalations.clear()
rows, year = cs.owid_rows('''entity,code,year,co2_intensity__gco2_kwh,co2_intensity__gco2_kwh__original_year
Afghanistan,AFG,2025,131.31,2024
Turkmenistan,TKM,2025,1306.2,2024
''')
check('owid reads the value, not __original_year', rows, {'AFG': 131.31, 'TKM': 1306.2})
check('owid still reports the year', year, '2025')

# --- OWID: still works when there is no provenance column
check('owid handles a plain four-column export',
      cs.owid_rows('entity,code,year,value\nIreland,IRL,2025,256.54\n')[0],
      {'IRL': 256.54})

# --- the gate: a year in a g/kWh field is impossible and must be refused
cs.escalations.clear()
_, kept = cs.sanity_gate([], {'ci': {'AFG': (131, 2024)}, 'gen': {}, 'co2': {}})
check('gate refuses 2024 g/kWh', kept['ci'], {})

# --- the gate: a hundred edits at once is a parse failure, not a day of news
cs.escalations.clear()
_, kept = cs.sanity_gate([], {'ci': {f'C{i:03d}': (100, 200) for i in range(100)}, 'gen': {}, 'co2': {}})
check('gate refuses the whole run above the edit limit', kept['ci'], {})
check('gate says why', any('parsing failure' in e for e in cs.escalations), True)

# --- the gate: an ordinary day still gets through untouched
cs.escalations.clear()
kept_e, kept_o = cs.sanity_gate([('Meta Aiken', 142.0, 150.0)],
                                {'ci': {'IRL': (257, 249)}, 'gen': {}, 'co2': {}})
check('gate passes a real change', (kept_e, kept_o['ci']),
      ([('Meta Aiken', 142.0, 150.0)], {'IRL': (257, 249)}))
check('gate stays quiet on a real change', cs.escalations, [])

print()
if failures:
    sys.exit(f'{len(failures)} failed: ' + ', '.join(failures))
print('all checks passed')
