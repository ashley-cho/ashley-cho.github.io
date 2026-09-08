# Context for a new session

Read this first, then `src/content/writing/` for the drafts.

## The project

A series working out the engineering of orbital data centers from first
principles. Not advocacy, not dismissal — arithmetic. Ashley is writing it; I'm
helping with the physics and the drafts.

## Working rules

- **One session per post.** This file plus the repo is the handoff.
- **Nothing publishes without review.** New posts land as `draft: true`. Ashley
  flips it to `false` when she's happy.
- **Tone: short and flat.** Ashley's own writing is direct. Earlier drafts were
  too long and too fond of asides — cut hard, prefer short sentences, drop
  throat-clearing. Every draft still needs her rewrite to sound like her.
- **Don't open a post with Starcloud** or any company. Open with physics or the
  bare gap.
- **Verify numbers before writing.** Run the arithmetic; don't inherit figures
  from articles.
- **Always cite, inline and hyperlinked.** Every factual claim, number, or
  external assertion gets a markdown link on the claim itself — not a source
  list at the bottom. If a claim can't be sourced, either cut it or say in the
  text that it's an estimate.

## Anchor numbers (100 MW = one hyperscale data center)

```
748 m²    radiator per MW      (80 °C, both faces, ε 0.9, −250 W/m² parasitic)
2,296 m²  solar array per MW   (1,361 W/m², 32% III-V cells)
~40 kg/kW mass                 (range 34–59)
3.07×     array ÷ radiator     — holds for any radiator above 13 °C
```

ISS calibration: 422 m² of radiator rejects 70 kW → 166 W/m² in practice.

## The sixteen problems

Power in: 1 collecting · 2 eclipse · 3 distribution
Heat out: 4 rejection · 5 transport · 6 temperature ceiling
Survival: 7 radiation (dose + bit flips) · 8 micrometeoroids · 9 drag · 10 obsolescence
Data: 11 ground bandwidth · 12 inter-satellite links · 13 distributed training
Structure: 14 unfolding · 15 pointing · 16 mass

## Series plan — one post per problem

The intro promises sixteen problems, so there are sixteen posts plus the intro.
Every post declares `problem: N` in its frontmatter and renders as
"Problem N of 16". Reading order does not have to equal problem order, because
each post is labelled — publish in whatever order the research is ready.

| # | Post | Status |
|---|---|---|
| — | The map (intro) — `what-it-would-take.md` | drafted |
| 1 | The array is bigger than the radiator | — |
| 2 | Eclipse, and why the battery is small | — |
| 3 | Volts, cables, and arcing in plasma | — |
| 4 | Space is cold, and it barely matters — `space-is-cold.md` | drafted |
| 5 | Nobody writes about the plumbing | — |
| 6 | You can't just run the chips hotter | — |
| 7 | Two kinds of radiation damage | — |
| 8 | Have no surface: MMOD and droplet radiators | — |
| 9 | Drag, and the altitude squeeze | — |
| 10 | Design for death, not longevity | — |
| 11 | The atmosphere is the whole problem | — |
| 12 | Lasers between things that drift | — |
| 13 | Lockstep across a moving fabric | — |
| 14 | Every joint is a place to fail | — |
| 15 | Three subsystems, one orientation | — |
| 16 | Kilograms per kilowatt (finale) | — |

Posts 2 and 9 are the thinnest and may end up short; 14 and 15 got substantially
richer once the design was drawn (see below).

## The reference design

Everything the posts say should be consistent with this, and vice versa. If a
post and the design disagree, one of them is wrong — say so rather than papering
over it.

- **Orbit** 650 km dawn-dusk sun-synchronous. Below the Van Allen belts, ~99%
  sunlit, and going higher costs 2.2x launch mass to save 11% radiator area.
- **Module** 100 kW. Size set by the largest panel that unfolds with no robot.
  239 m² array (4% oversized for beta drift), 75 m² radiator at 80 °C.
- **Chips mounted on the radiator panel**, so the coolant loop never crosses a
  joint. 4 joints total, none carrying coolant or rotating power.
- **Sun-pointing attitude**, so the solar array is body-fixed and there is no
  gimbal — the ISS SARJ failure mode is absent rather than mitigated.
- **Clusters of 25 modules** sharing one bus. Saves ~1,000 t of thrusters,
  radios and batteries; shrinks the optical mesh from 1,000 nodes to 40; each
  module still self-deploys, so nothing needs robotic assembly.
- **Thermal system specced for 150 °C**, operated at 80 °C, so a
  wide-bandgap chip generation drops in without a redesign.
- **No servicing.** 5-year life, graceful degradation, replaced by launch,
  active deorbit at end of life.
- ~30 kg/kW after clustering. ~3,000 t and ~30 Starship launches for 100 MW.
  This is below the published 34-59 kg/kW range and is our own estimate, not a
  source — say so wherever it appears.
- **Optimise kg per kilowatt-YEAR, not kg per kilowatt.** Most removable mass is
  margin (radiator thickness, shielding, propellant), so stripping it shortens
  life and comes back as replacement launches. 40 kg/kW beats 30 once the
  heavier build keeps a third more capacity alive.

Drawn up at the artifact "Orbital Data Center, Drawn to Scale", which includes
an audit of the design against all sixteen problems.

## Open questions

- **ORDEM debris flux.** Needs a real run at `ordem.appdat.jsc.nasa.gov`
  (guest account works). Query flux vs. particle diameter at 650 km SSO. The
  sub-millimetre population is calibrated on Space Shuttle data that stopped in
  2011 — quote the uncertainty band, not the central value.
- **Concentrator mass trade** for post 3. Sketched, not worked.

## Site mechanics

Astro, static. New post = a `.md` file in `src/content/writing/`; filename
becomes the URL. Frontmatter: title, description, date, series, seriesPart,
draft. Math via `$...$` and `$$...$$`. Push to `main` and GitHub Actions
deploys to https://ashley-cho.github.io.
