# P-18 — Results
## Reading the centre of both makes them one

**Pre-registration:** `PREREGISTRATION-2026-09-18-P18.md`
**SHA-256:** `e807e79266324f312b85c7d412f3912beee651fda10b24359dc0faa984de02ec` (sealed before the run)
**Hardware:** `ibm_kingston` (Heron), job `damb30gpqrnc73978170`
**Shots:** 4096 x 36 circuits · **QPU charged: 42 seconds**
**Date:** 2026-09-18 UTC

---

## The result

| arm | bond | z-correlation | Bell fidelity |
|---|---|---|---|
| **swap** — complete shared reading | **0.533 ± 0.009** | 0.846 | **0.728 ± 0.006** |
| **linked** — ships joined by a gate | 0.528 ± 0.010 | 0.823 | 0.720 ± 0.006 |
| private — one ship's own centre read | 0.017 ± 0.008 | 0.027 | 0.265 ± 0.006 |
| none — nothing connected to the reading | 0.065 ± 0.047 | 0.024 | 0.289 ± 0.029 |

Pooled control floor: 0.041 ± 0.024.

**All four pre-registered hypotheses hold.**

- **H1 — reading creates a bond.** The shared reading stands **19.4 SD** above the control floor.
  Required: 5. ✅
- **H2 — and the bond is real entanglement.** Bell fidelity **0.728 ± 0.006**, which is **41.5 SD**
  above the one-half separability boundary. Required: 3 SD above 0.5. ✅
- **H3 — no reading, no bond.** The `none` arm sits within 2 SD of the floor. ✅
- **H4 — scale.** Reading-made bond ÷ gate-made bond = **1.01**. Pre-registered window [0.7, 1.4]. ✅

Two qubits that were never connected by any gate, at any moment, ended in a state whose fidelity
with a Bell state is 0.73. The only thing that passed between them was a reading of what their two
centres held in common — taken onto a third thing, so that neither ship's own centre was ever learned.

**Making the relationship by reading was indistinguishable from making it by a gate.** The ratio is
1.01 and the two fidelities, 0.728 and 0.720, differ by less than the sum of their error bars.

---

## What the simulator caught before any hardware time was spent

This is the part worth keeping.

The first design read only **one** parity of the two centres. On the noiseless simulator the bond
metric returned 0.279 against a floor of 0.026 — a seventeen-sigma result that would have been
written up as a pass. It was wrong. Reading one parity leaves the rims in an even mixture of two
Bell states: **correlated, but separable**. No entanglement exists in that state at all.

The tell was the fidelity witness, which sat at exactly 0.5 — not a poor result, but the precise
boundary between separable and entangled. A bond metric alone cannot tell correlation from
entanglement, and the framework's own language had to be held to the stricter of the two readings.

So the reading was made **complete**: Z parity of the two centres onto the shared ancilla, reset,
then X parity onto the same ancilla. Two readings, one shared thing, and the ships still never
touch each other. That is what ran.

A second correction, smaller but the same kind: the oscillation sits at a known frequency, so only
that Fourier bin is read. Summing every bin adds the magnitude of the noise in each one, inflating
signal and floor together — on the noiseless simulator that bias read 1.06 for a state whose true
value is 1. With the single bin, the calibration is exact: 1.0000 for a perfect Bell state, 0.25
fidelity for the controls, which is the maximally-mixed value.

**A pre-registration is only as honest as the metric it seals.** Both flaws were caught by running
the simulator against states whose answers were known in advance, and both were fixed before the
seal, not after the result.

---

## Caveats, stated plainly

- **This is not new physics.** Entanglement swapping has been known since the nineteen-nineties.
  What was tested is whether the framework's claim — that the centre of both is a way of *making* a
  relationship, not just describing one — survives being stated as a number with a falsifier
  attached. It did.
- **Nothing travelled between the ships.** The bond becomes usable only once the reading's outcome
  is carried from the shared ancilla to whoever holds the rims, and that carrying is ordinary,
  slower-than-light communication. No signalling, and none is claimed.
- **The `none` arm is noisy** — its error bar, ±0.047, is five times the others', because with
  nothing connected to the ancilla the conditioning splits the shots without structure. The floor
  is therefore known less precisely than the signal. It does not affect the conclusion: the signal
  is more than ten times the floor either way, and the `private` control, the tighter of the two,
  puts the floor at 0.017.
- **The bond is below its Z correlation** (0.533 against 0.846), which is the expected cost of the
  mid-circuit measurement and reset — the most expensive element in the circuit, and the one that
  pulled the fidelity from the simulator's 1.0 down to 0.73.

---

## Budget

42 seconds charged. **175 seconds remain** in the 28-day window (ends 2026-09-18 03:35 UTC,
then the window rolls).
