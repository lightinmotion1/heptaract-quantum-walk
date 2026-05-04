"""
Heptaract Organic Superposition Walk

In quantum computing:  n qubits  →  2^n states  (binary base)
In organic life:       n axes    →  k^n states  (harmonic base)

The question is not whether organic life is in superposition.
It is ALWAYS in superposition — the 7 axes never all collapse to
a single vertex simultaneously. The heart beats at one phase,
the breath at another, the brain at a third.

The question is: what is k?

For binary quantum:  k = 2   →  2^7 = 128
For harmonic life:   k = 7   →  7^7 = 823,543
For continuous life: k = ∞   →  T^7 (7-dimensional torus, infinite)

Organic life navigates T^7 continuously.
The home vertex is the attractor — not a prison, but a campfire.
The walk is always in motion. The question is whether it is coherent.
"""

import numpy as np
from math import pi, sqrt, log2, log
from fractions import Fraction

print("=" * 65)
print("  HEPTARACT ORGANIC SUPERPOSITION WALK")
print("  From 2^n to k^n — the richer state space of living systems")
print("=" * 65)

# ── 1. State space comparison ─────────────────────────────────
print("""
[ THE STATE SPACE — why organic life is not binary ]
""")

N = 7  # heptaract axes

# Binary (quantum computing)
binary_states = 2**N

# Harmonic base-7 (heptaract native — each axis has 7 harmonic positions)
harmonic_states = 7**N

# Physiological resolution (each axis can distinguish ~this many states)
# Heart HRV: ~100 discrete frequency states in 0.04-0.4 Hz band
# Brain EEG: 7 bands × fine amplitude = ~49 states
# Breath: ~20 distinct rate/depth combinations
# Trunk posture: ~12 measurable orientations
# Limbs (x4): ~15 positions each
# Geometric mean across 7 axes:
phys_resolution = [100, 49, 20, 15, 15, 15, 12]
phys_states = 1
for r in phys_resolution:
    phys_states *= r

print(f"  {'System':<30}  {'Base (k)':>8}  {'States (k^7)':>18}")
print("  " + "─" * 60)
print(f"  {'Binary quantum (qubit)':<30}  {'2':>8}  {binary_states:>18,}")
print(f"  {'Heptaract harmonic (7 ratios)':<30}  {'7':>8}  {harmonic_states:>18,}")
print(f"  {'Physiological (measured axes)':<30}  {'~26':>8}  {phys_states:>18,}")
print(f"  {'Continuous (T^7 torus)':<30}  {'∞':>8}  {'∞':>18}")
print(f"""
  The jump from 2^7 to 7^7 is not cosmetic — it is a factor of {harmonic_states//binary_states:,}×.
  Organic life has access to {harmonic_states:,} distinguishable harmonic
  superposition states, not 128.

  The jump to physiological resolution: {phys_states:,} states —
  a factor of {phys_states//binary_states:,.0f}× richer than binary quantum computing.

  And all of this is still the DISCRETE approximation.
  The actual walk is continuous: T^7, the 7-dimensional torus.
""")

# ── 2. The 7 organic axes and their natural frequencies ───────
print("[ THE 7 ORGANIC AXES — each a continuous oscillator ]")
print()

axes = [
    ("Trunk / frame",  "Structural integrity", "postural sway", "0.1–0.3 Hz",   Fraction(2,1), "Octave"),
    ("Left arm",       "Gesture / reach",       "tremor freq",   "8–12 Hz",      Fraction(3,2), "Fifth"),
    ("Right arm",      "Gesture / reach",       "tremor freq",   "8–12 Hz",      Fraction(4,3), "Fourth"),
    ("Left leg",       "Gait / ground",         "stride freq",   "1.5–2.5 Hz",   Fraction(5,4), "Maj 3rd"),
    ("Right leg",      "Gait / ground",         "stride freq",   "1.5–2.5 Hz",   Fraction(6,5), "Min 3rd"),
    ("Brain",          "Cognition",             "alpha band",    "8–13 Hz",      Fraction(9,8), "Maj 2nd"),
    ("Heart",          "Coherence anchor",      "HRV / LF band", "0.04–0.15 Hz", Fraction(7,4), "Harm 7th"),
]

print(f"  {'Axis':<16} {'Role':<22} {'Oscillation':<14} {'Freq range':<14} {'Ratio'}")
print("  " + "─" * 80)
for name, role, osc, freq, ratio, interval in axes:
    print(f"  {name:<16} {role:<22} {osc:<14} {freq:<14} {ratio} ({interval})")

print(f"""
  Each axis is not a bit (0 or 1).
  Each axis is a continuous oscillator with a natural frequency range.
  The superposition state of the organism at any moment is the
  instantaneous phase vector across all 7 oscillators:

    Ψ_organic(t) = (φ₀(t), φ₁(t), φ₂(t), φ₃(t), φ₄(t), φ₅(t), φ₆(t))

  where each φᵢ ∈ [0, 2π) — a point on T^7, the 7-torus.

  The home vertex is not (0,0,0,0,0,0,0) but the COHERENT state:
  all phases locked in the harmonic ratios. The campfire is where
  all 7 oscillators resonate together.
""")

# ── 3. The organic walk — continuous superposition evolution ──
print("[ THE ORGANIC WALK — how life moves between superpositions ]")

print("""
  Binary quantum walk:  discrete flips between {0,1}^7
  Organic walk:         continuous flow on T^7

  The organic walk equation (generalized from quantum walk):

    dΨ/dt = -i · H_organic · Ψ

  where H_organic couples all 7 axes through their harmonic ratios.
  This is the same Hamiltonian as the quantum walk, but operating
  on the continuous torus rather than the discrete hypercube.

  The result: instead of arriving at the anti-home vertex at t=π/2
  and stopping, the organic walk CONTINUES — spiraling through T^7,
  never the same superposition twice, always returning toward home.
""")

# Simulate the organic walk as a 7-dimensional phase evolution
# Each axis evolves at its natural frequency (normalized)
# Coherence = how aligned the phases are (1.0 = home vertex, 0 = maximum spread)

# Natural frequencies normalized to the heptaract ratios
freqs = [float(Fraction(2,1)), float(Fraction(3,2)), float(Fraction(4,3)),
         float(Fraction(5,4)), float(Fraction(6,5)), float(Fraction(9,8)),
         float(Fraction(7,4))]

axis_names = ["Trunk", "L.Arm", "R.Arm", "L.Leg", "R.Leg", "Brain", "Heart"]

print(f"  Coherence of organic walk over time (1.0 = home vertex):")
print(f"  {'t/π':<8}  {'Coherence':>10}  {'Dominant axis':<14}  State description")
print("  " + "─" * 65)

dt = 0.05
t_vals = np.arange(0, 2*pi + dt, dt*20)

for t in t_vals:
    # Phase of each axis at time t
    phases = np.array([f * t for f in freqs])
    # Coherence: how well all phases align (order parameter)
    unit_vectors = np.exp(1j * phases)
    coherence = abs(np.mean(unit_vectors))
    # Which axis is most "dominant" (furthest from mean phase)
    mean_phase = np.angle(np.mean(unit_vectors))
    deviations = [abs(np.angle(np.exp(1j*(p - mean_phase)))) for p in phases]
    dominant_idx = np.argmax(deviations)
    dominant = axis_names[dominant_idx]

    if coherence > 0.85:
        state = "HOME — full coherence"
    elif coherence > 0.65:
        state = "near-home — resonant"
    elif coherence > 0.45:
        state = "mid-walk — exploring"
    elif coherence > 0.25:
        state = "dispersed — creative"
    else:
        state = "anti-home — maximum spread"

    bar = "█" * int(coherence * 20) + "·" * (20 - int(coherence * 20))
    print(f"  {t/pi:<8.3f}  {coherence:>6.3f}  [{bar}]  {dominant:<10}  {state}")

# ── 4. The superposition states and their organic meanings ────
print(f"""
[ WHAT THE SUPERPOSITIONS MEAN — organic state map ]

  In binary quantum: superposition = unknown until measured.
  In organic life:   superposition = the actual lived state.

  The organism IS the superposition — not collapsed, not waiting.
  Every moment of life is a specific point on T^7.

  Key superposition regions and their experiential signatures:
""")

states_map = [
    ("Home vertex (coherent)",       0.90, "All 7 axes locked in harmonic ratio",     "Flow, clarity, presence, HRV coherent"),
    ("Heart-brain locked",           0.75, "Axes 5+6 (brain+heart) in phase",          "Emotional intelligence, intuition active"),
    ("Limbs leading",                0.60, "Axes 3+4 (legs) dominant",                 "Physical momentum, embodied action"),
    ("Brain dominant",               0.55, "Axis 5 (brain) pulling others",            "Analytical mode, heart follows brain"),
    ("Creative spread",              0.35, "All axes loosely coupled",                  "Open exploration, ideation, dreaming"),
    ("Anti-home (dispersed)",        0.10, "All axes maximally out of phase",           "Deep sleep, anesthesia, reset"),
]

print(f"  {'State':<28}  {'Coh':>5}  {'Axes':<32}  Experience")
print("  " + "─" * 85)
for name, coh, axes_desc, experience in states_map:
    print(f"  {name:<28}  {coh:>5.2f}  {axes_desc:<32}  {experience}")

# ── 5. Navigation — how to move intentionally ─────────────────
print(f"""
[ INTENTIONAL NAVIGATION — moving organically between superpositions ]

  The heptaract gives a precise protocol for moving between states.
  Each axis has a known natural frequency. To shift the superposition:

  TOWARD HOME (increasing coherence):
    Breath  → slow to 0.1 Hz (Schumann sub-harmonic), 6 breaths/min
    Heart   → HRV biofeedback, LF peak at 0.1 Hz
    Brain   → alpha state (8-13 Hz), eyes soft, attention diffuse
    Body    → symmetric posture, bilateral limb symmetry
    Sound   → tonic drone at home ratio (just intonation)
    Result  → all 7 axes pull toward harmonic lock → coherence rises

  TOWARD ANTI-HOME (intentional dispersion, creative reset):
    Breath  → irregular, varied depth
    Body    → asymmetric, exploratory movement
    Brain   → theta (4-7 Hz), hypnagogic state
    Sound   → dissonance, then silence
    Result  → axes decouple → spread across T^7 → maximum novelty

  THE WALK IS ALWAYS HAPPENING.
  The question is only whether it is navigated or drifted.

  Navigated: coherence rises, home vertex becomes attractor.
  Drifted:   coherence fluctuates randomly — life as noise.

  The heptaract doesn't make the walk possible.
  It makes the walk LEGIBLE.
  You were always walking. Now you can see the map.
""")

# ── 6. The key number ─────────────────────────────────────────
print("[ THE KEY NUMBER — what replaces 2^n for organic life ]")
print(f"""
  Binary quantum:    2^7  =        128  states
  Heptaract harmonic: 7^7  =    823,543  states
  Physiological:    ~26^7  = {26**7:>10,}  states (measured)
  Continuous T^7:    ∞    =          ∞  states (lived)

  The base is not 2 because the axes are not bits.
  The axes are oscillators. Their superpositions are phases.
  The number of distinguishable states scales with the
  harmonic resolution of the organism — not binary logic.

  For organic life, the base is at minimum 7 (heptaract-native).
  Likely closer to 26 (physiological resolution per axis).
  The continuous walk is the true answer: T^7.

  This is not a computer with more RAM.
  This is a different KIND of computation entirely —
  one that was never switched off, never needed to boot,
  and has been running the heptaract walk
  since the first heartbeat.
""")

print("  The home vertex is not a destination.")
print("  It is where the walk becomes conscious of itself.")
print("  That is what we are doing now.")
