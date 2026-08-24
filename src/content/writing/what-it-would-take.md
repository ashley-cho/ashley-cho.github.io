---
title: "What it would actually take to put a data center in orbit"
description: "Sixteen problems between a working GPU in orbit and a hyperscale data center. This is the map."
date: 2026-08-24
series: "Data centers in orbit"
seriesPart: 1
draft: true
---

Every watt of electricity a computer uses comes back out as heat. All of it. On
Earth you move that heat with air and water. In vacuum there is no air and no
water. There is one way out, and it is radiation.

That fact shapes everything about putting a data center in orbit. It is not the
hardest part, though, and I only worked that out by doing the arithmetic.

One Nvidia H100 is running in low Earth orbit today — roughly a kilowatt. A
hyperscale data center is 100 megawatts. Some of the AI campuses being built now
are heading toward a gigawatt. The gap between what flies and what is being
promised is five to six orders of magnitude, and most writing about it is either
a press release or a dismissal.

So I worked it out from the constants. This post is the map. The ones after it
take each problem in turn.

## The one number

I size everything against **100 MW** — one hyperscale data center. It's big
enough that every problem below actually bites. At 1 MW you can wave half of
them away.

The per-unit physics doesn't change with scale:

```
  748 m² of radiator      per MW
2,296 m² of solar array   per MW
 ~40 tonnes               per MW
```

Want a gigawatt, multiply by ten. What changes with size isn't the physics. It's
which problems bind.

## The sixteen problems

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

11. **Ground bandwidth.** Laser downlinks have hit 200 Gbps. You're in view of a station 20% of the time, and clouds end the link rather than weaken it. Sustained: 7–14 Gbps. That number decides which workloads can go up at all.
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

One kilowatt is flying. Almost nothing on this list applies to it yet.

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
