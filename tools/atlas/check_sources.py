#!/usr/bin/env python3
"""Mechanical half of the daily atlas refresh.

Pulls the sources whose comparison is pure arithmetic — Epoch AI campus power,
and the three Our World in Data series behind gen.py's constants — diffs them
against what is committed, and (unless --report-only) writes back the ones it
is allowed to write back.

What it will change on its own:
  * Current power (MW) for a campus already in sites.py EPOCH, matched through
    build/epochmap.json so the name match is exact, never fuzzy.
  * A carbon-intensity value in gen.py's CIFULL table.
  * A generation or CO2 value in gen.py's NAT table.

What it will NOT change, and escalates instead:
  * A campus Epoch has added, removed or renamed. A new site needs a zip or
    lat/lon, an operator, and an AVERT region before it can be mapped, and
    guessing any of those would put an invented number on the page.
  * Anything touching calib.json, policy.json, override.json, disputed.json,
    regs.json or news.json. Those encode judgement — the admission tests, what
    counts as measured, which of two disagreeing sources to show — and a script
    that edited them would be inventing the argument the page is making.

Exit codes: 0 nothing moved | 10 wrote changes | 20 needs a human | 1 broke.

    python3 tools/atlas/check_sources.py [--report-only] [--epoch-csv FILE]
"""
import argparse, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, 'build')
UA = {'User-Agent': 'ashley-cho.github.io atlas daily refresh (+https://github.com/ashley-cho)'}

EPOCH_CSV = 'https://epoch.ai/data/data_centers/data_centers.csv'
OWID = {
 'ci':  'https://ourworldindata.org/grapher/carbon-intensity-electricity.csv?csvType=filtered&useColumnShortNames=true&time=latest',
 'gen': 'https://ourworldindata.org/grapher/electricity-generation.csv?csvType=filtered&useColumnShortNames=true&time=latest',
 'co2': 'https://ourworldindata.org/grapher/annual-co2-emissions-per-country.csv?csvType=filtered&useColumnShortNames=true&time=latest',
}

notes, changes, escalations = [], [], []


def get(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')


# ---------------------------------------------------------------- Epoch AI

def parse_epoch(text):
    """Name -> MW.

    Deliberately not csv.DictReader: Epoch's Selected Sources column has
    contained unescaped double quotes, which makes a strict parser swallow the
    following record whole. Anchoring on the record start is robust to that.
    """
    pat = re.compile(r'^(?!Name,)([^,\n"]+),([0-9.]*),([0-9.]*),([0-9.]*),', re.M)
    out = {}
    for m in pat.finditer(text):
        name, mw = m.group(1).strip(), m.group(3).strip()
        if not name:
            continue
        try:
            out[name] = float(mw) if mw else 0.0
        except ValueError:
            escalations.append(f'Epoch: could not read power for {name!r} (got {mw!r})')
    return out


def check_epoch(csv_text):
    sys.path.insert(0, BUILD)
    from sites import EPOCH
    committed = {r[0]: float(r[1]) for r in EPOCH}
    name_map = json.load(open(os.path.join(BUILD, 'epochmap.json'), encoding='utf-8'))['map']

    live = parse_epoch(csv_text)
    if len(live) < 50:
        escalations.append(f'Epoch: only parsed {len(live)} rows, expected ~86. Not trusting this pull.')
        return

    unknown = [n for n in live if n not in name_map]
    gone = [n for n in name_map if n not in live]
    for n in unknown:
        escalations.append(f'Epoch: NEW or RENAMED row {n!r} ({live[n]} MW) — needs a location and an AVERT region before it can be mapped.')
    for n in gone:
        escalations.append(f'Epoch: row {n!r} has disappeared from the CSV (maps to {name_map[n]!r}).')

    edits = []
    for epoch_name, mw in live.items():
        site = name_map.get(epoch_name)
        if site is None or site not in committed:
            continue
        old = committed[site]
        # sites.py rounds; only a real move counts
        if abs(mw - old) > 0.05:
            edits.append((site, old, mw))
    if edits:
        for site, old, new in edits:
            changes.append(f'Epoch: {site} {old:g} -> {new:g} MW')
        return edits
    notes.append(f'Epoch: {len(live)} campuses, no power change.')
    return []


def write_epoch(edits):
    path = os.path.join(BUILD, 'sites.py')
    src = open(path, encoding='utf-8').read()
    for site, old, new in edits:
        # rewrite only the MW field of that row, leaving everything else alone
        pat = re.compile(r'(\(' + re.escape(json.dumps(site, ensure_ascii=False)) + r',)\s*[0-9.]+(,)')
        src, n = pat.subn(lambda m: f'{m.group(1)}{new:g}{m.group(2)}', src, count=1)
        if n != 1:
            raise SystemExit(f'sites.py: could not rewrite the row for {site!r} ({n} matches) — aborting rather than guessing')
    open(path, 'w', encoding='utf-8').write(src)


# ------------------------------------------------------------ Our World in Data

def owid_rows(text):
    """entity/code -> (year, value) from a filtered OWID csv."""
    lines = [l for l in text.splitlines() if l.strip()]
    head = lines[0].split(',')
    try:
        ci, yi = head.index('code'), head.index('year')
    except ValueError:
        return {}, None
    vi = len(head) - 1
    out, year = {}, None
    for l in lines[1:]:
        p = l.split(',')
        if len(p) <= vi or not p[ci]:
            continue
        try:
            out[p[ci]] = float(p[vi])
        except ValueError:
            continue
        year = p[yi]
    return out, year


def check_owid(kind, text, current, tol, label, decimals):
    live, year = owid_rows(text)
    if not live:
        escalations.append(f'OWID {kind}: could not parse the CSV; left as committed.')
        return {}
    edits = {}
    for iso, old in current.items():
        if iso not in live:
            continue
        new = round(live[iso], decimals)
        if abs(new - old) > tol:
            edits[iso] = (old, new)
    if edits:
        for iso, (o, n) in sorted(edits.items()):
            changes.append(f'OWID {label}: {iso} {o:g} -> {n:g}')
    else:
        notes.append(f'OWID {label}: latest year {year}, {len(live)} entities, no change.')
    return edits


# ------------------------------------------------------------------- gen.py

def read_gen():
    src = open(os.path.join(BUILD, 'gen.py'), encoding='utf-8').read()
    cif = re.search(r'CIFULL="([^"]+)"', src).group(1)
    ci = {a: int(b) for a, b in (x.split(':') for x in cif.split())}
    nat = {}
    for iso, a, b, ya, yb in re.findall(r'"([A-Z]{3})":\s*\[([0-9.]+),\s*([0-9.]+),\s*(\d+),\s*(\d+)\]', src):
        nat[iso] = (float(a), float(b), int(ya), int(yb))
    return src, ci, nat


def write_gen(ci_edits, gen_edits, co2_edits):
    path = os.path.join(BUILD, 'gen.py')
    src, ci, nat = read_gen()
    if ci_edits:
        new_ci = dict(ci)
        for iso, (_o, n) in ci_edits.items():
            new_ci[iso] = int(round(n))
        blob = ' '.join(f'{k}:{v}' for k, v in new_ci.items())
        src = re.sub(r'CIFULL="[^"]+"', 'CIFULL="' + blob + '"', src, count=1)
    for iso in set(list(gen_edits) + list(co2_edits)):
        if iso not in nat:
            continue
        g, c, yg, yc = nat[iso]
        if iso in gen_edits:
            g = gen_edits[iso][1]
        if iso in co2_edits:
            c = co2_edits[iso][1]
        pat = re.compile(r'("' + iso + r'":\s*\[)[0-9.]+,\s*[0-9.]+(,\s*\d+,\s*\d+\])')
        src, n = pat.subn(lambda m: f'{m.group(1)}{g:g}, {c:g}{m.group(2)}', src, count=1)
        if n != 1:
            raise SystemExit(f'gen.py: could not rewrite NAT[{iso}] — aborting rather than guessing')
    open(path, 'w', encoding='utf-8').write(src)


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report-only', action='store_true', help='diff and report, write nothing')
    ap.add_argument('--epoch-csv', help='read Epoch from a local file instead of the network')
    a = ap.parse_args()

    _src, ci_now, nat_now = read_gen()
    gen_now = {k: v[0] for k, v in nat_now.items()}
    co2_now = {k: v[1] for k, v in nat_now.items()}

    try:
        text = open(a.epoch_csv, encoding='utf-8').read() if a.epoch_csv else get(EPOCH_CSV)
        epoch_edits = check_epoch(text) or []
    except Exception as e:
        escalations.append(f'Epoch: unreachable ({e.__class__.__name__}: {e}). Left as committed.')
        epoch_edits = []

    owid_edits = {}
    for kind, url in OWID.items():
        try:
            text = get(url)
        except Exception as e:
            escalations.append(f'OWID {kind}: unreachable ({e.__class__.__name__}: {e}). Left as committed.')
            continue
        if kind == 'ci':
            owid_edits['ci'] = check_owid(kind, text, ci_now, 1.0, 'carbon intensity', 0)
        elif kind == 'gen':
            owid_edits['gen'] = check_owid(kind, text, gen_now, 0.5, 'generation TWh', 1)
        else:
            # OWID reports CO2 in tonnes; NAT holds Mt
            live, year = owid_rows(text)
            live = {k: v / 1e6 for k, v in live.items()}
            edits = {}
            for iso, old in co2_now.items():
                if iso in live and abs(round(live[iso], 1) - old) > 0.5:
                    edits[iso] = (old, round(live[iso], 1))
            if edits:
                for iso, (o, n) in sorted(edits.items()):
                    changes.append(f'OWID CO2 Mt: {iso} {o:g} -> {n:g}')
            else:
                notes.append(f'OWID CO2: latest year {year}, no change.')
            owid_edits['co2'] = edits

    wrote = False
    if not a.report_only:
        if epoch_edits:
            write_epoch(epoch_edits); wrote = True
        if any(owid_edits.get(k) for k in ('ci', 'gen', 'co2')):
            write_gen(owid_edits.get('ci') or {}, owid_edits.get('gen') or {}, owid_edits.get('co2') or {})
            wrote = True

    report = {'changes': changes, 'escalations': escalations, 'notes': notes, 'wrote': wrote}
    print(json.dumps(report, indent=1, ensure_ascii=False))

    if escalations:
        return 20
    return 10 if changes else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        print(f'check_sources failed: {e.__class__.__name__}: {e}', file=sys.stderr)
        sys.exit(1)
