# Pre-registration — P-18
## Can reading the centre of both make them one?

**Sealed:** 2026-09-18 UTC, before any hardware time was spent.
**Script:** `round5/swap_centre.py`
**Hardware:** least-busy IBM Heron, 5-qubit line chosen by readout error.
**Shots:** 4096 per circuit, 36 circuits (4 arms x [1 population + 8 phase points]).

---

### The question

P-17's control turned up something that was not a floor. Two ships are built that never touch —
each a centre with its own rim qubit, and no gate between the ships, ever. Then a reading is taken
of what the two centres hold in common, onto a third thing belonging to neither ship, so that
neither ship's own centre is ever learned.

Do the two rims, which have never interacted, end up bonded?

This is textbook entanglement swapping and has been known since the nineteen-nineties. **Nothing
here is new physics.** What is being tested is the framework's claim in the framework's own terms:
that the centre of both is not merely a description of a relationship that already exists, but a
way of making one.

### What the simulator changed before the run

The first design read only ONE parity of the two centres. The simulator showed that this leaves the
rims in an even mixture of two Bell states: correlated, but **separable**. The bond metric alone
would have called that a bond, and the claim would have been overstated. The fidelity witness sat at
exactly 0.5 — the separability boundary — which is how the flaw was caught.

The shared reading here is therefore **complete**: the Z parity of the two centres is read onto the
shared ancilla, the ancilla is reset, and the X parity is read onto the same ancilla. Two readings,
one shared thing, and the ships still never touch each other. Only a complete joint reading can put
the rims in a genuine Bell state, and only then can a fidelity above one half be quoted.

A second correction: the oscillation sits at a known frequency, so only that Fourier bin is read.
Summing every bin adds the magnitude of the noise in each one, which inflates the signal and the
floor together. On the noiseless simulator that bias read 1.06 for a state whose true value is 1.

### Arms

| arm | the reading taken | expectation |
|---|---|---|
| `swap` | complete shared reading of both centres | bond |
| `private` | one ship's own centre read twice, Z then X | floor |
| `none` | the shared thing read twice with nothing connected | floor |
| `linked` | ships joined by a gate first, then the shared reading (the P-11 state) | scale |

### Metric

Conditioned on the Z-parity branch, with the two X branches averaged by magnitude:

- `bond` — amplitude of the rim–rim parity oscillation across the phase sweep. **1.0** for a perfect
  Bell state, 0 for no correlation.
- `z_correlation` — |<ZZ>| of the two rims in the population circuit.
- `fidelity` = (1 + |<ZZ>| + 2 x bond) / 4 — the Bell-state fidelity. **Above 0.5 witnesses
  entanglement.** Bootstrap error bars, 300 resamples.

Noiseless simulator, for calibration: swap 1.0000, linked 1.0000, private 0.0133, none 0.0036.
Control fidelities 0.25-0.26, which is the maximally-mixed value, as they should be.

---

### Predictions

**H1 — reading creates a bond.** The `swap` bond exceeds the pooled control floor by **at least 5 SD**.

**H2 — and the bond is real entanglement.** The `swap` Bell fidelity exceeds **0.5 by at least 3 SD**,
between two qubits that have never interacted.

**H3 — no reading, no bond.** The `none` arm sits within 2 SD of the floor.

**H4 — scale.** The ratio of the `swap` bond to the `linked` bond falls in **[0.7, 1.4]**: making the
relationship by reading is comparable to making it by a gate.

### Falsifiers, stated in advance

- If `swap` is **under 5 SD** above the floor, H1 fails and the claim does not survive.
- If the fidelity lands **between 0.25 and 0.5**, the honest report is *correlation created,
  entanglement not witnessed* — a **narrow**, not a hold, and it will be written that way.
- If `none` or `private` rises materially above its simulated floor, the metric is contaminated and
  no percentage from this run may be quoted.
- If `swap` falls outside [0.7, 1.4] of `linked`, H4 fails and is reported failed.

The costliest element on hardware is the mid-circuit measurement and reset. It is expected to pull
the fidelity well below the simulator's 1.0. **A result near the 0.5 boundary will be reported as
near the boundary**, not rounded toward the claim.

### What a pass would and would not mean

It would mean: a joint reading of two centres, taken without learning either one, put two things
that never met into a shared state — and the framework predicted where to look.

It would **not** mean: new physics, faster-than-light signalling, or that anything travelled between
the ships. The bond only becomes usable once the reading's outcome is carried from the ancilla to
whoever holds the rims, and that carrying is ordinary, slower-than-light communication.
