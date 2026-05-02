"""
Heptaract pitch-matching experiment.

Geometry: 7-cube. 128 vertices, each a 7-bit address (a1..a7) in {0,1}^7.
Each axis carries a frequency ratio. A vertex = which axes are "on".
Vertex pitch = product of active ratios, folded into one octave [1,2).
"Home" = vertex whose folded ratio is closest to a simple integer ratio (low
denominator in lowest terms when expressed as a rational approximation).
"""

from fractions import Fraction
from math import log2, gcd
from functools import reduce

# --- 7 axes ---
# Use 7-limit just intonation: the building-block intervals music actually
# resolves to. Picking the 7 smallest "consonant" ratios above 1/1.
AXES = [
    ("octave",     Fraction(2, 1)),
    ("fifth",      Fraction(3, 2)),
    ("fourth",     Fraction(4, 3)),
    ("maj third",  Fraction(5, 4)),
    ("min third",  Fraction(6, 5)),
    ("harm 7th",   Fraction(7, 4)),
    ("maj 2nd",    Fraction(9, 8)),
]

ROOT_HZ = 432.0  # try 432 since the user is in metaphor-land; swap to 440 anytime

def fold_to_octave(r: Fraction) -> Fraction:
    """Bring ratio into [1, 2)."""
    while r >= 2:
        r /= 2
    while r < 1:
        r *= 2
    return r

def vertex_ratio(bits):
    r = Fraction(1)
    for b, (_, ratio) in zip(bits, AXES):
        if b:
            r *= ratio
    return fold_to_octave(r)

def consonance(r: Fraction) -> int:
    """Lower = more consonant. Sum of numerator + denominator in lowest terms."""
    return r.numerator + r.denominator

def cents(r: Fraction) -> float:
    return 1200 * log2(float(r))

# --- enumerate all 128 vertices ---
verts = []
for n in range(128):
    bits = tuple((n >> i) & 1 for i in range(7))
    r = vertex_ratio(bits)
    verts.append((bits, r))

# unique pitch classes
classes = {}
for bits, r in verts:
    classes.setdefault(r, []).append(bits)

print(f"Vertices: {len(verts)}, distinct pitch classes: {len(classes)}\n")

# --- the "home song": most consonant pitch classes ---
ranked = sorted(classes.keys(), key=lambda r: (consonance(r), cents(r)))
print("HOME SONG — the 12 most consonant vertex pitches")
print(f"{'ratio':>10}  {'cents':>8}  {'Hz @ 432':>10}  multiplicity  active-axis count(s)")
for r in ranked[:12]:
    bits_list = classes[r]
    counts = sorted({sum(b) for b in bits_list})
    hz = ROOT_HZ * float(r)
    print(f"{str(r):>10}  {cents(r):>8.1f}  {hz:>10.2f}  {len(bits_list):>12}   {counts}")

# --- triangular center: 3-vertex faces ---
# In the 7-cube, every "2-face" is a square (4 vertices). A triangle isn't a
# native face of a hypercube — but we can ask: which TRIPLES of vertices that
# share Hamming-distance 1 from a common center form a consonant 3-chord?
# That's the closest geometric analogue: 3 axes branching from one vertex.
print("\nTRIANGULAR CENTERS — vertices whose 3-axis neighborhoods form consonant triads")
print(f"{'center bits':>20}  {'triad ratios':>30}  consonance")

triads = []
from itertools import combinations
for center_n in range(128):
    cbits = tuple((center_n >> i) & 1 for i in range(7))
    cr = vertex_ratio(cbits)
    # pick any 3 of the 7 axes to flip
    best_for_center = None
    for axes_chosen in combinations(range(7), 3):
        triad = []
        for ax in axes_chosen:
            nbits = list(cbits); nbits[ax] ^= 1
            triad.append(vertex_ratio(tuple(nbits)))
        # chord consonance = sum of pairwise consonance vs center
        score = sum(consonance(t / cr if t > cr else cr / t) for t in triad)
        if best_for_center is None or score < best_for_center[0]:
            best_for_center = (score, axes_chosen, triad)
    triads.append((best_for_center[0], cbits, cr, best_for_center[1], best_for_center[2]))

triads.sort()
for score, cbits, cr, axes_chosen, triad in triads[:8]:
    triad_str = ", ".join(str(t) for t in triad)
    axis_names = "+".join(AXES[a][0] for a in axes_chosen)
    print(f"{str(cbits):>20}  center={cr}  via {axis_names}")
    print(f"{'':>20}  triad: {triad_str}   score={score}")

# --- the 7/1 "center home" ---
# Interpret "7/1" as: vertex where the 7th harmonic is the dominant carrier.
# Look for vertices whose folded ratio is exactly 7/4 (octave-equivalent of 7/1)
# or closest to it.
print("\n7/1 CENTER HOME — vertices anchored on the 7th harmonic (7/4 octave-folded)")
target = Fraction(7, 4)
near_seven = sorted(classes.keys(), key=lambda r: abs(cents(r) - cents(target)))[:5]
for r in near_seven:
    delta = cents(r) - cents(target)
    print(f"  {str(r):>10}  ({cents(r):>7.1f}¢, Δ={delta:+.1f}¢)  reached by {len(classes[r])} vertex paths")

# --- "do we share a home song?" ---
# If another civilization built the same 7-cube but with shuffled axes, would
# they land on the same home pitch? Test: shuffle axis assignments and see
# how stable the top-1 home vertex is.
import random
print("\nCROSS-CIVILIZATION TEST — shuffle the 7 axis labels, does HOME stay home?")
random.seed(7)
hits = 0; trials = 1000
def home_for(perm):
    cls = {}
    for n in range(128):
        bits = tuple((n >> i) & 1 for i in range(7))
        r = Fraction(1)
        for b, idx in zip(bits, perm):
            if b: r *= AXES[idx][1]
        r = fold_to_octave(r)
        cls.setdefault(r, 0)
        cls[r] += 1
    return min(cls.keys(), key=lambda r: (consonance(r), cents(r)))

baseline = home_for(list(range(7)))
print(f"  baseline home pitch: {baseline}  ({cents(baseline):.1f}¢)")
for _ in range(trials):
    perm = list(range(7)); random.shuffle(perm)
    if home_for(perm) == baseline:
        hits += 1
print(f"  same home under random axis-relabel: {hits}/{trials} = {hits/trials:.1%}")
print("  -> if high, the 'home song' is invariant under who labels which axis,")
print("     i.e. any culture wiring the same 7 intervals into a 7-cube finds the same tonic.")
