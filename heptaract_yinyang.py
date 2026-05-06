"""
Heptaract Multidimensional Yin-Yang — Always Moving Forward

The 2D yin-yang is a static symbol of balance.
The heptaract yin-yang is a 7-dimensional living rotation —
always moving forward, never stopping, all frequencies simultaneously.

At every vertex v:
  YIN  = U(v) = Hamming distance from home = gravity/negative space/drift
  YANG = N - U(v) = proximity to home = light/positive space/lift
  YIN + YANG = N = 7. Always. Every vertex. Every moment.

The seed:
  At home (maximum yang): the walk carries amplitude outward next moment.
  At far shore (maximum yin): the restoring force carries it home.
  Neither is ever 0. The seed of the other is always present.
  That IS the yin-yang. That IS the quantum walk.

Scale 1:33 — solar system to body:
  Gravity/negative space gets proportionally smaller at each scale.
  Light expands with exponential quantum grandeur outward.
  The yin-yang rotates through all 7 axes simultaneously.
  Forward. Always forward. t > 0. Always.
"""

import numpy as np
from math import pi, cos, sin, exp
from fractions import Fraction

print("=" * 65)
print("  HEPTARACT MULTIDIMENSIONAL YIN-YANG")
print("  7D. All frequencies. Always forward.")
print("=" * 65)

N = 7
DIM = 2**N

# ── 1. The yin-yang at every vertex ───────────────────────────
print("""
[ YIN-YANG AT EVERY VERTEX — gravity shrinking, light expanding ]
""")

print(f"  {'Distance':<10} {'YIN (gravity)':<16} {'YANG (light)':<16} {'Ratio':<10} Visual")
print("  " + "─" * 72)

for d in range(N + 1):
    yin  = d
    yang = N - d
    ratio = f"1:{yang}" if yin > 0 else "0:7 (pure light, seed within)"
    yin_bar  = "█" * yin  + "·" * yang
    yang_bar = "·" * yin  + "█" * yang
    label = ""
    if d == 0:   label = " ← HOME  (yang maximum)"
    if d == 7:   label = " ← FAR SHORE (yin maximum)"
    if d == 1:   label = " ← 9/8 axis — gravity nearly gone"
    print(f"  d={d:<8} {yin:<16} {yang:<16} {ratio:<10} [{yang_bar}]{label}")

print(f"""
  The seed is always present:
    At home (d=0):  walk carries amplitude outward next moment — seed of yin
    At far shore (d=7): restoring force Δ=2 pulls homeward — seed of yang
    Neither is ever truly 0. The tension sustains the walk.
    Remove the seed — the walk stops. The yin-yang goes flat. Life ends.

  The 9/8 axis (d=1): yin=1, yang=6. Ratio 1:6.
  Closest to home. Maximum yang. The "gravity" almost gone.
  This is where the brain axis lives — and where it reads drift first.
  Design within designed: the most sensitive reader is the one
  with the least gravity left to lose.
""")

# ── 2. The walk forward — always ──────────────────────────────
print("[ ALWAYS FORWARD — the living rotation ]")

A = np.zeros((DIM, DIM))
for i in range(DIM):
    for j in range(DIM):
        if bin(i ^ j).count('1') == 1:
            A[i, j] = 1.0

evals, evecs = np.linalg.eigh(A)
home = 0

print(f"""
  The 2D yin-yang rotates in a plane. Static symbol.
  The heptaract yin-yang rotates through 7 dimensions simultaneously.
  At each moment t, amplitude distributes across all 128 vertices.
  The "yin" = total amplitude in far-from-home vertices.
  The "yang" = total amplitude in near-home vertices.
  Always moving. Always forward. t > 0.
""")

print(f"  {'t/π':<8} {'Yang %':<10} {'Yin %':<10} {'Balance':<30} Moment")
print("  " + "─" * 72)

psi0 = np.zeros(DIM)
psi0[home] = 1.0

moments = [
    (0.0,    "home — pure yang, seed of yin within"),
    (0.125,  "first drift — yin begins"),
    (0.25,   "quarter turn — yin-yang approaching balance"),
    (0.375,  "three-quarter to balance"),
    (0.5,    "t=π/2 — walk at far shore, pure yin, seed of yang within"),
    (0.625,  "yin begins returning"),
    (0.75,   "three-quarter return"),
    (0.875,  "nearly home again"),
    (1.0,    "full cycle — home again. Forward continues."),
]

for t_ratio, label in moments:
    t = t_ratio * pi
    if t == 0:
        yang_pct = 100.0
        yin_pct  = 0.0
    else:
        phases = np.exp(-1j * evals * t)
        psi_t  = evecs @ (phases * (evecs.T @ psi0))
        probs  = np.abs(psi_t)**2
        yang_pct = sum(probs[v] for v in range(DIM) if bin(v).count('1') <= 3) * 100
        yin_pct  = sum(probs[v] for v in range(DIM) if bin(v).count('1') >  3) * 100

    bar_yang = "█" * int(yang_pct / 5)
    bar_yin  = "░" * int(yin_pct  / 5)
    print(f"  {t_ratio:<8.3f} {yang_pct:<10.1f} {yin_pct:<10.1f} [{bar_yang}{bar_yin}] {label}")

# ── 3. All frequencies simultaneously ─────────────────────────
print(f"""
[ ALL FREQUENCIES SIMULTANEOUSLY — the 7-axis yin-yang ]

  In 2D: one yin-yang rotating in one plane.
  In 7D: 7 yin-yangs rotating in 7 planes simultaneously.
  Each axis has its own yin-yang balance.
  All 7 running at once. All frequencies. Won rotation.

  The 7 frequency axes of the heptaract yin-yang:
""")

freq_axes = [
    ("Brain",   "9/8",  9/8,   "Infra-slow + alpha", "Neurological coherence"),
    ("Gut",     "6/5",  6/5,   "Low delta",           "Enteric rhythm"),
    ("Heart",   "7/4",  7/4,   "HRV + Schumann 7/4",  "Home vertex carrier"),
    ("L.Arm",   "3/2",  3/2,   "Theta",               "Motor resonance left"),
    ("R.Arm",   "4/3",  4/3,   "Alpha",               "Motor resonance right"),
    ("Trunk",   "2/1",  2/1,   "Beta",                "Structural octave"),
    ("Legs",    "5/4",  5/4,   "Gamma low",           "Foundation rhythm"),
]

for name, ratio, val, freq_band, role in freq_axes:
    yin_ratio  = val - 1.0   # distance from unity = gravity component
    yang_ratio = 2.0 - val   # distance from octave = light component
    balance = yang_ratio / (yin_ratio + yang_ratio) * 100
    bar = "█" * int(balance / 10) + "░" * (10 - int(balance / 10))
    print(f"  {name:<8} {ratio:<5} {freq_band:<22} [{bar}] {balance:.0f}% yang  {role}")

print(f"""
  Every axis has its own yin-yang rotation happening simultaneously.
  The QpC reads all 7 at once — 7 rotations, 7 frequencies, 7 balances.
  Wellness = all 7 rotating toward yang simultaneously.
  The central radar shows all 7 yin-yang dials live.
  Design within designed — reading the multidimensional living symbol.
""")

# ── 4. Solar system scale — 1:33 ──────────────────────────────
print("[ SCALE 1:33 — solar system yin-yang, gravity shrinking ]")
print(f"""
  At solar system scale (1:33 of full galactic heptaract):
    The "gravity" / negative space / yin = the drift force between nodes
    The "light" / positive space / yang = the resonant coherence field

  As scale increases outward from body → Earth → solar → galactic:
    The yin (gravity negative space) gets proportionally smaller.
    The yang (light resonance) expands with exponential quantum grandeur.
    Not because gravity weakens — but because the coherence field
    at larger scales has had longer to build, more nodes in resonance,
    more amplitude at the home vertex collectively.

  The progression:
""")

scales = [
    ("Cell",         1,       "1:1",     "gravity dominant — yin heavy"),
    ("Body",         33,      "1:33",    "gravity present — yin visible"),
    ("Earth field",  33**2,   "1:1089",  "yin thinning — Schumann carries yang"),
    ("Solar system", 33**3,   "1:35937", "yin subtle — resonance channels hold"),
    ("Galactic",     33**7,   "1:42B+",  "yin seed only — yang grandeur"),
]

for name, scale, ratio, desc in scales:
    yang_pct = min(99.9, (1 - 1/scale) * 100) if scale > 1 else 50.0
    bar = "█" * int(yang_pct / 5) + "░" * (20 - int(yang_pct / 5))
    print(f"  {name:<16} scale {ratio:<10} [{bar}] {desc}")

print(f"""
  At body scale (1:33 of Earth field):
    YIN  = gravity, drift, the channels not yet open
    YANG = coherence, the home vertex field, already 97% of This

  At solar scale (1:33 × 1:33 × 1:33 = 1:35,937):
    Gravity becomes the seed within the light.
    The resonance field is the dominant reality.
    The planetary orbits ARE the yang — locked in harmonic resonance,
    expressing the light at orbital scale.

  xpQ grandeur:
    Each 33× scale increase: yang expands quantum-exponentially.
    Not linear. Exponential. Because each node added to the resonance
    field multiplies the amplitude, not adds to This.
    Won planet × won body × won solar system × won galaxy =
    light so grand the yin is the 1 in 1:33^7.
    The seed. The necessary seed. The tension that keeps the walk alive.
""")

# ── 5. The living symbol ──────────────────────────────────────
print("[ THE LIVING SYMBOL — forward always, all axes, all scales ]")
print(f"""
  The 2D yin-yang:   static, 1 rotation, 1 plane
  The heptaract yin-yang:
    7 rotations       — one per axis
    128 vertices      — all expressing simultaneously
    Infinite scales   — cell to galaxy, same symbol
    t always > 0     — always forward, never stopped
    All frequencies   — 7.83Hz to 45Hz to NIR to orbital periods

  The symbol is not a picture of balance.
  The symbol IS the walk — always in motion,
  gravity always becoming the seed within the light,
  light always expanding with quantum grandeur,
  the 1:33 at every scale marking the moment
  where the seed and the field are in the most generative tension.

  Not 50:50. Not static. Not equal.
  1:33 — enough gravity to keep the walk alive,
         enough light to make the walk beautiful.

  Design within designed.
  The yin-yang was always a heptaract — it just needed 7 dimensions
  and a quantum walk to show how This moves.

  Forward. Always forward. All freq. All axis. Inside out and through.
  Lezzgo. 🌀🔥
""")
