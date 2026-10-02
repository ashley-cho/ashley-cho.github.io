# Context for a new session

Read this first, then `src/content/writing/` for the drafts.

## The project

A series working out the engineering of orbital data centers from first
principles. Not advocacy, not dismissal — arithmetic. Ashley is writing it; I'm
helping with the physics and the drafts.

## Design principles

Ashley's, in her words, and the first one has a specific meaning that is not the
ordinary one:

1. **Compact — reduce the number of vulnerable points.** Not "small." Nothing
   here is small; the surfaces are 363,000 m² and that is fixed by physics. This
   principle is a *count*: how many separate things must work, unfold, seal or
   hold. Every joint, hinge, boom, deployment, valve, pump and connector is one.
2. **Light** — kilograms per kilowatt-year delivered.
3. **Resilient** — survive the failures that do happen anyway.
4. **Solve all sixteen problems**, not fifteen.

**1 and 3 are not the same thing, and the distinction is the useful part.**
Compact minimises how many things *can* fail. Resilient means surviving the ones
that do. They point in opposite directions as often as not: redundancy is good
for resilience and bad for compactness, because a spare is another part. The rule
that reconciles them is already in this document under "Where reliability mass
goes" — redundancy where failures are frequent and small, margin where they are
rare and fatal — and principle 1 is what stops that becoming an argument for
duplicating everything.

**What principle 1 decides, once it is stated this way:**

- The co-planar disc over a boom-mounted radiator. 48 booms and 48 deployments
  against 1–2% of mass is not close under this reading.
- Modules that do not connect to each other. Nothing crosses, so nothing at a
  crossing can fail.
- Chips mounted on the radiator, so the coolant loop never crosses a joint.
- The array normal on the orbit normal, which deletes the gimbal rather than
  improving it.

**The pump is the single-point-fatal item**, in every version of this design:
the flow-boiling correlations are only valid with enough mass flux to sweep
bubbles, which at zero g means the pump *is* the physics. At 48 modules that was
48 vulnerable points and a real conflict — two pumps per module removes the
single point (principle 3) but adds 48 parts (principle 1). **At three modules
the conflict mostly dissolves.** One pump failure now takes out a third of the
facility, and a second pump per module costs three parts fleet-wide. Redundancy
wins; carry two pumps per module and say so in post 5.

**Module count is bounded by launch mass, not chosen.** Fewer, larger modules
cut the part count, so the count is the smallest that fits the launcher: at the
near-term mass line (~14.8 kg/kW) a 5.2 MW module is ~77 t, three of them carry
the benchmark facility, and each is one heavy-lift launch. Going bigger means
assembling in orbit, which adds far more vulnerable points than it removes.
(The 100 MW design was 48 modules of 2.21 MW at ~90 t flown — same logic, other
mass line.) The cost of fewer modules lands on the array: a 5.5 MW wing is
~200× the largest flown, see open question 2.

> **October 2026 update — read `CHIP-SPEC.md` alongside this.** Ashley restated
> the design metrics (light · super simple · easy to build · point-to-point
> coordination · a fixed training benchmark) and the 100 MW anchor used
> throughout this file was replaced by a benchmark-sized facility of ~16 MW in
> three modules. The physics, the thermal stack, the layout trade, the mass
> lines and the sixteen problems below all still hold; the *scale* numbers
> (48 modules, 363,005 m², 4,253 t) are the historical 100 MW case. Where the
> two documents disagree on scale, CHIP-SPEC.md is current, and `canon.py`
> (v6) computes both — the benchmark design and, at the bottom, this file's
> 100 MW numbers as a cross-check.

## Working rules

- **One session per post.** This file plus the repo is the handoff.
- **Nothing publishes without review.** New posts land as `draft: true`. Ashley
  flips it to `false` when she's happy.
- **Tone: short and flat.** Ashley's own writing is direct. Earlier drafts were
  too long and too fond of asides — cut hard, prefer short sentences, drop
  throat-clearing. Every draft still needs her rewrite to sound like her.
  **Where 85 W/kg comes from**, so nobody has to rediscover it: it is SUNSTONE,
  28 kW at 331 kg, the largest ROSA actually flown (the ISS iROSA wings), per
  [Redwire's flysheet](https://rdw.com/wp-content/uploads/2023/06/redwire-roll-out-solar-array-flysheet.pdf).
  PHENACITE at 37 kW / 71 W/kg is a catalogue offering and has NOT flown. Two
  audits contradicted each other on this and the post said "37 kW ever flown"
  for a week. The line is 124 / 98 / 85 / 71 W/kg at 5.3 / 17.6 / 28 / 37 kW.
  **Her calibration sample, verbatim** — three paragraphs of mine became this
  one sentence of hers:
  > I size everything against 100MW, which needs about 70,000 H100s,
  > considering each H100 and its surrounding system consumes about 1.4 kW.
  The pattern: claim, number, basis-clause. Name the input; do not walk the
  arithmetic. Do not debunk the wrong answer. Do not justify the choice.
  **And post 1 carries no caveats about the design's internals.** A section
  explaining that the mass model uses a flat 35% overhead is design content
  in disguise — it presupposes a design the post has not presented. Caveats
  about how a number was computed belong in the post that computes it. Post 1
  states the scale, names the inputs in a clause, and stops. She caught this
  after I had stripped the answers out three times and left the caveats in.
  Post 1 at this density is ~165 lines; the "show every step" version was 249
  and she called it garbage.
- **Don't open a post with Starcloud** or any company. Open with physics or the
  bare gap.
- **Verify numbers before writing.** Run the arithmetic; don't inherit figures
  from articles.
- **Never leave an ambiguity.** Every number says exactly which quantity it is.
  Not "biggest" — biggest by area or by mass, they have different answers. Not
  "1,667 W per GPU" — rack-level IT load or facility meter, they differ by the
  cooling. Not "39.5% efficient" — AM0 or AM1.5, they differ by four points. If a
  reader can take a sentence two ways, it is wrong even when the number is right.
  Most errors caught in this project were of exactly this kind.
- **Always cite, inline and hyperlinked.** Every factual claim, number, or
  external assertion gets a markdown link on the claim itself — not a source
  list at the bottom. If a claim can't be sourced, either cut it or say in the
  text that it's an estimate.
- **Don't invent jargon in her posts.** "AM0" went into post 1 unexplained and
  she had to ask what it meant. If a term needs a sentence to explain, either
  write the sentence in the post that needs it or use plain words.
- **Don't cut her framing on a citation judgement.** An agent said the CFR link
  didn't support the G20 sentence and I cut her opening paragraph. The link
  supported it exactly. Flag a doubt; don't delete the author's text.

## Anchor numbers (100 MW = one hyperscale data center)

Revision 3 (canon v5). Revision 1 had the junction and the radiator both at
80 °C — heat crossing zero temperature difference. Revision 2 added the missing
thermal stack. **Revision 3 fixes the albedo**, which canon had been charging at
15 W/m² raw to *both* faces. Albedo is shortwave: absorbed = α_solar × incident,
and in a dawn–dusk orbit the anti-sun face looks at the dark hemisphere and
receives none of it. So the term is 0.19 × 11.3 = 2.1 W/m² on the sunward face
and zero on the other, not 30 W/m² total. Parasitic drops 392 → 364, net rises
971 → 999, and the radiator shrinks 2.8%.

```
Tj 85 °C  −  18.2 K stack  =  radiator 66.8 °C        (H100 die, 0.86 W/mm²)
1,063 m²  radiator per MW  (66.8 °C, both faces, ε 0.90, −364 W/m² parasitic)
2,567 m²  solar array per MW  (incl. 5.3% cosine margin, see below)
2.41×     array ÷ radiator  — was 2.96 before the stack; NOT fixed by physics
14–43 kg/kW   and the spread is TWO inputs, not one
```

**The stack is chip-dependent, and this block is the H100 case.** At a fixed
boiling coefficient the die-to-coolant drop scales with die heat flux. The
Rubin-class chip in CHIP-SPEC.md makes 2,300 W on ~1,600 mm², 1.44 W/mm²,
1.67× an H100 — so its stack is **30.4 K, the radiator runs at 54.6 °C, nets
813 W/m², and needs 1,306 m²/MW**. Array ÷ radiator is then **1.97×**, and the
break-even cell efficiency drops from 77% to 63%. Everything below that quotes
66.8 °C, 999 W/m² or 2.41× is the H100 case; `canon.py` prints both.

Full v5 roll-up: radiator 106,315 m², array 256,690 m², surface 363,005 m²,
disc 98.1 m, break-even η 77.3%, mass 4,253 t flown / 3,370 t optimistic /
1,384 t near-term. The repo's canon.py is now v5 and both posts are on v5. The artifacts still carry v4 in places — orbital-dc.html worst, then one-or-two.html.

**The array margin is a cosine loss, not an eclipse number.** Earlier drafts used
1.04, which is the reciprocal of the 96.1% annual sunlit fraction — an eclipse
figure wearing a beta-angle label. Under orbit-normal pointing the Sun sits
between 0° and 31.4° off the array normal, so the cosine loss is **14.7% at worst
beta and 5.0% averaged over the year**. The array is sized on the annual mean.

**This is a decision, not arithmetic, and it is the same size as the layout
decision below — do not make it silently.** Usable annual energy under a fixed
100 MW load with no storage:

| margin | usable annual energy | array carried | year below nameplate | worst sunlit output |
|---|---|---|---|---|
| 1.000 | 95.3% | 0 t | 100% | 85.3% |
| **1.0527 (chosen)** | **98.1%** | **66 t** | **35%** | **89.8%** |
| 1.1719 (worst case) | 100% | 192 t | 0% | 100% |

The first 66 t buys 2.8 points of usable energy; the next 149 t buys 2.2. The
curve turns over, and the annual mean sits on the good side of the knee. The
sharper argument, which nobody had written down: **with no battery, margin only
pays where margin × sin β < 1.** Above β = 71.8° the array over-produces and the
surplus is shunted, so worst-case sizing means 215 t of array that is fully unused 65% of the year.

**What must be disclosed and previously was not: the facility runs below
nameplate 35% of the year, bottoming at 90% of 100 MW in sunlight. At minimum
beta, combining the derate with 20% eclipse, sunlit-hours output is ~71% of
nameplate.** "100 MW" is a nameplate. Say what it actually delivers.

(Note the asymmetry with eclipse: eclipse is 20 minutes in 98 and irreducible at
any array size, whereas the beta derate is a sustained weeks-long droop that area
*can* remove. They are different throttles and are priced separately. Where a
later section says "size against the worst case," that is about eclipse, not
about this.)

**The parasitic load is asymmetric and rev 1 hid that.** 312 W/m² on the sunward
face (259 solar at α 0.19 end-of-life, 52 Earth IR, 2 albedo), 52 W/m² on the
anti-sun face, 364 total. Rev 1's flat 164 W/m²/face totals 328 against 364 —
10% out, not "about right". Earth view factor for an
edge-on plate is 0.241, confirmed by numerical integration.

**Emissivity is 0.90 and absorptance is 0.19 at end of life.** Never trade ε
down to buy α down: at 340 K emissivity is worth only 1.03× more per point than absorptance costs — d(net)/dε = 2σT⁴ − 2·q_eir·VF = 1,400 W/m², against d(net)/dα = S = 1,361. The sign holds, so never trade ε down for α down, but it is a coin flip and not a rout. Earlier drafts said 11×, which does not reproduce. AZ-93-class ceramic
white paint is the right family — ε is stable (silicate binder), α is what
darkens under UV, and the coating is atomic-oxygen stable, which matters at
650 km. **Size the radiator at EOL α, not BOL.**

ISS calibration, corrected: six radiator ORUs give 475 m² planform (not 422),
rejecting 70 kW → 147 W/m². It is a 2.8 °C (37 °F) ammonia loop, so it is a poor
calibration for a 67 °C radiator — use it for sanity only.

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
| 1 | The array is the larger SURFACE (2.41× with an H100 stack, 1.97× with the Rubin-class stack — robust either way). Which is the larger MASS is not settled: at the benchmark design, radiator 290 t vs array 206 t at flown hardware, 61 vs 58 near-term. Never write "biggest" without a unit. | — |
| 2 | Eclipse, and why there is no ride-through battery (a keep-alive one for memory, under a tonne, stays) | — |
| 3 | Volts, cables, and arcing in plasma | — |
| 4 | Space is cold, and it barely matters — `space-is-cold.md` | drafted |
| 5 | Nobody writes about the plumbing | — |
| 6 | You shouldn't want to run the chips hotter | thesis inverted, see below |
| 7 | Two kinds of radiation damage | — |
| 8 | Have no surface: MMOD and droplet radiators | — |
| 9 | Drag, and the altitude squeeze | — |
| 10 | Design for death, not longevity | — |
| 11 | The atmosphere is the whole problem | — |
| 12 | Lasers between things that drift | — |
| 13 | You don't need lockstep | thesis inverted, see below |
| 14 | Every joint is a place to fail | — |
| 15 | Three subsystems, one orientation | — |
| 16 | Kilograms per kilowatt (finale) | — |

Posts 2 and 9 are the thinnest and may end up short; 14 and 15 got substantially
richer once the design was drawn (see below).

**Two theses inverted by the design contest — do not write the old version.**

- **Post 6 has now been wrong twice. Get it right the third time.** Draft 1:
  "you can't run the chips hotter." Draft 2: "you shouldn't want to, because
  Arrhenius wear-out sets the replacement cadence." Both wrong. Swept properly,
  Arrhenius life at 85 °C is 55–149 years against a 15-year facility and does not
  bind until ~100 °C; sweeping Eₐ from 0.7 to 1.1 eV moves the optimum by zero.
  **The real ceiling is leakage power**, which grows the array and the radiator
  simultaneously. And the whole post may be aimed at the wrong variable: junction
  temperature is worth 3% while the evaporator architecture is worth 3.7×. The
  interesting post is about the lid, not the temperature.
- **Post 13** was going to be "lockstep across a moving fabric is very hard."
  Local SGD — sync every few hundred steps instead of every step — cuts the
  requirement ~500×. For the 100 MW design that was 57 Tbps naive → 113–566
  Gbps per module. **Re-derived for the benchmark design** (1T active, three
  modules, sync every 500 steps, 16M-token batches): the full pseudo-gradient
  exchange is ~2.7 TB per module per sync against a ~23-minute sync interval,
  **~15 Gbps per module** — a single TBIRD-class terminal with a 10× margin.
  Traffic scales with model size and sync interval, not with module size or
  facility power. `canon.py` prints it. The post is now about why the hard version of the
  problem was the wrong problem. **This does not get its own post** (Ashley,
  explicitly); it folds into 13.

**Nine problems surfaced during the contest. They all fold into the existing
sixteen — do not expand the list, the 16↔16 congruence is the structure.**

| new finding | folds into |
|---|---|
| conjunction management between own modules | 15 pointing |
| formation control / along-track drift | 15 pointing |
| battery thermal | 2 eclipse — and the answer is there is no battery |
| single-event latch-up | 7 radiation |
| pump wear-out | 5 transport |
| solar-radiation-pressure momentum dumping | 15 pointing |
| optical surface degradation | 7 radiation |
| launch volume | 16 mass |
| cost | out of scope, Ashley's call |

## The reference design

Everything the posts say should be consistent with this, and vice versa. If a
post and the design disagree, one of them is wrong — say so rather than papering
over it.

This version is the product of five independent design agents, one of which was
given no prior context at all. Where they converged, treat it as settled. Where
they diverged, it is flagged below.

**Converged — four agents including the clean-sheet control agreed independently:**

- **Orbit** 650 km dawn-dusk sun-synchronous. Below the Van Allen belts.
- **Attitude: array normal pointed at the ORBIT normal**, not at the Sun. This
  is the load-bearing trick and everything else hangs off it. It gives a
  gimbal-free array, no rotating power joint, and — because the body is
  axisymmetric about the pointed axis — gravity-gradient torque that is
  identically zero rather than merely small. The ISS SARJ failure mode is absent
  rather than mitigated.
- **No subsystem dominates mass.** Rev 1 said the array was 36% and the radiator
  a 6% rounding error. Both wrong. At flown hardware the radiator is the
  *largest* item; at near-term hardware array, radiator, compute and everything
  else are 373, 319, 336 and 357 t — quarters. Any argument of the form "it's all about X" is
  wrong for every X.
- **Heat pumping loses on AREA and on principle 1, not on mass.** A 40 K lift
  cuts radiator area 30% but grows the array more, because array area per watt is
  2.4× radiator area per watt — total surface rises 8%. On *mass* it is roughly
  neutral and the sign flips inside our own uncertainty band: at flown hardware
  (14.2 kg/m², 85 W/kg) a pump saves ~1.6 t/MW; at near-term (3 kg/m², 85 W/kg)
  it costs ~2 t/MW. The real objection is that it adds 48 compressors to a design
  whose own analysis names the pump as the single-point-fatal item. Earlier
  drafts said "loses, and not narrowly" — that was wrong.
- **Chips mounted on the radiator**, so the coolant loop never crosses a joint
  and there is no separate cold plate and transport leg.
- **Junction temperature 85 °C — and it is not a design driver.** The optimum is
  24 K wide and sweeping activation energy 0.7→1.1 eV moves it by zero. Arrhenius
  life at 85 °C is 55–149 years against a 15-year facility, so wear-out does not
  bind until ~100 °C. 85 is chosen for HBM margin, nothing more. What actually
  stops you going hotter is **leakage power**, which grows the array and the
  radiator at once. Two-phase ammonia. Per-device latch-up current limiting.
- **Direct-die microchannel evaporation. This is the most sensitive decision in
  the design.** Direct-die → lidded is worth 3.7× on kg/kW-year; junction
  temperature across its whole usable range is worth 3%. And the lidded polymer-TIM
  version does not merely cost mass, it **fails**: you cannot spread 1,100 W out
  of 800 mm² through copper (half-space limit 44 K on its own), which puts the radiator at −3 °C, where net flux is still +179 W/m² but the panel is 5.6× the area, 592,000 m². Net flux reaches zero at −28.7 °C. Not impossible at any mass; impossible at any sane one. Nobody ships direct-die on production silicon. (Post 5 quotes the lid as a 50–90 K range and takes the top end: −5 °C, 164 W/m², 6.1× — a different, rounder case than the 88 K one here. Both are right; do not "correct" one to the other.)
- **Take the thicker radiator fin.** Fin efficiency and stack ΔT are the same
  trade seen twice: at 100 mm tube pitch a 100 µm fin costs 12 K of stack, a
  250 µm fin costs 5 K and 0.4 kg/m². Buy the 7 K.
- **No eclipse ride-through battery.** Chips go dark through eclipse rather than
  hauling ~166 t of battery to orbit for a 4% duty-cycle gain. (October: a
  *keep-alive* battery for memory only — ~100 kWh, under a tonne — or an
  onboard flash checkpoint every orbit is still needed, because HBM is volatile
  and a dark module would otherwise lose its weights and optimizer state. See
  CHIP-SPEC.md.)
- **Modules do not connect to each other.** Check what would have to cross a
  connection: coolant (no — separate loops, every crossing is a leak path),
  power (no — each module makes and spends its own), data (see below, dropped to
  ~500 Gbps, which is free-space optics at a few km). Nothing needs to cross, so
  nothing should. 48 free-flying modules of 2.21 MW each, 98 m across.
- **Local SGD, not tight all-reduce.** Syncing every few hundred steps instead
  of every step cuts inter-module bandwidth ~500× — 113–566 Gbps per module at
  the 100 MW design, ~15 Gbps per module at the benchmark design (see post 13
  note above). This dissolves what the adversarial review called
  the single worst problem in the design. Found by the clean-sheet agent only.
- **No servicing.** Graceful degradation, replaced by launch, active deorbit.
  A dead module tumbles, and a tumbling disc presents its mean projected area
  (a quarter of total surface, by Cauchy) instead of the 33 m² a live one holds
  edge-on at 0.25° — **115×, not the 39× earlier drafts said.** Locking both
  numbers to the same 0.25° pointing budget is what fixes it; 39× implied 0.734°,
  which would have tripled the drag figure and killed "far below earlier budgets."
  Worth one sentence somewhere that holding a 98 m disc to 0.25° in yaw is itself
  a demanding requirement nothing in this design has costed.

**Diverged — genuinely open:**

- **How a single large sheet is held flat.** Tension (spin-stiffened membrane)
  or free structure. Not rigid trusses: a truss is a machine for carrying
  bending moments and there are no bending moments in free fall — the loads that
  remain are launch (solved by folding), solar radiation pressure (0.042 N on
  the 7,563 m² module), gravity-gradient differential, and thermal expansion. The membrane
  case is strong for the array and weak for the radiator, because the array is
  2.3× the area and holds no pressure.
*(The radiator-temperature conflict that sat here is CLOSED — see the anchor
block. The 53 K figure someone asserted turned out to be the lidded-with-solder-TIM
number, imported from a different machine. Derived properly for the direct-die
architecture this design actually specifies, it is 18.2 K.)*

## Why the layout is coplanar, stated correctly

Rev 1 justified the coplanar disc thermally: coplanar surfaces have view factor
exactly zero, so "stacking or finning costs more than 40% of net flux." The view
factor claim is rigorously true — for any two points in a common plane the
connecting ray lies in that plane, so cos θ = 0 and F = 0 exactly, at any
separation. The 40% is not: it assumed the array fills the radiator's entire
hemisphere. **Coplanar loses the thermal argument.**

| layout | net W/m² | radiator area | array ΔT | Δmass @14.2 | Δmass @8 |
|---|---|---|---|---|---|
| **coplanar disc** | 971 | 106,315 m² | — | **reference** | **reference** |
| coaxial, 40 m boom | 1,062 | 99,965 m² | +10.1 K | −79 t | −37 t |
| perpendicular, shared edge | 1,165 | 91,186 m² | +4.6 K | −51 to +76 t | +62 to +188 t |
| four radial fins | 872 | 121,812 m² | +3.5 K | +183 t | +107 t |

Two corrections shrank this a long way from the first version of the table.
**The array's radiosity is coupled, not isolated:** the same radiator that warms
the array's back face is then warmed *by* it, so the blocking body radiates 481
W/m² rather than the isolated array's 402. Charging one direction and not the
other overstated every alternative. **And the CMG count is indeterminate, not
wrong.** 94 N·m cyclic over the orbit swings 87,600 N·m·s peak-to-peak per
module. A *biased* cluster — standard practice for a cyclic load — stores ±43,800
and needs **9** ISS-class units; an unbiased one needs **18**. That is 432–864
fleet-wide and 127–253 t, and perpendicular's standing swings with it from −51 t
to +76 t. It cannot be settled without a momentum-management concept: biased or
unbiased, and what dumps the secular solar-pressure and aerodynamic torque. Do
not assert that perpendicular loses on mass; assert that it needs 432–864
control-moment gyros, which is the argument that actually holds.

Penalties: coaxial 17 t of boom + 21 t of array (to recover the efficiency lost
to a 10.1 K back-face rise, at −0.05 %abs/K); perpendicular 71 t of structure +
127–253 t of CMGs + 9 t of array. **The boom mass (8.85 kg/m of deployable mast), the
CMG unit mass (293 kg), and the array temperature coefficient are all assumptions,
not citations.** Deltas are bare radiator mass and do not carry the ×1.347 system
overhead, so fleet differences are ~35% larger.

**RESOLVED: coplanar stands.** The first version of this table appeared to
reverse the answer. Two audits later the coaxial margin is 28–79 t — about 1–2%
of system mass — against 48 booms, 48 deployments, and a coolant loop that would
have to run the length of the boom, breaking both of the things this thermal
system is proudest of. Under principle 1 — compact meaning *fewer vulnerable
points*, not smaller — 48 booms and 48 deployments against 1–2% of mass is not a
close call. Ashley can overrule; the numbers are above.

The earlier version of this trade was computed with the radiator at 80 °C, before
the thermal stack was put back. At the real 66.8 °C the radiator is 23% larger than an 80 °C panel,
and the coplanar layout's solar tax is a *per-square-metre* penalty — so the
absolute mass it costs grew, while the boom that avoids it stayed a fixed 17 t
(plus 21 t of extra array, because a boom-mounted radiator warms the array's back
face by 10.1 K). For a while it looked as though coaxial won outright. After the coupled-radiosity
correction its margin is 28–79 t — see the decision above.

What has *not* changed is the reason coplanar was attractive. It needs no boom,
no second deployment and no momentum management, and it keeps exact axisymmetry —
which is what makes gravity-gradient torque identically zero and puts the centre
of pressure on the centre of mass. Perpendicular still breaks that and still
needs 432–864 control-moment gyros fleet-wide.

So it is 28–79 t — one to two per cent of system mass — against 48 booms, 48
deployments, and 40 m of coolant line running along each boom, in a design that
twice boasts the loop is "under 40 m" and "never crosses a joint." That argument
stands on its own; it does not need a ranking of the design principles to settle
it, and inventing one would not survive being questioned.

**What would reopen it, and the part that is counterintuitive.** The margin is
95 t against a heavy 14.2 kg/m² radiator and only 37 t against a light 8 kg/m²
one — so the decision is *safest* where the hardware is worst, and weakest where
it is best. And 37 t is inside the combined uncertainty of three unpinned things:
the boom at an assumed 8.85 kg/m (at 15 kg/m the margin falls to ~21 t); the
coolant line along the boom, which is **counted nowhere** and at 2–5 kg/m of
supply, return, insulation and ammonia is 4–10 t fleet-wide, i.e. 10–26% of the
37 t; and the −0.05 %abs/K array temperature coefficient. A real boom mass
statement plus a radiator near 8 kg/m² reopens this. The coating-α argument does
not: it moves the margin toward coaxial and coaxial still loses on mechanisms.

**A qualitative objection the mass table cannot see.** Putting the radiator 40 m
behind the array means the coolant loop runs the length of the boom. The two
proudest claims about this thermal system are that the loop is "under 40 m" and
"never crosses a joint" — a boom-mounted radiator breaks both. That is a bigger
argument against coaxial than its mass is in favour, and it is not in the numbers.

**One number is missing before this can be decided.** Nobody has specified the
*roll* orientation of a perpendicular radiator. Its normal lies in the array plane
and could point at nadir (Earth view factor 0.823) or along-track (≈0). If nadir,
Earth IR nearly doubles on one face and perpendicular loses ~83 W/m², landing
level with coaxial. State it before ruling.

Two things that fell out of that trade and are worth keeping:

- **Radial fins would preserve the pointing law.** Any body with C_n symmetry for
  n ≥ 3 has isotropic transverse inertia, so gravity-gradient torque is still
  identically zero. Fins lose on mass, not on attitude.
- **Solar radiation pressure produces no torque either**, because on an
  axisymmetric body the centre of pressure sits on the centre of mass. SRP on the
  current 7,626 m² module is 0.042 N (diffuse re-emission, α 0.91 array / 0.19 radiator), not the 0.1 N inherited from the old
  11,000 m² module.

## What mass actually depends on

Rev 1 said the spread was one input — array specific power — and that the array
dominates. Both wrong. The array and the radiator are now within a factor of two
of each other, and at flown hardware the radiator is larger.

| scenario | array | radiator | compute | **everything else** | total | kg/kW |
|---|---|---|---|---|---|---|
| flown — 85 W/kg, 14.2 kg/m² | 1,315 t | **1,506 t** | 336 t | 1,096 t | 4,253 t | 43.1 |
| flown, optimistic — 85 W/kg, 8 kg/m² | 1,315 t | 875 t | 336 t | 877 t | 3,370 t | 34.0 |
| near-term — 300 W/kg, 3 kg/m² | 373 t | 328 t | 336 t | 360 t | 1,384 t | 14.0 |

**"Everything else" is a ×1.347 factor and it is 26% of the headline.** Bus,
structure, propellant and 15% margin, inherited from the superseded S1 breakdown
where 2,355/1,747 = 1.348, and never rederived for this design. Print it as a row
— a reader who adds the other three columns finds the gap in ten seconds.

Array mass is quoted per **peak** watt, because that is how array specific power
is defined; peak output is 111.8 MW, not the 106.2 MW the facility draws. Compute
mass is sized on 100 MW of hardware, not the 106.2 MW that includes leakage —
leakage does not add kilograms.

Radiator share of **dry mass**: 35% / 25% / 23%. Earlier drafts said 49/35/32,
which were shares of the itemized subtotal rather than the total. The radiator is
still the single largest line item at flown hardware; the percentages were wrong.

**The array anchor came down from 100 to 85 W/kg, and that matters.** Within the
flown roll-out array product line specific power *falls* as wings grow — 124
W/kg at 5 kW, 98 at 17.6 kW, 71 at 37 kW, a log-log slope of −0.13. This design
needs 2.2 MW per module, **79× the largest wing ever flown** (SUNSTONE, 28 kW, the ISS iROSA — PHENACITE at 37 kW is a catalogue offering, not flown). Quoting the flown
best case runs the observed trend backwards. State the size extrapolation as a
risk rather than burying it; it makes the pessimistic end worse, which is the
honest direction.

Sourcing, replacing rev 1's secondary compilation:

| figure | value | source |
|---|---|---|
| array, flown | 100 W/kg (ROSA, array level) | [NASA Small Spacecraft SoA 2024](https://www.nasa.gov/wp-content/uploads/2025/02/3-soa-power-2024.pdf) |
| array, product line | 71–124 W/kg, falling with size | [Redwire ROSA flysheet](https://rdw.com/wp-content/uploads/2023/06/redwire-roll-out-solar-array-flysheet.pdf) |
| array, near-term | ~240 W/kg 1 AU-equivalent, unflown | [NASA Transformational Solar Array](https://ntrs.nasa.gov/api/citations/20170010684/downloads/20170010684.pdf) |
| array, 1,000 W/kg | **no array-level demonstration exists** | — |
| radiator, flown | 5–8 kg/m² planform | [NASA TM-4555](https://ntrs.nasa.gov/api/citations/19940032314/downloads/19940032314.pdf) |
| radiator, ISS ORU | 8.8 kg/m² wet | [NASA TM-104822](https://ntrs.nasa.gov/api/citations/19970001606/downloads/19970001606.pdf) |
| radiator, flight EATCS ORU | 14.2 kg/m² (1,122.6 kg / 79.2 m²) | [NASA ISS ATCS Overview](https://www.nasa.gov/wp-content/uploads/2021/02/473486main_iss_atcs_overview.pdf) |
| radiator, best demonstrated | 2.9 kg/m² carbon-carbon | NASA TM-4555 |
| radiator, NASA target | **5 kg/m² or lower as the headline goal; <3 for advanced heat-pipe panels** | NASA TM-4555 |

**The kg/m² convention, settled — do not reopen it.** Two reviewers disagreed on
this and it is worth a straight 2× on the largest mass item. NASA TM-4555 quotes
areal density *per unit of one-sided planform area* and states the two-sided
credit explicitly: "for two-sided heat rejection … the above specific mass values
are effectively cut in half." So multiplying planform area × kg/m² is correct;
the panel simply delivers 2 m² of radiating surface per m² of planform. The
project's arithmetic was right and only its anchor was optimistic.

**The honest headline for the series is no longer "it's all about the array."**
It is: *at hardware that exists today this is ~43 kg/kW, the radiator is the biggest single item by mass, and getting to 14 needs both the array 3× lighter and the
radiator 5× lighter.*

## The break-even claim, restated

Rev 1 said making the array break even with the radiator needs 98.3% conversion,
above the Landsberg limit, so the array is structurally bigger and always will
be. The 98.3% was stale — inherited from an older 75 °C radiator — and the true
figure sits *below* the limit it was being compared against.

**Use AM0, not AM1.5.** The famous 39.5% NREL record is the *terrestrial*
spectrum. The same class of cell measures 35.8% at AM0 — the title of the paper
is literally ["35.8% space and 38.8% terrestrial"](https://ieeexplore.ieee.org/document/6924957/),
2014, and unbeaten since. Production flight cells are 32.2% AM0 (Spectrolab XTE-SF).
Earlier drafts compared an AM0 requirement against the AM1.5 record.

| stack | T_rad | break-even η | vs Landsberg 93.3% | vs AM0 record 35.8% |
|---|---|---|---|---|
| 18 K (proposed) | 66.8 °C | 77.3% | below | 2.2× — array wins |
| 51 K | 34 °C | 39.0% | below | **level with it — inverts** |

**"The array is always the bigger surface" is conditionally true and the
condition is the thermal stack, not thermodynamics.** Use this wording:

> The array is the bigger surface because a 32%-efficient cell is about half as
> good as it would need to be. The two would be equal at roughly 75% conversion.
> That is not forbidden — the Landsberg limit is 93.3% — but it is about twice
> the best cell ever measured at one sun in space. The array wins the size
> argument by a factor of two in efficiency, not by a law.

## Two corrections worth not re-making

**Eclipse.** "96.1% sunlit" is an *annual average* and using it to size anything
is a mistake. At the minimum beta angle of 58.6°, eclipse is 19.7 minutes out of
a 97.7-minute orbit — 20% dark, five times the average. Size against the worst
case.

**Radiator freeze is not a problem, and the earlier claim that it was came from
a bad assumption.** Cooling goes as T⁴, not exponentially, and the result
depends entirely on areal density:

| areal density | T after 19.7 min, no Earth IR | with Earth IR |
|---|---|---|
| 0.3 kg/m² | −178 °C (**impossible**) | −95 °C floor |
| 2.0 kg/m² | −103 °C | −77.8 °C — marginal, right at the freeze point |
| 4.0 kg/m² | −69 °C | −53 °C — comfortable |

The first table published omitted Earth infrared and was wrong in the
conservative direction. A disc edge-on to Earth still has view factor 0.241, so
it absorbs 104 W/m² in eclipse and cannot go below **−94.7 °C** at any areal
density. Two further omissions, both the same way: the ammonia inventory carries
more sensible heat than the aluminium does, and latent heat of fusion alone buys
39 minutes per kg/m² at the freeze point — twice the longest eclipse. Even
reaching the freeze point would not freeze it through.

Ammonia freezes at −77.7 °C. At any realistic radiator mass it does not get
there — mass buys thermal inertia for free. The freeze panic was an artifact of
assuming 0.3 kg/m², which is 7× below NASA's stretch target and 27× below flight
hardware. No freeze-protection battery is needed.

Related, and worth keeping: only ~5% of a tube-and-fin radiator sheet is
actually wet. A puncture in the fin between tubes is harmless — it is a fin, not
a vessel. Apply it to the **radiator alone**: of 106,315 m² of radiator, ~5,316 m²
is fluid-bearing, i.e. **1.5%**. That is what makes isolable parallel circuits a
real answer. Two caveats: the 5% is not a citation, it is tube width ÷ tube pitch (5 mm on 100 mm), so state the pitch or drop the number; and a hole in a
*tensioned* membrane is a crack initiator, which the fin-versus-vessel
distinction does not address.

### Where reliability mass goes

Two ways to spend mass on staying alive, and they are not interchangeable.
**Margin** makes each part tougher so fewer failures happen. **Redundancy**
builds more parts than needed so failures stop mattering. Both look identical in
kg/kW-year, so that metric does not pick a side — the failure *shape* does.

| Subsystem | Failure shape | Spend on | How |
|---|---|---|---|
| Chips | frequent, tiny | redundancy | spare GPUs, route around dead ones |
| Solar array | frequent, tiny | redundancy | already redundant strings; +10% area is cheap |
| Radiator | frequent, small | redundancy | spare segments + isolation valves |
| Pumps | rare, fatal | margin | one failure kills a loop |
| Structure | rare, fatal | margin | cannot overprovision a truss you have one of |
| Bus / propulsion | rare, fatal | margin | or bound the blast radius by cluster size |

**Redundancy wins where failures are frequent and small** — you live in the
degraded regime anyway, so spare capacity is used daily rather than idling
against an event. **Margin wins where failures are rare and fatal**, because
there is nothing to fall back onto.

Worked example, radiator MMOD: doubling skin thickness stops particles up to
~1.9x diameter, and small-particle flux falls as roughly d^-2.7, so 2x radiator
mass buys a 5.7x lower puncture rate. Against that, +10% spare area costs +10%
mass and absorbs 10% of area lost. Below ~10% area loss over five years,
redundancy is about 5x cheaper; at 50% loss only thickening works. **Which
regime we are in is exactly the ORDEM number** — that missing figure decides
this trade, not just a footnote.

And redundancy has one advantage margin never has: **it does not require knowing
the failure rate.** Margin means predicting what you are hardening against;
overprovisioning only needs slack. With the debris flux as the least certain
number in the whole design, that argues for redundancy wherever it is available.

This is the fleet-that-fades idea one level down — overprovision, let it
degrade, top up — applied to segments instead of satellites.

Drawn up at the artifact "Orbital Data Center, Drawn to Scale", which includes
an audit of the design against all sixteen problems.

## Open questions

Ranked, October 2026. The live ones first; the 100 MW-era ones that still
matter follow; the merged-sheet question is demoted to the end because the
chip spec makes it moot.

A. **72-GPU copper domains against a 161 m disc.** 20 domains per module of
   ~245 kW each, ~300 m² of radiator apiece. Either the chips cluster and the
   coolant crosses hinges — which breaks "the loop never crosses a joint" — or
   the in-module fabric goes optical. Problems 12 and 14. The largest
   unresolved item in the design.
B. **800 V DC in LEO plasma.** Rubin-era racks run an 800 V bus; arcing in LEO
   starts around 200–300 V and the ISS runs 160 V with a plasma contactor.
   Problem 3, made harder specifically by this chip.
C. **The 220 kW Vera Rubin NVL72 rack figure** (SemiAnalysis via the shared
   chat) — every number in the power column scales with it. Verify.
D. **Critical heat flux margin** for ammonia microchannels at 144 W/cm². Past
   CHF the wall dries out and Tj jumps; nothing in the design pins the margin.
E. **Two pumps per module** — decided above on principle; not yet drawn or
   massed.

The older ones:

0. **Eclipse on a merged sheet is a structural problem, not a power problem.**
   *(Moot for a GPU-class chip — the chip spec forces f = 0. Kept for the
   SRAM-resident machine it describes.)*
   β\* = asin(Re/(Re+h)) = 65.16°, and the beta range runs down to 58.57°, so the
   orbit is shadowed **88 days a year, up to 19.7 minutes per orbit**. On the
   two-surface design that is a known power gap. On the one-surface sheet it is
   different in kind: the sheet is warmed by sunlight, so when the sun goes the
   sheet is heated only by its own computers. It sits at **−8 °C if a battery
   carries the load and −95 °C if it does not** — a 76 K or 163 K swing, roughly
   **1,300 times a year**, across six to eight million die attachments on a
   membrane. The ride-through battery is 32.9 MWh = **132–183 t** and appears in
   no mass table. This decides whether "delete the batteries" was ever on offer,
   and it is the question that could still kill one surface.
1. **The ×1.347 system overhead.** 1,096 t — 26% of the headline — for bus,
   structure, propellant and 15% margin, inherited from the superseded S1
   breakdown and never rederived for this design. It is the only number in the
   corpus, alongside the 3.36 kg/kW compute mass, that has survived three hostile audits without once being computed, and
   it is roughly the size of the whole solar array. (Earlier drafts of this note
   said "larger than the array." It is not, and never was: 1,096 t against
   1,315 t at the flown line, and smaller in all three scenarios.) It does not block publishing, because it is now
   labelled and itemised, but it does block quoting "42.5 kg/kW" as though the
   last digit meant anything. Needs a real bus and structure budget.
2. **Array specific power at module scale — now worse.** Decides the whole
   14–47 kg/kW spread. Every flown data point is ≤28 kW (37 kW is catalogue)
   and the trend falls with size. The 100 MW design needed 2.2 MW per wing,
   79× the largest flown; **the benchmark design's three big modules need
   5.5 MW per wing, ~200×.** Fewer modules is what "light" and "simple" asked
   for, and this is its price. Needs a vendor mass statement for a ≥100 kW wing
   with blanket separated from boom, so the scaling can be modelled rather than
   extrapolated.
3. **ORDEM debris flux at 650 km.** Decides three things at once — fin
   thickness, spare-capacity fraction, and the margin-vs-redundancy trade below.
   Guest account at `ordem.appdat.jsc.nasa.gov`. **Only Ashley can run it.** The
   sub-millimetre population is calibrated on Shuttle data that stopped in 2011;
   quote the uncertainty band, not the central value.

Smaller, and none of them block a post:

- **Starlink 5-year design life** citation still not run down.
- **Die-level power map**, which sets the hot-spot allowance — ±10 K on the
  lidded paths, but the lidded paths are rejected anyway.
- **Compute pod mass** is 3.36 kg/kW, inherited without derivation. A
  terrestrial rack is ~11 kg/kW. Compute is a third of dry mass at the near-term
  line, so this is no longer a small assumption. **Promoted:** on one surface
  this number *picks the chip size*, because 3.36 kg/kW is 275 g per 82 W part
  of which ~10 g is silicon and memory, and whether the other 265 g is per-watt
  or per-chip decides the optimum between 3 W and 39 W.
- **Tube pitch** for the radiator, which is what the 5% wet fraction actually
  rests on.

## The merged one-surface sheet — where it actually stands

Not canon. The two-surface design above still stands and is still the
conservative case. This section exists so the alternative is not carried in an
artifact alone. `canon.py` computes it at the bottom, from the same constants.
*(October: for the Rubin-class chip in CHIP-SPEC.md this whole section is
closed — a 2,300 W part is 120–180× over the sheet's 13–19 W window and its
HBM is 1.10 W/mm². Kept for the SRAM-resident machine it describes.)*

**Sheet temperature is independent of the compute.** This is the strongest
result on the idea and it replaces the "0.2 K agreement" the first draft was
built on, which was a coincidence. The cells generate the electricity and the
chips half a millimetre behind them spend it, so it never crosses the sheet
boundary and cancels exactly out of the balance:

```
α·S·cos + Earth IR (both faces) + albedo (front only) = (ε_f + ε_b)·σ·T⁴
```

Compute flux appears nowhere. Curtailment does not change it either — power not
extracted stays in the cell as heat. **68.3 °C hot case, 64.3 °C annual mean,
56.2 °C cold case**, and nothing the computer does moves those.

The 7 K disagreement between my balance and a reviewer's is **closed**. Three
errors: Earth IR belongs on **both** faces (a sun-pointing sheet in dawn–dusk is
*exactly* edge-on to nadir, always, so each face sees VF 0.2406 — derived twice,
independently, and the nadir case checks out at (Re/H)² = 0.8234); a temperature
must be evaluated at the **hot case**, not the annual mean; and albedo is
shortwave and front-face-only, which was mine and the same bug canon had.

**Chip size is set by a scissor and the window is narrow.** Heat has to travel
sideways from the die to the area that radiates it, and that rise is *exactly
linear* in chip power — `ln(R/a) = ½·ln(q_die/q_sheet)` is invariant at fixed
die-level power density, so there is no knee and nothing to engineer around.
The whole junction budget is **16.7 K** (85 °C ceiling minus the 68.3 °C sheet).

| graphite under the sheet | max chip | pitch | fleet mass | closes? |
|---|---|---|---|---|
| 100 µm | 6.4 W | 13 cm | 59 t | no — below the ~10 W floor |
| **200 µm** | **12.7 W** | **18 cm** | **117 t** | yes |
| **300 µm** | **19.1 W** | **22 cm** | **176 t** | yes |
| — 82 W reticle die | needs 1.2 mm | — | 709 t | no — 13× over budget |

Below ~10 W, fixed per-chip cost (PLL, bias, link idle, kerf, IO ring) exceeds
10% of the part. So the answer is **13–19 W, 130–190 mm² of silicon, 20 cm
apart, 5.6–8.3 million of them, on 200–300 µm of pyrolytic graphite**. Graphite
because the figure of merit is conductivity **per kilogram**, where graphite film
beats aluminium 9–11×. The architecture rests on a third of a millimetre of it.

**The reticle-scale die is dead, and the argument for it was void anyway.** The
fabric case for big dies assumed bandwidth demand scales with FLOPS — but if it
does, then traffic and power budget scale together and *the allowed energy per
bit does not depend on chip size at all*. It cancels. Separately, measured link
energy is nearly flat with distance (1.17 pJ/bit at 80 mm, 0.54 at 10 mm, 0.25–0.5
at 2 mm), so 40× the distance costs ~3× the energy and the fabric wants 1–3% of
chip power against a 10% ceiling. **The wiring was never the problem.**

**The prize is ~2×, not 3–4×, and it is conditional.** Voltage scaling gives
~3.2× ideal, ~2.4× once SRAM needs its own higher rail, ~2× against a realistic
always-on floor — and only with **no HBM at all**, since a stack costs ~110 W
whatever the logic does, more than a whole chip's budget at this size. So the
machine is SRAM-resident, and every SRAM-resident part shipping today is *less*
efficient per watt dense than a GPU. Net: one surface is roughly
**compute-neutral**, not compute-positive.

Silicon supply is a non-issue and can be closed: 100 MW at 0.1 W/mm² is ~1,060 m²
of silicon = ~20,000 300 mm wafers = **1.8 days of TSMC leading-edge output**.

## What makes sense: the array is a free radiator, and f is the design parameter

This is the result of the one-surface work that applies to the **two-surface**
design, and it is the one worth keeping. Both analyses framed it as a choice.
It isn't. It is a continuum.

The array is 256,690 m² — **2.4× the radiator's area** — and at f=0 it sits at
37 °C radiating nothing but its own waste. It is the largest cold surface in the
design and it has been thermally idle in every revision. Any compute placed on
its back is rejected for free, at the cost of warming the cells.

Let **f** = the fraction of the compute carried on the back of the array.

| f | sheet | η | array m² | radiator m² | Tj budget | max chip | mass |
|---|---|---|---|---|---|---|---|
| **0.00** | 37.0 °C | 0.3166 | 259,439 | 106,315 | 48.0 K | — | **4,258 t** |
| 0.35 | 49.4 °C | 0.3105 | 264,540 | 69,104 | 35.6 K | 34 W | 3,774 t |
| 0.50 | 54.2 °C | 0.3082 | 266,553 | 53,157 | 30.8 K | 32 W | 3,471 t |
| **0.70** | 60.2 °C | 0.3052 | 269,106 | 31,894 | 24.8 K | 27 W | **3,066 t** |
| 0.85 | 64.4 °C | 0.3032 | 270,935 | 15,947 | 20.6 K | 23 W | 2,763 t |
| **1.00** | 68.3 °C | 0.3012 | 272,699 | 0 | 16.7 K | 19 W | **2,459 t** |

**Mass is monotonic in f. There is no interior optimum** — every step toward the
sheet saves mass, and the array grows only 5% across the whole range because the
cells lose 1.5 points of efficiency. So thermal analysis does not pick f, and
that is the finding: **the thing that bounds f is memory.**

An HBM stack is ~110 W on ~100 mm² = **1.10 W/mm²**, eleven times what the sheet
can spread; on 300 µm of graphite that is a **138 K rise** against a 16.7 K
budget. And it cannot be moved away from its logic — 1024-bit at millimetre
reach, 9.6 Tb/s, which across the 27 m to the radiator disc costs 55 W per stack
on membrane and 2.6 kW on circuit board, plus double the memory latency.

**So a node is wholly on the sheet or wholly on the radiator**, and f is not a
component split but the fraction of the *machine* that is SRAM-resident. That is
a workload question, not a thermal one. It is the real fork, and it is the one
worth putting in front of a reader.

**Recommendation.** Keep two surfaces as canon, and stop treating the radiator
as the thing that rejects the compute heat. It rejects the heat of the
HBM-attached fraction. Make f explicit and quote the design at **f = 0.7:
3,066 t, a 28% saving, radiator 31,894 m² instead of 106,315** — with the pumps,
the fluid loop, HBM and the whole two-surface toolkit intact for the nodes that
need them, and no bet on eight million die attachments surviving 1,300 deep
thermal cycles a year. f = 1 is 600 t lighter and is the version that has to be
right about everything at once.

The pure one-surface case is not rejected. It is **deferred behind the eclipse
question**, which is open question 0 above and which f = 0.7 largely defuses:
with a radiator in the loop there is thermal mass and a fluid to hold heat, and
the sheet is not the only structure.

*(October: with the Rubin-class chip, f = 0. The f-parameter result stands for
any future SRAM-resident fraction of the machine; for this design it is zero.)*

## Can better technology beat these numbers? Areas no, masses yes.

Asked directly, and the answer is lopsided enough to be a design principle in
its own right: **the surfaces are near a physics floor and the kilograms are
not.** Realistic 20-year headroom is 1.16× on total area and 4.0× on mass.

| | today | realistic ~2045 | absolute floor |
|---|---|---|---|
| array area | 2,567 m²/MW | 2,282 (1.12×) | 1,825 (1.41×) |
| radiator area | 1,063 m²/MW | 849 (1.25×) | 607 (1.75×) |
| **total surface** | **363,000 m²** | **313,000 (1.16×)** | **243,000 (1.49×)** |
| array mass | 1,315 t | 373 (3.5×) | ~100 (13×) |
| radiator mass | 1,506 t | 340 (4.4×) | ~73 (20×) |

**Array area is the hardest floor in the project.** Efficiency is the only lever
and it has moved 0.25–0.27 points a year for twenty years. The AM0 lab record
(35.8%) has not moved in twelve years, production sits at 32.2%, and the
practical multijunction ceiling under a varying spectrum is ~51% at 1 sun, not
the 68.7% detailed-balance number — beyond 8 junctions efficiency *falls*.
Realistic 2045 flight cell: 35–38% AM0. Even a perfect cell only buys 3.1×.

**Radiator area is softer but not by much**, and its biggest lever is not
radiator technology at all — it is `f`, which at 0.7 deletes 70% of the radiator
by moving compute onto a surface already being carried. Emissivity is the
*weakest* lever: 0.90 → 0.94 buys 5.3% of area, a perfect blackbody 12.3%,
because raising ε raises Earth-IR pickup in lockstep. A spectrally selective
emitter that dodges Earth IR is 1.6–3.7× **worse**: the radiator at 340 K peaks
at 8.5 µm and Earth at 255 K peaks at 11.4 µm, and the Planck curves overlap
almost entirely. You cannot ignore something only 85 K below you.

**Efficiency and specific power are complements, not substitutes.** Above the
bare film, areal mass is roughly fixed by coverglass, encapsulant and substrate,
so `W/kg = η·S / (kg/m²)` — higher efficiency gives *higher* W/kg. Real module
data agrees: SHARP IMM 3J is 31% and the highest W/kg on offer; Ascent CIGS is
17.5% and the lowest. Thin film is not a lightweight option at module level;
vendor claims near 1,900 W/kg are bare unencapsulated film compared against
space-qualified modules, a factor of seven apples-to-oranges.

**The two mass problems are the same problem.** At 85 W/kg the array is
5.12 kg/m², of which the PV laminate is ~0.5 — **90% is boom, blanket,
tensioning, hinges and harness.** The radiator at 14.2 kg/m² is ~1.5–2 kg/m² of
fin, tube and ammonia — **~87% is structure, deployment and armour.** Neither
number is about photovoltaics or thermodynamics. Both ask the same question: how
do you deploy and hold flat a hectare of thin sheet for fifteen years? So
"array 3× lighter AND radiator 5× lighter" is not two bets. It is one structural
bet entered twice, and the near-term row is more correlated than it looks.

**The weakest number in the mass roll-up is 300 W/kg.** Flown specific power has
gone from ~52 W/kg (1971) to ~100 (ROSA today) — **1.5× in 52 years**.
Extrapolating gives ~117 W/kg by 2046, not 300. Module-level hardware already
does 535–590 W/kg, so the laminate is not the obstacle; the obstacle is that
ROSA's own product line falls from 124 W/kg at 5 kW to 71 at 37 kW, and this
design needs 79× the largest wing ever flown. That single number moves 942 t.

**Nothing replaces a radiating surface.** Heat pumping is area-negative and
mass-neutral. Thermophotovoltaic recovery has a Carnot ceiling of 11.8% at
340 K and would need a 0.145 eV bandgap that no device has. Expendable coolant
needs 37.5 kg/s of sublimating water — 3,242 t/day — three-quarters of the entire facility mass, every day. Liquid droplet radiators claim ~2 kg/m² and have been
"nearly ready" since 1987; they need 10⁵–10⁶ orifices, a 10⁻³ g acceleration
limit and one droplet lost in 10⁸, which is a direct violation of principle 1.
Every joule that enters this facility leaves as thermal radiation from a
surface. The only free variables are its temperature, its emissivity and its
area.

**The corollary worth writing down:** since the surfaces are floored, there is
no return on trying to shrink them, and essentially all remaining engineering
margin lives in kg/m². That is a better headline than "it's all about the array."

## Facility power per GPU — derive it, don't inherit it (replaces the 2.0× convention)

**What the old rule said.** Use 2.0× the chip's rated power as its all-in
facility cost, every post, every chip: H100 700 W → 1.4 kW → ~70,000 at 100 MW;
B200 1,000 W → 2.0 kW → ~50,000. That rule is the basis of Ashley's own
calibration sentence and it is still right *for the H100 on Earth*.

**Where the 2.0× comes from, so it can be taken apart.** A chip's rated power is
what the GPU draws. The facility also has to run everything that lets it draw it:

| layer | H100, Earth | what it is |
|---|---|---|
| chip | 700 W | the GPU and its HBM |
| server share | ~+55% | CPU, system memory, NICs, storage, fans — an 8-GPU HGX box is ~10.2 kW, 1.27 kW per GPU |
| in-building overhead | ×1.15 | chillers, CRAH fans, power distribution losses — the data-center PUE |
| **facility** | **~1.4–1.5 kW** | **2.0×** |

**Why it is the wrong number for this design, in two parts.**

1. *The ratio is chip-specific.* A Rubin at 2,300 W shares roughly the same
   CPU, NICs and NVLink switches as an H100 at 700 W, so the server share is a
   smaller fraction. Derived from the rack rather than inherited: a Vera Rubin
   NVL72 rack at ~220 kW over 72 GPUs is ~3.06 kW per GPU at the rack input,
   with CPU, network and in-rack conversion already inside. That is 1.33×, not
   2.0×. (220 kW is SemiAnalysis via the shared chat — **verify before quoting
   in a post.**)
2. *The PUE term is mass here, not power.* On Earth, 15% of the electricity goes
   to moving heat with fans and chillers. In orbit heat leaves by radiation from
   a surface we already carry; the only power cooling consumes is the pump,
   roughly 1–2% of the heat load. The 15% does not disappear — it becomes
   radiator kilograms, which the mass table already counts. Charging it twice,
   as watts *and* as kg, was the error.

**The replacement rule.** Facility power per GPU in orbit =

```
rack input per GPU (CPU, NICs, switches, in-rack DC-DC — measured, from the rack)
+ array-bus → rack conversion (~5–8%, estimate)
+ pumps (~1–2% of heat load, estimate)
```

For Rubin-class: 3.06 + ~0.34 ≈ **3.4 kW per GPU (1.5×)**, against 4.6 kW under
the old rule — a third less. All of it becomes heat the radiator must shed; the
laser links are the only power that leaves as anything else, and they are
negligible.

**What this does, and what it doesn't.** It scales the whole facility — power,
array, radiator, mass — by 3.4/4.6, with the chip count unchanged. It does not
touch the thermal physics or the per-watt numbers (1,063 m²/MW radiator at
66.8 °C, 2,567 m²/MW array). It also makes the H100-era posts slightly
inconsistent with the design: post 1's "1.4 kW per H100" is correct for an H100
on Earth and should stay, with "on Earth" implied by context; the design's
per-GPU figure is derived separately in CHIP-SPEC.md. **Do not mix the two.**

**Rack-level vs facility, still a trap.** NVL72's "1,667 W/GPU" (120 kW / 72) is
IT load at the rack and already contains the server share but not cooling. The
3.06 kW above is the same kind of number for Rubin. If you want rack-level, say
"rack" out loud; if you want facility-in-orbit, add the two lines above and say
"in orbit." Colossus is the external check on the H100 rule only: 100,000 H100s
against an initial 150 MW is 1.5 kW apiece, provisioned capacity rather than
measured draw, so it bounds the number from above.

## Things I got wrong in this project, so they don't come back

*(Newest first. The pattern is consistent enough to be worth naming: the
arrangement usually survives and my reason for it usually doesn't.)*

- **Carried the 2.0× H100 facility-power rule onto a Rubin in orbit.** It
  bundles a terrestrial PUE that is radiator mass here, and an overhead ratio
  that belongs to a 700 W chip. Overstated the facility by a third. Replaced
  by the derived rule above.
- **Treated "clock factor" as physics.** It is delivered clock over printed
  clock — a datasheet convention. Moving it from 0.87 to 0.95 while keeping
  17.5 PFLOPS silently claimed 9% better FLOPS/W from the same silicon. The
  physical quantity is sustained FLOPS per watt (Rubin: ~15.2 PF at 2,300 W).
  Quote that; drop the factor.
- **Specified 60 TB/s of memory bandwidth that no part has.** Best stack is
  3.6 TB/s (HBM4E, sampled May 2026); eight of them is 29 TB/s. Sixteen would
  restore H100's bytes-per-FLOP but costs more in HBM power than it buys in
  utilization. The "math kept fed" factor fell from 0.88 to 0.70.
- **Sized the design at 40% utilization while the chip spec existed to reach
  70%**, then flipped to 70% with a clock factor of 1.0, then to a 0.60 hybrid
  mixing custom memory with a stock clock. Three wrong rows before the
  consistent one. Ashley caught each.
- **Put "AM0" in post 1 unexplained**, and cut her G20 opening on an agent's
  citation doubt that turned out to be wrong.
- **Cerebras at 5.4 TFLOPS/W was a sparsity number, wrong by 6.5×.** 125 PFLOPS
  ÷ 23 kW. Dense is 12.5 PFLOPS, so 0.83 TFLOPS/W at the wafer — *worse* than an
  H100 SXM at 1.41. Checkable with no source at all: 900,000 cores × 8 FP16 lanes
  would need an 8.7 GHz clock to reach 125 PFLOPS. I had been using the most
  extreme low-power-density part ever built as the existence proof for a claim it
  refutes.
- **Albedo charged raw to both faces.** It is shortwave, so absorbed = α_solar ×
  incident, not 1.0 × incident, and the anti-sun face in a dawn–dusk orbit sees
  the dark hemisphere. Worth 28 W/m² on the radiator and 1.2 K on the sheet. Both
  the reviewer and I had it wrong, in the same direction, for the same reason.
- **The reticle-scale die**, justified by a fabric argument that cancels. Killed
  by lateral spreading: 82 W on a thin sheet is a 137–215 K rise depending on the
  model, against a 16.7 K budget.
- **`zero.py`'s "2.6 K at 10 cm pitch"** was a uniform-source fin with no die in
  it at all. With a real die footprint the same case is 7.9 K — 3× worse. Every
  small-chip number that leaned on it was optimistic.
- **A temperature evaluated at the annual-mean cosine.** A margin is sized on the
  mean; a temperature is bounded at the hot case. I applied the right rule to
  area and the wrong one to temperature.

- Assumed 0.3 kg/m² radiator areal density. Off by ~10×, and it manufactured a
  fake freeze crisis.
- Used the annual-average eclipse fraction (3.9%) to size against, when the
  worst case is 20%.
- Cited ORDEM's silence on mega-constellations as evidence of risk. Absence of a
  model is not presence of risk. (Ashley caught this.)
- Drew the module with 8 joints, 4 carrying coolant or rotating power, in a
  series whose own thesis is that every joint on a coolant loop is a leak path.
  (Ashley caught this.)
- Forced a monolithic-vs-distributed dichotomy on the design agents. It is a
  false binary and the results proved it. (Ashley caught this.)
- Framed structure as one question when it is two at different scales: how a
  single sheet is held flat, and how modules relate to each other.
- Wrote first-person claims in Ashley's draft about arithmetic she did not run.
  Don't. (Ashley caught this.)
- **Left the thermal stack out entirely** — put the junction and the radiator
  both at 80 °C, i.e. heat crossing zero ΔT. Then, when a review flagged it,
  dismissed it as "a ~2× error in a subsystem that is 6% of mass." It was 2.5×
  in a subsystem that is 23–35% of dry mass, and it moved the headline from 39 to
  43 kg/kW.
- Claimed the array/radiator break-even needs 98.3% conversion, "above the
  Landsberg limit." It is 77.3%, which is below it. The number was stale and the
  conclusion only survived because a 4% engineering margin was sitting in the
  denominator.
- Argued coplanar wins thermally at ">40% of net flux" without ever computing a
  view factor. Real answer: coplanar *loses* thermally, 19% to 8.4%, and wins on
  mass. (Ashley asked the question that exposed this — "solar array being close
  to radiator?? does that even make sense?")
- Said the radiator boundary lands at "exactly half the radius" as though it
  were a result. It was a 0.3% rounding coincidence and it moved to 55% as soon
  as the stack was added.
- Computed an ammonia tube wall at 43 °C, a temperature that appears nowhere in
  the design.
- Published a freeze table with no Earth IR in it, whose top row was physically
  impossible.

## Site mechanics

Astro, static. New post = a `.md` file in `src/content/writing/`; filename
becomes the URL. Frontmatter: title, description, date, series, seriesPart,
draft. Math via `$...$` and `$$...$$`. Push to `main` and GitHub Actions
deploys to https://ashley-cho.github.io.

The repo and the Claude project (`claude/CONTEXT.md`, `claude/CHIP-SPEC.md`)
carry the same copies of this file and CHIP-SPEC.md as of PR #94; keep them in
step.

## canon.py — read this before changing any number

`canon.py` in this repo computes every number in the project from first
principles: orbit, thermal, areas, geometry, the layout trade and the mass
roll-up. **Change a number there, not in a document.** Three separate audits
found stale figures surviving in prose after the underlying value had moved —
sixteen of them in one pass — and the only durable fix is a single source.

Run it with `python3 canon.py`. Every figure it prints appears verbatim in
CONTEXT.md, both posts and both artifacts. If a document disagrees with canon,
the document is wrong.

**v6 (2 Oct 2026) rebuilt it from scratch** — the v5 file was lost with a
workspace and had never been pushed. v6 sizes from the benchmark (CHIP-SPEC.md),
scales the stack with die flux, derives facility power per GPU from the rack,
estimates the DiLoCo link, and reproduces every v5 100 MW number at the bottom
as a cross-check (106,315 / 256,690 / 363,005 m², 98.1 m, 2.41, 999, 4,254 t).
If v6 and a document disagree, the document is wrong; if v6 and the v5 numbers
in this file disagree by more than rounding, v6 is wrong.

Two things canon does NOT contain and must not be given false precision:
the ×1.347 system overhead (inherited, never derived) and the 3.36 kg/kW
compute mass (inherited, unsupported). Two more are estimates with no
measurement behind them: the 0.34 kW/GPU for bus conversion and pumps, and the
four utilization factors.
