---
title: "A Hard Problem"
subtitle: "Sixteen problems between one GPU in orbit and a frontier training run"
description: "Sixteen problems to solve to have a data center in space."
date: 2026-08-24
field: Spaceflight
series: "Data centers in orbit"
seriesPart: 1
draft: true
---

Nobody wants data centers in their backyard, and the climate argument against
them keeps losing — the US has just [cut climate, debt and sustainability from
the 2026 G20 program](https://www.cfr.org/articles/us-g20-presidency-narrow-agenda-2026)
in favor of energy supply chains and new technology.

So why not put the data center in space, where there's room and the sunlight
is stronger?

A data center needs energy, semiconductors, and somewhere to put the heat.
Every watt a computer draws comes back out as heat, and on Earth we move it
with air and water. In vacuum there's neither, so radiation is the only exit.
And with no atmosphere overhead, micrometeoroids, debris and cosmic rays
arrive undiminished.

Sixteen things have to work.

## How big

I size everything against one job: **train a frontier model in one 60-day
release cycle**. I take that model to be a trillion active parameters trained
on 30 trillion tokens. The tokens are the latest disclosed figure —
[DeepSeek V4-Pro trained on 33 trillion](https://arxiv.org/abs/2606.19348) —
and the parameters are my assumption, since closed labs publish none and
DeepSeek's 49 billion active is believed to be well below the frontier.
Training costs [about 6 FLOP per parameter per token](https://arxiv.org/abs/2203.15556),
so the run is 1.8×10²⁶ FLOP, and sixty days is 5.2 million seconds:
**35 exaFLOPS, sustained, for two months.**

For scale, [Llama 3 405B](https://arxiv.org/abs/2407.21783) was 3.8×10²⁵ FLOP
on 16,384 H100s. This is nearly five of those every two months.

How many chips and how many megawatts that takes depends on the chip and on
how much of its rated speed real training uses — [Llama 3 ran at 38–43% of the
H100's BF16 rating](https://arxiv.org/abs/2407.21783), and [Llama 4 Behemoth at
about 20% of its FP8 rating](https://ai.meta.com/blog/llama-4-multimodal-intelligence/).
Both are design choices and come later. Whatever the facility's power turns
out to be, what it actually delivers over a year is problems 1 and 2.

## Three equations

**Collecting.** Array area is the power you want over what a square meter of
sunlight delivers:

$$
A_{\text{array}} = \frac{P}{S \cdot \eta \cdot \cos\theta}
$$

**Rejecting.** Radiator area is the power you must shed over what a square
meter radiates, net of what it absorbs:

$$
A_{\text{rad}} = \frac{P}{n\,\varepsilon\sigma T_{\text{rad}}^{4} - q_{\text{parasitic}}}
$$

**Heat flows downhill.** The radiator runs colder than the chips by whatever
it costs to get the heat out of them:

$$
T_{\text{rad}} = T_{j} - \Delta T_{\text{stack}}
$$

$S$ is the solar constant, 1,361 W/m² above the atmosphere. $\sigma$ is
Stefan–Boltzmann. Those two are physics. Everything else is a choice:

- $\eta$ — cell efficiency. Which cell you buy.
- $\cos\theta$ — how square-on the array is to the sun. Gimbal, or accept a seasonal droop.
- $n$ — how many faces see cold sky. One if something sits behind the panel, two if it floats free.
- $\varepsilon$ — emissivity, how well the surface radiates. What you paint it.
- $q_{\text{parasitic}}$ — heat coming *in*: sunlight the paint absorbs, Earth's infrared, albedo. A radiator in low orbit is looking at the sun and a warm planet.
- $T_j$ — junction temperature, how hot you run the silicon.
- $\Delta T_{\text{stack}}$ — the temperature lost carrying heat from silicon to radiating surface. Every kelvin here is paid for in area.
- The orbit. It sets the eclipse, the drag, the dose, and how much of the sky is Earth.

Put 32% cells, square-on to the sun, into the first equation and you get
**2,300 m² of array per megawatt**. The radiator's area depends on how hot it
runs, which is problem 4. Double the power and both areas double.

## The sixteen problems

Follow one watt. It starts as sunlight, gets caught by a panel, crosses a power
bus, does its work in a chip, and leaves as heat through a radiator. Then the
trained model has to reach the ground, and the whole thing has to survive.

**Power in**

1. **Collecting it.** A gimballed array costs mass and a rotating joint; a fixed array costs a seasonal droop.
2. **Eclipse.** Even a dawn-dusk orbit, the sunniest plane there is, has a shadow season below about 1,400 km. At 650 km it is 96% sunlit over a year, and on 88 days the shadow runs up to 20 minutes of each 98-minute orbit. Batteries carry it, or the facility stops.
3. **Distributing it.** Low voltage means cable mass. High voltage arcs, because low orbit is full of plasma. Both get worse with size.

**Heat out**

4. **Rejecting it.** Radiation only. The panel absorbs sunlight and Earth infrared the whole time it sheds, and it has to run colder than the chips.
5. **Moving it.** Conduction through metal doesn't reach far. Getting heat from a dense rack to a distant panel needs pumped loops at a scale nobody has flown, and every meter of loop can leak.
6. **The ceiling.** Radiated power goes as $T^4$, so running the chips hotter looks like the strongest lever there is. Something stops you well short. What, and at what cost, is a whole post.

**Survival**

7. **Radiation.** Cumulative dose degrades chips slowly and shielding helps. Single-event upsets flip a bit instantly, come from cosmic rays you can't shield, and have to be absorbed in software.
8. **Micrometeoroids and debris.** A 1 mm aluminum grain at a 10 km/s closing speed carries the energy of a 70 mph fastball into a 1 mm spot, and every square meter of array and radiator is thin surface to hit. [NASA's ORDEM](https://orbitaldebris.jsc.nasa.gov/modeling/ordem.html) gives the flux. What a hole costs depends on which surface it's in.
9. **Drag.** Huge area, low mass, atmosphere that hasn't quite ended. You burn propellant continuously. Higher orbits cost dose instead.
10. **Obsolescence.** Three-year chips, fifteen-year spacecraft. Starlink builds for a short life and planned disposal; whether that transfers to hardware you can't cheaply replace is the question.

**Data**

11. **Ground bandwidth.** Lasers have [hit 200 Gbps](https://ntrs.nasa.gov/citations/20230000434), but a station is in view about 20% of the time and clouds end the link. [Sustained rate is a small fraction of peak](https://arxiv.org/pdf/2604.27197). For training the traffic is lopsided the other way from serving: the dataset goes up once, the trained weights come down once, and a bad week of weather delays a model rather than a user.
12. **Links between satellites.** Lasers aimed with microradian precision between platforms kilometers apart.
13. **One job across many.** Lockstep training trades gradients between every chip every step and stalls on one dropped link. Whether lockstep is actually required is the question.

**Structure**

14. **Unfolding it.** Stowed volume, panels radiating into each other while folded, and every hinge on a coolant loop being a leak path that has to work first time.
15. **Pointing it.** Arrays want the sun. Radiators want cold sky. Comms want a moving ground station. One orientation.
16. **Mass.** Published estimates span [34–59 kg per kW](https://arxiv.org/pdf/2604.27197). It comes down to two numbers, [array watts per kilogram](https://www.nasa.gov/wp-content/uploads/2025/02/3-soa-power-2024.pdf) and radiator kilograms per square meter, where the [ISS radiator panels](https://www.nasa.gov/wp-content/uploads/2021/02/473486main_iss_atcs_overview.pdf) are 14.2 kg/m² against a [1994 NASA goal of 5 kg/m² or lower](https://ntrs.nasa.gov/api/citations/19940032314/downloads/19940032314.pdf). Every problem above ends up here, and much of the removable mass is margin: radiator thickness buys puncture tolerance, shielding buys dose tolerance, propellant buys years.

## Which ones exist at which size

| Around | What starts to bite |
|---|---|
| 50 kW | Heat rejection stops being trivial |
| 100 kW | Heat transport stops being a conduction problem, and the panel stops unfolding without robots |
| a few MW | One spacecraft stops being enough; you assemble in orbit or fly in formation |

[A single H100 is flying today](https://www.datacenterdynamics.com/en/news/starcloud-1-satellite-reaches-space-with-nvidia-h100-gpu-now-operating-in-orbit/)
on a 60 kg satellite. Almost nothing on this list applies to it yet.

Sixteen problems, one post each, then one that draws the facility.

If you know this material and something here is wrong, tell me.

---

**Next:** problem 1 — collecting the power, when the [roll-out wings on the
ISS](https://rdw.com/wp-content/uploads/2023/06/redwire-roll-out-solar-array-flysheet.pdf)
are rated at 28 kilowatts each.
