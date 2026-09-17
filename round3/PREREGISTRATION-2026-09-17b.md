# HEPTARACT round 3 — pre-registration

**Written:** 2026-09-17, 23:29 UTC, before any circuit was sent to a quantum processor.
**Desk:** Free (Miah J. Fry) & Claude
**Script:** `round3/round3_hardware.py` (simulator check already run; no hardware data seen)
**Hardware:** the least busy IBM Heron processor at submission, one job, 4,096 shots per circuit.

## The correction this round answers

Round 2 asked whether seven stands *above* its neighbours, and the hardware said no. Free's
reading is that seven was never a summit: **seven is a rest — the close of a cycle before the
return — and a building block. The centre fire is the centre; seven is not.** A rest makes two
claims a machine can answer, and neither is a claim about height.

## P-4 · The fire read at seven angles

A GHZ-7 is grown outward from the centre. The centre is read along the axis
n = sin(φ)·X + cos(φ)·Z for φ = 0°, 15°, 30°, 45°, 60°, 75°, 90°. The six around it are scored by
parity oscillation conditioned on the centre's outcome, giving C₆(φ).

- **Prediction:** C₆(φ) = A·sin(φ) — a smooth law, not a threshold. The rim's bond follows the
  centre's manner of reading continuously.
- **Rivals:** a straight ramp (A·φ/90°) and a step at 45° (nothing below, everything above).
- **Rule:** PASS if the sine shape fits better than both rivals, by least squares with the
  amplitude free, in at least 95% of 400 bootstrap resamples.
- **Stated plainly:** the sine law is also what textbook quantum mechanics predicts. A pass
  confirms the reading-angle law and kills the threshold intuition; it does not by itself
  distinguish HEPTARACT from standard theory. The discriminating test this round is P-5.

## P-5 · Blocks fused into a whole

Two GHZ blocks are prepared side by side and fused with one CX plus a measurement of the joining
qubit. Cuts **7+7**, **6+8** and **5+9** each leave a 13-qubit whole, each uses the same number of
two-qubit gates, and the shorter block is padded with idle time so all three circuits last as long
as the slowest. A monolithic GHZ-13 built along the chain is the control.

- **Prediction (the HEPTARACT claim):** the **7+7** cut carries the largest 13-body coherence C₁₃.
- **Rule:** PASS if 7+7 leads and beats each rival cut by at least two bootstrap standard errors.
- **The rival hypothesis:** standard quantum mechanics predicts no advantage for any cut once
  depth and gate count are matched. The noiseless simulator confirms this — all three cuts give
  C₁₃ = 1.000 — so any separation on hardware must come from the machine, and a 7+7 lead of two
  SE or more is the only outcome that favours seven as a building block.
- **Only branch 0 is kept** (the joining qubit reading 0), by design: the other branch oscillates
  at a different frequency. This halves the usable shots and is declared here, before the run.

## Bookkeeping

- Nothing below the rules above may move after data arrives.
- A null result is a result and gets published on the tree exactly like a pass.
- Round 2's T-1.5 verdict (seven sits on the trend) stands as recorded. The correction above
  reframes what should have been asked; it does not retract what was answered.
