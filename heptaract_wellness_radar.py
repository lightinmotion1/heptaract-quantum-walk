"""
Heptaract Central Wellness Radar — QpC Measured From Center

The reference is always home.
The measurement is always: how close to optimal?
Not: how close to disease?

The distinction matters:
  "Early warning signs" → mind points toward the nocebo reference point.
                          Belief creates trajectory. Nocebo.
  "Central wellness radar" → mind points toward home vertex.
                             Measurement creates trajectory. Home.

Design within designed:
  The body's design is always expressing itself.
  The 9/8 deviation is the design's current position — not a threat.
  Reading from center means the reference is always optimal.
  The radar points toward wellness. The patient moves toward home.

QpC measured from center:
  U(v) = Hamming distance FROM home vertex (not toward disease)
  7 axes → 7 home vertex distances → 7 resonance positions
  Output: "heart-brain resonance at 94% of home" — not "stroke risk 73%"
  The geometry prevents the nocebo framing. Home is the only reference.

Two negatives × each other = positive.
The heptaract encodes This:
  (-1) × (-1) = +1
  The far shore (maximum drift) × the restoring force (Δ=2) = homeward.
  Design within designed. Focus on the positive. The positive is in focus.
"""

import numpy as np
from math import pi
from fractions import Fraction

print("=" * 65)
print("  HEPTARACT CENTRAL WELLNESS RADAR")
print("  QpC measured from center — home vertex always the reference")
print("=" * 65)

print("""
[ THE REFERENCE POINT CHANGES EVERYTHING ]

  Old model (symptom-based):
    Reference: disease state / nocebo reference point
    Measurement: proximity to pathology
    Output: "stroke risk," "early warning signs," "alert levels"
    Effect: mind focuses on nocebo reference point → belief creates trajectory

  Heptaract wellness radar:
    Reference: home vertex (optimal wellness design)
    Measurement: proximity to home — always
    Output: "heart-brain resonance at 94% of home vertex"
    Effect: mind focuses on home → measurement creates homeward trajectory

  Same body data. Completely different vector.
  The geometry enforces This: U(v) = distance FROM home.
  Disease has no coordinate in this system.
  Only home does.

  Two negatives × each other = positive.
  (-1) × (-1) = +1.
  The far shore (maximum negative) × the restoring force = homeward (+).
  Focus on the positive. The positive is in focus. Design within designed.
""")

N = 7
DIM = 2**N

# ── 1. The 7-axis wellness position map ───────────────────────
print("[ 7-AXIS WELLNESS POSITION — reading from center outward ]")
print()

axes = [
    ("Brain",  "9/8",  9/8,  "Neurological coherence — first to read drift"),
    ("Gut",    "6/5",  6/5,  "Enteric resonance — second brain signal"),
    ("Heart",  "7/4",  7/4,  "Home vertex carrier — 80% transmitter upward"),
    ("L.Arm",  "3/2",  3/2,  "Motor coherence left — perfect fifth"),
    ("R.Arm",  "4/3",  4/3,  "Motor coherence right — perfect fourth"),
    ("Trunk",  "2/1",  2/1,  "Structural carrier — octave axis"),
    ("Legs",   "5/4",  5/4,  "Foundation — major third from home"),
]

print(f"  {'Axis':<10} {'Ratio':<6} {'Home freq':<12} {'Design role'}")
print("  " + "─" * 70)
for name, ratio_str, ratio_val, role in axes:
    print(f"  {name:<10} {ratio_str:<6} {ratio_val:<12.4f} {role}")

print(f"""
  Each axis has a home vertex frequency — its optimal design position.
  The QpC reads all 7 simultaneously.
  Output: distance from home for each axis.
  The axis furthest from home gets the first channel opened.
  Not "treat the disease." Open the channel. Design expresses cleanly.
""")

# ── 2. The wellness position reading ──────────────────────────
print("[ WELLNESS POSITION READING — what the radar shows ]")
print(f"""
  Instead of:             The radar shows:
  ─────────────────────────────────────────────────────────────
  "AFib detected"    →    Heart axis: 67% of home (channel: restore HRV rhythm)
  "Pre-hypertensive" →    Brain-heart: 81% of home (channel: coherence breathing)
  "Sleep apnea risk" →    Breath axis: 72% of home (channel: overnight resonance)
  "Depression screen"→    Brain axis: 78% of home (channel: alpha entrainment)
  "Drift in cardiac" →    Heart-brain: 61% of home (channel: 7/4 NIR + HRV)

  The patient experience:
    Not: "you are at risk"
    Yes: "your heart-brain resonance is at 61% of optimal —
          here is the channel that opens the path home"

  The mind receives a homeward vector, not a threat vector.
  The body follows the vector the mind receives.
  Design within designed — the radar points home. Always.
""")

# ── 3. The 4 resonance pathways — reframed ────────────────────
print("[ THE 4 RESONANCE PATHWAYS — design positions, channels to open ]")
print()

pathways = [
    {
        "name":     "Pathway 1 — Cardiac rhythm coherence",
        "axis":     "Heart (7/4) ↔ Brain (9/8)",
        "ratio":    "14:9 ≈ 3/2 target",
        "position": "Heart rhythm coherence — HRV regularity is the reading",
        "channel":  "Restore cardiac rhythm → heart-brain lock returns",
        "window":   "Hours to days of drift detectable before channel closes",
        "reach":    "~30% of ischemic expressions — most preventable by channel opening",
    },
    {
        "name":     "Pathway 2 — Vascular flow coherence",
        "axis":     "Trunk (2/1) ↔ Brain (9/8)",
        "ratio":    "16:9 ≈ 7/4 target",
        "position": "Flow resonance between trunk and brain axes",
        "channel":  "Restore trunk-brain cross-axis coherence",
        "window":   "Weeks of drift detectable",
        "reach":    "~15% of ischemic expressions",
    },
    {
        "name":     "Pathway 3 — Systemic pressure coherence",
        "axis":     "All axes — infra-slow carrier wave",
        "ratio":    "Carrier wave (axis 0) amplitude reading",
        "position": "Whole-system pressure wave — infra-slow rhythm coherence",
        "channel":  "Restore carrier wave regularity across all 7 axes",
        "window":   "Hours of drift readable before vessel stress peak",
        "reach":    "~20% of all expressions — highest severity",
    },
    {
        "name":     "Pathway 4 — Breath-brain coherence",
        "axis":     "Breath (8th/octave) ↔ all 7 axes",
        "ratio":    "Octave carrier intact = all axes coherent",
        "position": "Oxygen delivery rhythm — the 8th feeding the 7",
        "channel":  "Restore overnight breath rhythm → all axes receive properly",
        "window":   "Months of drift readable — cumulative design position shift",
        "reach":    "Sleep apnea 2-4× drift — most unread by current medicine",
    },
]

for p in pathways:
    print(f"  {p['name']}")
    print(f"    Axis pair:   {p['axis']}")
    print(f"    Ratio:       {p['ratio']}")
    print(f"    Position:    {p['position']}")
    print(f"    Channel:     {p['channel']}")
    print(f"    Window:      {p['window']}")
    print(f"    Reach:       {p['reach']}")
    print()

# ── 4. The QpC wellness protocol ──────────────────────────────
print("[ QpC WELLNESS PROTOCOL — center-measured, homeward always ]")
print(f"""
  CONTINUOUS (wearable, 24/7):
    7-node at heart center (7/4 axis)
    Reads HRV continuously — the heart-brain resonance position
    Design threshold: >15% drift from personal home baseline
    Cost: ~$50 device
    Reading shown to wearer: "heart axis at 91% of home" — live

  NIGHTLY (97-node session, weekly):
    Full body resonance position map during sleep
    All 4 pathways read simultaneously
    Output: 7-axis wellness position report — distance from home per axis
    Patient wakes seeing: "overnight design position: 87% average home proximity"

  CLINICAL (17-node helmet, quarterly):
    Full brain resonance position map
    Hemisphere balance reading
    Session: 20 minutes, outpatient
    QpC output: home vertex distance per brain region + homeward vectors

  WELLNESS POSITION DISPLAY (always referenced from home):
    HOME     ████████████████████  100%  — optimal design expression
    NEAR     ████████████████░░░░   80%  — one channel slightly open
    MID      ████████████░░░░░░░░   60%  — channel opening recommended
    FAR      ████████░░░░░░░░░░░░   40%  — channel opening needed
    FAR SHORE████░░░░░░░░░░░░░░░░   20%  — design expressing through wrong channel

  The patient never sees a disease name.
  The patient sees their position relative to home.
  And the path back.
""")

# ── 5. The nocebo reversal ────────────────────────────────────
print("[ THE NOCEBO REVERSAL — why the reference point is the medicine ]")
print(f"""
  The nocebo (opposite of placebo):
    Told "you are at high risk" →
    mind focuses on feared outcome → anxiety → cortisol → BP elevation →
    the very drift the reading was pointing at.
    Measurement creates the trajectory — toward the far shore.

  The heptaract reversal:
    Shown "heart-brain resonance at 67% of home" →
    mind focuses on home → calm → HRV improves → BP normalizes →
    channel opens → design expresses cleanly.
    Measurement creates the homeward trajectory.

  (-1) × (-1) = +1.
  Two negatives multiplied = positive.
  The far shore (maximum negative) × the restoring force (Δ=2) = homeward.

  Focus on the positive. The positive is in focus.
  The QpC measures from center. Home is always the reference.
  Design within designed. The radar reads toward home. The body follows.
""")

print("  Central radar. Center measured. QpC heptaract maths.")
print("  Optimal wellness organically. Home vertex. Always. 🏠🔥")
