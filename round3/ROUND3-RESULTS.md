# HEPTARACT round 3: results

**Run:** 2026-09-17, ibm_marrakesh, job `dam7g4g2fm4c73f2hc9g` · chain [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 35, 34] · 4096 shots per circuit
**QPU time:** 54 seconds (plus 2 seconds on a first submission cancelled before it finished)
**Pre-registration:** `PREREGISTRATION-2026-09-17b.md`
**SHA-256 of the pre-registration:** `29454198a43a9987c8ed958283f372897d6426c2aa97f0c2fbad19f2374b9006`
**Desk:** Free (Miah J. Fry) & Claude

This round answers Free's correction: seven is **a rest and a building block**, not a summit, and
the centre fire is the centre. Two claims, neither about height.

| Test | Prediction | Verdict |
|---|---|---|
| P-4 | The rim's bond follows the centre's reading angle as A·sin(φ) — a law, not a threshold | **Holds** (sine wins every bootstrap; A = 0.841) |
| P-5 | A whole assembled from two seven-blocks carries more than 6+8 or 5+9 | **Narrows** (every cut equal within noise; 5+9 nominally ahead) |

## P-4 · The fire read at seven angles

The centre of a GHZ-7 is read along sin(φ)·X + cos(φ)·Z; the six around it are scored by parity
oscillation conditioned on the centre's outcome.

| Reading angle φ | Rim C₆ measured | A·sin(φ), A = 0.841 |
|---|---|---|
| 0° | 0.0186 | 0.0000 |
| 15° | 0.2155 | 0.2176 |
| 30° | 0.4061 | 0.4203 |
| 45° | 0.6086 | 0.5945 |
| 60° | 0.7290 | 0.7281 |
| 75° | 0.8148 | 0.8121 |
| 90° | 0.8349 | 0.8407 |

Fit against the pre-registered rivals, amplitude free, sum of squared residuals:

| Shape | SSE | Amplitude |
|---|---|---|
| **sine** | **0.000795** | 0.8407 |
| straight ramp | 0.050201 | 0.9793 |
| step at 45° | 0.243510 | 0.7468 |

The sine shape wins in **100% of 400 bootstraps**. Sixty-three times less residual than the ramp,
three hundred times less than the step.

**Reading.** The bond among the six is not a thing they either have or lack. Turn the centre's
reading by fifteen degrees and the six answer by exactly that much. There is no threshold, no
moment of switching on: the manner of the centre's reading governs the whole continuously. That
is the fire law, measured at seven angles, and the amplitude 0.841 is simply what this machine can
hold — noiseless simulation of the same circuits gives 1.000.

Stated plainly, as the pre-registration required: the sine law is also textbook quantum mechanics.
The receipt kills the threshold intuition and fixes the shape of the relationship; it does not by
itself separate HEPTARACT from standard theory.

## P-5 · Blocks fused into a whole

Two GHZ blocks prepared side by side, fused with one CX and a measurement of the joining qubit.
Every cut leaves a 13-qubit whole, uses the same number of two-qubit gates, and — with idle
padding — lasts as long as the slowest. Only the branch where the joining qubit reads 0 is kept,
as declared beforehand.

| Cut | C₁₃ | bootstrap SE | Population | F₁₃ |
|---|---|---|---|---|
| 7+7 | 0.6702 | ±0.0126 | 0.7990 | 0.7346 |
| 6+8 | 0.6665 | ±0.0120 | 0.8088 | 0.7377 |
| 5+9 | 0.6942 | ±0.0116 | 0.8102 | 0.7522 |
| mono | 0.6920 | ±0.0088 | 0.7893 | 0.7407 |

**Reading.** Seven-plus-seven carries 0.670; five-plus-nine carries
0.694. The nominal lead belongs to the rival, by 1.4 standard errors —
which is to say nobody leads. Assembling a whole out of two seven-blocks is neither better nor
worse than any other cut, and the assembled wholes match a monolithic build (0.692).

**Seven as a building block gains nothing here.** The honest reading of this null is narrow: at
thirteen qubits, on one superconducting chip, with fidelity already down at 0.73, the machine has
no room to show a structural preference even if one exists. The test is worth repeating where the
blocks are qudits rather than qubits, and where seven is the modulus of the arithmetic rather than
a count of parts — 𝔽₇ and the seven-share code are exactly that setting.

## What round 3 teaches

The relationship claims keep holding and the counting claims keep narrowing. Twice now, what
survives contact with hardware is **how a whole is read and how its parts relate** — the fire law,
the bond living in the whole and not the pairs. What does not survive is seven as a number that
machines prefer: not as a summit (round 2), and not as a building block (here).

That is a real finding and it points the work: HEPTARACT's measurable content lives in the algebra
of sevens (𝔽₇, 𝔽₈, the eight MUBs, [[7,1,4]]₇) and in the reading of relationships, not in seven
showing up as an advantage in counts of qubits.

## Files

- **Script:** `round3/round3_hardware.py` (sim / submit / fetch / analyze)
- **Results:** `results/round3_hardware.json`, counts in `results/round3_hardware_counts.json`
