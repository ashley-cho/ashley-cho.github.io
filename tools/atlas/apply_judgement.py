#!/usr/bin/env python3
"""Apply a judgement-pass payload to the four ledger files.

The daily cron (atlas-refresh.yml) deliberately cannot touch news.json,
policy.json, regs.json or disputed.json: those hold the admission tests and the
reasoning, and a job that edits them on a timer is inventing the argument the
page makes. This script is the other half of that rule, not a hole in it. It is
driven by a payload a *session* wrote after doing the judgement pass, and it
refuses anything it cannot check:

  - only those four files are ever written; calib.json, override.json,
    newload.json and sites.py are out of scope, because moving a fitted number
    needs arithmetic in a commit message and a human reading it;
  - every field of every record is checked against the shape already in the
    file, and unknown keys are an error rather than a silent pass-through;
  - a news item may only be dated today or yesterday, so nothing can be
    backdated past the 14-day window or dated into the future;
  - an admitted anchor must land inside the 0.3-0.85 load-factor band. That is
    Test 2 of the admission policy, enforced here rather than trusted;
  - regs entries may only name a metro or campus that exists on the map;
  - at most MAX_OPS records change in one run, for the same reason
    check_sources.py has a 12-edit ceiling: a payload that wants to rewrite the
    ledger wholesale is a bug, not a busy day.

Nothing here decides anything. It is a gate on edits that were decided
elsewhere, and everything it passes still goes through a pull request and CI.

Usage:
    python3 tools/atlas/apply_judgement.py --payload FILE [--check] [--build-dir DIR]
"""

import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
MAX_OPS = 8

# Per-file formatting. These files are read by humans in diffs; a tool that
# reformats them turns a one-line change into a 200-line one. Each setting was
# measured against the committed file, not assumed: they are the only
# json.dumps arguments that reproduce it byte for byte.
FORMATS = {
    'news.json':     dict(indent=2, ensure_ascii=False, newline=True),
    'policy.json':   dict(indent=1, ensure_ascii=False, newline=True),
    'regs.json':     dict(indent=None, ensure_ascii=True, newline=False),
    'disputed.json': dict(indent=None, ensure_ascii=False, newline=False),
}
WRITABLE = set(FORMATS)

NEWS_KEYS = {'date', 'kind', 'title', 'detail', 'effect', 'moved', 'src', 'url'}
NEWS_KINDS = {'data', 'announce', 'policy'}
REGS_KEYS = {'k', 'place', 'body', 'ref', 'date', 'iso', 'metros', 'national',
             'head', 'body_text', 'url', 'sites'}
REGS_MUTABLE = {'head', 'body_text', 'ref', 'date', 'url', 'metros', 'sites'}
ADMIT_KEYS = {'place', 'body', 'fig', 'lf', 'role', 'basis', 'why'}
REJECT_KEYS = {'place', 'fig', 'test', 'why'}
DISPUTED_VAL_KEYS = {'twh', 'pct', 'src', 'yr', 'url'}

LF_LO, LF_HI = 0.30, 0.85


class Refused(Exception):
    """A payload that did not pass a check. The message is the whole point."""


def load(build, name):
    with open(os.path.join(build, name), encoding='utf-8') as fh:
        return json.load(fh)


def save(build, name, data):
    if name not in WRITABLE:
        raise Refused(f'{name} is not writable by this path')
    fmt = FORMATS[name]
    with open(os.path.join(build, name), 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=fmt['indent'], ensure_ascii=fmt['ensure_ascii'])
        if fmt['newline']:
            fh.write('\n')


def map_names(build):
    """Metro and campus names as the map knows them, for reference checking."""
    src = open(os.path.join(build, 'sites.py'), encoding='utf-8').read()
    ns = {}
    exec(compile(src, 'sites.py', 'exec'), ns)   # the file is data, committed alongside
    return ({row[0] for row in ns['METROS']}, {row[0] for row in ns['EPOCH']})


def want(obj, keys, what):
    if not isinstance(obj, dict):
        raise Refused(f'{what}: expected an object, got {type(obj).__name__}')
    got = set(obj)
    missing, extra = keys - got, got - keys
    if missing:
        raise Refused(f'{what}: missing {sorted(missing)}')
    if extra:
        raise Refused(f'{what}: unknown {sorted(extra)} — this path only writes '
                      f'the fields already in the file')


def text(obj, key, what, least=1):
    v = obj.get(key)
    if not isinstance(v, str) or len(v.strip()) < least:
        raise Refused(f'{what}: {key} must be text of at least {least} characters')
    return v


def url(obj, what):
    v = obj.get('url')
    if not isinstance(v, str) or not v.startswith('https://'):
        raise Refused(f'{what}: url must be https')
    return v


def check_news(add, today):
    ok = {today, today - datetime.timedelta(days=1)}
    for i, item in enumerate(add):
        what = f'news.add[{i}]'
        want(item, NEWS_KEYS, what)
        try:
            when = datetime.date.fromisoformat(item['date'])
        except (TypeError, ValueError):
            raise Refused(f'{what}: date must be YYYY-MM-DD')
        if when not in ok:
            raise Refused(f'{what}: date {item["date"]} is neither today nor '
                          f'yesterday. Items expire on their own after 14 days; '
                          f'nothing may be dated around that.')
        if item['kind'] not in NEWS_KINDS:
            raise Refused(f'{what}: kind must be one of {sorted(NEWS_KINDS)}')
        if not isinstance(item['moved'], bool):
            raise Refused(f'{what}: moved must be true or false')
        text(item, 'title', what, 8)
        text(item, 'detail', what, 40)
        effect = text(item, 'effect', what, 20)
        text(item, 'src', what, 2)
        url(item, what)
        if item['moved'] and not re.search(r'\d', effect):
            raise Refused(f'{what}: moved is true, so effect must name the '
                          f'before and after figures')


def check_regs(add, update, regs, metros, sites):
    have = {r['k'] for r in regs}
    for i, entry in enumerate(add):
        what = f'regs.add[{i}]'
        want(entry, REGS_KEYS, what)
        k = entry['k']
        if not re.fullmatch(r'[a-z0-9_]{2,24}', str(k)):
            raise Refused(f'{what}: k must be a short lowercase slug')
        if k in have:
            raise Refused(f'{what}: k {k!r} already exists — use regs.update')
        have.add(k)
        if not isinstance(entry['national'], bool):
            raise Refused(f'{what}: national must be true or false')
        for field, known in (('metros', metros), ('sites', sites)):
            val = entry[field]
            if not isinstance(val, list):
                raise Refused(f'{what}: {field} must be a list')
            unknown = [n for n in val if n not in known]
            if unknown:
                raise Refused(f'{what}: {field} names nothing on the map: {unknown}')
        text(entry, 'place', what, 2)
        text(entry, 'body', what, 4)
        text(entry, 'ref', what, 3)
        text(entry, 'date', what, 4)
        text(entry, 'head', what, 12)
        text(entry, 'body_text', what, 200)
        if not re.fullmatch(r'[A-Z]{3}', str(entry['iso'])):
            raise Refused(f'{what}: iso must be a 3-letter code')
        url(entry, what)
    for i, patch in enumerate(update):
        what = f'regs.update[{i}]'
        if not isinstance(patch, dict) or 'k' not in patch:
            raise Refused(f'{what}: needs k')
        if patch['k'] not in have:
            raise Refused(f'{what}: no entry with k {patch["k"]!r}')
        extra = set(patch) - REGS_MUTABLE - {'k'}
        if extra:
            raise Refused(f'{what}: {sorted(extra)} may not change through this '
                          f'path; only {sorted(REGS_MUTABLE)}')
        for field, known in (('metros', metros), ('sites', sites)):
            if field in patch:
                unknown = [n for n in patch[field] if n not in known]
                if unknown:
                    raise Refused(f'{what}: {field} names nothing on the map: {unknown}')
        if 'url' in patch:
            url(patch, what)
        if 'body_text' in patch:
            text(patch, 'body_text', what, 200)


def check_policy(admit, reject, recheck, policy):
    places = {r['place'] for r in policy['rejected']}
    for i, entry in enumerate(admit):
        what = f'policy.admit[{i}]'
        want(entry, ADMIT_KEYS, what)
        if entry['role'] not in {'anchor', 'override'}:
            raise Refused(f'{what}: role must be anchor or override')
        try:
            lf = float(entry['lf'])
        except (TypeError, ValueError):
            raise Refused(f'{what}: lf must be a number')
        if entry['role'] == 'anchor' and not (LF_LO <= lf <= LF_HI):
            raise Refused(
                f'{what}: implied load factor {lf} is outside {LF_LO}-{LF_HI}, so '
                f'the two sources are counting different fleets. That fails Test 2: '
                f'record it as an override with the scope mismatch declared, the way '
                f'China is, rather than admitting it as an anchor.')
        text(entry, 'place', what, 2)
        text(entry, 'body', what, 2)
        text(entry, 'fig', what, 4)
        text(entry, 'basis', what, 4)
        text(entry, 'why', what, 40)
    for i, entry in enumerate(reject):
        what = f'policy.reject[{i}]'
        want(entry, REJECT_KEYS, what)
        text(entry, 'place', what, 2)
        text(entry, 'fig', what, 3)
        text(entry, 'test', what, 4)
        text(entry, 'why', what, 40)
    for i, entry in enumerate(recheck):
        what = f'policy.recheck[{i}]'
        want(entry, {'place', 'why'}, what)
        if entry['place'] not in places:
            raise Refused(f'{what}: {entry["place"]!r} is not in the rejected list')
        text(entry, 'why', what, 40)


def check_disputed(sets):
    for iso, body in sets.items():
        what = f'disputed.set[{iso}]'
        if not re.fullmatch(r'[A-Z]{3}', str(iso)):
            raise Refused(f'{what}: key must be a 3-letter country code')
        want(body, {'note', 'vals', 'using'}, what)
        text(body, 'note', what, 60)
        text(body, 'using', what, 2)
        if not isinstance(body['vals'], list) or len(body['vals']) < 2:
            raise Refused(f'{what}: vals needs at least two competing figures — '
                          f'a dispute with one side is not a dispute')
        for j, val in enumerate(body['vals']):
            want(val, DISPUTED_VAL_KEYS, f'{what}.vals[{j}]')
            url(val, f'{what}.vals[{j}]')


def apply(payload, build, today):
    unknown = set(payload) - {'news', 'regs', 'policy', 'disputed'}
    if unknown:
        raise Refused(f'payload: unknown sections {sorted(unknown)}. This path '
                      f'writes news, regs, policy and disputed — nothing else. '
                      f'Anything that moves a fitted number stays manual.')

    news_ops = payload.get('news', {})
    regs_ops = payload.get('regs', {})
    pol_ops = payload.get('policy', {})
    dis_ops = payload.get('disputed', {})
    for name, ops, allowed in (('news', news_ops, {'add'}),
                               ('regs', regs_ops, {'add', 'update'}),
                               ('policy', pol_ops, {'admit', 'reject', 'recheck'}),
                               ('disputed', dis_ops, {'set'})):
        extra = set(ops) - allowed
        if extra:
            raise Refused(f'{name}: unknown operations {sorted(extra)}; '
                          f'allowed: {sorted(allowed)}')

    news_add = news_ops.get('add', [])
    regs_add, regs_update = regs_ops.get('add', []), regs_ops.get('update', [])
    admit = pol_ops.get('admit', [])
    reject = pol_ops.get('reject', [])
    recheck = pol_ops.get('recheck', [])
    dis_set = dis_ops.get('set', {})

    total = (len(news_add) + len(regs_add) + len(regs_update) + len(admit)
             + len(reject) + len(recheck) + len(dis_set))
    if total == 0:
        raise Refused('payload: nothing to do. If nothing moved, do not run this.')
    if total > MAX_OPS:
        raise Refused(f'payload: {total} edits, ceiling is {MAX_OPS}. A quiet day '
                      f'that produces a wholesale rewrite is a bug.')

    news = load(build, 'news.json')
    regs = load(build, 'regs.json')
    policy = load(build, 'policy.json')
    disputed = load(build, 'disputed.json')
    metros, sites = map_names(build)

    check_news(news_add, today)
    check_regs(regs_add, regs_update, regs, metros, sites)
    check_policy(admit, reject, recheck, policy)
    check_disputed(dis_set)

    before = len(news['items'])
    news['items'].extend(news_add)
    if len(news['items']) < before:
        raise Refused('news: items may only be added; expiry is by date')

    by_k = {r['k']: r for r in regs}
    for patch in regs_update:
        by_k[patch['k']].update({k: v for k, v in patch.items() if k != 'k'})
    regs.extend(regs_add)

    policy['admitted'].extend(admit)
    policy['rejected'].extend(reject)
    for entry in recheck:
        for row in policy['rejected']:
            if row['place'] == entry['place']:
                row['why'] = entry['why']
    disputed.update(dis_set)

    return {'news.json': news, 'regs.json': regs,
            'policy.json': policy, 'disputed.json': disputed}, total


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--payload', required=True, help='JSON file of edits')
    ap.add_argument('--check', action='store_true', help='validate, write nothing')
    ap.add_argument('--build-dir', default=BUILD)
    ap.add_argument('--today', default=None, help='override for tests, YYYY-MM-DD')
    args = ap.parse_args(argv)

    today = (datetime.date.fromisoformat(args.today) if args.today
             else datetime.datetime.now(datetime.timezone.utc).date())
    try:
        with open(args.payload, encoding='utf-8') as fh:
            payload = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f'refused: payload is not valid JSON ({exc})', file=sys.stderr)
        return 2

    try:
        files, total = apply(payload, args.build_dir, today)
    except Refused as exc:
        print(f'refused: {exc}', file=sys.stderr)
        return 2

    if args.check:
        print(f'ok: {total} edit(s) would apply')
        return 0
    for name, data in files.items():
        save(args.build_dir, name, data)
    print(f'applied {total} edit(s): ' + ', '.join(sorted(files)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
