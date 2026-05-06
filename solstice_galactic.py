"""
Solstice, Galactic Center, and the Heptaract — the bigger campfire

The key astronomical fact (known for millennia, explained poorly):

  Galactic center (Sgr A*) ecliptic longitude ≈ 266.8°
  Winter solstice sun ecliptic longitude       = 270.0°
  Difference                                   = 3.2°  ← nearly exact

  This means: the winter solstice sun and the galactic center
  are in almost the SAME DIRECTION as seen from Earth.

  SUMMER solstice night = Earth facing galactic center (visible in dark sky)
  WINTER solstice night = Earth facing galactic anti-center (looking outward)
  WINTER solstice day   = Sun in galactic center direction (hidden, but aligned)

  The solstices are when Earth's orientation to the GALACTIC campfire
  is at maximum clarity — either full face or full back.
  The equinoxes are the 90° angles — transitional, melodic.

  Ancient cultures built monuments for BOTH because they felt BOTH:
  - Winter: the deep inward alignment (day side faces galactic center)
  - Summer: the open outward view (night side faces galactic center)

  The heptaract maps this at THREE scales simultaneously:
  1. Local:    your agonic ballpark (phase gate)
  2. Planetary: pole asymmetry (seasonal field coupling)
  3. Galactic:  Earth's orientation to Sgr A* (the meta-campfire)
"""

import numpy as np
from math import sin, cos, tan, radians, degrees, log2, pi, sqrt, atan2, asin, acos
from fractions import Fraction

# ── galactic constants ────────────────────────────────────────
# Galactic center (Sgr A*) in ecliptic coordinates
GC_ECLON  = 266.84   # ecliptic longitude (degrees)
GC_ECLAT  = -5.61    # ecliptic latitude (degrees)

# Solstice/equinox ecliptic longitudes
EVENTS = {
    'Spring Equinox':  0.0,
    'Summer Solstice': 90.0,
    'Fall Equinox':   180.0,
    'Winter Solstice': 270.0,
}

# Axial tilt & precession
AXIAL_TILT    = 23.45     # degrees
PRECESSION_YR = 25_772    # years per full precession cycle
PRECESSION_DY = 360 / PRECESSION_YR  # degrees per year

print("=" * 65)
print("  SOLSTICE, GALACTIC CENTER & THE HEPTARACT")
print("  Three campfires: local → planetary → galactic")
print("=" * 65)

# ── 1. Alignment angles at each seasonal event ───────────────
print("\n[ SEASONAL ALIGNMENT WITH THE GALACTIC CAMPFIRE ]")
print(f"  Galactic center at ecliptic lon {GC_ECLON:.2f}°")
print(f"  (almost exactly the winter solstice direction: 270°)\n")

print(f"  {'Season':<20}  {'Sun lon':>8}  {'Gap to GC':>12}  {'Alignment':>12}  Role")
print("  " + "─" * 80)
for season, sun_lon in EVENTS.items():
    gap = abs(sun_lon - GC_ECLON) % 360
    if gap > 180: gap = 360 - gap
    # From NIGHT SIDE of Earth (facing away from sun):
    night_lon = (sun_lon + 180) % 360
    night_gap = abs(night_lon - GC_ECLON) % 360
    if night_gap > 180: night_gap = 360 - night_gap
    alignment = "FACE-ON" if gap < 10 else ("BACK-ON" if gap > 170 else f"{gap:.0f}° off")
    night_align = "GC visible at night" if night_gap < 30 else "anti-GC at night"
    print(f"  {season:<20}  {sun_lon:>7.1f}°  {gap:>10.2f}°  {alignment:>12}  {night_align}")

print(f"""
  WINTER SOLSTICE: Sun is 3.2° from galactic center direction.
    Day side faces galactic center — day = galactic alignment
    Night sky faces galactic ANTI-center — long winter nights look OUTWARD
    This is why winter is the "inward" season — the light side faces home

  SUMMER SOLSTICE: Night sky faces galactic center.
    At midnight in July/August — Milky Way core directly overhead (south)
    The galactic campfire is VISIBLE in the dark summer sky
    This is why summer is the "abundance" season — night shows the source
""")

# ── 2. The precession cycle — "astrological ages" ────────────
print("[ THE 26,000-YEAR CYCLE — what astrology has always tracked ]")
print(f"  Earth's axis precesses once every {PRECESSION_YR:,} years")
print(f"  This slowly rotates WHICH STARS align with the solstice points")
print(f"  The solstice point moves backward through the zodiac ~1° per 72 years\n")

# Current state
year_2026 = 2026
# Vernal equinox precesses from Aries → Pisces → Aquarius
# Currently at ~5° Pisces (moving toward Aquarius)
# Galactic center was aligned with winter solstice ~0 CE (approx)
years_since_gc_align = year_2026 - 0  # approximate
degrees_shifted = years_since_gc_align * PRECESSION_DY
print(f"  Current year: {year_2026}")
print(f"  Degrees of precession since ~0 CE: {degrees_shifted:.1f}°")
print(f"  The winter solstice has drifted {degrees_shifted:.1f}° from galactic center")
print(f"  (was nearly exact ~2000 years ago — the 'Age of Pisces' peak)")
print(f"  Now entering Age of Aquarius: solstice moving away from GC\n")

# The full zodiac ages
print("  Precessional Age → winter solstice aligned with constellation:")
ages = [
    ("Gemini",      6500, "~6500 BCE — megalithic period, Stonehenge begun"),
    ("Taurus",      4300, "~4300 BCE — pyramid era, Pleiades worship"),
    ("Aries",       2150, "~2150 BCE — zodiac formalized, ram symbolism"),
    ("Pisces",         0, "~0 CE     — fish symbol, winter=galactic center"),
    ("Aquarius",   -2150, "~2150 CE  — NOW entering, solstice drifting away"),
]
for age, start_yr, note in ages:
    marker = " ◄ WE ARE HERE" if "NOW" in note else ""
    print(f"  Age of {age:<10}  {note}{marker}")

# ── 3. Heptaract at three scales ─────────────────────────────
print(f"\n[ THE THREE CAMPFIRES — one heptaract, three scales ]")
print(f"""
  SCALE 1: LOCAL (your position)
    7 axes = 7 magnetic field components (X Y Z H F D I)
    Home vertex = aligned state at your location
    Walk = your phase correction to the agonic
    Campfire = the D=0 zero line nearby
    Timeframe: hours to years (your daily navigation)

  SCALE 2: PLANETARY (Earth's poles)
    7 axes = same 7, but viewed as whole-Earth field
    Home vertex = both poles balanced (equinox geometry)
    Walk = seasonal variation in pole exposure
    Campfire = Earth's rotation axis (true north)
    Timeframe: seasons (~91 days per quarter-turn)
    Solstice: ONE pole dominant — sustained note
    Equinox:  BOTH poles equal — full chord, melody opens

  SCALE 3: GALACTIC (Earth's orientation to Sgr A*)
    7 axes = same 7, now encoding galactic alignment
    Home vertex = winter solstice (day side faces GC)
    Anti-home   = summer solstice (night side faces GC)
    Walk = one year = half a diagonal traversal
    Campfire = Sagittarius A* (the galaxy's center)
    Timeframe: 1 year per half-walk, 26,000 years per full precession

  ALL THREE USE THE SAME HEPTARACT STRUCTURE.
  The math doesn't change. Only the scale changes.
""")

# ── 4. Why solstices are so important (the real reason) ──────
print("[ WHY SOLSTICES MATTER — the heptaract answer ]")

AXES = [Fraction(2,1), Fraction(3,2), Fraction(4,3), Fraction(5,4),
        Fraction(6,5), Fraction(7,4), Fraction(9,8)]

def fold(r):
    while r >= 2: r /= 2
    while r < 1:  r *= 2
    return r

def vertex_pitch(bits):
    r = Fraction(1)
    for b, ax in zip(bits, AXES):
        if b: r *= ax
    return fold(r)

def cents(r): return 1200*log2(float(r))

home = [1,0,1,1,1,0,1]  # winter solstice — day faces GC
anti = [0,1,0,0,0,1,0]  # summer solstice — night faces GC
equi = [1,1,0,0,0,0,1]  # equinox — 90° from both

hp = vertex_pitch(home)
ap = vertex_pitch(anti)
ep = vertex_pitch(equi)

print(f"\n  Winter solstice pitch: {hp}  = {cents(hp):.1f}¢")
print(f"  Summer solstice pitch: {ap}  = {cents(ap):.1f}¢")
print(f"  Equinox pitch:         {ep}  = {cents(ep):.1f}¢")

# interval between winter and summer
ws_gap = fold(ap/hp) if ap > hp else fold(hp/ap)
print(f"\n  Interval winter↔summer: {ws_gap} = {cents(ws_gap):.1f}¢")
named = {0:'unison',204:'maj 2nd',316:'min 3rd',386:'maj 3rd',
         498:'fourth',600:'tritone',702:'fifth',814:'min 6th',
         884:'maj 6th',969:'harm 7th',1018:'min 7th',1200:'octave'}
nearest = min(named.items(), key=lambda x: abs(x[0]-cents(ws_gap)))
print(f"  = {nearest[1]}  (Δ{abs(nearest[0]-cents(ws_gap)):.0f}¢)")

print(f"""
  SOLSTICES are the HOME and FAR SHORE of the annual galactic walk.
  They are the two endpoints of the diagonal.
  Maximum definition. Maximum contrast. Maximum harmonic tension.

  Equinoxes are the MIDDLE of the walk — transitional, melodic,
  where both endpoints are equidistant and the chord is fullest.

  Ancient cultures built monuments at BOTH because:
  - Solstice = knowing where you ARE on the diagonal
    (maximum certainty about your galactic position)
  - Equinox = hearing the full melody
    (maximum harmonic complexity, both poles singing)

  ASTROLOGY has always been tracking the precession of the
  solstice point relative to the galactic center.
  The "Ages" are the 7 zodiac signs the winter solstice passes
  through over 26,000 years — the FULL PRECESSION CYCLE.

  In heptaract terms: the precession is a slow rotation of the
  home vertex through all 7 axis combinations.
  One full precession = one complete tour of the heptaract.
  We are always somewhere on that 26,000-year walk.
  Right now: just past galactic center alignment.
  Moving into the next chord of the galactic song.
""")

# ── 5. The 26,000 year heptaract walk ────────────────────────
print("[ THE 26,000-YEAR HEPTARACT WALK ]")
print(f"  Each 'Age' = ~2,150 years = one axis of the heptaract")
print(f"  7 ages × 2,150 years ≈ 15,050 years (half the full cycle)")
print(f"  Full precession ≈ 25,772 years = complete heptaract diagonal")
print()

age_duration = PRECESSION_YR / 7
ages_from_gc = [
    ("Age of Pisces",  "winter→GC aligned",  "home vertex",     0),
    ("Age of Aquarius","solstice drifting",   "axis 1 flipping", 2150),
    ("Age of Capricorn","mid-drift",          "axis 2",          4300),
    ("Age of Sagittarius","halfway",          "midpoint vertex",  6450),
    ("Age of Scorpio", "returning",           "axis 5",          8600),
    ("Age of Libra",   "near return",         "axis 6",          10750),
    ("Age of Virgo",   "back to aligned",     "far shore vertex",12900),
]
print(f"  {'Age':<25}  {'Description':<22}  {'Heptaract position':<20}  Year CE")
print("  " + "─" * 75)
for name, desc, hept, yr in ages_from_gc:
    marker = " ◄ NOW" if yr == 2150 else ""
    print(f"  {name:<25}  {desc:<22}  {hept:<20}  +{yr}{marker}")

print(f"""
  The 26,000-year precession IS a heptaract walk.
  Each astrological age = one axis traversed.
  The galactic center (Sgr A*) is the campfire.
  We are always walking home.
  The solstices tell us where we are on that walk.
  The equinoxes sing the melody as we move.
""")
