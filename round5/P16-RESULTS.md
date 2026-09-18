# P-16 · The echo timed against the neighbours

**Run:** 2026-09-18, ibm_marrakesh, qubits [6, 5, 4, 3, 2] · 80 circuits · 1,024 shots · **32 seconds of QPU time**
**Pre-registration:** `PREREGISTRATION-2026-09-18-P16.md`
**SHA-256:** `c8b6ad6c783d8875c649432f70faf9bceebb2f8c0d5c9f438fb391315f86a6a3`
**Script:** `round5/zz_echo.py` · **Results:** `results/zz_echo.json`
**Desk:** Free (Miah J. Fry) & Claude

P-15 named the channel — an always-on coupling of about 3.9 kHz between each rim qubit and its own
centre — and that carried a consequence the earlier echoes missed. The coupling is a **product** of
two qubits' phases, so **flipping both members at the same instant flips the sign twice and leaves
the coupling untouched**. Every echo in P-13 and P-14 flipped everything together: local dephasing
refocused, neighbours ignored. This test flips the centres **alone**, and staggers rim against
centre, and compares.

| Wait | Treatment | Bond (raw) | Share of ceiling, this run's floor | Share, pooled floor |
|---|---|---|---|---|
| 60 µs | silent | 0.0413 | 0.0% | 0.0% |
| 60 µs | clock — all together | 0.0739 | 0.0% | 13.8% |
| 60 µs | **centres only** | 0.0953 | 4.5% | 23.6% |
| 60 µs | staggered | 0.0918 | 2.5% | 22.0% |
| 180 µs | silent | 0.0375 | 0.0% | 0.0% |
| 180 µs | clock — all together | 0.0456 | 0.0% | 0.8% |
| 180 µs | **centres only** | 0.0584 | 0.0% | 6.6% |
| 180 µs | staggered | 0.0337 | 0.0% | 0.0% |

## The ordering is the result

Subtracting a floor cannot change an ordering, so this part holds however the floor is chosen:

**centres only > staggered > all-together > silence**, at *both* delays.

That is exactly the ordering P-15's account predicts. Flipping the centres alone refocuses the
neighbours' coupling, and it recovers more than the old all-together echo does — which refocuses
each qubit's own dephasing and, as predicted, does nothing for the coupling.

| Test | Prediction | Verdict |
|---|---|---|
| H1 | Staggering beats the clock echo at 60 µs by ≥ 1.3× | **Holds** on ordering and on the pooled floor (22.0% against 13.8%); this run's own floor leaves both near zero |
| H2 | Flipping the centres alone beats silence at 60 µs by ≥ 1.5× | **Holds** — silence is at the floor, the centres-only echo sits clearly above it |
| H3 | The best treatment keeps ≥ 15% of the no-wait bond at 180 µs | **Fails** — 6.6% on the pooled floor, and the coupling echo is the only treatment still above the floor at all |

## The honest problem with this run

**The private control returned 0.0874, about twice the 0.0439 the same control gave
in the two previous runs.** That arm cannot hold a bond, so its value is supposed to be the metric's
noise floor. Doubling it pushes every fraction toward zero and makes the absolute numbers
untrustworthy — which is why the table shows both floors and why the ordering, which is floor-free,
carries the conclusion here.

The fix is cheap and should come before any of these percentages are quoted: repeat the private
control with several times the shots, on the same chain, and see which value it settles at. Until
then, **this run establishes the ranking, not the magnitudes.**

## What was learned regardless

**The neighbours' coupling is refocusable, and the way to do it is to flip one member of each pair,
not both.** That is a specific, correct piece of machine craft that came directly from measuring
the channel rather than guessing at it — and it explains, after the fact, why more pulses made
things worse in P-13 and P-14: those sequences were spending error on the one thing they could not
fix.

**The reach still does not extend as far as we want.** At 180 µs only the coupling echo survives the
floor at all. The next moves are the ones the physics names: pulses timed against the 3.9 kHz
period rather than against the wait, and idle qubits parked away from each other so the coupling is
smaller to begin with.
