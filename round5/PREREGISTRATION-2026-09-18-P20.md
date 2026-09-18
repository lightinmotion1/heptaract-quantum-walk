# Pre-registration — P-20
## Was the diagnosis right? Parking the spent, or merely hurrying.

**Sealed:** 2026-09-18 UTC, before any hardware time was spent.
**Script:** `round5/park_centre.py`
**Hardware:** least-busy IBM Heron, 8-qubit line chosen by readout error and T2.
**Shots:** 4096 per circuit, 54 circuits (6 arms x [1 population + 8 phase points]).

---

### Why this run exists

P-19 failed as pre-registered, and stays failed. Afterwards a diagnosis was offered: the first
reading leaves its spent qubits alive in superposition beside the carriers, and P-15 measured that
neighbour coupling at 3.9 kHz while P-16 established what a neighbour in superposition does. The
evidence was the split in the two-hop numbers — z-correlation surviving at 0.587 while the phase
collapsed to 0.062, which is dephasing rather than decay.

**That diagnosis arrived after the data, which makes it a hypothesis and not a finding.** This run
exists to give it a fair chance to be wrong, and it names in advance what would sink it.

Two candidate causes are separated so neither can hide behind the other:

- **NEIGHBOURS** — the spent qubits hum next to the carriers.
- **TIME** — the second reading simply takes too long and the ends dephase while waiting.

### Arms

| arm | what it is | isolates |
|---|---|---|
| `none` | no reading | ceiling on a,b · a floor on a,f |
| `first` | one reading | one hop on a,d |
| `naive` | P-19 exactly | **the replication** |
| `parked` | sequential, spent qubits **reset** after the first reading | NEIGHBOURS — same elapsed time, quiet neighbours |
| `parallel` | the two readings run **concurrently**, nothing parked | TIME — same neighbours, about half the wait |
| `parked_parallel` | both together | — |

Barriers are now held to the qubits each reading touches, so the disjoint readings may overlap.
Transpiled circuit durations are recorded at submission, so the claim that `parallel` is genuinely
shorter is checked against the schedule rather than assumed.

The noiseless simulator returns **1.0000 for all six arms**, which is the correct validation: these
are noise interventions, not logic changes. It also clears the one thing that could have been
logically wrong — resetting the spent qubits does **not** destroy the end-to-end bond, so the Pauli
frame does not depend on them.

---

### Predictions

**H0 — the replication.** `naive` reproduces P-19: within 3 SD of **0.062**, and below 0.15.
**If H0 fails, nothing else in this run is interpretable and no other hypothesis may be read.**

**H1 — a fix works.** At least one of the three fixed arms exceeds `naive` by **5 SD** and reaches a
bond of **0.25 or better**.

**H2 — the mechanism is neighbours, not time.** `parked` beats `naive` by more than `parallel` does,
by at least 2 SD of the naive bar.

**H3 — entanglement is recovered.** The best fixed arm's Bell fidelity exceeds **0.5 by 3 SD**.

**H4 — the cost becomes multiplicative.** The best fixed arm lands near `(one_hop / ceiling)²`,
which P-19 put at roughly **0.42** of ceiling.

### Falsifiers, stated in advance

- **If `parked` ≈ `naive` and `parallel` ≈ `naive`** — neither fix moves the bond by 5 SD — then the
  dephasing-from-spent-neighbours diagnosis is **WRONG**, is retracted in full, and P-19's failure
  stands unexplained. That is a proper outcome and will be written as one.
- **If `parallel` helps and `parked` does not**, the cause is elapsed time, not neighbours. The
  specific neighbour claim is **retracted** even though the fix works, because the published reason
  would have been wrong.
- **If `parked` helps but `parallel` also helps just as much**, the two causes are not separated by
  this design and no mechanism may be named.
- If `naive` does not reproduce P-19, the run is void for everything except that fact.
- If a fixed arm's gain comes with a *fall* in z-correlation, the "gain" is a metric artifact and
  will be reported as one.

**A named risk:** parking uses a reset, which is a measurement, and a measurement on `b` sits
directly beside `a`. Crosstalk from that reset could cost more than the quiet buys. If parking
fails, that is one of the two live explanations and will not be quietly dropped.

### What a pass would and would not mean

It would mean the reach of a composed centre is limited by what is left lying beside the carriers,
which is an engineering fact with a known remedy — and that P-19's failure was ours, not the
framework's.

It would **not** rehabilitate P-19. That test failed as written and the record keeps it that way.
