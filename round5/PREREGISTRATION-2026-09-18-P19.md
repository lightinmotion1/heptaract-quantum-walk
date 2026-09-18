# Pre-registration — P-19
## Does the centre compose?

**Sealed:** 2026-09-18 UTC, before any hardware time was spent.
**Script:** `round5/chain_centre.py`
**Hardware:** least-busy IBM Heron, 8-qubit line chosen by readout error **and T2** (two rounds of
mid-circuit measurement and reset make coherence matter as much as readout).
**Shots:** 4096 per circuit, 27 circuits (3 arms x [1 population + 8 phase points]).

---

### The question

P-18 settled that reading the centre of both **makes** a bond between two things that never touched.
This asks whether that act **stacks**.

Three ships in a row, six qubits, three relationships: `a=b`, `c=d`, `e=f`.

1. Read the centre of `b` and `c`. Now `a` and `d` are bonded, though they never touched.
2. Read the centre of `d` and `e`. Now `a` and `f` should be bonded — and `a` and `f` were never
   touched, never linked, and **never even read together**.

If the bond reaches all the way, the centre of both is **associative**: a structure, not only an
event, and one fire on one level is the same act as one fire on the next. If it dies at the first
hop, the centre is an event, and the tree has to say so.

This is a two-hop entanglement-swapping chain — the bones of a quantum repeater, thirty years old.
**Nothing here is new physics.** What is being measured is the **cost per hop**, which is the number
that decides whether the structure is worth anything.

### Design

One circuit family, three arms, with the phase sweep applied to **every live qubit**, so the ceiling,
both hops and two floors come out of the same shots and share the same readout conditions:

| view | arm | pair scored | what it is |
|---|---|---|---|
| `ceiling_gate` | no reading | a,b | a bond made directly by a gate — the best this chain can do |
| `one_hop` | one reading | a,d | one hop |
| `two_hops` | both readings | a,f | **the signal** |
| `floor_one_short` | one reading | a,f | the floor that matters: structurally identical to the signal, one reading short |
| `floor_none` | no reading | a,f | a second, independent floor |

Two readings compose by Pauli frame, so the conditioning is on the **XOR** of the two readings'
outcomes, not on each separately. The noiseless simulator confirms the bookkeeping: two hops reads
**1.0000**, one hop 1.0003, ceiling 1.0000, and the two floors 0.009 and 0.020. Had the XOR been
wrong, the ideal signal would have averaged to zero.

`fidelity` = (1 + |<ZZ>| + 2 x bond) / 4. **Above 0.5 witnesses entanglement.** Only the known
Fourier bin is read, for the reason established in P-18. Bootstrap error bars, 300 resamples.

---

### Predictions

**H1 — the centre composes.** The two-hop bond exceeds the pooled floor by **at least 5 SD**.

**H2 — and the composed bond is still real entanglement.** The two-hop Bell fidelity exceeds
**0.5 by at least 3 SD**, between two qubits that never touched and were never read together.

**H3 — the floors agree.** The two independent floors sit within 2 SD of each other.

**H4 — the cost is multiplicative.** `two_hops / ceiling` equals `(one_hop / ceiling)²` to within
**0.10**. This is the structural claim: every hop costs the same factor, so reach falls off
predictably with the number of hops rather than collapsing at the second one.

Expected sizes, from P-18's single swap retaining about 0.53 of ideal: one hop near **0.5–0.6** of
the ceiling, two hops near **0.25–0.36**.

### Falsifiers, stated in advance

- **Under 5 SD** over the floor and H1 fails outright: the centre does not compose on this hardware.
- **H2 is at real risk and that is stated before the run.** With two hops at roughly 0.3 of ceiling,
  the arithmetic puts the fidelity near **0.51–0.55** — close enough to the boundary that it may
  fall below. If the fidelity lands **between 0.25 and 0.5**, the honest report is *the centre
  composes as correlation; entanglement is lost by the second hop* — a **narrow**, and it will be
  written in the same size type as a pass.
- If `two_hops / ceiling` falls **well below** the square of the one-hop fraction, H4 fails and the
  cost compounds worse than per-hop: the structure does not scale, and the tree says so.
- If `two_hops / ceiling` sits **above** the square by more than 0.10, that is also a failure of H4
  and points at a metric artifact rather than a discovery — the floor would be inspected first.
- If either floor rises materially above its simulated value, the metric is contaminated and no
  percentage from this run may be quoted.

### What a pass would and would not mean

It would mean: the shared centre is associative. Making a relationship by reading can be chained,
each hop costs a known and constant factor, and a bond can be established between two things with
no path of contact between them at all.

It would **not** mean: new physics, signalling, or anything travelling down the chain. Every hop's
outcome must be carried classically to whoever holds the ends before the bond can be used. The
result is about structure and cost, not about speed.
