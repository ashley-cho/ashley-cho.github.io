# Data Center Power Atlas — build pipeline

Rebuilds the atlas. There are **two copies and they must always agree**:

| copy | file | published by |
|---|---|---|
| the site, at `/datacenters/` | `public/datacenters/index.html` | pushing to `main` (GitHub Pages) |
| the artifact | `tools/atlas/dist/artifact.html` | the Artifact tool, no credentials needed |

Both are one self-contained file: no CDN, no runtime fetches, so they still
render years from now.

## Rebuild

    ./tools/atlas/refresh.sh          # -> public/datacenters/index.html
    python3 tools/atlas/artifact.py   # -> tools/atlas/dist/artifact.html

Run **both**. The artifact form is the same markup without the
`doctype/html/head/body` wrapper, which the artifact host supplies itself.
Skipping the second command is how the artifact silently falls behind the
site — it has happened once already.

Plain Python 3, no packages: geocoding and country codes come from committed
caches (`zipcache.json`, `isocache.json`), so a rebuild needs nothing but the
interpreter.

## Stages

| file | does |
|---|---|
| `build/sites.py` | the source data: 86 named AI campuses, 63 metro markets |
| `build/build.py` | geocodes sites, attaches eGRID subregion carbon factors → `entities.json` |
| `build/gen.py` | merges entities with calibration, regulations, overrides → `data.json` |
| `assemble.py` | inlines data into `parts/` → `dist/index.html` |
| `artifact.py` | same, minus the document wrapper → `dist/artifact.html` |

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

### When an anchor moves, re-derive — do not absorb the error

Each basis takes the mean of its own anchors: `kIea` from the world and US
readings, `kNat` from Ireland and the Netherlands. If any anchor lands outside
±5% at the current factor, re-derive that factor and put the arithmetic and the
resulting residuals in the commit message. France is an out-of-sample check and
is never fitted to.

Worked example, 4 Sep 2026 — Berkeley Lab's *2025 Update* moved the US from
176 TWh (2023) to 192 TWh (2024):

    US implied     192 / (53.7 GW × 8.76)  = 0.408
    world implied  415 / (122.2 GW × 8.76) = 0.388
    kIea = mean                            = 0.398   (was 0.381)

At the old 0.381 the US anchor sat −6.7%, outside the band. After
re-derivation: world +2.6%, US −2.5%, Ireland +0.3%, Netherlands −0.3%,
France +6.4% (out-of-sample, unchanged).

## Working in the Cowork sandbox

`device_bash` runs in a Linux sandbox over a mount that lets git *create* its
lock files but not delete them. Every git write therefore leaves a stale
`.git/index.lock` that makes the next git write fail with
`Unable to create index.lock: File exists`.

- Clear locks by **moving**, not deleting: `mv .git/index.lock _to_delete/`
- Do it before each git write, and once more at the end so the terminal on the
  Mac is not left blocked.
- **Never run `git merge` in the sandbox.** It half-applies, fails writing the
  index, and leaves the worst of these locks. Merge on GitHub.
- Never run `npm test` / `npm ci` / `npm install` there either: `node_modules`
  holds macOS-native binaries and the sandbox is Linux. CI validates the Astro
  build on push; that is the gate.

## AVERT (US marginal emission rates)

`build/avert.json` is a committed static table: the 14 AVERT regional avoided
CO2 rates (Uniform EE profile, 2023) from EPA AVERT v4.3, plus the state and
eGRID-subregion to AVERT-region map, each entry marked `clear` or `split` with
the alternative region recorded for the split ones.

Do NOT refresh this daily. EPA republishes the workbook roughly once a year
(v4.3 was April 2024, covering 2017-2023). Check it annually at
https://www.epa.gov/avert/avoided-emission-rates-generated-avert and, if a newer
edition exists, replace `rates_lb` and bump `meta.year` / `meta.src`.

Rules that hold when editing it:

1. Use the Uniform EE profile. It is AVERT's flat, around-the-clock shape, which
   is the mirror image of a flat load addition. The wind and solar profiles are
   shaped and are the wrong instrument for a data centre.
2. A new state or subregion added to sites.py must get a `map` entry, or the
   build prints it under "AVERT unmapped US state/subregion" and that site
   silently falls back to the country figure. Treat that print as an error.
3. If a mapping is genuinely ambiguous, mark it `split` and record the
   alternative. The sensitivity claim on the Accuracy tab (flipping every split
   assignment moves the US figure by 0.3%) has to be recomputed if the site list
   changes materially.
4. AVERT reports CO2, the grid averages here are CO2e. Do not silently mix them
   without keeping the caveat on the page.
