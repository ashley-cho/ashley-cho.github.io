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
import argparse, csv, io, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, 'build')
UA = {'User-Agent': 'ashley-cho.github.io atlas daily refresh (+https://github.com/ashley-cho)'}

EPOCH_CSV = 'https://epoch.ai/data/data_centers/data_centers.csv'
# csvType=full, not filtered. The filtered export is not what it looks like:
# `annual-co2-emissions-per-country` is filtered to the entities *selected on
# the grapher page*, which on 2 Nov 2026 was seven of them (232 bytes) against
# 247 rows for the same year in the full export - so 33 of the 40 CO2 figures
# here had never been compared, and check_owid went on reporting "no change".
# The two electricity graphers return all 192 countries but drop every
# aggregate, which is why the world row was never checked in any series. Full
# exports plus a latest-year-per-entity read is the only form that covers both.
OWID = {
 'ci':  'https://ourworldindata.org/grapher/carbon-intensity-electricity.csv?csvType=full&useColumnShortNames=true',
 'gen': 'https://ourworldindata.org/grapher/electricity-generation.csv?csvType=full&useColumnShortNames=true',
 'co2': 'https://ourworldindata.org/grapher/annual-co2-emissions-per-country.csv?csvType=full&useColumnShortNames=true',
}

# gen.py keys the world row WLD; OWID codes it OWID_WRL. Without this the world
# generation and CO2 figures - the ones feeding the global intensity the page
# quotes - are skipped silently on every run.
ALIAS = {'WLD': 'OWID_WRL'}

notes, changes, escalations = [], [], []


def get(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')


# ---------------------------------------------------------------- Epoch AI

def parse_epoch(text):
    """Name -> MW, read with a real CSV parser and keyed by column name.

    Epoch's Selected Sources column holds quoted fields with embedded newlines,
    so the file cannot be read a line at a time. A line-anchored regex here
    previously reported power figures that appear nowhere in the row it named
    (Google New Albany 453 -> 333, Meta Aiken 142 -> 69, both invented on
    18 Sep 2026). csv.reader handles the quoting, and the power column is found
    by its header rather than its position, because the layout has moved before.
    """
    try:
        rows = list(csv.reader(io.StringIO(text)))
    except csv.Error as e:
        escalations.append(f'Epoch: CSV would not parse ({e}). Left as committed.')
        return {}
    if not rows:
        escalations.append('Epoch: empty CSV.')
        return {}
    head = [h.strip() for h in rows[0]]
    try:
        ni, mi = head.index('Name'), head.index('Current power (MW)')
    except ValueError:
        escalations.append(
            f'Epoch: expected Name and "Current power (MW)" columns, got {head[:6]}. '
            'Not trusting this pull.')
        return {}

    out, clash = {}, set()
    for r in rows[1:]:
        if len(r) <= max(ni, mi):
            continue
        name = r[ni].strip()
        if not name:
            continue
        raw = r[mi].strip()
        try:
            mw = float(raw) if raw else 0.0
        except ValueError:
            escalations.append(f'Epoch: could not read power for {name!r} (got {raw!r})')
            continue
        if name in out and out[name] != mw:
            clash.add(name)
        out[name] = mw

    for n in sorted(clash):
        escalations.append(
            f'Epoch: {n!r} appears more than once with different power — not guessing '
            'which row is the campus.')
    return {k: v for k, v in out.items() if k not in clash}


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
    """code -> value at each entity's own latest year, from a full OWID csv.

    Read with csv.reader rather than split(','): the full exports carry every
    entity, and entity names there are not guaranteed comma-free the way a
    seven-row filtered export happened to be.
    """
    try:
        rows = list(csv.reader(io.StringIO(text)))
    except csv.Error as e:
        escalations.append(f'OWID: CSV would not parse ({e}). Left as committed.')
        return {}, None
    if not rows:
        return {}, None
    head = [h.strip() for h in rows[0]]
    try:
        ci, yi = head.index('code'), head.index('year')
    except ValueError:
        return {}, None
    # The value is not reliably the last column. OWID appends provenance
    # columns such as co2_intensity__gco2_kwh__original_year to some
    # exports, and reading that one wrote the year 2024 into the carbon
    # intensity of 93 countries on 18 Sep 2026. Take the first column that is
    # neither an identifier nor provenance.
    cand = [i for i, h in enumerate(head)
            if h not in ('entity', 'code', 'year') and not h.endswith('__original_year')]
    if not cand:
        return {}, None
    vi = cand[0]
    # A full export holds every year, so pick each entity's newest row rather
    # than whichever happened to come last in the file.
    best = {}
    for r in rows[1:]:
        if len(r) <= max(ci, yi, vi) or not r[ci]:
            continue
        try:
            yr, val = int(r[yi]), float(r[vi])
        except ValueError:
            continue
        if r[ci] not in best or yr > best[r[ci]][1]:
            best[r[ci]] = (val, yr)
    out = {k: v for k, (v, _yr) in best.items()}
    year = str(max(yr for _v, yr in best.values())) if best else None
    return out, year


def check_owid(kind, text, current, tol, label, decimals, scale=1.0):
    live, year = owid_rows(text)
    if not live:
        escalations.append(f'OWID {kind}: could not parse the CSV; left as committed.')
        return {}
    if scale != 1.0:
        live = {k: v * scale for k, v in live.items()}
    edits, checked, missing = {}, 0, []
    for iso, old in current.items():
        key = iso if iso in live else ALIAS.get(iso)
        if key is None or key not in live:
            missing.append(iso)
            continue
        checked += 1
        new = round(live[key], decimals)
        if abs(new - old) > tol:
            edits[iso] = (old, new)
    # Say what was actually compared. A run that silently skipped most of the
    # file still appended "no change" before 2 Nov 2026, which is how 33 of the
    # 40 CO2 figures and every world figure went unexamined for weeks. Reporting
    # the count is what makes the next such narrowing visible on the day.
    if missing:
        escalations.append(
            f'OWID {label}: {checked} of {len(current)} committed figures found in '
            f'the export; not compared: {", ".join(sorted(missing))}')
    if edits:
        for iso, (o, n) in sorted(edits.items()):
            changes.append(f'OWID {label}: {iso} {o:g} -> {n:g}')
    else:
        notes.append(f'OWID {label}: latest year {year}, {len(live)} entities, '
                     f'{checked} of {len(current)} committed figures checked, no change.')
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

# ------------------------------------------------------------------- sanity

# The range outside which a number cannot be the thing it claims to be. These
# are not tuning knobs: a value landing outside one means a column was misread,
# not that the world did something surprising. The real maxima sit well inside
# them - Turkmenistan at 1306 g/kWh is the dirtiest grid on record, and the
# widest NAT rows are the world totals.
BOUNDS = {
    'epoch': (0.0, 5000.0, 'MW'),
    'ci':    (1.0, 1500.0, 'g/kWh'),
    'gen':   (0.1, 60000.0, 'TWh'),
    'co2':   (0.1, 60000.0, 'Mt'),
}

# One morning's genuine news does not move this many series at once. A run that
# wants to is reporting a parse failure: on 18 Sep 2026 a column-order bug
# produced 100 edits, every one of them wrong, and nothing objected.
MAX_EDITS = 12


def sanity_gate(epoch_edits, owid_edits):
    """Drop impossible values, and refuse the whole run if it looks like a parse failure."""
    lo, hi, unit = BOUNDS['epoch']
    kept_epoch = []
    for site, old, new in epoch_edits:
        if lo <= new <= hi:
            kept_epoch.append((site, old, new))
        else:
            escalations.append(
                f'Epoch: refusing {site} {old:g} -> {new:g} {unit}, outside {lo:g}-{hi:g}. '
                'That is a misread column, not a value that moved.')

    kept_owid = {}
    for kind, label in (('ci', 'carbon intensity'), ('gen', 'generation'), ('co2', 'CO2')):
        lo, hi, unit = BOUNDS[kind]
        keep = {}
        for iso, (old, new) in (owid_edits.get(kind) or {}).items():
            if lo <= new <= hi:
                keep[iso] = (old, new)
            else:
                escalations.append(
                    f'OWID {label}: refusing {iso} {old:g} -> {new:g} {unit}, outside '
                    f'{lo:g}-{hi:g}. That is a misread column, not a value that moved.')
        kept_owid[kind] = keep

    total = len(kept_epoch) + sum(len(v) for v in kept_owid.values())
    if total > MAX_EDITS:
        escalations.append(
            f'{total} values wanted to change in one run, past the limit of {MAX_EDITS}. '
            'That is the shape of a parsing failure rather than a day of news, so nothing '
            'was written. Check the source column layouts before re-running.')
        return [], {k: {} for k in kept_owid}
    return kept_epoch, kept_owid


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
            # OWID reports CO2 in tonnes; NAT holds Mt. This used to be its own
            # inline comparison, which is precisely why it never gained the
            # alias or the coverage report the other two now get.
            owid_edits['co2'] = check_owid(kind, text, co2_now, 0.5, 'CO2 Mt', 1,
                                           scale=1 / 1e6)

    epoch_edits, owid_edits = sanity_gate(epoch_edits, owid_edits)
    # the report has to describe what was written, not what was proposed
    changes[:] = [f'Epoch: {s_} {o:g} -> {n:g} MW' for s_, o, n in epoch_edits]
    for _kind, _label in (('ci', 'carbon intensity'), ('gen', 'generation TWh'), ('co2', 'CO2 Mt')):
        for _iso, (_o, _n) in sorted((owid_edits.get(_kind) or {}).items()):
            changes.append(f'OWID {_label}: {_iso} {_o:g} -> {_n:g}')

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
