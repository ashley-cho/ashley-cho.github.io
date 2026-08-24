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

## Series plan

1. The map (this is the intro) — `what-it-would-take.md`
2. Space is cold, and it barely matters — `space-is-cold.md`
3. The array is bigger than the radiator
4. You can't just run the chips hotter
5. Nobody writes about the plumbing
6. What is the right module size?
7. Two kinds of radiation damage
8. Have no surface: MMOD and droplet radiators
9. The atmosphere is the whole problem (bandwidth)
10. Lockstep across a drifting formation
11. The fleet that fades — Ashley's own idea, the strongest one in the series
12. Kilograms per kilowatt (finale)

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
