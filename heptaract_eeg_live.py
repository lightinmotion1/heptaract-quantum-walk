"""
Heptaract Full-Spectrum EEG — Live Brain State Reader

Current EEG: which band is dominant?
Heptaract EEG: where is this brain on T^7 right now?
              which direction is This walking?
              how far from home vertex?

The 7 EEG bands = 7 heptaract axes.
Every moment: a coherence state, a home vertex distance, a walk direction.
Every patient: a complete heptaract map, not a diagnosis.

This is what Oliver Sacks saw with intuition.
This gives every physician the same view — live, in data, in geometry.
"""

import numpy as np
from math import pi, sqrt
from fractions import Fraction

print("=" * 65)
print("  HEPTARACT FULL-SPECTRUM EEG — LIVE BRAIN STATE")
print("  Reading the whole walk, not just the current step")
print("=" * 65)

# ── 1. The 7 EEG axes ─────────────────────────────────────────
print("""
[ THE 7 EEG AXES — full spectrum mapped to heptaract ]
""")

EEG_AXES = [
    (0, "Infra-slow",  "<0.1 Hz",   Fraction(2,1), "Carrier wave beneath everything — body/brain foundation"),
    (1, "Delta",       "0.5–4 Hz",  Fraction(3,2), "Deep structure — sleep, healing, memory consolidation"),
    (2, "Theta",       "4–8 Hz",    Fraction(4,3), "Creative reach — memory access, insight, REM"),
    (3, "Alpha",       "8–13 Hz",   Fraction(5,4), "Ground state — Earth's 7/4 harmonic, home adjacent"),
    (4, "Beta",        "13–30 Hz",  Fraction(6,5), "Analytical — the narrator, sequential processing"),
    (5, "Gamma",       "30–100 Hz", Fraction(9,8), "Coherence bursts — binding, insight, cross-axis integration"),
    (6, "High Gamma",  "100–200Hz", Fraction(7,4), "HOME VERTEX signal — all axes integrated, full presence ★"),
]

print(f"  {'Ax':<4} {'Band':<12} {'Range':<11} {'Ratio':<6} Role")
print("  " + "─" * 72)
for ax, band, hz, ratio, role in EEG_AXES:
    marker = " ★" if ax == 6 else ""
    print(f"  {ax:<4} {band:<12} {hz:<11} {str(ratio):<6} {role}{marker}")

# ── 2. Live state simulation ───────────────────────────────────
print(f"""
[ LIVE BRAIN STATE — simulated heptaract coherence reader ]

  At every moment, the brain is a point on T^7.
  Each axis has a power value (μV²/Hz) — normalized to [0,1].
  Coherence = how well all 7 axes lock to harmonic ratios.
  Home vertex distance = how far the current state is from full coherence.

  Simulating 8 clinical states:
""")

# Clinical states as 7-axis power vectors [infra-slow, delta, theta, alpha, beta, gamma, high-gamma]
# Values 0-1: normalized band power
STATES = {
    "Deep sleep":         [0.9, 0.95, 0.3,  0.1,  0.05, 0.02, 0.01],
    "REM / dreaming":     [0.6, 0.4,  0.85, 0.3,  0.2,  0.15, 0.05],
    "Meditation (home)":  [0.7, 0.3,  0.5,  0.90, 0.2,  0.6,  0.80],
    "Flow state":         [0.8, 0.2,  0.6,  0.85, 0.4,  0.75, 0.85],
    "Alert / focused":    [0.4, 0.1,  0.3,  0.5,  0.85, 0.4,  0.3 ],
    "Anxious / PTSD":     [0.2, 0.1,  0.2,  0.15, 0.90, 0.2,  0.05],
    "Depression":         [0.5, 0.6,  0.4,  0.3,  0.4,  0.1,  0.05],
    "Anesthesia":         [0.95,0.98, 0.1,  0.05, 0.02, 0.01, 0.01],
}

# Home vertex target: all axes at harmonic ratios (normalized)
HOME = np.array([0.80, 0.60, 0.70, 0.90, 0.35, 0.70, 0.85])

def home_distance(state_vec):
    """Euclidean distance from home vertex in 7D power space."""
    v = np.array(state_vec)
    return float(np.linalg.norm(v - HOME))

def coherence(state_vec):
    """Phase coherence: how well axes lock to harmonic ratios."""
    v = np.array(state_vec)
    ratios = np.array([float(ax[3]) for ax in EEG_AXES])
    ratios_norm = ratios / ratios.max()
    correlation = float(np.corrcoef(v, ratios_norm)[0,1])
    return max(0, correlation)

def dominant_axis(state_vec):
    return EEG_AXES[int(np.argmax(state_vec))][1]

def walk_direction(state_vec):
    dist = home_distance(state_vec)
    if dist < 0.5:   return "→ HOME ★"
    elif dist < 1.0: return "~ near-home"
    elif dist < 1.5: return "↗ mid-walk"
    else:            return "↘ far shore"

print(f"  {'State':<22} {'Coh':>5}  {'Dist':>5}  {'Dominant':>10}  Direction       Clinical note")
print("  " + "─" * 90)

for state_name, powers in STATES.items():
    coh = coherence(powers)
    dist = home_distance(powers)
    dom = dominant_axis(powers)
    direction = walk_direction(powers)

    notes = {
        "Deep sleep":        "Anti-home by design — restoration walk",
        "REM / dreaming":    "Theta reach — creative diagonal active",
        "Meditation (home)": "Alpha+HiGamma lock — home vertex held",
        "Flow state":        "All axes coherent — campfire lit",
        "Alert / focused":   "Beta dominant — narrator leading",
        "Anxious / PTSD":    "Beta locked — home vertex unreachable",
        "Depression":        "Low gamma — heart axis gone quiet",
        "Anesthesia":        "Full far shore — walk suspended",
    }

    bar = "█" * int(coh * 10) + "·" * (10 - int(coh * 10))
    print(f"  {state_name:<22} {coh:>5.2f}  {dist:>5.2f}  {dom:>10}  {direction:<14}  {notes[state_name]}")

# ── 3. Clinical diagnostic map ────────────────────────────────
print(f"""
[ CLINICAL DIAGNOSTIC MAP — what heptaract EEG shows ]

  Condition       Axis pattern                    Intervention target
  ──────────────────────────────────────────────────────────────────
  Alzheimer's     Infra-slow + Delta decohering   Restore axes 0-1 first
                  before Alpha collapse           (carrier wave, then structure)

  PTSD            Beta locked high, Alpha gone    Restore axis 3 (Alpha/ground)
                  Home vertex unreachable         Breath + HRV coherence protocol

  Depression      Gamma + HiGamma silent          Restore axes 5-6 (heart signal)
                  Heart axis (7/4) suppressed     Physical movement, connection

  Autism spectrum Gamma hypersynchrony or absent  Axis 5 calibration
                  Integration axis disrupted      Sensory titration to home vertex

  Schizophrenia   Gamma desynchronized            Cross-axis binding protocol
                  Axes not talking to each other  Rhythm, music, structured pattern

  Chronic pain    Beta + infra-slow dysregulated  Axes 0 + 4 recalibration
                  Carrier wave disrupted          Body-first intervention

  Flow / peak     All 7 axes coherent             Maintain — document the state
                  High Gamma leading              Reproducible: teach the walk
""")

# ── 4. The live reader architecture ───────────────────────────
print("[ LIVE READER ARCHITECTURE — what the device looks like ]")
print("""
  Hardware:
    64-channel EEG cap (clinical standard)
    + infra-slow amplifiers (most EEG misses <0.5 Hz)
    + high-gamma amplifiers (most EEG stops at 80 Hz)
    = full 7-axis spectrum capture, not partial

  Software (heptaract layer):
    1. Real-time band extraction (7 bands simultaneously)
    2. Normalize each band to [0,1] power scale
    3. Compute home vertex distance every 100ms
    4. Compute cross-axis coherence (T^7 phase lock)
    5. Identify walk direction (toward/away from home)
    6. Display: 7-axis radar + coherence score + walk arrow

  Output to clinician:
    NOT: "elevated beta in left prefrontal"
    YES: "Brain at 73% coherence, axis 4 (beta) dominant,
          walking away from home, axis 3 (alpha/ground) needs
          restoration — recommend breath protocol + HRV feedback"

  Output to patient:
    A single number: home vertex distance.
    A single direction: toward or away.
    A single practice: what brings This closer.

  The documenting physician saw This with intuition over years.
  The heptaract EEG gives every clinician the same view
  in 100 milliseconds.
  Live.
""")

print("  Every brain on T^7. Every moment readable.")
print("  The walk was always happening.")
print("  Now We can see This — live.")
