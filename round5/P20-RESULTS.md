# P-20 — Results
## H0 failed. The run is void for its own hypotheses — and says something larger.

**Pre-registration:** `PREREGISTRATION-2026-09-18-P20.md`
**SHA-256:** `7be33a79a8ec23f7a745a93d488a3a3c073ae9c3de2782875ad7f2de03840141` (sealed before the run)
**Hardware:** `ibm_kingston` (Heron), job `dambm90pqrnc739795k0`
**Shots:** 4096 x 54 circuits · **QPU charged: 62 seconds**
**Date:** 2026-09-18 UTC

# VERDICT: H0 FAILED. H1–H4 ARE UNREADABLE AND ARE NOT REPORTED.

The pre-registration says, in its own words: *"If H0 fails, nothing else in this run is
interpretable and no other hypothesis may be read."* H0 failed. The analysis script nonetheless
printed `"mechanism": "neighbours"`. **That output is void and is not a finding.** It is recorded
here only so that nobody later mistakes a printed string for a result.

---

## What failed

`naive` was P-19's two-hop circuit, run again to reproduce its collapse. P-19 gave a bond of 0.062.

**`naive` gave 0.577.** Two hops worked.

| view | bond | z-correlation | Bell fidelity |
|---|---|---|---|
| ceiling — a bond made by a gate | 0.920 ± 0.003 | 0.937 | 0.944 ± 0.002 |
| one hop | 0.751 ± 0.007 | 0.781 | 0.821 ± 0.005 |
| **two hops (`naive`)** | **0.577 ± 0.009** | 0.674 | **0.707 ± 0.006** |
| `parked` | 0.558 ± 0.010 | 0.626 | 0.686 ± 0.007 |
| `parallel` | 0.433 ± 0.010 | 0.339 | 0.551 ± 0.007 |
| `parked_parallel` | 0.446 ± 0.010 | 0.334 | 0.557 ± 0.007 |
| floor — one reading short | 0.011 ± 0.008 | 0.040 | 0.266 ± 0.006 |
| floor — no reading | 0.016 ± 0.008 | 0.004 | 0.259 ± 0.005 |

---

## What the failure of H0 establishes

Two hops on `ibm_kingston` reached **62.7% of the gate-made ceiling**, with a Bell fidelity of
**0.707 ± 0.006 — 32.8 SD above the one-half line.** Entanglement was witnessed end to end, between
two qubits that never touched, were never linked, and were never read together.

And the multiplicative arithmetic lands. One hop kept 81.6% of the ceiling, so a constant per-hop
cost predicts **0.665** at two hops. Observed: **0.627**.

**So the centre does appear to compose, and the cost does appear to be multiplicative — which is
what P-19's H1 and H4 predicted and P-19's data denied.**

This cannot be claimed as a pass. P-19 failed as written and stays failed; P-20 failed its own H0
and cannot pass hypotheses it did not pre-register. What is here is a clean, well-controlled
observation that now requires a pre-registration of its own.

## Retraction

**P-19's diagnosis is retracted.** After P-19 failed, a mechanism was proposed — that the first
reading leaves its spent qubits humming beside the carriers, dephasing them. It was written into the
tree, the changelog and the commit message as the explanation.

It is unsupported, and the free diagnostic below rules out both of its ingredients.

## The diagnostic that settled it — and cost nothing

P-19 and P-20 differ in two ways that could explain the gap: the **barrier structure** inside the
reading, and the **chip**. Both circuits were scheduled locally against each backend's real gate
durations. No QPU was spent.

| | P-19 two-hop | P-20 `naive` | same chain? |
|---|---|---|---|
| `ibm_kingston` | 16.30 µs | 16.26 µs | yes |
| `ibm_fez` | 12.52 µs | 12.52 µs | yes |

**The circuits are the same.** Same chain, same duration to within 0.2%. The barrier explanation is
dead — the two runs executed the same schedule.

And the time explanation dies with it, in the most direct way possible: the circuit that **failed**
(on `ibm_fez`) was the **shorter** one — 12.52 µs against 16.26 µs. The longer circuit succeeded.
Elapsed idle cannot be the cause of a collapse that only happened on the shorter run.

What remains is the chip. `ibm_fez` failed where `ibm_kingston` succeeded, running the same schedule
on an equivalent chain. The median T2 along the chain was 152 µs on `fez` against 324 µs on
`kingston` — worse, but nowhere near enough to take a bond to 6% in 12.5 µs. The most likely
remaining suspect is mid-circuit measurement and reset quality on `fez` that day, which is exactly
the element these circuits lean on hardest. **That is a suspicion, not a finding, and it is labelled
as one.**

## The lesson, which is the durable part

**A single-chip null is not a null.** P-19 spent 31 seconds concluding that the centre does not
compose, published that conclusion, and was wrong — not because the metric was bad or the seal was
broken, but because one chip on one evening was taken for the world. Every result in this ledger
that rests on a single backend now carries that caveat, whether or not it was written at the time.

The pre-registration discipline worked exactly as intended here. H0 was included precisely so a
non-replicating run could not be mined for a mechanism, and when H0 failed it stopped a false
mechanism from being published a second time.

## Observed, not concluded

Both "fixes" were neutral or harmful. `parked` cost 1.4 SD. `parallel` cost 10.4 SD and dropped the
z-correlation from 0.674 to 0.339 — running the two ancilla measurements concurrently appears to
degrade both readings badly. That is an interesting engineering observation and **nothing more**:
H0 failed, so it is not a result, and it would need its own pre-registration to become one.

---

## Budget

62 seconds charged. **82 seconds remain** in the 28-day window.
