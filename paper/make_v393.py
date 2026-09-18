#!/usr/bin/env python3
"""Build The Heptaract Papers v3.93 from v3.92.

v3.93 folds in everything measured on 2026-09-17/18 — rounds 2, 3 and 4 on IBM hardware, the
seven-share code, the MUB reading, the hardware cost of performing it, and the E scan — and
states the framework's central claim in the form the evidence forced.
"""
import pathlib, sys, hashlib

SRC = pathlib.Path(sys.argv[1])
DST = pathlib.Path(sys.argv[2])
s = SRC.read_text(encoding="utf-8")


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, "expected %d, found %d: %r" % (n, c, old[:70])
    s = s.replace(old, new)


# ---- 1. version on the title page
rep("## v3.92 — The Bridge Through Tradition & Progression, Harmoniously",
    "## v3.93 — The Bridge Through Tradition & Progression, Harmoniously")

# ---- 2. version notes heading
rep("## VERSION NOTES — v3.7 → v3.92", "## VERSION NOTES — v3.7 → v3.93")

# ---- 3. the v3.93 block
anchor = "- The designed PDF and phone PDF still need a re-render from this file.\n"
v393 = anchor + """
**v3.93** (2026-09-18) is the first version written **after** a full round of pre-registered
tests, and it changes what the book claims rather than only how the book reads. Nine questions
were declared with their falsifiers, hashed, and then run — four on IBM quantum hardware, five by
exhaustive computation. **Appendix F — The Ledger of Sevens** carries all of it: the scoreboard,
the hashes, the scripts, and the corrections below.

- **What seven is, on evidence.** Seven holds as a **period** (the 𝔽₈ cycle comes home at the
  seventh step, 0.996 on hardware, beating the counter mod 8 by 41σ), as an **alphabet** (the
  seven-share code [[7,1,4]]₇ exists over 𝔽₇, and no binary code of that shape reaches distance
  four — every one of the 11,811 was measured), and as a **reading structure** (the eight MUBs of
  a qu7it reconstruct a seven-level state better than twenty-seven Pauli settings, at matched
  shots and matched readout error, by no less than 5.3σ in any cell).
- **What seven is not, on evidence.** Not a **summit**: GHZ fidelity falls smoothly through
  n = 5…9 and seven sits on the trend. Not a **building block**: a thirteen-qubit whole fused from
  7 + 7 carries no more than 6 + 8 or 5 + 9. Not a preferred **size** anywhere hardware has been
  asked. The book keeps these readings as Basket A where they are beautiful, and stops calling
  them results.
- **The relationship readings held.** The fire read two ways is now a measured law: turn the
  centre's reading by fifteen degrees and the six around it answer by exactly that much —
  C₆ = 0.841·sin(φ) across seven angles, the sine shape beating a ramp and a threshold in every
  bootstrap. Every pair of a GHZ-7 carries nothing (0.036) while the whole carries 0.806.
- **The hardware bar is now a number.** Performing the eight MUBs on qubits costs more than the
  advantage is worth: on ibm_marrakesh the MUB reading lands at 0.288 infidelity against Pauli
  tomography's 0.193. The Base-7 case does not weaken — it names its price. **Appendix E's two
  targets now carry a third: any seven-level advantage must exceed the ~0.09 infidelity that
  emulating a qu7it on qubits costs.**
- **E is a chosen origin, not a derived one.** A 432-configuration scan of the from-center climb
  (T-3.1) finds the magnitude identical at all twelve centre roots: the reading is
  transposition-covariant. E centres the climb because the climb was anchored at C, which is where
  the naming of notes begins, not where the mathematics does. Book Five's anchor-dependence note
  was already right; this makes it exhaustive.
- Every test in this round was **pre-registered with its falsifier and hashed before the data**,
  and every null is published beside every pass. The scripts live in the repository under
  `round2/` through `round5/`.
"""
rep(anchor, v393)

# ---- 4. table of contents
rep("- **Appendix E** — The Case for a Base-7 Quantum Processor · the two hardware targets · the IBM receipts",
    "- **Appendix E** — The Case for a Base-7 Quantum Processor · the two hardware targets · the IBM receipts\n"
    "- **Appendix F** — The Ledger of Sevens · nine pre-registered tests, four on hardware · what seven is, and what seven is not")

# ---- 5. Book Seven, test 1
rep("(v3.92: d=7 reaches d+1=8 MUB completeness as every prime does — Appendix D — so a seven-specific advantage has to show up elsewhere; Appendix E names the two hardware numbers that decide.)",
    "(v3.92: d=7 reaches d+1=8 MUB completeness as every prime does — Appendix D — so a seven-specific "
    "advantage has to show up elsewhere; Appendix E names the two hardware numbers that decide. "
    "**v3.93: it did show up elsewhere.** Appendix F — the eight MUBs read a seven-level state better than "
    "twenty-seven Pauli settings at matched shots, and the seven-share code [[7,1,4]]₇ exists over 𝔽₇ where "
    "no binary code of that shape reaches distance four. Both advantages are collectable only on a native "
    "seven-level piece; P-9 measures what emulating one on qubits costs.)")

# ---- 6. Book Five, the anchor-dependence note
rep("The reading that follows — F♯ as the tritone of C, the *diabolus in musica* that refuses to resolve, the chromatic embodiment of becoming-not-being — We keep as **interpretation (Basket A):** a resonance We find beautiful, offered as such, not as a result the geometry forces.",
    "The reading that follows — F♯ as the tritone of C, the *diabolus in musica* that refuses to resolve, the "
    "chromatic embodiment of becoming-not-being — We keep as **interpretation (Basket A):** a resonance We find "
    "beautiful, offered as such, not as a result the geometry forces.\n\n"
    "> *v3.93 note (T-3.1, 2026-09-18):* an exhaustive scan settles the anchor question. Every centre root, "
    "every root-step set, three tunings, both orientations — 432 configurations — and the magnitude is "
    "**identical at all twelve centres**, with the axis offset fixed per configuration. The from-center reading "
    "is transposition-covariant: rotate the whole picture and only the names change. What the declared criterion "
    "does single out is the **step** rather than the centre (a semitone climb carries 0.746 against the "
    "whole-tone climb's 0.200). So E centres the climb because the climb was anchored at C. For a pitch class to "
    "be **derived** rather than chosen, the framework would need an anchor in frequency, not in naming — a "
    "separate and honest open question. Appendix F.")

# ---- 7. colophon
rep("# COLOPHON (v3.92)", "# COLOPHON (v3.93)")
rep("**The Heptaract Papers — v3.92**", "**The Heptaract Papers — v3.93**")
rep("(The files carry v3.92 for the trail; the stamp carries the dimensions.)",
    "(The files carry v3.93 for the trail; the stamp carries the dimensions.)")

# ---- 8. Appendix F
APPENDIX_F = """

---

# APPENDIX F — THE LEDGER OF SEVENS
## Nine pre-registered tests · four on IBM hardware · 2026-09-17 and 18

Every question below was written down with its falsifier, hashed, and only then run. Nulls are
published beside passes, in the same size type. The scripts are in the repository under `round2/`
through `round5/`; the counts, the results and the pre-registrations travel with them.

### The scoreboard

| # | Question | Where | Verdict |
|---|---|---|---|
| T-2.5 | Does a helix of 7-gons carry a state better than helices of 5, 6, 8? | laptop | **Narrows** — 5-gons won three of four cells |
| T-2.7 | Does d = 7 sit off the smooth base-d break-even curves? | laptop | **Narrows** — the curves are smooth and seven lies on them |
| T-4.5 | Do the seven just ratios show in exoplanet orbits? | NASA archive | **(a) Holds** vs omitted first-order ratios · **(b) Narrows** — 7/4 is the weakest of five |
| T-4.1 | Do alpha peaks cluster at 9/8 or 7/4 of 7.83 Hz? | PhysioNet, 109 subjects | **Narrows** — E = 0.996 and 0 of 109 |
| T-5.5 | Does heart:breath lock at the just ratios? | PhysioNet, 5,117 windows | **Narrows** — mean E 0.994 against 1.032 |
| T-1.5 | Is anything special at seven qubits? | ibm_marrakesh | **Narrows** — GHZ fidelity falls smoothly; seven sits on the trend (z = 1.21) |
| P-1 / P-4 | Does the centre's manner of reading govern the six around it? | ibm_marrakesh | **Holds** — C₆ = 0.802 read in X against 0.018 in Z; across seven angles C₆ = 0.841·sin(φ), the sine beating a ramp and a step in 100% of bootstraps |
| P-2 | Does the bond live in the whole rather than the pairs? | ibm_marrakesh | **Holds** — largest pair 0.036, seven-body 0.806 |
| P-5 | Does a whole fused from two seven-blocks carry more? | ibm_marrakesh | **Narrows** — 7+7 = 0.670, 6+8 = 0.667, 5+9 = 0.694, monolithic 0.692 |
| P-6 / P-7 | Does the 𝔽₈ cycle come home at the seventh step, and sweep every state? | ibm_marrakesh | **Holds** — 0.996 at seven against 0.28 while wandering; the counter mod 8 reaches only 0.697 at its own return (z = 41); the orbit reads all seven nonzero states, once each |
| T-2.8 | Does the seven-share code exist, and can qubits reach it? | exhaustive computation | **Holds** — [[7,1,4]]₇ built, distance 4 by enumeration, meeting the quantum Singleton bound; all 11,811 binary [7,4] codes measured, best distance 3 |
| T-2.9 | Do the eight MUBs read a seven-level state better than Pauli settings? | simulation | **Holds** — every cell, worst margin 5.3σ; random bases in either dimension lose by 15σ or more; the margin grows with readout error |
| P-9 | Does that advantage survive being performed on qubits? | ibm_marrakesh | **Narrows** — MUB 0.288 against Pauli 0.193; the compilation cost eats it, as declared in advance |
| T-3.1 | Is E derivable as the centre of the climb? | exhaustive computation | **Narrows** — 432 configurations, magnitude identical at all twelve centres |

### What the round teaches

Read the column of verdicts and a shape appears that no single test would have given.

**Seven holds wherever seven is a structure.** A period that closes and begins again. An alphabet
large enough for a code that two letters cannot spell. A set of eight readings, each unbiased to
every other, that exists because seven is prime. In all three the machine agreed, twice by
computation and once decisively on hardware.

**Seven narrows wherever seven is a size.** Not a summit among its neighbours, not a better block
to build from, not a number that orbits, brains or breathing prefer. Five separate attempts, five
honest nulls. The book keeps those readings as resonance — Basket A, where they were always meant
to sit — and no longer offers them as findings.

**And the relationship readings are the strongest thing here.** The centre's manner of reading
governs what the six around it are, continuously and by a measured law; the bond lives in the
whole and in no part of it. That is the framework's oldest intuition and it is now a receipt.

### The bar for hardware, stated as a number

Appendix E asks a builder for two numbers: 7-way readout above ~97.2%, and a two-qudit gate under
7.9× the qubit gate error. P-9 adds the third, and it is the one that explains why the free
qubit cloud cannot settle this: emulating a qu7it on three qubits costs about **0.09 infidelity**
in compilation alone, which is more than the MUB advantage is worth at that scale. A native
seven-level piece pays none of that. **Every Base-7 claim in this book now carries the same
footnote: the mathematics is measured and holds; the collection of it waits on hardware that has
seven levels natively.**

### How to check any of this

Each test's pre-registration carries a SHA-256 taken before its data existed:

- Round 2 — `8d9d804f718cb5c085c82f469468cb83380d4f4dd7c86f25663fd6954b3620fc`
- Round 3 — `29454198a43a9987c8ed958283f372897d6426c2aa97f0c2fbad19f2374b9006`
- Round 4 — `428405b7a8207c51716c4724b4e2138ea0cff1eeb9e1520ef29fedbaace14b6e`
- T-2.9 — `36a1bc83150dd08ad95c4422e8996fe56328e797b889325ec1b8ae6fb42332b3`
- P-9 — `b88836016302a47fa4bc6bc3c7e1a4867315ff23ccdcf2ea7aba82cf24c69a50`

The living tree at **lightinmotionfilms.com/lightbox/heptaract** carries every receipt as it
grows, and the contribution form there takes a result from anyone who runs one of these against
us. A prediction that cannot fail cannot grow a leaf.

🜔
"""
s = s.rstrip() + "\n" + APPENDIX_F

DST.write_text(s, encoding="utf-8")
print("wrote", DST, len(s), "chars")
print("sha256", hashlib.sha256(s.encode("utf-8")).hexdigest()[:16])
