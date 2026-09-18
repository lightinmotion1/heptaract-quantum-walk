# P-15 · Which channel eats the shared bond?

**Run:** 2026-09-18, ibm_marrakesh, qubits [6, 5, 4, 3, 2] · 86 circuits · 1,024 shots · **32 seconds of QPU time**
**Pre-registration:** `PREREGISTRATION-2026-09-18-P15.md`
**SHA-256:** `a1d8c1c1fbf44a5f34b6ae67b2b3efc49e1ca10b4f5a8da2ace45c9ac1407757`
**Script:** `round5/decay_channels.py` · **Results:** `results/decay_channels.json`
**Desk:** Free (Miah J. Fry) & Claude

P-14 found the shared bond dying three to five times faster than the published dephasing allows.
Rather than argue about why, each suspect was measured on the same qubits in the same idle.

| Qubit | T₁ published | T₁ measured | T₂ published | T₂\* measured | T₂ echo measured | ZZ to its centre |
|---|---|---|---|---|---|---|
| q6 | 175.4 µs | **252.1** µs | 152.7 µs | **118.1** µs | 138.8 µs | **3.93** kHz |
| q2 | 209.1 µs | **303.5** µs | 217.0 µs | **177.1** µs | 229.2 µs | **3.8** kHz |

## The arithmetic

| Model for a two-carrier bond | Lifetime |
|---|---|
| from the **published** T₂ values | 89.6 µs |
| from the **measured** T₂\* values | 70.9 µs |
| measured T₂\* **plus** the neighbours' coupling | 16.0 µs |
| **what P-14 actually saw** | **≈ 30 µs** |

## The verdicts, as declared

| Test | Prediction | Verdict |
|---|---|---|
| H1 | Measured T₂\* is at most 0.7× the published T₂ for at least one rim qubit | **Fails** — 0.77× and 0.82×. The published numbers do flatter the machine, by about a fifth, but not by the margin declared. |
| H2 | The coupling between each rim qubit and its centre is at least 5 kHz | **Fails** — 3.93 and 3.80 kHz. The neighbours are talking, just below the bar. |
| H3 | T₂\* alone under-predicts the loss by ≥ 1.5×, and adding the coupling closes half the gap | **Holds in direction, overshoots in size.** T₂\* alone predicts 70.9 µs against an observed 30 — a factor of 2.4. Adding the coupling predicts 16.0 µs, which is now too *fast*. |

## What this actually tells us

**It is the neighbours.** Energy decay is not the culprit — T₁ measured 252 and 304 µs, longer than
published and far longer than anything here. Free dephasing alone is too slow to account for the
loss: 71 µs against an observed 30. **The always-on coupling between each rim qubit and its own
centre — about 3.9 kHz each — supplies the missing rate**, because a qubit coupled to a neighbour
that is itself in superposition cannot keep its phase: the neighbour's uncertainty becomes the
qubit's dephasing.

**And our first model of that effect is about twice too strong.** Treating the coupling as pure
dephasing at 1/(2πζ) predicts 16 µs where 30 µs was seen. The truth sits between the two models —
which is what an honest first model should do, and it says the next refinement is the shape of the
coupling term rather than another suspect.

**So the reach of the shared centre is an engineering number.** The cures are known: time the echo
against the coupling rather than against the wait, park idle qubits away from each other, or use
pulses that cancel ZZ specifically. None of them touch the framework's claim — they change how long
a machine can hold a relationship steady, which is exactly what P-12 said the limit was.

## Where the ledger stands

Five relationship tests hold (P-1, P-2, P-4, P-10, P-11), and three tests of **reach** — P-12,
P-13, P-14 — have now been followed down to their cause. The thing between two objects has never
once shown a decay of its own. Everything that limits it has turned out to belong to the carriers,
and now we know which carrier property, by name and by number.
