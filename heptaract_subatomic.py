"""
Heptaract Sub-Atomic — The Relationship Structure Beneath The Atom

What sits under the body, under the chemistry, under the atom?
The same question the framework asks everywhere else, asked one floor lower:
  is there a seven-shaped relationship structure at the sub-atomic scale,
  and can We check This rather than assert This?

This module checks This. Pure standard library — no numpy, no qiskit —
so any tester can run This on any machine and read the receipts directly.

FIVE RECEIPTS, COMPUTED LIVE:

  1. THE SETTLED HYPERCUBE IS FIVE, NOT SEVEN.
     One generation of matter — 16 left-handed Weyl fermions — is exactly
     the 16 even-parity vertices of a 5-cube (the SO(10) spinor weights).
     Every Standard Model charge is a linear function of the vertex.
     All four gauge anomalies cancel. This is settled textbook math, and
     the honest lead: the geometry of a generation is a PENTERACT.

  2. THE HEPTARACT IS THE NEXT RUNG, AND This IS SO(14).
     The 128 heptaract vertices split by parity into 64 + 64 — exactly the
     two Weyl spinors of SO(14). Each 64 decomposes as two generations
     plus two mirror generations. Real math; an open GUT problem.

  3. PARITY IS CHIRALITY, AND SEVEN IS ODD.
     The perfect-transfer walk crosses 7 edges. Odd. So home vertex and far
     shore lie in OPPOSITE parity classes: the walk carries 64 to 64-bar.
     The repo's t = +pi/2 / t = -pi/2 is a chirality exchange, not a
     translation. The Hamming distance from home is an exact U(1) charge.

  4. THE SEVEN AXES CARRY AN ALGEBRA, NOT JUST A LIST.
     Seven imaginary octonion units, seven Fano-plane points, seven lines.
     The axes multiply. G2 = Aut(O) is the holonomy group of the very
     7-manifolds M-theory compactifies on. Verified here numerically.

  5. A STANDARD MODEL FERMION CARRIES SEVEN COMMUTING LABELS.
     Jz, T3L, Y, lambda3, lambda8, B, L. Stated WITH the anomaly caveat,
     because the caveat is the interesting part.

Nothing here claims new physics. This claims a relationship structure,
checks This, and marks plainly where the assignment is forced by the math
and where This is still a choice We are making.
"""

import itertools
import random
from fractions import Fraction as F

BAR = "=" * 68
SUB = "-" * 68


def rule(title):
    print()
    print(BAR)
    print("  " + title)
    print(BAR)


# =====================================================================
print(BAR)
print("  HEPTARACT SUB-ATOMIC RELATIONSHIP STRUCTURE")
print("  The floor beneath the atom, checked rather than asserted")
print(BAR)


# =====================================================================
# RECEIPT 1 — ONE GENERATION IS THE EVEN HALF OF A 5-CUBE (SO(10) 16)
# =====================================================================
rule("RECEIPT 1 — THE SETTLED HYPERCUBE OF MATTER IS FIVE")

print("""
  A weight of the SO(10) spinor is a 5-vector of +-1/2 with an EVEN
  number of minus signs. That is one parity class of a 5-cube: 2^5 / 2 = 16.

  Coordinates 1,2,3 = colour (SU(3)_c).  Coordinates 4,5 = weak (SU(2)_L x SU(2)_R).

  Every Standard Model charge is then a linear function of the vertex:

      B - L  =  (2/3) (s1 + s2 + s3)
      T3L    =  (s4 - s5) / 2
      T3R    = -(s4 + s5) / 2
      Y/2    =  T3R + (B - L)/2
      Q      =  T3L + Y/2
""")

half = F(1, 2)
SIGNS = (half, -half)


def weights(n):
    """All 2^n vertices of the n-cube as +-1/2 vectors, and their parity."""
    for bits in itertools.product((0, 1), repeat=n):
        s = tuple(-half if b else half for b in bits)
        yield bits, s, sum(bits) % 2   # parity 0 = even number of minus signs


def sm_charges(s):
    colour = s[0] + s[1] + s[2]
    BmL = F(2, 3) * colour
    T3L = (s[3] - s[4]) / 2
    T3R = -(s[3] + s[4]) / 2
    Yh = T3R + BmL / 2            # Y/2
    Q = T3L + Yh
    return BmL, T3L, T3R, 2 * Yh, Q


def name_state(bits):
    """Name the field from where the minus signs fall."""
    nc = sum(bits[:3])            # minus signs in colour
    nw = sum(bits[3:])            # minus signs in weak
    return {
        (0, 0): "nu^c   right-handed neutrino",
        (0, 2): "e^c    anti-electron",
        (1, 1): "q      (u,d) quark doublet",
        (2, 0): "u^c    anti-up quark",
        (2, 2): "d^c    anti-down quark",
        (3, 1): "l      (nu,e) lepton doublet",
    }[(nc, nw)]


gen = [(bits, s) for bits, s, par in weights(5) if par == 0]
print("  16 even-parity vertices of the 5-cube = one generation:\n")
print("   vertex   field                          B-L     T3L     Y       Q")
print("  " + SUB)
tally = {}
for bits, s in gen:
    BmL, T3L, T3R, Y, Q = sm_charges(s)
    nm = name_state(bits)
    tally[nm] = tally.get(nm, 0) + 1
    print(("   %s   %-30s %-7s %-7s %-7s %-7s"
           % ("".join(str(b) for b in bits), nm, BmL, T3L, Y, Q)).rstrip())

print("\n  Multiplicities (colour counting falls out of the geometry):")
for nm, k in sorted(tally.items(), key=lambda kv: -kv[1]):
    print("     %-30s x %d" % (nm, k))
print("     %-30s = %d states" % ("TOTAL", sum(tally.values())))

# --- anomaly cancellation, computed from the vertex set alone ---
sumY = sumY3 = sumQ = sumBmL = F(0)
sumY_colour = sumY_doublet = F(0)
for bits, s in gen:
    BmL, T3L, T3R, Y, Q = sm_charges(s)
    sumY += Y
    sumY3 += Y ** 3
    sumQ += Q
    sumBmL += BmL
    if sum(bits[:3]) in (1, 2):            # colour-charged states
        sumY_colour += Y
    if T3L != 0:                           # weak-doublet states
        sumY_doublet += Y

print("""
  ANOMALY CANCELLATION — computed from the parity class, nothing assumed:""")
checks = [
    ("gravity x U(1)_Y     sum Y", sumY),
    ("U(1)_Y^3             sum Y^3", sumY3),
    ("SU(3)^2 x U(1)_Y     sum Y over coloured", sumY_colour),
    ("SU(2)^2 x U(1)_Y     sum Y over doublets", sumY_doublet),
    ("SO(10) trace         sum (B-L)", sumBmL),
    ("neutrality           sum Q", sumQ),
]
for label, val in checks:
    print("     %-40s = %-4s  %s" % (label, val, "OK" if val == 0 else "FAIL"))

print("""
  READING — LANE 2, settled.
  Anomaly freedom of a generation is not a numerical accident tuned by hand.
  This is a PARITY CONDITION on the vertices of a hypercube. The honest
  headline for This framework: the settled hypercube of matter has FIVE
  axes, not seven. We lead with This because a framework that hides their
  own inconvenient count is not doing math.
""")


# =====================================================================
# RECEIPT 2 — THE HEPTARACT IS THE SO(14) SPINOR
# =====================================================================
rule("RECEIPT 2 — THE HEPTARACT AT THE SUB-ATOMIC FLOOR IS SO(14)")

hept = list(weights(7))
even = [(b, s) for b, s, p in hept if p == 0]
odd = [(b, s) for b, s, p in hept if p == 1]
print("""
  Same construction, seven coordinates. A Weyl spinor of SO(2n) has
  2^(n-1) weights = one parity class of an n-cube. For n = 7:
""")
print("     heptaract vertices          = %d" % len(hept))
print("     even parity class (64)      = %d   <- SO(14) spinor" % len(even))
print("     odd  parity class (64-bar)  = %d   <- conjugate spinor" % len(odd))

# decomposition under SO(10) x SO(4): coords 1-5 and 6-7
d_16_2 = [x for x in even if sum(x[0][:5]) % 2 == 0]
d_16b_2 = [x for x in even if sum(x[0][:5]) % 2 == 1]
print("""
  Split the seven axes as 5 + 2 — SO(14) contains SO(10) x SO(4),
  and SO(4) = SU(2) x SU(2). The 64 decomposes by the parity of the
  first five coordinates alone:
""")
print("     (16,  2, 1)   generations       = %d states  = %d x 16"
      % (len(d_16_2), len(d_16_2) // 16))
print("     (16-bar, 1, 2)   mirrors        = %d states  = %d x 16"
      % (len(d_16b_2), len(d_16b_2) // 16))
print("     64 = 2 generations + 2 mirror generations")

print("""
  READING — LANE 2 for the math, OPEN for the physics.
  The math is exact and checkable above: the heptaract IS the weight
  hypercube of SO(14), and SO(14) = SO(4k+2) with k=3, so their spinor is
  complex and anomaly-free — a legitimate grand-unified candidate on those
  two counts.

  The honest problem, stated plainly and not buried: This delivers MIRROR
  generations alongside the ordinary ones, and mirror fermions are not
  observed at accessible energy. Any heptaract reading of matter owes an
  account of where the mirrors went. We do not have that account. We have
  the shape of the question: the mirrors sit in the OPPOSITE parity class
  from their partners, and parity is exactly what the heptaract walk moves.
  That is Receipt 3, and This is a research programme, not a result.
""")


# =====================================================================
# RECEIPT 3 — PARITY IS CHIRALITY; THE WALK IS ODD
# =====================================================================
rule("RECEIPT 3 — THE WALK IS ODD, SO THE WALK FLIPS CHIRALITY")

home = (0,) * 7
far = (1,) * 7
print("""
  Identify heptaract bit 1 with a minus sign in the weight vector.
""")
print("     home vertex 0000000  ->  weight (+1/2)^7   parity even  -> 64")
print("     far shore   1111111  ->  weight (-1/2)^7   parity odd   -> 64-bar")
print("     Hamming distance home -> far = %d edges (ODD)"
      % sum(a != b for a, b in zip(home, far)))
print("""
  Seven is odd, so the two ends of the perfect-transfer walk cannot sit in
  the same parity class. The repo's headline result — P = 1.0 at t = pi/2,
  depth-2, zero entanglement — carries the spinor onto their conjugate.

     t = +pi/2   64      ->  64-bar     (far shore)
     t = -pi/2   64-bar  ->  64         (home)

  The framework already said This in their own tongue: the walk goes to the
  far shore and the walk comes home. In sub-atomic language that sentence
  reads: the antipodal walk on an odd-dimensional cube is a chirality
  exchange. Same geometry. Two vocabularies.
""")

print("  THE HAMMING CHARGE — distance from home is an exact U(1) charge:\n")
print("     k = Hamming wt   X = sum(s_i) = 7/2 - k    parity class")
print("  " + SUB)
for k in range(8):
    X = F(7, 2) - k
    print("        %d              %-8s                  %s"
          % (k, X, "64" if k % 2 == 0 else "64-bar"))
print("""
  X is the charge under the diagonal U(1) in the SO(14) Cartan. So the
  framework's U(v) — the "magnetic desire" potential of
  heptaract_magnetic_desire.py, the Hamming distance from center fire —
  is not a metaphor imported into physics. On this identification This is
  a conserved additive quantum number, linear in the distance from home.
""")


# =====================================================================
# RECEIPT 4 — THE SEVEN AXES CARRY AN ALGEBRA (FANO / OCTONIONS)
# =====================================================================
rule("RECEIPT 4 — THE SEVEN AXES MULTIPLY: FANO PLANE AND OCTONIONS")

# Fano plane, cyclic construction: lines {i, i+1, i+3} mod 7
lines = [tuple(sorted(((i) % 7, (i + 1) % 7, (i + 3) % 7))) for i in range(7)]
lines = sorted(set(lines))
pairs_covered = {}
for ln in lines:
    for p in itertools.combinations(ln, 2):
        pairs_covered[p] = pairs_covered.get(p, 0) + 1
pt_incidence = {i: sum(1 for ln in lines if i in ln) for i in range(7)}

print("""
  Give the seven axes the only structure seven points can carry that makes
  them multiply: the Fano plane, PG(2,2). Lines {i, i+1, i+3} mod 7.
""")
print("     lines:", ", ".join("{%d,%d,%d}" % ln for ln in lines))
print("     points                            = %d" % 7)
print("     lines                             = %d" % len(lines))
print("     points per line                   = %s"
      % sorted({len(ln) for ln in lines}))
print("     lines per point                   = %s"
      % sorted(set(pt_incidence.values())))
print("     every pair on exactly one line    = %s"
      % all(v == 1 for v in pairs_covered.values()))
print("     pairs covered                     = %d of %d"
      % (len(pairs_covered), 21))

# octonion multiplication table over units e0..e7 (e0 = 1, e1..e7 imaginary)
MUL = [[(0, 0)] * 8 for _ in range(8)]
for a in range(8):
    MUL[0][a] = (1, a)
    MUL[a][0] = (1, a)
for a in range(1, 8):
    MUL[a][a] = (-1, 0)
for i in range(7):
    a, b, c = (i % 7) + 1, ((i + 1) % 7) + 1, ((i + 3) % 7) + 1
    for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
        MUL[x][y] = (1, z)
        MUL[y][x] = (-1, z)


def omul(u, v):
    out = [0.0] * 8
    for i, ui in enumerate(u):
        if ui == 0:
            continue
        for j, vj in enumerate(v):
            if vj == 0:
                continue
            sgn, k = MUL[i][j]
            out[k] += sgn * ui * vj
    return out


def onorm2(u):
    return sum(x * x for x in u)


random.seed(7)


def rand_o():
    return [random.uniform(-1, 1) for _ in range(8)]


# checks
sq_ok = all(MUL[a][a] == (-1, 0) for a in range(1, 8))
anti_ok = all(MUL[a][b][0] == -MUL[b][a][0]
              for a in range(1, 8) for b in range(1, 8) if a != b)
norm_err = 0.0
for _ in range(2000):
    u, v = rand_o(), rand_o()
    norm_err = max(norm_err,
                   abs(onorm2(omul(u, v)) - onorm2(u) * onorm2(v)))

# associativity inside a Fano line (quaternion subalgebra) vs outside
def unit(k):
    v = [0.0] * 8
    v[k] = 1.0
    return v


def assoc_gap(i, j, k):
    lhs = omul(omul(unit(i), unit(j)), unit(k))
    rhs = omul(unit(i), omul(unit(j), unit(k)))
    return max(abs(a - b) for a, b in zip(lhs, rhs))


line_gap = max(assoc_gap(a + 1, b + 1, c + 1)
               for ln in lines for a, b, c in itertools.permutations(ln))
off_line = [(i, j, k) for i, j, k in itertools.permutations(range(1, 8), 3)
            if tuple(sorted((i - 1, j - 1, k - 1))) not in lines]
off_gap = max(assoc_gap(*t) for t in off_line)
# alternativity: (xx)y = x(xy)
alt_err = 0.0
for _ in range(500):
    u, v = rand_o(), rand_o()
    lhs, rhs = omul(omul(u, u), v), omul(u, omul(u, v))
    alt_err = max(alt_err, max(abs(a - b) for a, b in zip(lhs, rhs)))

print("""
  The seven lines are the seven quaternionic triples. The multiplication
  table they generate is checked here, not assumed:
""")
print("     e_a^2 = -1 for all seven                    %s" % ("OK" if sq_ok else "FAIL"))
print("     e_a e_b = - e_b e_a                         %s" % ("OK" if anti_ok else "FAIL"))
print("     |uv|^2 = |u|^2 |v|^2  (2000 random pairs)   max err %.2e" % norm_err)
print("     alternative: (uu)v = u(uv)  (500 pairs)     max err %.2e" % alt_err)
print("     associative INSIDE a Fano line              max gap %.2e" % line_gap)
print("     associative OFF the lines                   max gap %.2e" % off_gap)
print("""
  So: a normed division algebra, alternative, associative exactly on the
  seven lines and nowhere else. The seven axes are not a list of labels.
  They are the imaginary part of the octonions, and their relationships
  are the Fano incidences.

  WHY This matters sub-atomically — LANE 2, published, not ours:
    * Furey (Eur. Phys. J. C 78, 375, 2018) derives SU(3)_c x SU(2)_L x U(1)_Y
      from ladder operators of the algebra C (x) H (x) O. The colour SU(3)
      appears as the stabiliser of one imaginary octonion unit inside G2.
    * G2 = Aut(O) has dimension 14 and rank 2, acts on exactly these seven
      imaginary units, and is the holonomy group of the 7-manifolds that
      M-theory compactifies on to give chiral matter and non-abelian gauge
      fields in four dimensions (Acharya & Witten, 2001).
    * 11 = 4 + 7. Eleven-dimensional supergravity on the round S^7 gives
      SO(8) gauge symmetry (Freund-Rubin; Duff, Nilsson, Pope 1986).

  None of That is This framework's invention. All of This is the seven
  already standing at the sub-atomic floor in mainstream literature, and
  This is where a heptaract reading of matter has to connect or fail.
""")


# =====================================================================
# RECEIPT 5 — SEVEN COMMUTING LABELS, WITH THE CAVEAT
# =====================================================================
rule("RECEIPT 5 — SEVEN COMMUTING LABELS ON A STANDARD MODEL FERMION")

labels = [
    ("Jz",       "little group SO(3)", "spin projection", "exact"),
    ("T3L",      "SU(2)_L Cartan",     "weak isospin",    "exact"),
    ("Y",        "U(1)_Y",             "hypercharge",     "exact"),
    ("lambda3",  "SU(3)_c Cartan 1",   "colour isospin",  "exact"),
    ("lambda8",  "SU(3)_c Cartan 2",   "colour hyperch.", "exact"),
    ("B",        "accidental U(1)_B",  "baryon number",   "ANOMALOUS"),
    ("L",        "accidental U(1)_L",  "lepton number",   "ANOMALOUS"),
]
print("\n     label     origin                 reads              status")
print("  " + SUB)
for a, b, c, d in labels:
    print("     %-9s %-22s %-18s %s" % (a, b, c, d))

print("""
     rank SU(3) x SU(2) x U(1) = 2 + 1 + 1 = 4
     + spin Cartan                        = 1   -> 5 gauge/Lorentz labels
     + accidental global B, L             = 2   -> 7 commuting labels

  THE CAVEAT, WHICH IS THE INTERESTING PART — LANE 2.
  B and L are conserved perturbatively but are individually broken by the
  electroweak anomaly. Only B - L survives exactly. So the count of
  EXACTLY conserved commuting labels is 5 + 1 = 6, and the seventh is real
  only at the classical / perturbative level, where it is real all day.

  We do not get to round That up. A framework that counts to seven by
  quietly keeping an anomalous charge has counted to six and lied. What We
  say instead is the honest and still-interesting thing: the seventh label
  exists, is used constantly in practice, and is destroyed by exactly the
  mechanism — the chiral anomaly — that Receipt 3 says the heptaract walk
  moves. The seventh axis is the anomalous one. That is a falsifiable place
  to look, not a decoration.
""")


# =====================================================================
# THE HONESTY BLOCK
# =====================================================================
rule("WHAT This DOES NOT CLAIM")
print("""
  Said plainly, so no tester wastes a week finding out for Themself:

  * No new force, no new particle, no modification to the Standard Model
    Lagrangian is proposed here.
  * No mass is predicted. The 19 (26 with neutrino masses) free parameters
    of the Standard Model are not derived, reduced, or explained.
  * No energy scale is assigned. The heptaract spectral gap Delta = 2 is
    dimensionless in the walk; there is no calibration to GeV, and We do
    not have one. Marked UNASSIGNED, not marked pending.
  * The just-intonation pitch labelling of the axes (2/1, 7/4, 3/2, 4/3,
    5/4, 6/5, 9/8) is a labelling isomorphism on seven objects. This is
    beautiful, This is useful for memory and for the body work, and This
    carries NO sub-atomic claim. Do not couple the two.
  * The Schumann band (7.83 Hz and their ladder) is a cavity resonance of
    the Earth-ionosphere system. That is classical electrodynamics at
    metre-to-megametre scale. It has nothing to do with particle physics
    and We are not going to pretend otherwise to make a page rhyme.
  * The bit-to-minus-sign identification in Receipt 3 is OUR CHOICE, not a
    derivation. It is the natural one and the whole reading rests on This.
    A tester who shows the identification cannot be made canonical has
    taken the load out of Receipt 3, and We would want to know.

  What This DOES claim: a checkable relationship structure. Hypercube
  parity is chirality; the settled matter hypercube is five; the heptaract
  is the next complex-spinor rung and is SO(14); the seven axes carry the
  octonion algebra that mainstream work already ties to SU(3) x SU(2) x U(1)
  and to G2 holonomy. Every line of That is above, computed, and falsifiable.
""")

print(BAR)
print("  Five receipts. One honest count of five where We wanted seven.")
print("  The heptaract sits one rung up, and the rung has a name: SO(14).")
print("  Center fire. Checked, not asserted. \U0001f525")
print(BAR)
