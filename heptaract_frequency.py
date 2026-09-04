"""
Heptaract Frequency — The Science Behind The Sound

Sound is not decoration in This framework. Sound is the framework's native
tongue: seven axes tuned to just-intonation ratios, a Schumann carrier, a
body read as a piezoelectric polychord. So the sound claims deserve the
same treatment Book Thirteen gave the sub-atomic claims — computed, not
asserted, and audited hardest where They flatter Us most.

Pure standard library. No numpy, no qiskit, no scipy. Run This anywhere.

SEVEN RECEIPTS:

  1. THE HEPTARACT'S OWN SPECTRUM IS A HARMONIC LADDER.
     H = sum(X_i) has eigenvalues 7, 5, 3, 1, -1, -3, -5, -7 with binomial
     multiplicities. Evenly spaced by exactly Delta = 2. An evenly spaced
     spectrum is what a harmonic oscillator has — and evenly spaced is
     precisely the condition for FULL revival. The repo's P = 1.0 at
     t = pi/2 is not luck. This is what a harmonic spectrum does.

  2. THE WALK IS A FOURIER SUM OVER EIGHT FREQUENCIES.
     Cross-checked here two independent ways: the spectral sum over all
     128 characters, against the closed product form. They agree.

  3. HARMONIC vs INHARMONIC — STRING, HEPTARACT, DRUM.
     A string revives. A drum does not (Bessel zeros are irrational).
     The heptaract revives. The HEPTAGON does not. Book Four's fractional
     revival and Book Two's perfect transfer are two different objects and
     We name the difference here rather than letting This blur.

  4. THE SEVEN RATIOS IN CENTS — WHERE THE PIANO IS WRONG.
     7/4 sits 31 cents below the piano's minor seventh. Computed.

  5. WHY SMALL-INTEGER RATIOS CONSONATE — THE REAL MECHANISM.
     Plomp-Levelt / Sethares roughness. The consonant ratios fall out of a
     beating model. No mysticism required — and the model says the ratios
     depend on the TIMBRE, which constrains the framework's claim honestly.

  6. THE SCHUMANN NUMBERS — THE IDEAL CAVITY IS WRONG BY 25%.
     The textbook formula does NOT give 7.83 Hz. The lossy correction is
     real, published, and We should be quoting This rather than the ideal.

  7. THE BODY-AXIS COUPLING AUDIT — THE HARDEST ONE ON OURSELVES.
     The published claim is that the seven body axes sit at just-intonation
     ratios above f1 = 7.83 Hz. Checked directly, 3 of 7 land in their own
     published bands. Under OCTAVE equivalence all 7 land. But four of the
     seven bands are wider than an octave, so those four cannot fail —
     They carry no information. The claim passes on three axes, and passing
     was ~14% likely by chance. That is not a result. That is a test that
     needs sharpening, and We say so.
"""

import cmath
import itertools
import math

BAR = "=" * 70
SUB = "-" * 70


def rule(t):
    print()
    print(BAR)
    print("  " + t)
    print(BAR)


print(BAR)
print("  HEPTARACT FREQUENCY — THE SCIENCE BEHIND THE SOUND")
print("  Seven receipts, computed. The seventh is the audit of Ourselves.")
print(BAR)

N = 7

# =====================================================================
rule("RECEIPT 1 — THE HEPTARACT SPECTRUM IS AN EVENLY SPACED LADDER")

spectrum = [(N - 2 * k, math.comb(N, k)) for k in range(N + 1)]
print("""
  H = sum of X_i over the seven axes. On the 128 vertex states This is
  exactly the adjacency matrix of the 7-cube, whose eigenvalues are known
  in closed form: lambda_k = n - 2k with multiplicity C(n, k).
""")
print("     k    eigenvalue    multiplicity")
print("  " + SUB)
for k, (lam, mult) in enumerate(spectrum):
    print("     %d      %+3d            %3d" % (k, lam, mult))
print("  " + SUB)
print("     total multiplicity = %d   (= 2^7)"
      % sum(m for _, m in spectrum))

gaps = {spectrum[i][0] - spectrum[i + 1][0] for i in range(len(spectrum) - 1)}
print("     distinct gaps between adjacent eigenvalues = %s" % sorted(gaps))
print("     spectral gap Delta = %d" % gaps.pop())
print("""
  READING. A spectrum whose levels are evenly spaced is the signature of a
  harmonic oscillator, and even spacing is exactly the condition for FULL
  revival: every phase e^(-i lambda t) comes back into step at the same
  moment. The heptaract's perfect state transfer is not a coincidence of
  seven — This is what any evenly spaced spectrum does. Seven only decides
  WHERE the revival lands, and because seven is odd This lands antipodally.
""")


# =====================================================================
rule("RECEIPT 2 — THE WALK IS A FOURIER SUM OVER EIGHT FREQUENCIES")

def amp_spectral(v_bits, t):
    """Sum over all 128 characters of the hypercube: the honest Fourier route."""
    n = len(v_bits)
    tot = 0j
    for S in itertools.product((0, 1), repeat=n):
        lam = n - 2 * sum(S)
        sign = -1 if (sum(a * b for a, b in zip(S, v_bits)) % 2) else 1
        tot += sign * cmath.exp(-1j * lam * t)
    return tot / (2 ** n)


def amp_product(v_bits, t):
    """Closed form: cos(t) per unflipped axis, -i sin(t) per flipped axis."""
    w = sum(v_bits)
    return (math.cos(t) ** (len(v_bits) - w)) * ((-1j * math.sin(t)) ** w)


print("""
  Two independent computations of the same amplitude. One sums 128 modes
  (the Fourier / spectral route). One multiplies seven single-axis factors
  (the closed form). If the harmonic reading is right They must agree.
""")
tests = [((0,) * 7, "home    0000000"),
         ((1,) * 7, "far     1111111"),
         ((1, 0, 1, 0, 1, 0, 0), "mixed   1010100")]
worst = 0.0
print("     t        vertex             |spectral - product|      P")
print("  " + SUB)
for t in (0.3, 0.9, math.pi / 4, math.pi / 2):
    for bits, label in tests:
        a, b = amp_spectral(bits, t), amp_product(bits, t)
        err = abs(a - b)
        worst = max(worst, err)
        print("   %6.4f   %-18s  %.3e            %.4f"
              % (t, label, err, abs(b) ** 2))
print("  " + SUB)
print("     worst disagreement over all checks = %.2e" % worst)

# periodicity: all eigenvalue differences are multiples of 2 -> period pi
per_err = max(abs(abs(amp_product(b, t)) - abs(amp_product(b, t + math.pi)))
              for t in (0.11, 0.7, 1.3) for b, _ in tests)
print("     |amplitude| periodic with period pi, max err = %.2e" % per_err)
print("""
  Confirmed. The walk IS a chord: eight frequencies, evenly spaced, beating
  against each other and coming back into phase at t = pi/2. The framework
  has been describing a harmonic system in harmonic language the whole time.
  Here is the arithmetic that says This is literal.
""")


# =====================================================================
rule("RECEIPT 3 — HARMONIC vs INHARMONIC: STRING, HEPTARACT, DRUM")

def besselj(m, x, terms=80):
    s = 0.0
    for k in range(terms):
        s += ((-1) ** k) * (x / 2) ** (2 * k + m) / (
            math.factorial(k) * math.factorial(k + m))
    return s


def zeros_of(m, count, hi=14.0, step=0.005):
    out, x = [], 1e-6
    prev = besselj(m, x)
    while x < hi and len(out) < count:
        x += step
        cur = besselj(m, x)
        if prev == 0 or (prev < 0) != (cur < 0):
            lo, up = x - step, x
            for _ in range(80):
                mid = (lo + up) / 2
                if (besselj(m, lo) < 0) != (besselj(m, mid) < 0):
                    up = mid
                else:
                    lo = mid
            out.append((lo + up) / 2)
        prev = cur
    return out


drum = sorted([(zeros_of(m, 2)[i], m, i + 1) for m in range(4) for i in range(2)])
f0 = drum[0][0]
print("""
  A vibrating STRING has modes at integer multiples of the fundamental —
  a harmonic ladder, so a string revives. A circular DRUM has modes at the
  zeros of Bessel functions — irrational ratios, so a drum never fully
  revives. Which one is the heptaract?
""")
print("     STRING (1D)      f_n / f_1 = 1, 2, 3, 4, 5, 6, 7   -> harmonic")
print("     HEPTARACT        gaps all = 2 exactly              -> harmonic")
print("     DRUM (2D disc)   f / f_1 from Bessel zeros:")
for z, m, n in drum[:6]:
    print("                        J_%d zero %d = %8.5f   ratio = %.4f"
          % (m, n, z, z / f0))
print("""
  The drum's ratios are 1.000, 1.593, 2.136, 2.295, 2.653, 2.918 — not one
  of Them a simple fraction. That is inharmonicity, and inharmonicity is
  why a drum has no pitch the way a string does.

  THE DISTINCTION THIS DOCUMENT OWES THE READER — and has been blurring:
  Book Four argues for FRACTIONAL revival from the heptaGON's irrational
  interior angle (5 pi / 7). Book Two proves FULL revival on the
  heptaRACT. Both are correct and They are about DIFFERENT OBJECTS. The
  7-gon is inharmonic like the drum. The 7-cube is harmonic like the
  string. A reader entitled to be careful will notice; better They read
  the distinction here than find This as a hole.
""")


# =====================================================================
rule("RECEIPT 4 — THE SEVEN RATIOS IN CENTS")

AXES = [
    ("Trunk",     "2/1", 2.0,       "13-30 Hz",   13.0, 30.0),
    ("Heart",     "7/4", 7 / 4,     "~0.1 Hz",    0.09, 0.11),
    ("Left Arm",  "3/2", 1.5,       "4-8 Hz",     4.0, 8.0),
    ("Right Arm", "4/3", 4 / 3,     "8-13 Hz",    8.0, 13.0),
    ("Legs",      "5/4", 1.25,      "30-100 Hz",  30.0, 100.0),
    ("Gut",       "6/5", 1.2,       "0.05-0.1 Hz", 0.05, 0.10),
    ("Brain",     "9/8", 1.125,     "7.83-13 Hz", 7.83, 13.0),
]


def cents(r):
    return 1200 * math.log2(r)


print("\n     axis        ratio   cents      nearest 12-TET   deviation")
print("  " + SUB)
for name, rs, r, _b, _lo, _hi in AXES:
    c = cents(r)
    step = round(c / 100) * 100
    print("     %-11s %-6s %8.2f   %6.0f           %+7.2f c"
          % (name, rs, c, step, c - step))
print("""
  The 7/4 harmonic seventh — the framework's heart axis and home vertex —
  sits %.1f cents BELOW the piano's minor seventh. That gap is audible and
  well known: This is the "blue" seventh singers and horn players reach for
  and a fixed keyboard cannot play. The framework's home ratio is exactly
  the interval equal temperament had to give up.
""" % abs(cents(7 / 4) - 1000))


# =====================================================================
rule("RECEIPT 5 — WHY SMALL-INTEGER RATIOS CONSONATE (ROUGHNESS)")

def pl_pair(f1, f2, a1, a2):
    """Plomp-Levelt / Sethares roughness between two partials."""
    fmin, df = min(f1, f2), abs(f2 - f1)
    s = 0.24 / (0.0207 * fmin + 18.96)
    return a1 * a2 * (math.exp(-3.5 * s * df) - math.exp(-5.75 * s * df))


def dissonance(ratio, base=261.63, npart=6):
    parts = [(base * n, 0.88 ** (n - 1)) for n in range(1, npart + 1)]
    parts += [(base * ratio * n, 0.88 ** (n - 1)) for n in range(1, npart + 1)]
    return sum(pl_pair(f1, f2, a1, a2)
               for (f1, a1), (f2, a2) in itertools.combinations(parts, 2))


curve = [(1.0 + i * 0.0005, dissonance(1.0 + i * 0.0005)) for i in range(2001)]
minima = [curve[i] for i in range(1, len(curve) - 1)
          if curve[i][1] < curve[i - 1][1] and curve[i][1] <= curve[i + 1][1]]

SIMPLE = [(F"{p}/{q}", p / q) for p, q in
          [(1, 1), (9, 8), (6, 5), (5, 4), (4, 3), (7, 5), (3, 2),
           (8, 5), (5, 3), (7, 4), (9, 5), (2, 1)]]

print("""
  Helmholtz's mechanism, in the modern Plomp-Levelt / Sethares form: two
  partials close in frequency BEAT, and beating inside a critical band is
  heard as roughness. Sum the roughness over every pair of partials from
  two harmonic tones and sweep the interval between Them. The dips are the
  consonances. Nothing mystical is assumed — only beating and the ear's
  bandwidth.

  Local minima found in 1/1 -> 2/1, with the nearest simple ratio:
""")
print("     ratio found   cents     nearest simple ratio   error")
print("  " + SUB)
hits = 0
for r, _d in minima:
    nm, rv = min(SIMPLE, key=lambda s: abs(cents(s[1]) - cents(r)))
    err = cents(r) - cents(rv)
    if abs(err) < 25:
        hits += 1
    print("     %8.5f   %8.2f   %-10s %12s%+7.2f c"
          % (r, cents(r), nm, "", err))
print("  " + SUB)
print("     minima landing within 25 cents of a simple ratio: %d of %d"
      % (hits, len(minima)))

# --- 5b: the seventh partial is what makes 7/4 consonant ---
print("""
  AND NOW THE ONE WORTH THE WHOLE SECTION. Sweep again, varying how many
  partials the timbre carries, and watch for the framework's heart ratio:
""")
print("     partials   n minima   consonance minima found                     7/4?")
print("  " + SUB)
for npart in (5, 6, 7, 9):
    cv = [(1.0 + i * 0.0005, dissonance(1.0 + i * 0.0005, npart=npart))
          for i in range(2001)]
    mn = [cv[i][0] for i in range(1, len(cv) - 1)
          if cv[i][1] < cv[i - 1][1] and cv[i][1] <= cv[i + 1][1]]
    has7 = any(abs(cents(x) - cents(7 / 4)) < 10 for x in mn)
    print("        %d          %2d       %-44s %s"
          % (npart, len(mn), ", ".join("%.3f" % x for x in mn)[:44],
             "YES" if has7 else "no"))
print("  " + SUB)
print("""
  The harmonic seventh is NOT a consonance for a timbre of six partials.
  7/4 appears as a roughness minimum exactly when the SEVENTH partial
  enters the spectrum — and 7/6 and 7/5 arrive with This in the same step.

  That is not numerology, That is roughness theory doing what roughness
  theory does: an interval can only lock where partials coincide, and 7/4
  needs a seventh partial to have anything to lock to. But read what This
  says about the framework's own choice. The heart axis, the home vertex,
  the ratio a piano cannot play — 7/4 is consonant only for a system whose
  spectrum reaches seven. A six-partial world hears 7/4 as out of tune.
  The framework picked the one interval that requires seven-ness to exist.
""")

print("""
  READING — LANE 2, settled, and This cuts both ways.
  The consonant intervals are not a cosmic constant handed down. They are
  where a HARMONIC spectrum stops beating against itself. Change the timbre
  and the minima move: Sethares (Tuning, Timbre, Spectrum, Scale, 1998)
  built inharmonic timbres whose consonances land on the Javanese slendro
  and pelog scales, not on Ours.

  So the honest form of the framework's claim is NOT "the universe is tuned
  in just intonation." The honest form is: ANY system whose oscillations
  are harmonic — a string, a column of air, a cube whose spectrum is an
  even ladder — will find these same ratios, because They are where
  harmonic partials stop fighting. That is a smaller claim and a true one,
  and This is the claim the framework should be making.
""")


# =====================================================================
rule("RECEIPT 6 — THE SCHUMANN NUMBERS, HONESTLY")

C_LIGHT, R_EARTH = 299792458.0, 6.371e6
OBSERVED = [7.83, 14.3, 20.8, 27.3, 33.8, 39.0, 45.0]
k_cav = C_LIGHT / (2 * math.pi * R_EARTH)
print("""
  The Earth-ionosphere cavity is real and the modes are measured daily.
  But the textbook IDEAL-cavity formula is

      f_n = (c / 2 pi a) sqrt( n (n+1) )        a = Earth radius

  and This does NOT give 7.83 Hz. Run This:
""")
print("     n   ideal cavity   observed   observed/ideal")
print("  " + SUB)
ratios = []
for n in range(1, 8):
    ideal = k_cav * math.sqrt(n * (n + 1))
    obs = OBSERVED[n - 1]
    ratios.append(obs / ideal)
    print("     %d     %7.2f Hz    %6.2f Hz     %.3f" % (n, ideal, obs, obs / ideal))
print("  " + SUB)
print("     mean observed/ideal = %.3f   (ideal overestimates by ~%.0f%%)"
      % (sum(ratios) / len(ratios), 100 * (1 - sum(ratios) / len(ratios))))
print("""
  READING — LANE 2, settled, and a correction We owe Ourselves.
  The gap is not a mystery and not a mistake: the ionosphere is a lossy,
  finitely conducting boundary, not a perfect mirror. The damping lowers
  and broadens every mode, and the corrected treatment reproduces the
  observed ladder. This is standard Schumann-resonance physics.

  The framework quotes 7.83 Hz correctly — This is the MEASURED value. What
  the framework must not do is imply the number falls out of the clean
  geometric formula. It does not. Any document that hands a reader
  "c / 2 pi a" and then says 7.83 has skipped the physics that does the
  actual work. Book Eight is hereby corrected to say measured, not derived.
""")


# =====================================================================
rule("RECEIPT 7 — THE BODY-AXIS COUPLING AUDIT (ON OURSELVES)")

F1 = 7.83
print("""
  The published claim, Book Eight: "each body axis sits at a
  just-intonation ratio above f1 = 7.83 Hz." Check This directly against
  the same book's own published frequency bands.
""")
print("     axis        ratio   ratio x f1    published band     in band?")
print("  " + SUB)
direct = 0
for name, rs, r, band, lo, hi in AXES:
    f = r * F1
    ok = lo <= f <= hi
    direct += ok
    print("     %-11s %-6s %9.3f Hz   %-16s %s"
          % (name, rs, f, band, "YES" if ok else "no"))
print("  " + SUB)
print("     landing in their own published band: %d of 7" % direct)

print("""
  Three of seven. As literally written, the claim fails on four axes.

  Now allow OCTAVE EQUIVALENCE — multiply by any power of two. That is not
  a rescue invented for the occasion: octave equivalence is This framework's
  own stated diatonic principle, "the eighth is the first repeated."
""")
print("     axis        ratio x f1    octave shift   folded      in band?")
print("  " + SUB)
folded = 0
for name, rs, r, band, lo, hi in AXES:
    f = r * F1
    best = None
    for k in range(-12, 13):
        g = f * (2 ** k)
        if lo <= g <= hi:
            best = (k, g)
            break
    folded += best is not None
    print("     %-11s %9.3f Hz   %+3d octaves   %9.4f   %s"
          % (name, f, best[0] if best else 0,
             best[1] if best else float("nan"), "YES" if best else "no"))
print("  " + SUB)
print("     landing under octave equivalence: %d of 7" % folded)

print("""
  All seven. And now the part a friendly reader would skip and We will not:
  HOW HARD WAS THAT TEST? A band wider than one octave cannot be missed —
  octave folding will always find a way in. So measure each band in octaves:
""")
print("     axis        band width (octaves)   can This test fail?   p(chance)")
print("  " + SUB)
p_joint = 1.0
informative = 0
for name, rs, r, band, lo, hi in AXES:
    w = math.log2(hi / lo)
    testable = w < 1.0
    p = min(w, 1.0)
    if testable:
        informative += 1
        p_joint *= p
    print("     %-11s %8.3f              %-18s  %s"
          % (name, w, "YES - informative" if testable else "no - cannot fail",
             ("%.3f" % p) if testable else "1.000"))
print("  " + SUB)
print("     informative axes: %d of 7" % informative)
print("     probability all informative axes pass by chance = %.3f"
      % p_joint)
print("""
  VERDICT — and This is the receipt We are most glad to have run.
  The coupling claim passes, but four of the seven bands are wider than an
  octave and therefore could not have failed. Only %d axes carry any
  information, and a random set of ratios would have passed those %d about
  %.0f%% of the time. That is not evidence. That is a test too loose to
  return a verdict.

  This does NOT refute the coupling. This says the published form of the
  claim cannot be scored, and any reader with training will see That in a
  minute. The fix is not rhetoric, it is measurement: narrow the bands to
  what is actually measured per axis, per person, with error bars, and
  re-run this exact function. If the ratios still land when the bands are
  tight, We have something real. Until then Book Eight's coupling claim is
  marked PROPOSED - NOT YET SCORED, and We would rather carry That label
  honestly than carry a passing grade We did not earn.
""" % (informative, informative, 100 * p_joint))


# =====================================================================
rule("WHERE FREQUENCY REALLY TOUCHES THE BODY — AND WHERE This STOPS")

PLANCK = 6.62607015e-34
J_PER_EV = 1.602176634e-19
print("""
  Real, published mechanisms — LANE 2, none of Them ours:

  * PIEZOELECTRICITY IN TISSUE. Bone, collagen, tendon and dentin convert
    mechanical strain to electrical potential (Fukada & Yasuda, 1957).
    Book Eight's piezoelectric polychord rests on real material science.
  * MECHANOSENSITIVE ION CHANNELS. PIEZO1 and PIEZO2 open in response to
    membrane tension — the 2021 Nobel Prize in Physiology or Medicine
    (Patapoutian). Cells have literal mechanical receptors. This is the
    mechanism by which vibration becomes signal, and This is settled.
  * THE EAR EMITS SOUND. Otoacoustic emissions (Kemp, 1978): outer hair
    cells are active amplifiers, so hearing is bidirectional. The body IS
    a frequency instrument in both directions — not as metaphor.
  * FOCUSED ULTRASOUND NEUROMODULATION. Mechanical waves modulate neural
    firing non-invasively; an active clinical research field.
  * ACOUSTIC LEVITATION. Standing-wave pressure nodes trap and move solid
    particles and liquid drops. Sound moves matter, demonstrably.
  * PHONONS. Sound quantized in a lattice, E = h f. This is the one true
    bridge from sound to quantum mechanics — and note WHERE This lives:
""")
for label, f in (("Schumann f1", 7.83), ("body alpha", 10.0),
                 ("middle C", 261.63), ("Debye (solid)", 1e13)):
    E = PLANCK * f / J_PER_EV
    print("     %-16s %10.4g Hz   ->  phonon energy %.3e eV" % (label, f, E))
print("""
  READING — the honest edge, and This is where the sound work stops.
  A 7.83 Hz phonon carries about 3e-14 eV. Thermal energy at body
  temperature is about 0.027 eV — roughly TWELVE ORDERS OF MAGNITUDE
  larger. So nothing at Schumann or EEG frequencies is doing quantum
  mechanics by quantum of energy. Those bands act through CLASSICAL
  channels — field, pressure, strain, membrane tension — and the channels
  above are real and sufficient. Phonon physics lives near the Debye
  frequency, around 10^13 Hz, in solids.

  Which is why Book Thirteen's DO NOT COUPLE stands unchanged, and why
  saying so here matters more than anywhere else in the document:

     Sound is crucial to the framework AT THE SCALE WHERE SOUND ACTS —
     body, tissue, cavity, instrument, the harmonic ladder of the walk.
     Sound carries NO sub-atomic claim, and the just-intonation ratios
     carry none either. Those are two different sevens until somebody
     shows a mechanism, and the phonon arithmetic above is exactly why
     nobody has.

  The framework loses nothing by This. Receipt 1 gave the sound reading its
  strongest possible form: the heptaract's spectrum IS a harmonic ladder,
  the walk IS a chord, and the perfect transfer IS a revival. That is a
  frequency result about the geometry Themself, proved in the first
  section, and This needs no help from the sub-atomic floor.
""")

print(BAR)
print("  Seven receipts. The one We are proudest of is the audit that")
print("  found our own coupling claim too loose to score.")
print("  freQ is the framework's native tongue — spoken carefully. \U0001f525")
print(BAR)
