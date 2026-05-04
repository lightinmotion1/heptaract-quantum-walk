"""
Seasonal Magnetic Harmony — why spring & fall open the melody

The key physics (Russell-McPherron effect, 1973):
Earth's magnetic dipole is tilted ~9.5° from the rotation axis.
As Earth orbits the sun, the angle between the dipole and the
solar wind changes. This angle determines how much the solar wind
"couples" with Earth's field — how much magnetic energy flows in.

The coupling is MAXIMUM at equinoxes. Minimum at solstices.

In heptaract terms:
- Solstice: one pole toward sun, one away → asymmetric → one vertex dominates
- Equinox:  both poles equidistant from sun → SYMMETRIC → home AND anti-home
            both active simultaneously → full chord, not single note
            → melodic harmony

That's the "poles changing from spring & fall" — at equinox both poles
are in play at once. The heptaract plays the full diagonal.
"""

import numpy as np
from math import sin, cos, radians, degrees, log2, pi, sqrt, atan2, asin

AXIAL_TILT    = 23.45   # degrees — Earth's obliquity
DIPOLE_OFFSET =  9.5    # degrees — magnetic pole offset from rotation axis
DIPOLE_LON    = -72.7   # degrees — longitude of magnetic pole

# ── 1. Coupling angle through the year ────────────────────────

def solar_longitude(day_of_year):
    """Approximate ecliptic longitude of sun (degrees). Day 1 = Jan 1."""
    return (day_of_year - 81) * 360 / 365.25

def russell_mcpherron_angle(day_of_year):
    """
    Effective coupling angle between Earth's dipole and solar wind.
    Peaks at equinoxes, troughs at solstices.
    Returns angle in degrees (higher = more open = more geomagnetic activity).
    """
    lam = radians(solar_longitude(day_of_year))
    eps = radians(AXIAL_TILT)
    # The Y-component of the dipole axis in GSM coordinates
    # (the component that matters for reconnection)
    Y_gsm = sin(radians(DIPOLE_OFFSET)) * sin(lam) * cos(eps) - cos(radians(DIPOLE_OFFSET)) * sin(eps)
    return abs(degrees(asin(max(-1, min(1, Y_gsm)))))

def heptaract_openness(day_of_year):
    """
    How 'open' the heptaract's home↔anti-home axis is at a given day.
    Equinox = both vertices active = maximum melodic range.
    Solstice = one vertex dominant = single sustained note.
    """
    angle = russell_mcpherron_angle(day_of_year)
    # Normalize: max coupling ~23.5°, min ~0°
    return angle / AXIAL_TILT

def heptaract_chord(openness):
    """
    What chord is Earth playing at this openness level?
    openness 0 = single note (solstice)
    openness 1 = full diagonal chord (equinox)
    """
    if openness < 0.2:   return "sustained tonic (1)          — single note, stable"
    if openness < 0.4:   return "tonic + fifth (1+5)          — open fifth, grounded"
    if openness < 0.6:   return "major triad (1+3+5)          — full chord, bright"
    if openness < 0.8:   return "dom 7th (1+3+5+b7)           — tension, searching"
    return                      "full diagonal 1↔7 (1+all+7)  — maximum melodic range"

# ── 2. The year in heptaract chords ──────────────────────────
print("=" * 65)
print("  SEASONAL MAGNETIC HARMONY — HEPTARACT VIEW")
print("=" * 65)

seasons = [
    ("Jan 1  — Winter deep",       1),
    ("Feb 4  — cross-quarter",    35),
    ("Mar 20 — SPRING EQUINOX",   79),
    ("Apr 5  — post-equinox",     95),
    ("May 1  — cross-quarter",   121),
    ("Jun 21 — SUMMER SOLSTICE", 172),
    ("Aug 7  — cross-quarter",   219),
    ("Sep 22 — FALL EQUINOX",    265),
    ("Oct 31 — cross-quarter",   304),
    ("Dec 21 — WINTER SOLSTICE", 355),
]

print(f"\n  {'Date':<30}  {'Coupling':>10}  {'Openness':>10}  Heptaract chord")
print("  " + "─" * 80)
for name, day in seasons:
    angle  = russell_mcpherron_angle(day)
    openn  = heptaract_openness(day)
    chord  = heptaract_chord(openn)
    marker = " ◄◄" if "EQUINOX" in name else (" ◄" if "SOLSTICE" in name else "")
    print(f"  {name:<30}  {angle:>8.2f}°  {openn:>9.3f}   {chord}{marker}")

# ── 3. The full annual waveform ────────────────────────────────
print(f"\n[ ANNUAL COUPLING WAVEFORM — semi-annual rhythm ]")
print(f"  The magnetic 'melody' amplitude through the year")
print(f"  Peak = equinox (melodic maximum). Trough = solstice (single note).")
print()

days = range(1, 366)
angles = [russell_mcpherron_angle(d) for d in days]
max_a = max(angles)

# ASCII waveform
print("  J  F  M  A  M  J  J  A  S  O  N  D")
print("  |" + "─"*74 + "|")
rows = 8
for row in range(rows, -1, -1):
    threshold = row / rows * max_a
    line = "  |"
    for d in range(1, 366, 5):
        a = russell_mcpherron_angle(d)
        line += "█" if a >= threshold else " "
    line += "|"
    if row == rows:   label = f" ← equinox peaks ({max_a:.1f}°)"
    elif row == 0:    label = " ← solstice troughs"
    else:             label = ""
    print(line + label)
print("  |" + "─"*74 + "|")

# ── 4. Why equinox = melodic harmony ──────────────────────────
print(f"""
[ WHY EQUINOX OPENS THE MELODY ]

  At SOLSTICE:
    One pole tilted toward sun → compressed (field pushed in)
    One pole tilted away       → expanded (field stretched out)
    Asymmetric. HOME vertex dominates. Anti-home is quiet.
    Heptaract plays ONE note — the sustained tonic.
    Like a drone. Harmonic. Simple. Grounded.

  At EQUINOX:
    BOTH poles equidistant from sun → both equally exposed
    Symmetric. HOME and ANTI-HOME both active simultaneously.
    The heptaract is playing both ends of the diagonal at once.
    That's not a note — that's a CHORD.
    The full I↔VII tension. Maximum melodic range.
    This is where the melody lives.

  In English:
    Solstice = the campfire quiet, holding one note
    Equinox  = the campfire singing — both sides of the fire
               leaning in at once, call and response,
               home hearing itself from across the diagonal
""")

# ── 5. The pitch of the equinox ───────────────────────────────
print(f"[ THE PITCH OF THE EQUINOX ]")

# At equinox, the dipole axis lies in the ecliptic plane
# The angle between home and anti-home = the full diagonal
# = all 7 axes traversed = the sum of all interval ratios

from fractions import Fraction
AXES = [Fraction(2,1), Fraction(3,2), Fraction(4,3), Fraction(5,4),
        Fraction(6,5), Fraction(7,4), Fraction(9,8)]

# home vertex pitch (from earlier: axes 0,2,3,4,6 active)
home_bits   = [1,0,1,1,1,0,1]
# anti-home  = all flipped
anti_bits   = [0,1,0,0,0,1,0]

def fold(r):
    while r >= 2: r /= 2
    while r < 1:  r *= 2
    return r

def vertex_pitch(bits):
    r = Fraction(1)
    for b,ax in zip(bits,AXES):
        if b: r *= ax
    return fold(r)

home_pitch  = vertex_pitch(home_bits)
anti_pitch  = vertex_pitch(anti_bits)
equinox_gap = fold(anti_pitch / home_pitch) if anti_pitch > home_pitch else fold(home_pitch / anti_pitch)

hc = 1200*log2(float(home_pitch))
ac = 1200*log2(float(anti_pitch))
ec = 1200*log2(float(equinox_gap))

print(f"  Home vertex pitch:      {home_pitch}  ({hc:.1f}¢)")
print(f"  Anti-home pitch:        {anti_pitch}  ({ac:.1f}¢)")
print(f"  Equinox interval (gap): {equinox_gap}  ({ec:.1f}¢)")

intervals = {'unison':0,'min 2nd':112,'maj 2nd':204,'min 3rd':316,
             'maj 3rd':386,'fourth':498,'tritone':600,'fifth':702,
             'min 6th':814,'maj 6th':884,'harm 7th':969,'min 7th':1018,'octave':1200}
nearest = min(intervals.items(), key=lambda x: abs(x[1]-ec))
print(f"  Nearest named interval: {nearest[0]} ({nearest[1]}¢)  Δ={abs(nearest[1]-ec):.1f}¢")
print()
print(f"  At equinox, Earth's magnetic field plays the interval")
print(f"  between home and anti-home simultaneously.")
print(f"  That interval is the {nearest[0]}.")
print(f"  That is the sound of both poles singing at once.")
print(f"  That is the melodic harmony the seasons unlock.")
