---
title: "Space is cold, and it's the least relevant fact about cooling a data center"
description: "Everyone reaches for the 3-kelvin background when they explain orbital data centers. It contributes about five parts in a billion."
date: 2026-08-24
series: "Data centers in orbit"
seriesPart: 2
draft: true
---

[The map](/writing/what-it-would-take/) listed sixteen problems between a
kilowatt in orbit and a hundred megawatts. This post takes the first of them.

Heat, because heat is where every explanation of this idea goes first — and
where almost every explanation goes wrong in the same way.

## The thing everyone says

The pitch is always some version of this: space is cold. The cosmic microwave
background sits at 2.7 kelvin. A data center in orbit can dump its waste heat
into that enormous cold reservoir, and you get cooling for free.

It sounds right. It has a real number in it. And the number is almost entirely
irrelevant.

## Why the 3 kelvin doesn't matter

A surface radiating into space sheds heat according to Stefan–Boltzmann:

$$
P = \varepsilon \sigma \left(T_{\text{rad}}^{4} - T_{\text{sink}}^{4}\right)
$$

Everything hinges on that fourth power. Run a radiator at 80 °C — 353 K, about
as hot as you can get the back of a working server — against a 3 K sink, and the
sink's contribution to the bracket is:

$$
\left(\frac{3}{353}\right)^{4} \approx 5 \times 10^{-9}
$$

Five parts in a billion. If the background were 3 K or 30 K or 0 K, your
radiator would perform the same to nine significant figures. **The cold of space
is free, and it is also nearly meaningless.** What matters is how hot *your*
side is.

That is not a pedantic correction. It changes what you optimize. "Space is cold"
suggests the environment is doing work for you. It isn't. Every watt you shed is
bought entirely with your own temperature.

## What is actually true

Two things, and they pull in opposite directions.

The first is genuinely hard: **there is no convection.** On Earth, a data center
moves heat with air and water — fans, chilled water loops, evaporative towers.
All of that requires a fluid to carry heat away, and in vacuum there is no
fluid. Radiation is the only exit. It is the mechanism of last resort in
terrestrial engineering, and in orbit it is the only one you have.

The second is the part nobody mentions: **heat is also coming in.**

A radiator panel in low Earth orbit sits in a shooting gallery of thermal
inputs. Direct sunlight is 1,361 W/m². Roughly 30% of that bounces off Earth and
comes back up at you as albedo. Earth itself glows in the infrared at about
240 W/m². Even with a good optical solar reflector coating — the kind of
silvered surface that reflects most sunlight while still radiating efficiently —
a panel absorbs somewhere between 200 and 350 W/m² that it did not ask for.

Which means the *effective* sink your radiator works against isn't 3 K at all.
In LEO it behaves more like 250–290 K. You are not radiating into the void. You
are radiating into a fairly warm room that happens to have no air in it.

## What it costs

Put those together and you can size the thing. Both faces of the panel radiate,
emissivity around 0.9, minus 250 W/m² of parasitic load:

| Radiator temperature | Net flux | Area for 100 MW |
|---|---|---|
| 60 °C | 1,007 W/m² | 99,000 m² |
| 80 °C | 1,337 W/m² | 74,800 m² |
| 100 °C | 1,729 W/m² | 57,800 m² |
| 127 °C | 2,367 W/m² | 42,300 m² |

Seventy-five thousand square metres for one hyperscale data center's worth of
compute. That is about eleven soccer fields of radiator, unfolded in orbit, to
run a facility that on Earth fits in a warehouse with a chiller plant on the
roof.

And look at the shape of that table. Going from 60 °C to 127 °C more than halves
the area. That is the fourth power doing its work — and it is the single
strongest lever anyone building this has. Almost everything interesting about
orbital thermal design turns out to be an argument about how to run the radiator
hotter. (That's the next post but one, and the answer is not what you'd guess.)

## A calibration, because these numbers are hard to feel

The International Space Station has the largest active thermal control system
ever flown. Its ammonia-loop radiators cover **422 m² and reject 70 kW** — about
166 W/m² in practice, well under the theoretical figure, precisely because of
the solar and Earth-IR loading described above.

So a 100 MW orbital data center needs roughly **177 times the ISS's entire
radiator area.**

I had heard, secondhand, that a space data center would need a radiator "ten
times the size of the ISS." Ten times the ISS's *radiator area* is 4,220 m²,
which sheds about 5.6 MW — not a hyperscale data center, off by nearly a factor
of twenty. But ten times the ISS's *overall footprint* — the station's 109 m
truss by 73 m array span is about 8,000 m² of bounding box — comes to
80,000 m², within about 7% of the 100 MW figure.

Both readings circulate. They differ by roughly 19×. It's worth knowing which
one you've been told.

## Where this leaves us

The framing to carry forward is that this is not a cold problem. It is a
temperature-and-area problem, and the cold of space is a boundary condition so
generous it has stopped being interesting.

Which sets up the thing that genuinely surprised me when I worked it out, and
which inverts the premise most people arrive with. Everyone assumes cooling is
the hard part of putting a data center in orbit.

It isn't. The solar panels are three times bigger than the radiators.

That's next.

---

*This is the second post in a series working through the engineering of orbital
data centers from first principles. Corrections are genuinely welcome — the numbers
here are mine, and I'd rather find out they're wrong from you than not find out.*
