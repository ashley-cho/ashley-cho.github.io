---
title: "Space is cold, and it's the least relevant fact about cooling a data center"
description: "Everyone reaches for the 3-kelvin background when they explain orbital data centers. It contributes about seven parts in a billion."
date: 2026-09-02
field: Spaceflight
series: "Data centers in orbit"
seriesPart: 5
problem: 4
draft: true
---

Every explanation of orbital compute starts with the cold. The cosmic
microwave background sits at [2.7 kelvin](https://lambda.gsfc.nasa.gov/product/cobe/),
so a data center in orbit can dump its waste heat into that reservoir for free.
The number is real, and it doesn't matter.

This post assumes what the series settles later: a 15.8 MW facility sized for
one frontier training run per 60 days, a 650 km dawn-dusk orbit, a flat
radiator edge-on to Earth with both faces radiating, GPU-class chips at about
1.4 W per square millimetre of die, silicon capped at 85 °C, coolant boiling
directly on the die, and a pumped two-phase loop from chip to panel.

## Why the 3 kelvin doesn't matter

A surface radiating into space sheds heat by Stefan–Boltzmann:

$$
q = n\,\varepsilon \sigma \left(T_{\text{rad}}^{4} - T_{\text{sink}}^{4}\right)
$$

$q$ is watts per square metre, $n$ the number of faces that see sky,
$\varepsilon$ emissivity, $\sigma$ the Stefan–Boltzmann constant, and the two
temperatures are the panel's and the sink's, in kelvin.

Everything hinges on the fourth power. A radiator at 54.6 °C, where this
design's ends up, is 328 K, so the sink's share of the bracket against a 3 K
sky is (3/328)⁴, seven parts in a billion. **The cold of space is free, and it
is also nearly meaningless.** Every watt you shed is bought with your own
temperature.

## What is actually true

Two things, and both make it harder.

**There is no convection.** On Earth a data center moves heat with air and
water. In vacuum there is no fluid, so radiation is the only exit — the
mechanism of last resort on Earth, and the only one in orbit.

**Heat is also coming in**, from three sources.

Sunlight, 1,361 W/m² on the sunward face with the sun square-on, the hot case,
of which the panel keeps whatever the coating fails to reflect. Good white
paint [darkens under UV](https://ntrs.nasa.gov/api/citations/20080018585/downloads/20080018585.pdf),
and at an assumed end-of-life absorptance of 19% that is **258.6 W/m²**, 71% of
everything the panel takes in.

Earth's infrared, [239 W/m²](https://en.wikipedia.org/wiki/Outgoing_longwave_radiation).
Edge-on, each face sees the planet with a view factor of 0.241 and absorbs at
its emissivity of 0.90: **51.8 W/m²** on each face, since the panel radiates
from both sides and collects from both too.

Albedo, sunlight bounced off the planet, about 11 W/m² on the sunward face at
the same 19%: **2.1 W/m²**. The anti-sun face looks at the unlit half of the
planet and gets none.

That is 312.5 W/m² on the sunward face, 51.8 on the other, **364 W/m² in
total**. Solve 364 = 2 × 0.90 × σ × T⁴ and the temperature that pushes back
that hard is 244 K. The *effective* sink is −29 °C, a room with no air in it.
The 3 K background sits somewhere behind that and never gets a vote.

## The number that actually sets the size

The hotter the panel, the smaller it can be, and what caps its temperature is
the chips: **heat only flows downhill.** The radiator runs at the junction
temperature — the silicon itself — minus whatever it costs to carry the heat
out of the chip and into the panel. That drop is the thermal stack, and every
kelvin of it is paid for in area.

How big the drop is comes down to two things: how densely the chip makes heat,
and whether the coolant boils on bare silicon or through a metal lid and a
layer of thermal paste, which is how essentially every server CPU package on
Earth is built. Direct-die on this chip costs about 30 K, so an 85 °C junction
puts the radiator at 54.6 °C. On an H100, which makes heat at 0.86 W/mm²
instead of 1.4, the same path costs 18 K. A lid costs 50 to 90 K. At the
bottom of that range the radiator sits at 35 °C, nets 556 W/m² and is 1.5
times the size; at the top it sits at −5 °C, nets 164 W/m² and is five times
the size. At −29 °C it rejects nothing at all.

| Radiator temperature | Net flux | Planform area at 16.8 MW |
|---|---|---|
| 40 °C | 617 W/m² | 27,200 m² |
| 54.6 °C — this design | 813 W/m² | 20,700 m² |
| 60 °C | 893 W/m² | 18,800 m² |
| 80 °C | 1,223 W/m² | 13,700 m² |
| 100 °C | 1,615 W/m² | 10,400 m² |

Net flux is 2 × 0.90 × σ × T⁴ − 364. Area is 16.8 MW over that, the extra 6%
being the leakage the silicon draws at 85 °C without doing work.

The 30 K stack is more than a third of the panel: without it the radiator
could sit at 85 °C and shed the same heat from 12,800 m².

## A calibration

The ISS radiators are rated for [70 kW through six units of
79.2 m²](https://www.nasa.gov/wp-content/uploads/2021/02/473486main_iss_atcs_overview.pdf),
475 m² in all, so about **147 W/m²**. This design's panel nets 813 W/m². Most
of the gap is temperature — the ISS loop is set to 2.8 °C, where the same
parasitic load leaves 228 W/m² — and the rest is the drop through the loop and
fin efficiency.

So this facility needs about **44 times the ISS's radiator planform area**.

## Where this leaves us

Cooling a data center in orbit is a temperature-and-area problem, and the cold
of space is a boundary condition that has stopped being interesting. The
biggest lever on the radiator's share of kilograms per kilowatt is whether
there is a lid between the chip and the coolant — a millimetre of metal and
paste every server on Earth has, and this one can't afford. The second is the
chip's own heat density, which is why a chip built for orbit wants to spread
the same work over more silicon.

That's a later post. The next one is about getting the heat from the chip to
this panel at all, which is where the design stops being about temperature and
starts being about plumbing.

---

*Part of a series working through the engineering of orbital data centers from
first principles. Corrections are welcome.*
