# Pre-registration — P-21
## Does the centre compose? Asked of two chips under one seal.

**Sealed:** 2026-09-18 UTC, before either job was submitted.
**Script:** `round5/cross_chip.py`
**Hardware:** `ibm_kingston` AND `ibm_fez`, 8-qubit line on each, chosen by readout error and T2.
**Shots:** 3072 per circuit, 27 circuits per chip (3 arms x [1 population + 8 phase points]).

**Both jobs are submitted before either result is fetched.** Nothing can be tuned between them.

---

### Why this run exists

P-19 ran the two-hop chain on `ibm_fez`, got 0.062, called it a failure of composition, and
published a mechanism to explain it. P-20 ran the same schedule on `ibm_kingston` and got 0.577.
The mechanism was retracted. Local scheduling showed the two circuits were the same schedule on the
same chain shape, and that the failing one was the SHORTER — so neither barriers nor idle time could
account for the gap. What differed was the chip.

That left the real question unsealed. P-20's two-hop number is clean, but P-20's own H0 failed, so
by its own rule nothing in it may be claimed. This run seals the question properly.

It asks two chips at once, because **the lesson we paid for twice is that a single-chip null is not
a null — and a single-chip pass is worth no more.** P-19 would not have been published if this rule
had been in force.

### Design

Three Bell pairs on a line: `a=b`, `c=d`, `e=f`. Read the centre of `b` and `c`; read the centre of
`d` and `e`. Ask whether `a` and `f` — which never touched, were never linked, and were never read
together — end bonded.

| arm | scored | what it gives |
|---|---|---|
| `none` | a,b / a,f | the gate-made ceiling, and a floor |
| `first` | a,d / a,f | one hop, and a second floor one reading short of the signal |
| `both` | a,f | **two hops** |

Readings compose by Pauli frame, so conditioning is on the XOR of the two outcomes. The noiseless
simulator returns 1.0000 for ceiling, one hop and two hops, with floors at 0.003 and 0.017.
Each chip's calibration — per-qubit T1, T2 and readout error along the chosen chain — and the
scheduled two-hop circuit duration are recorded **at submission**, so that if the chips disagree,
the reason is already on file rather than reconstructed afterwards.

---

### Predictions

**H1 — the centre composes, on every chip.** On **each chip independently**, the two-hop bond exceeds
that chip's pooled floor by **at least 5 SD**.

**H2 — and the composed bond is real entanglement, on every chip.** On **each chip independently**,
the two-hop Bell fidelity exceeds **0.5 by at least 3 SD**.

**H3 — the cost is multiplicative, on every chip.** On each chip, `two_hops / ceiling` equals
`(one_hop / ceiling)²` to within **0.10**.

**H1, H2 and H3 are claimed only if they hold on BOTH chips.** A pass on one chip and a failure on
the other is reported as a **split**, not as a pass, and the tree will say the question is
chip-dependent.

**H4 — the `fez` question, with both readings named in advance.**

- `fez` two-hop bond **below 0.15** → P-19's collapse **reproduced**. That would make the collapse a
  real, repeatable property of this chip running this circuit — a genuine finding, and it would mean
  P-19's *number* was sound even though P-19's *explanation* was not.
- `fez` two-hop bond **above 0.40** → the collapse **does not reproduce**, and P-19's result was a
  transient condition on one chip on one evening. The retraction stands and deepens.
- **Between 0.15 and 0.40** → **ambiguous**, and it will be reported as ambiguous. No story will be
  built on a middling number.

### Falsifiers, stated in advance

- If the two-hop bond fails the 5 SD bar on **either** chip, H1 fails and composition is **not**
  established by this run.
- If either chip's fidelity sits at or below 0.5, H2 fails there and the honest report for that chip
  is *composes as correlation, entanglement not witnessed*.
- If the multiplicative gap exceeds 0.10 on either chip, H3 fails there and the per-hop cost is not
  constant, whatever the bond does.
- If either chip's floor rises materially above its simulated value, that chip's percentages are
  void.
- If the two chips disagree on H1 or H2, **no composition claim is made at all** — the result is
  that this circuit's success depends on the backend, which is itself worth publishing and is the
  direct continuation of what P-19 and P-20 taught.

### What a pass would and would not mean

It would mean the shared centre is associative and the cost per hop is constant, demonstrated on two
independent machines under one seal — and that P-19's published failure was an artifact of asking
one chip.

It would **not** mean new physics. A two-hop swapping chain is the bones of a quantum repeater and is
thirty years old. Nothing travels down the chain; every reading's outcome must be carried classically
before the end-to-end bond can be used. What is being established is that the framework's claim,
stated as a number with falsifiers attached, survives being asked of more than one world.
