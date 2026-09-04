# Data Center Power Atlas — build pipeline

Rebuilds `public/datacenters/index.html`, which is served at
`/datacenters/` on the site. The page is a single self-contained file: no
CDN, no runtime fetches, so it still renders years from now.

## Rebuild

    ./tools/atlas/refresh.sh

## Stages

| file | does |
|---|---|
| `build/sites.py` | the source data: 86 named AI campuses, 63 metro markets |
| `build/build.py` | geocodes sites, attaches eGRID subregion carbon factors → `entities.json` |
| `build/gen.py` | merges entities with calibration, regulations, overrides → `data.json` |
| `assemble.py` | inlines data into `parts/` → `dist/index.html` |

## Source data

| file | holds |
|---|---|
| `build/calib.json` | the five measured national anchors the model is fitted to |
| `build/policy.json` | which national sources may override the IEA, and why each is in or out |
| `build/override.json` | China, counted on its own national statistics |
| `build/newload.json` | per-country carbon intensity of *new* load, not average grid |
| `build/disputed.json` | where credible sources disagree, so the page can show the spread |
| `build/regs.json` | regulatory filings that evidence data-centre-driven generation |

## The rule that keeps this defensible

Every parameter is fitted to measured national statistics, never chosen by
judgement. `policy.json` states the admission test in full. The short version:
a national figure must be **measured by an official body** (Test 1) and must
imply a **physically possible load factor** against the mapped capacity
(Test 2). Failing Test 2 does not mean a source is wrong — it means the two
datasets count different facilities, which is exactly what happens with China.

Adding a country means adding it to `calib.json` and recording the pass/fail
in `policy.json`. Do not add a figure that fails Test 1 just because it is
widely cited.
