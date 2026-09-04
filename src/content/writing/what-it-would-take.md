---
title: "A Hard Problem"
description: "Sixteen problems to solve to have a data center in space."
date: 2026-08-24
series: "Data centers in orbit"
seriesPart: 1
draft: true
---

No one wants a data center in their backyard, whether the argument is legitimate
or false. Climate change and disasters from it are threatening people's lives,
while the clean energy transition is no longer the most important issue for
humanity to solve. Instead, all eyes are on compute.

So why not put data centers in space, where the space is abundant (literally)
and the sunlight is stronger?

To run a data center you need energy, semiconductors, and a cooling system.
Every watt of electricity a computer uses comes back out as heat. All of it. On
Earth we move that heat with air and water. In vacuum there is no air and no
water. Only radiation works.

And in orbit there is no atmosphere overhead to absorb what the universe throws
at you — micrometeoroids, debris, cosmic rays. You protect yourself or you don't
get protected. So is there a way to put that damn thing in space and make it
useful?

## But first, how big are we talking?

This has to come first, because "data center in space" isn't one problem. It's a
different problem at every size. Some of what follows doesn't exist at all below
a megawatt, and some of it only turns nasty above thirty.

I size everything against **100 MW** — one hyperscale data center. Big enough
that every problem below actually bites; at 1 MW you can wave half of them away.
It's also roughly what the people building this say they're aiming at, so it
argues with the actual claim rather than a strawman.

Concretely, 100 MW buys you about **70,000 H100s**, or 55,000 Blackwells. Not
70,000 × 700 W — a 700 W chip costs you roughly 1.4 kW of facility power once
you count its share of CPU, memory, networking and power conversion. Sanity
check: xAI's Colossus runs ~100,000 H100s on ~150 MW, which is the same ratio.

That's 69 exaFLOPS peak, or about 28 effective once you allow for the fact that
real training never keeps the chips fed:

| Training run | Time at 100 MW |
|---|---|
| GPT-4 class (~2×10²⁵ FLOP) | 8 days |
| Llama 3 405B | 16 days |
| 10²⁶ FLOP frontier run | 42 days |
| 10²⁷ FLOP | 14 months |

So: one orbital facility is roughly one frontier training run per month.

The per-unit physics doesn't change with scale:

```
  748 m² of radiator      per MW
2,296 m² of solar array   per MW
 ~40 tonnes               per MW
```

Want a gigawatt, multiply by ten. What changes with size isn't the physics. It's
which problems bind.

## The sixteen problems

Follow one electron. It starts as sunlight, gets caught by a panel, crosses a
bus, does its work in a chip, and leaves as heat through a radiator. Every step
of that journey is a problem. Then the answer has to get to the ground, and the
whole thing has to survive up there while it happens.

**Power in**

1. **Collecting it.** 230,000 m² of array for 100 MW. Three times the radiator area.
2. **Eclipse.** A dawn-dusk orbit is 99% sunlit, not 100%. Batteries cover the gap and are dead mass the rest of the year.
3. **Distributing it.** Low voltage means enormous cable mass. High voltage arcs, because low orbit is full of plasma.

**Heat out**

4. **Rejecting it.** Radiation only. 75,000 m² of panel at 80 °C. The 2.7-kelvin background contributes almost nothing.
5. **Moving it.** Heat conducting through solid aluminium peters out after 30 cm. Getting it from a dense rack to a distant panel needs pumped loops at a scale nobody has flown.
6. **The ceiling.** Radiated power goes as temperature to the fourth, so running hot is the strongest lever there is. Chips stop at 100 °C. Pumping heat to a hotter radiator costs more power than it saves in area.

**Survival**

7. **Radiation.** Two problems in one word. Cumulative dose degrades chips slowly and shielding helps. Single-event upsets flip one bit instantly, come from cosmic rays you can't shield against, and have to be absorbed in software.
8. **Micrometeoroids.** A 1 mm grain at orbital speed carries the energy of a 70 mph fastball into a 1 mm spot. Spread 300,000 m² of thin, fluid-filled surface across five years and you get thirty times the ISS's lifetime exposure.
9. **Drag.** Huge area, low mass, atmosphere that hasn't quite ended. You burn propellant continuously. Fly higher and the radiation dose triples.
10. **Obsolescence.** Three-year chips, fifteen-year spacecraft. Starlink already builds for a five-year life and planned disposal, so this one may be solved by precedent.

**Data**

11. **Ground bandwidth.** Laser downlinks have hit 200 Gbps, but you're in view of a station only about 20% of the time and clouds end the link rather than weaken it. Sustained, that's 7–14 Gbps *per terminal* — so the ceiling isn't the laser, it's how many ground stations can see you at once. And the traffic is lopsided: 28 million output tokens a second is under 1 Gbps going down, while the prompts and context feeding it run ten to fifty times that going up, in the direction that's physically harder.
12. **Links between satellites.** Lasers aimed with microradian precision between platforms drifting 100–200 m apart.
13. **One job across many.** Training is lockstep — every chip trades gradients with every other chip, every step. One dropped link stalls the cluster, and you can't walk to the rack and swap a dead node.

**Structure**

14. **Unfolding it.** Stowed volume isn't the constraint. Folded panels radiating into each other is, and so is the fact that every hinge on a coolant loop is a leak path that has to work first time.
15. **Pointing it.** Arrays want the sun. Radiators want cold sky, away from the sun and away from Earth. Comms want a ground station that's moving. Three subsystems, one orientation.
16. **Mass.** 34–59 kg per kW. Every problem above ends up here.

## Which ones exist at which size

| Around | What starts to bite |
|---|---|
| 50 kW | Heat rejection stops being trivial |
| 100 kW | You need a pumped loop, and you hit the largest panel that unfolds without robots |
| 1 MW | The array overtakes the radiator; you need a second satellite, so coordination begins |
| 13 MW | Micrometeoroid exposure passes the ISS's entire lifetime |
| 30 MW | Graceful degradation stops being elegant and becomes mandatory |
| 100 MW | You measurably worsen the debris environment you're flying in |

One kilowatt is flying today. Almost nothing on this list applies to it yet.

## What I think everyone gets wrong

Every article about this is about cooling. Cooling is hard, and it's where I'll
start, because the standard explanation of it is wrong in an interesting way.

But it isn't the answer. This is a **mass-per-kilowatt problem**. Every item
above turns into kilograms you have to lift, and they trade against each other.
Run the radiator hotter and it shrinks, but the chips have to change. Go modular
and the plumbing gets easier, but every module buys its own thrusters and radios.
Fly higher and drag falls while shielding rises.

Cooling is one term in that budget. It isn't even the biggest. The solar array is.

## Where I'm unsure

Two numbers I haven't pinned down. The debris flux at the sizes that matter rests
on Space Shuttle measurements that stopped in 2011, so the error bars are wider
than the literature sounds. And I've sketched the concentrator trade for solar
arrays without working the mass side properly.

If you know this material and I've got something wrong, tell me.

---

**Next:** space is cold, and it's the least relevant fact about cooling a data center.
