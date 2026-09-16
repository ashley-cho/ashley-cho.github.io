#!/usr/bin/env python3
"""Turn a check_sources.py report into the commit message for the daily run."""
import json, sys

r = json.load(open(sys.argv[1], encoding='utf-8'))
ch, esc = r.get('changes', []), r.get('escalations', [])

def strip_src(line):
    # "Epoch: Google Mesa 183 -> 201 MW" -> "Google Mesa 183 -> 201 MW"
    return line.split(': ', 1)[1] if ': ' in line else line


head = 'Atlas: daily source check, no change'
if ch:
    head = 'Atlas: ' + (strip_src(ch[0]) if len(ch) == 1 else f'{len(ch)} source changes')
print(head)
print()
if ch:
    print('Applied:')
    for c in ch:
        print('  ' + c)
else:
    print('No source value moved; rebuilt so the page reports a live refresh date.')
if esc:
    print()
    print('Raised for review, not decided here:')
    for e in esc:
        print('  ' + e)
for n in r.get('notes', []):
    print()
    print(n)
    break
