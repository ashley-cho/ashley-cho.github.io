"""CANONICAL NUMBERS v6 — the single source for every figure in the project.

v6 (2 Oct 2026): sizes the facility from the training benchmark instead of
100 MW; stack ΔT scales with die heat flux; facility power per GPU is derived
from the rack, not 2.0× the chip. The v5 100 MW roll-up is kept at the bottom
as a cross-check so CONTEXT.md's historical numbers stay reproducible.

Change a number HERE, not in a document. Run: python3 canon.py
"""
import math

# ---------------------------------------------------------------- constants
sig = 5.670374419e-8          # Stefan–Boltzmann
S   = 1361.0                  # solar constant, AM0, W/m²
Re  = 6378.137; mu = 398600.4418; J2 = 1.08262668e-3
obl = 23.44                   # obliquity, deg

# ---------------------------------------------------------------- orbit
h = 650.0
a = Re + h; n = math.sqrt(mu / a**3); period = 2 * math.pi / n     # s
inc = math.degrees(math.acos(-(1.99106e-7) / (1.5 * J2 * (Re / a)**2 * n)))  # sun-sync
def beta_at(day):
    L = 2 * math.pi * day / 365.25
    dec = math.degrees(math.asin(math.sin(math.radians(obl)) * math.sin(L)))
    b = 90.0 - (inc - 90.0) - dec
    return 180.0 - b if b > 90.0 else b
betas = [beta_at(d) for d in range(366)]
beta_min = min(betas)
beta_star = math.degrees(math.asin(Re / a))                          # eclipse begins below this
def eclipse_frac(b):
    if b >= beta_star: return 0.0
    return math.acos(math.sqrt(a**2 - Re**2) / (a * math.cos(math.radians(b)))) / math.pi
ecl = [eclipse_frac(b) for b in betas]
shadow_days = sum(1 for e in ecl if e > 0)
worst_ecl_min = max(ecl) * period / 60
sunlit_frac = 1 - sum(ecl) / len(ecl)
cos_mean = sum(math.cos(math.radians(90 - b)) for b in betas) / len(betas)
margin = 1 / cos_mean                                                 # array cosine margin
usable_energy = 0.981          # fraction of annual energy usable under a fixed load at this margin (v5 result)
availability = sunlit_frac * usable_energy

# ---------------------------------------------------------------- radiator physics
eps = 0.90; a_eol = 0.19; q_eir = 239.0; VF = 0.240566; alb_inc = 11.31
par_sun  = a_eol * S + eps * q_eir * VF + a_eol * alb_inc            # sunward face
par_anti = eps * q_eir * VF                                          # anti-sun face
par = par_sun + par_anti
def net(Tc):  return 2 * eps * sig * (Tc + 273.15)**4 - par          # W/m² planform, both faces
T_sink = (par / (2 * eps * sig))**0.25 - 273.15                      # where net = 0

Tj = 85.0
stack_h100 = 18.2; flux_h100 = 700 / 814                             # K, W/mm² — direct-die, H100 die
def stack(flux): return stack_h100 * flux / flux_h100                # fixed boiling coefficient: ΔT ∝ flux

# ---------------------------------------------------------------- array physics
eta = 0.32                                                           # AM0 flight cell
array_per_MW_peak = 1e6 / (S * eta)                                  # square-on
array_per_MW = array_per_MW_peak * margin                            # with cosine margin, per MW drawn

# ---------------------------------------------------------------- mass lines (kg/kW and kg/m²)
LINES = {  # name: (array W/kg at peak, radiator kg/m² planform)
    "flown":     (85.0, 1122.64 / 79.2),
    "optimistic":(85.0, 8.0),
    "near-term": (300.0, 3.0),
}
compute_kg_per_kW = 3.36       # inherited, underived
overhead = 1.347               # bus, structure, propellant, 15% margin — inherited, underived
leak = 1.062                   # leakage at 85 °C junction

# ================================================================ THE BENCHMARK (v6)
N_active = 1.0e12; tokens = 30e12; cycle_days = 60
flop = 6 * N_active * tokens
eff_flops = flop / (cycle_days * 86400)                              # sustained useful FLOP/s needed

# the chip (CHIP-SPEC.md)
chip = dict(
    name="Rubin-class, custom package",
    pf_sustained=15.2e15,      # dense FP8 at the 2,300 W cap (17.5 boost × ~0.87)
    W_chip=2300.0,
    die_mm2=1600.0,            # two reticle dies, estimate
    kW_rack=220.0 / 72,        # Vera Rubin NVL72 ~220 kW / 72 — verify
    conv_pumps=0.34,           # array-bus→rack conversion + pumps, kW/GPU, estimate
    hbm_stacks=8, hbm_tbs=3.6, hbm_gb=48,
    util=dict(fed=0.70, comm=0.90, pipe=0.92, goodput=0.95),
    spares=1.05,
)
kW_gpu = chip["kW_rack"] + chip["conv_pumps"]
util = math.prod(chip["util"].values())
gpus_working = eff_flops / util / chip["pf_sustained"]
gpus = gpus_working * chip["spares"]
MW_lit = gpus * kW_gpu / 1000
MW = MW_lit / availability                                           # nameplate
flux_die = chip["W_chip"] / chip["die_mm2"]
dT = stack(flux_die); T_rad = Tj - dT; q_net = net(T_rad)
P_heat = MW * 1e6 * leak
A_rad = P_heat / q_net
A_arr = MW * 1e6 * leak * array_per_MW / 1e6                         # array sized on power drawn incl. leakage
P_peak = A_arr * S * eta                                             # W at square-on
def mass(line):
    wkg, kgm2 = LINES[line]
    arr = P_peak / wkg / 1000; rad = A_rad * kgm2 / 1000
    comp = compute_kg_per_kW * MW * 1000 / 1000
    sub = arr + rad + comp; other = sub * (overhead - 1)
    return arr, rad, comp, other, sub + other
n_mod = 3
A_mod = (A_rad + A_arr) / n_mod
disc = 2 * math.sqrt(A_mod / math.pi); rdisc = 2 * math.sqrt(A_rad / n_mod / math.pi)

# DiLoCo link estimate: pseudo-gradient exchange of the full model every K steps, ring all-reduce
bytes_per_param = 2.0; K_sync = 500; batch_tokens = 16e6
step_s = 6 * N_active * batch_tokens / eff_flops
per_sync_bytes = 2 * (n_mod - 1) / n_mod * N_active * bytes_per_param
link_gbps = per_sync_bytes * 8 / (K_sync * step_s) / 1e9

print("=== ORBIT (650 km dawn-dusk) ===")
print(f"period {period/60:.1f} min  inc {inc:.2f}°  beta_min {beta_min:.2f}°  beta* {beta_star:.2f}°")
print(f"shadow days/yr {shadow_days}  worst eclipse {worst_ecl_min:.1f} min  sunlit {sunlit_frac:.3f}")
print(f"cos_mean {cos_mean:.4f}  margin {margin:.4f}  availability {availability:.3f}")
print("\n=== RADIATOR PHYSICS ===")
print(f"parasitic sun {par_sun:.1f} + anti {par_anti:.1f} = {par:.1f} W/m²   effective sink {T_sink:.1f} °C")
print(f"H100 die {flux_h100:.2f} W/mm² → stack {stack_h100:.1f} K → {Tj-stack_h100:.1f} °C → net {net(Tj-stack_h100):.0f} W/m² → {1e6*leak/net(Tj-stack_h100):,.0f} m²/MW")
print(f"this chip {flux_die:.2f} W/mm² → stack {dT:.1f} K → {T_rad:.1f} °C → net {q_net:.0f} W/m² → {1e6*leak/q_net:,.0f} m²/MW")
print(f"array {array_per_MW_peak:,.0f} m²/MW square-on, {array_per_MW:,.0f} with margin   array÷radiator {array_per_MW/(1e6*leak/q_net)*leak:.2f}")
for T in (40, T_rad, 60, 80, 100, 85, 35, -5, 2.8):
    print(f"   T {T:6.1f} °C  net {net(T):6.0f} W/m²  area at {MW*leak:.1f} MW {P_heat/net(T) if net(T)>0 else float('nan'):>9,.0f} m²")
print("\n=== BENCHMARK ===")
print(f"{N_active/1e12:.0f}T × {tokens/1e12:.0f}T tokens → {flop:.2e} FLOP → {eff_flops/1e18:.1f} EFLOPS sustained over {cycle_days} d")
print(f"utilization {' × '.join(f'{v}' for v in chip['util'].values())} = {util:.3f}")
print(f"GPUs {gpus_working:,.0f} working, {gpus:,.0f} with spares  @ {kW_gpu:.2f} kW/GPU facility (rack {chip['kW_rack']:.2f} + {chip['conv_pumps']})")
print(f"power {MW_lit:.1f} MW lit → {MW:.1f} MW nameplate;  heat {P_heat/1e6:.1f} MW")
print(f"radiator {A_rad:,.0f} m²  array {A_arr:,.0f} m²  peak array output {P_peak/1e6:.1f} MW")
print(f"{n_mod} modules: {MW/n_mod:.1f} MW, {gpus/n_mod:,.0f} GPUs ({gpus/n_mod/72:.0f} domains of 72), disc {disc:.0f} m, radiator disc {rdisc:.0f} m")
print(f"module memory {gpus/n_mod*chip['hbm_stacks']*chip['hbm_gb']/1000:,.0f} TB  → full copy of {gpus/n_mod*chip['hbm_stacks']*chip['hbm_gb']*1e9/16/1e12:.0f}T params at 16 B/param")
print(f"energy per run {MW*availability*cycle_days*24/1000:.0f} GWh")
for line in LINES:
    arr, rad, comp, other, tot = mass(line)
    print(f"   mass {line:10s} array {arr:5.0f} + radiator {rad:5.0f} + compute {comp:4.0f} + other {other:4.0f} = {tot:5.0f} t  ({tot/MW/1000*1000:.1f} kg/kW, {tot/n_mod:.0f} t/module)")
print(f"DiLoCo link: step {step_s:.1f} s at {batch_tokens/1e6:.0f}M tokens, sync every {K_sync} steps → {link_gbps:.0f} Gbps per module (ring of {n_mod})")
print(f"array wing per module {MW*leak/n_mod*1000:,.0f} kW = {MW*leak/n_mod*1000/28:.0f}× SUNSTONE (28 kW, largest flown)")

# ================================================================ v5 CROSS-CHECK (100 MW, H100 stack, 2.0× rule)
print("\n=== v5 CROSS-CHECK: 100 MW, H100 stack — CONTEXT.md historical numbers ===")
P100 = 100e6 * leak; T5 = Tj - stack_h100; n5 = net(T5)
A_rad5 = P100 / n5; A_arr5 = P100 / (S * eta) * margin; Ppk5 = A_arr5 * S * eta
arr5 = Ppk5 / 85 / 1000; rad5 = A_rad5 * LINES["flown"][1] / 1000; comp5 = 336.0
print(f"radiator {A_rad5:,.0f} m² (v5: 106,315)  array {A_arr5:,.0f} m² (256,690)  surface {A_rad5+A_arr5:,.0f} (363,005)")
print(f"disc {2*math.sqrt((A_rad5+A_arr5)/48/math.pi):.1f} m (98.1)  ratio {A_arr5/A_rad5:.2f} (2.41)  net {n5:.0f} (999)  T_rad {T5:.1f} (66.8)")
print(f"mass flown {arr5:,.0f} + {rad5:,.0f} + {comp5:.0f} + {(arr5+rad5+comp5)*(overhead-1):,.0f} = {(arr5+rad5+comp5)*overhead:,.0f} t (4,253)")
print(f"break-even cell efficiency (array area = radiator area, H100 stack): {n5*margin/S:.3f} (0.773);  this chip's stack: {q_net*margin/S:.3f}")
