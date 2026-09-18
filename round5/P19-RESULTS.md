# P-19 — Results
## Does the centre compose? Not the way we built it.

**Pre-registration:** `PREREGISTRATION-2026-09-18-P19.md`
**SHA-256:** `c2dad3dfda82c8e460b8e5311c9db0e3918d6615f04f3ed610e94137ab306f70` (sealed before the run)
**Hardware:** `ibm_fez` (Heron), job `dambi15r85ps73fci6l0`
**Shots:** 4096 x 27 circuits · **QPU charged: 31 seconds**
**Date:** 2026-09-18 UTC

# VERDICT: H1, H2 and H4 FAIL. H3 holds.

**Three of the four pre-registered hypotheses failed.** This is written first and in the same size
type a pass would get.

---

## The result

| view | bond | z-correlation | Bell fidelity |
|---|---|---|---|
| ceiling — a bond made by a gate | 0.927 ± 0.003 | 0.907 | 0.940 ± 0.002 |
| **one hop** | **0.602 ± 0.009** | 0.772 | **0.744 ± 0.006** |
| **two hops** | **0.062 ± 0.011** | **0.587** | **0.428 ± 0.007** |
| floor — one reading short | 0.022 ± 0.010 | 0.030 | 0.268 ± 0.007 |
| floor — no reading | 0.010 ± 0.007 | 0.008 | 0.257 ± 0.004 |

Pooled floor: 0.016 ± 0.006.

- **H1 — the centre composes.** Two hops stands **3.8 SD** above the floor. Required: 5. **FAIL.**
- **H2 — the composed bond is still entanglement.** Fidelity **0.428 ± 0.007**, which is *below* the
  one-half boundary, by 10.3 SD. **FAIL**, and it fell into exactly the band the pre-registration
  named in advance: *composes as correlation, entanglement lost by the second hop.*
- **H3 — the floors agree.** 0.022 and 0.010, within their bars. **Holds.**
- **H4 — the cost is multiplicative.** One hop kept **65.0%** of the ceiling, so two hops should have
  kept **42.2%**. It kept **6.7%**. Gap of 0.355 against a pre-registered tolerance of 0.10. **FAIL**,
  and not narrowly — the second hop cost roughly **ten times** what the first one did.

One hop is in excellent shape: 0.602 bond, fidelity 0.744, entanglement plainly witnessed. P-18
replicated on different hardware, at a different chain length, with a tighter ceiling. The failure
is entirely in the second hop.

---

## What the failure says, which is more than "no"

The two-hop numbers do not fall together. **The z-correlation survived at 0.587 — far above the
0.03 floor — while the phase coherence collapsed to 0.062.** Classical correlation propagated the
full length of the chain. Only the phase died.

That is not decay. That is **dephasing**, and it has a specific signature: a Bell state losing phase
while keeping its Z correlation. Something dephased the two ends during the second reading.

**And we had already measured the mechanism, three tests earlier, and then failed to apply it.**
P-15 named an always-on coupling of about 3.9 kHz between each qubit and its neighbour, and P-16
established the consequence: *a neighbour left in superposition dephases whatever it is coupled to.*

Look at what this circuit does. The first reading takes the centre of `b` and `c` onto the shared
ancilla — and then **leaves `b` and `c` alive, in superposition, sitting directly beside `a` and `d`**,
which are the very qubits now carrying the bond. They sit there, dephasing their neighbours, through
the whole of the second reading. The second reading is the longest idle in the circuit: a measurement,
a reset, and a second measurement, all of it serialized behind a barrier that was not needed, because
the two readings act on disjoint qubits and could have run at the same time.

So the second hop was not asked to carry a relationship. It was asked to carry one while the spent
parts of the first hop sat next to it, humming.

**The honest reading of P-19 is therefore narrow and specific:** *the centre does not compose when
the leftovers of the previous reading are left in superposition beside the carriers.* Whether the
centre composes at all is **not settled by this run**, and the tree will not claim it is.

## What this does not license

It does not license a re-run dressed up as the original test. P-19 failed as pre-registered, and it
stays failed on the record whatever happens next. A fix gets its own pre-registration, its own hash
and its own number, and it must say in advance what result would mean the diagnosis above was wrong
— because a diagnosis that arrives after the data is a hypothesis, not a finding.

The one thing P-19 does establish, at 65.0% of ceiling with fidelity 0.744, is that **a single hop
is solid**. Everything else here is a question that has been made sharper, not answered.

---

## Budget

31 seconds charged. **144 seconds remain** in the 28-day window. The window is trailing, and
essentially all of the spend happened on 2026-09-18, so nothing meaningful returns until ~2026-10-16.
