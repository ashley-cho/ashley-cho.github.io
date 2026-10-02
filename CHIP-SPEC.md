# Chip spec and the design it sizes (settled 2 Oct 2026)

Supersedes the 100 MW anchor. CONTEXT.md still holds the physics (canon v5),
the thermal stack, the layout trade and the mass lines; this doc holds what
the facility is *for*, what chip it runs, and what that sizes. Where the two
disagree on scale, this one is current.

## Design metrics (Ashley's, in order)

1. Light, against the payload that has to lift it.
2. Looks super simple.
3. Easy to build.
4. Easy to coordinate through point-to-point communication.
5. Benchmark: ~1T active parameters × ~30T tokens in one 60-day cycle
   → 1.8×10²⁶ FLOP → **35 effective EFLOPS**.

Heat, chip count and satellite count are outputs of these, not inputs.

## How the chain runs

Each line below is one division. Everything downstream of the benchmark is
sized by it.

```
35 effective EFLOPS                        the benchmark, fixed (34.7 unrounded)
÷ 0.55 utilization                         → 63 EFLOPS of sustained chip capacity
÷ 15.2 PFLOPS sustained per chip           → 4,150 working chips
× 1.05 hot spares                          → 4,360 chips
× 3.4 kW facility power per chip           → 14.8 MW when all are lit
÷ 0.943 annual availability                → 15.7 MW nameplate
× 1.062 leakage                            → 16.7 MW of heat
÷ 813 W/m² net flux                        → 20,500 m² radiator
× 2,417 m² per MW drawn                    → 40,300 m² array (17.5 MW peak)
mass lines (array W/kg, radiator kg/m²)    → 232 t near-term, 740 t flown
```

Four numbers in that chain are the design: **0.55, 15.2, 3.4, 813.** The rest
is canon physics. `canon.py` (v6) prints every line of it. Each of the four is explained below, with what it replaced.

## The chip

A custom Rubin-class part — Rubin's silicon and process, repackaged for orbit.
The custom content is the memory, the fault tolerance and the operating point,
not the logic.

| | | basis |
|---|---|---|
| FP8 dense, **sustained** | **15.2 PFLOPS** | Rubin silicon at its 2,300 W cap. Nvidia's 17.5 is a boost-clock figure the chip holds ~87% of under sustained load (estimate from the H100 analogue, ~1,980 → ~1,750 MHz; Nvidia publishes no sustained rate). We quote the sustained number and carry no "clock factor". |
| chip power | 2,300 W | Rubin TDP, HBM included |
| **facility power per chip, in orbit** | **3.4 kW (1.5×)** | rack input 3.06 kW (Vera Rubin NVL72 ~220 kW ÷ 72 — SemiAnalysis via the shared chat, verify) + ~0.34 kW for array-bus conversion and pumps (estimate). Replaces the 2.0× H100 rule; see CONTEXT.md. |
| memory | 8 × HBM4E: 384 GB, 29 TB/s | best stack that exists (Samsung HBM4E sample, 3.6 TB/s, 48 GB, May 2026); Rubin's eight-stack shoreline |
| bytes per kFLOP | 1.65 | half of H100 BF16's 3.4; same as Llama 4 Behemoth had on H100 FP8 |
| tight-link domain | 72 GPUs, NVLink-class copper, ~2 m reach | the NVL72 domain |
| between domains and modules | local SGD / DiLoCo, sync every few hundred steps | ~15 Gbps per module for a 1T model (canon) |
| junction ceiling | 85 °C | HBM refresh-throttle limit; logic would take ~100 °C |
| fault tolerance | ECC on all memory, 5% hot spares, in-memory checkpoints | goodput factor |
| precision | FP8 matmuls; BF16/FP32 for embeddings, output head, norms, optimizer | the DeepSeek V3 pattern; no public run is "full FP8" |

### Utilization: 0.55, four factors

Utilization is useful FLOPS ÷ sustained FLOPS. It is the product of everything
that stops a chip doing useful math at its sustained rate:

| factor | measures | value | why |
|---|---|---|---|
| math kept fed | not waiting on memory | 0.70 | 1.65 B/kFLOP, half of H100 BF16's ratio, where big runs reached 40%+. Estimate. |
| communication hidden | not waiting on other chips | 0.90 | 72-GPU domain plus DiLoCo between domains. Estimate; DiLoCo unproven at frontier scale. |
| pipeline | not idling between stages | 0.92 | many small micro-batches. Estimate. |
| goodput | not lost to failures and rollbacks | 0.95 | ECC, hot spares, fast checkpoints. Estimate. |
| **product** | | **0.55** | |

There is no clock row. A "clock factor" (delivered clock ÷ printed clock) is a
datasheet convention, not a physical loss; it went to 1.0 by construction the
moment we quoted sustained FLOPS, and stopped being a factor. The physical
quantity it was standing in for — FLOPS per watt — is in the 15.2 PF / 2,300 W
line above.

Every factor is an estimate of best-case engineering; none is measured on a
frontier run. Disclosed FP8 MoE runs on Hopper sit at ~20%. The 40% "industry
rule of thumb" is BF16 on H100 (Llama 3: 38–43%) and is not the right
comparator for an FP8 chip.

### What was considered and not taken

- **16 HBM4E stacks (58 TB/s).** Restores H100's bytes-per-FLOP and lifts
  "math kept fed" to ~0.88, but at ~110 W a stack the chip grows to ~3.2 kW and
  the facility to more megawatts than the utilization saves. Memory power eats
  the gain. On-die stacked SRAM could restore the ratio without the HBM power;
  not quantified, not in the spec.
- **125 °C junction.** HBM caps at 85; the design's own analysis says junction
  temperature is worth 3% and leakage is the ceiling.
- **A lower-voltage "wide-and-slow" operating point.** Power goes as V²f, so
  holding a lower clock at lower voltage and adding silicon buys roughly 10%
  FLOPS per watt at the chip after leakage, HBM and SRAM-rail effects. Real,
  small, and an estimate — carried as a note, not in the numbers. Lower voltage
  also lowers the charge needed to flip a bit, which taxes goodput through more
  upsets. That coupling belongs in problem 7.
- **Stock Space-1 / Rubin as shipped.** HBM4 at 22 TB/s: fed ~0.60, utilization
  ~0.47. Fallback row below.

## Decisions on the facility side

- **Workload is training.** Slow cycles are acceptable: size to annual-mean
  availability (0.94 = 0.961 sunlit × 0.981 usable energy). A run that falls
  wholly inside the 88-day eclipse season takes ~78 days, at most once a year.
- **Light beats easy-to-build on structure.** Design at the near-term line
  (300 W/kg array, 3 kg/m² radiator); flown (85 W/kg, 14.2 kg/m²) is the
  fallback row. One structural bet entered twice: deploy and hold flat a
  ~160 m sheet at ~5 kg/m² all-in. Three modules also means a 5.5 MW wing,
  ~200× the largest flown. 300 W/kg has no array-level demonstration;
  2.9 kg/m² has one carbon-carbon demo.
- **Custom chip, with honest numbers.** The custom content (HBM4E, ECC, spares,
  domain layout) is worth 0.55 against ~0.47 stock — about 15% of mass. The
  large gains the shared chat first promised came from a 60 TB/s memory that
  does not exist and a clock factor that was bookkeeping.
- **No ride-through battery; a keep-alive one.** HBM is volatile, so a dark
  module loses weights and optimizer state. Memory keep-alive through a
  19.7-minute eclipse is ~100 kWh fleet-wide, under a tonne; or checkpoint
  the state to onboard flash every orbit (~3 min at 100 GB/s).
- **Radiator sized at the hot case with the Rubin stack.** Die flux 2,300 W over
  ~1,600 mm² (two reticle dies, estimate) = 1.44 W/mm², 1.67× the H100's 0.86;
  at a fixed boiling coefficient the 18.2 K stack becomes 30.4 K. Radiator at
  54.6 °C, net **813 W/m²** (vs 999 at 66.8 °C). Never shave it: an undersized
  radiator throttles, which costs chips, which costs radiator. Beyond the hot
  case, extra radiator buys nothing — a cooler chip does not compute faster.

## The facility it sizes

| | design (custom chip, near-term structure) | fallbacks |
|---|---|---|
| utilization | 0.55 | stock chip ~0.47 |
| sustained capacity needed | 63 EFLOPS | 74 EFLOPS |
| GPUs | 4,150 working, 4,360 with spares | ~5,100 |
| power, nameplate | **15.7 MW** (16.7 MW of heat) | 18.4 MW |
| radiator (813 W/m²) | 20,500 m² | 24,000 m² |
| array (2,417 m² per MW drawn) | 40,300 m² | 47,100 m² |
| mass | **232 t near-term** (array 58, radiator 61, compute 53, other 60) | 740 t flown; ~270 t stock chip |
| modules | **3 × 5.2 MW, ~77 t each** | 8 launches at flown structure |
| per module | 1,450 GPUs in 20 domains; disc 161 m, radiator the inner 93 m | |
| module memory | 558 TB — a full copy of ~35T parameters with training state at 16 B/param | |
| links | three modules, full mesh = ring, two laser terminals each; DiLoCo traffic ~15 Gbps per module (1T model, sync every 500 steps) | |
| energy per 60-day run | ~21 GWh | |

What changed from the previous version of this table (19.6 MW, 285 t): FLOPS
per chip 16.6 → 15.2 (dropped the clock factor, quoted sustained), power per
chip 4.6 → 3.4 kW (derived from the rack, dropped the terrestrial PUE). Nine
percent more chips, twenty percent less of everything else. Numbers are now
canon v6's, to the rounding shown.

## Still open

- **72-GPU copper domains against a 161 m disc.** 20 domains of 245 kW each
  (72 × 3.4 kW), ~300 m² of radiator apiece. Either the chips cluster and
  coolant crosses hinges (problem 14), or the in-module fabric goes optical
  (problem 12). The largest unresolved item.
- **800 V DC rack bus in LEO plasma.** Arcing from ~200–300 V; ISS runs 160 V
  with a plasma contactor. Problem 3, made harder by this chip.
- **CHF margin** for ammonia microchannels at 144 W/cm² — not pinned. Past it
  the wall dries out and Tj jumps. The pump remains the single-point-fatal item.
- **220 kW rack power** for Vera Rubin NVL72 — SemiAnalysis via the shared chat,
  unverified. Everything in the power column scales with it.
- **1T active / 30T tokens** is an assumption for closed frontier models.
- **Compute mass 3.36 kg/kW** (12 kg per GPU here) is inherited and underived.
- **Array wing at 5.5 MW per module is ~200× the largest flown** (SUNSTONE,
  28 kW). Fewer modules is what light and simple asked for; this is the price.
- **Heavy-lift to 650 km SSO at ~77 t per module** — assumed, not quoted.

## History, one line each

30 Sep: chip spec arrived from a shared chat (78e3d6a9); it forced f = 0 and
left the 100 MW design's areas and mass unchanged.
2 Oct: Ashley restated the metrics; benchmark replaced 100 MW; light beat
easy-to-build on structure. I sized at 40%, then 70% with clock 1.0, then a
0.60 hybrid, then 0.52 with clock 0.95 — four rows, each caught. Then the
60 TB/s memory turned out not to exist (8 × HBM4E = 29 TB/s), the clock factor
turned out to be bookkeeping (quote 15.2 PF sustained), and the 2.0× facility
power rule turned out to be an H100-on-Earth number (3.4 kW derived). Settled
at 0.55, 15.7 MW, 232 t, three modules; canon.py v6 rebuilt to print it.
