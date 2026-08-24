---
title: "What it would actually take to put a data center in orbit"
description: "There is one GPU in orbit today. A hyperscale data center is 100,000 times larger. This is a map of everything in between."
date: 2026-08-24
series: "Data centers in orbit"
seriesPart: 1
draft: true
---

There is an Nvidia H100 running in low Earth orbit right now. It went up on
Starcloud&#8209;1 in November 2025 — one GPU, roughly a kilowatt, orbiting the
planet while it works.

A hyperscale data center on the ground is about 100 megawatts. Some of the AI
training campuses being built today are heading toward a gigawatt.

**The gap is five to six orders of magnitude.** One kilowatt is flying. A
hundred thousand times that is being pitched. Google has published a paper on a
constellation of TPU satellites. SpaceX has filed for a constellation. Starcloud
has raised money at a billion-dollar valuation on the premise.

I got curious about whether the physics allows it, and found that most of what's
written about this is either a press release or a dismissal, with very little in
between that actually does the arithmetic. So I'm going to do the arithmetic.

This post is the map. It names every problem I could find, says roughly why each
one is hard, and admits which ones I don't yet know the answer to. The posts
after it take them one at a time.

## The one number to hold

I'll size everything against **100 megawatts** — one hyperscale data center's
worth of compute. Not because it's the right target, but because it's a unit
people already have a feel for, and because it's big enough that every problem
below actually bites. At 1 MW you can hand-wave half of them.

The useful thing is that the per-unit physics doesn't change with scale:

```
  748 m² of radiator   per MW
2,296 m² of solar array per MW
 ~40 tonnes             per MW
```

So if you'd rather think about a gigawatt, multiply by ten. If you'd rather
think about the demonstrator flying in 2027, divide by a hundred. The numbers
scale; only which problems bind changes, and I'll come back to that at the end.

## The map

### Power in — getting 100 MW of electricity

**Collecting it.** Sunlight in orbit is 1,361 W/m², good cells convert about a
third of it, so 100 MW needs roughly 230,000 m² of array. That is *three times
the radiator area*, which surprised me and inverts the premise most people
arrive with. The binding metric isn't efficiency, it's watts per kilogram —
and there's an interesting fight between traditional space cells and perovskites
that can hit 44 W per gram.

**Surviving eclipse.** Orbit the day/night terminator and you're in sunlight
~99% of the time. Not 100%: a few weeks a year the geometry slips and you need
batteries, which are dead mass the rest of the time.

**Moving it around.** 100 MW at low voltage means absurd cable mass. At high
voltage you get arcing and sputtering, because low Earth orbit is full of
plasma. The ISS runs 160 V for a reason.

### Heat out — getting 100 MW back out again

**Rejecting it.** Everyone starts here and almost everyone gets it wrong the
same way, by reaching for the 2.7-kelvin cosmic background. That number
contributes about five parts in a billion. The real constraint is your own
radiator temperature and the sunlight landing on the panel.

**Moving it.** This is the one nobody writes about, and I think it's harder than
rejection. Heat conducting through solid aluminium peters out after about 30 cm.
Getting kilowatts out of a dense rack and spread across 75,000 m² of panel is a
plumbing problem — pumped two-phase loops, at a scale nobody has flown.

**The temperature ceiling.** Radiated power goes as temperature to the fourth,
so running hotter is by far your strongest lever. But chips cap out around
100 °C, and pumping heat to a hotter radiator costs more power than it saves in
area. The real move is a chip *designed* to run hot — which is a semiconductor
research question, not a spacecraft one.

### Survival — staying alive up there

**Radiation.** Two different problems wearing one word. Cumulative dose degrades
electronics slowly and shielding helps. Single-event upsets flip one bit
instantly, come from cosmic rays you cannot shield against, and have to be
handled in software instead. Google's own TPU testing flagged the second one as
unresolved for training workloads.

**Micrometeoroids.** A one-millimetre grain at orbital speed carries the energy
of a 70 mph fastball delivered into a one-millimetre spot. Now spread 300,000 m²
of thin, fluid-filled surface across the sky for five years and count the hits.
The exposure is roughly thirty times what the ISS has accumulated in its entire
life.

**Drag.** Enormous area, low mass, still-detectable atmosphere. You burn
propellant continuously just to stay up. Fly higher to escape it and the
radiation dose triples.

**Obsolescence.** GPUs turn over every three to five years. Spacecraft are built
for fifteen. This one may have an answer already: Starlink is designed for a
five-year life and planned disposal, so the industry has normalised building
things meant to die.

### Data — talking to Earth and to each other

**The ground link.** Laser downlinks have demonstrated 200 Gbps from orbit. But
you're only in view of a given ground station about 20% of the time, and clouds
don't attenuate a laser link so much as end it. Sustained throughput lands
closer to 7–14 Gbps per terminal. That single fact decides which workloads can
live up there at all.

**Links between satellites.** Free-space optical between platforms drifting
100–200 m apart, each aiming a laser with microradian precision while
everything flexes and the orbit slowly deforms.

**Running one job across many.** Distributed training is lockstep — every chip
exchanges gradients with every other chip, every step. One dropped optical link
stalls the entire cluster. And when a node dies you can't walk to the rack and
swap it.

### Structure — actually building it

**Unfolding it.** Stowed volume turns out not to be the constraint; 230,000 m²
of blanket packs into about half a Starship bay. The constraints are that folded
panels radiate into *each other* rather than into cold sky, and that every hinge
on a coolant loop is both a leak path and a thing that has to work first time,
with no one there to fix it.

**Pointing it.** Three subsystems want three different orientations. Arrays want
the sun. Radiators want cold sky, edge-on to the sun and away from Earth. Comms
want a ground station that's moving. They fight, and the joints that resolve the
fight are heavy and have failed before.

**Mass.** 34–59 kilograms per kilowatt, which puts 100 MW somewhere around 4,000
tonnes. This is the term every other problem feeds into.

## Which problems exist at which size

Most of these don't switch on until the thing gets big, which is why the
demonstrators flying now don't tell you much about whether the concept works:

| Around | What starts to bite |
|---|---|
| 50 kW | Heat rejection stops being trivial |
| 100 kW | You need a pumped loop; you hit the largest panel that can unfold without robots |
| 1 MW | The array overtakes the radiator; you need more than one satellite, so coordination begins |
| 13 MW | Micrometeoroid exposure passes the ISS's entire lifetime |
| 30 MW | Graceful degradation stops being elegant and becomes mandatory |
| 100 MW | You are a non-trivial contributor to the debris environment you're flying in |

One kilowatt is flying today. Almost nothing on this list applies to it.

## The thing I think everyone gets wrong

Every article about this is about cooling. Cooling is genuinely hard, and it's
where I'll start, because the standard explanation of it is wrong in an
interesting way.

But it isn't the answer. **This is a mass-per-kilowatt problem.** Every item
above resolves into kilograms you have to lift, and they trade against each
other: run the radiator hotter and it shrinks but the chips have to change; go
modular and the plumbing gets easier but every module pays for its own thrusters
and radios; fly higher and drag falls while shielding rises. Cooling is one term
in that budget, and not even the largest one — the solar array is.

That's the frame I'll carry through the series, and I'll come back to it at the
end once every trade is on the table.

## Where I'm uncertain

Two numbers I haven't nailed down and will flag when they matter. The debris
flux at the relevant particle sizes rests on Space Shuttle measurements that
stopped in 2011, so the error bars are wider than the confident-sounding
literature suggests. And I've sketched the concentrator trade for solar arrays
without properly working the mass side.

If you know this material and I've got something wrong, I'd rather hear it than
not. That's most of why I'm writing it down in public.

---

**Next:** space is cold, and it's the least relevant fact about cooling a data
center.
