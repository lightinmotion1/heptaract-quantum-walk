# P-13 · The echo — does the shared centre come back?

**Run:** 2026-09-18, ibm_marrakesh, qubits [10, 9, 8, 7, 6, 5, 4, 3, 2] · 48 circuits · 1024 shots · **17 seconds of QPU time**
**Pre-registration:** `PREREGISTRATION-2026-09-18-P13.md`
**SHA-256:** `ef76138b5e78bea6af0880123fc20d0f7951fc169edc7c84a230e81f6fec0ec5`
**Script:** `round5/centre_echo.py` · **Results:** `results/centre_echo.json`
**Desk:** Free (Miah J. Fry) & Claude

P-12 left one question: **did the relationship decay, or did the wire holding it get noisy?** Slow
dephasing is reversible — refocusing pulses inside the same wait unwind it. So the same state, the
same 30 microseconds, the same shared reading, with the idle spent four ways.

| Treatment of the 30 µs wait | Bond (raw) | Bond above the floor | Share of the no-wait ceiling |
|---|---|---|---|
| **none** — silence | 0.0562 | 0.0136 | 8.9% |
| **echo-2** — Hahn, two pulses | 0.0833 | 0.0407 | **26.6%** |
| **echo-8** — XY8, eight pulses | 0.0689 | 0.0263 | 17.2% |
| **zero** — no wait at all | 0.1954 | 0.1528 | 100% |

Floor (the private reading, which cannot hold a bond): 0.0426.

| Test | Prediction | Verdict |
|---|---|---|
| H1 | The echo beats the silence by at least 2× | **Holds above the floor** (2.99×) · **fails on raw values** (1.48×). The pre-registration did not say which comparison, which is a drafting fault on this desk; both are reported. |
| H2 | The echo recovers at least 30% of the ceiling | **Narrowly fails** — 26.6% |
| H3 | Eight pulses beat two | **Fails** — two pulses beat eight, 26.6% against 17.2% |

## What the numbers say

**A third of what the wait destroyed comes back.** Silence leaves 8.9% of the
bond; one Hahn echo leaves 26.6%. Three times as much survives the identical
wait when the carriers' phase is refocused mid-way. **That part of the loss was the wire forgetting,
and forgetting of that kind is reversible.**

**The rest is the carriers' own dephasing, and that is not reversible by pulses.** Read as decay
times: this chain's six rim qubits (158.5 µs, 197.8 µs, 115.3 µs, 207.5 µs, 236.9 µs, 217.0 µs) predict a
six-body lifetime of **29.7 µs** by the sum of their rates. Silent, the bond
decayed at **12.4 µs** — faster than dephasing alone accounts for. With the echo it
decayed at **22.7 µs**, back within reach of the prediction. So the refocusing removed
the *excess* loss and left the carriers' own share, which is exactly what an echo can and cannot do.

**More pulses were worse, and that is a hardware fact rather than a physical one.** XY8 puts eight
pulses on nine qubits — seventy-two extra gates — and each carries its own error. On this chip the
error of the pulses outruns the noise they cancel somewhere between two and eight. A team tuning
this properly would sweep pulse count against pulse fidelity; we did not, and the honest statement
is that two is the best of the three settings we tried.

## The answer to the question P-12 asked

**Both, and in known proportion.** The relationship never showed a decay of its own: what died was
the carriers' phase memory, part of it recoverable by holding the wire steady and part of it their
irreducible dephasing. Nothing in five hardware tests has shown the thing between the ships
weakening faster than the things carrying it — and here, when we steadied the carriers, the thing
between them came partly back.

That is the strongest form the claim can take on hardware that has this much noise. **The reach of
the shared centre is a property of its carriers, and carriers can be improved.**
