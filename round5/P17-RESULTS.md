# P-17 · Settling the floor — and an accident worth its own test

**Run:** 2026-09-18, ibm_marrakesh, qubits [6, 5, 4, 3, 2] · 32 circuits · 4096 shots · **41 seconds of QPU time**
**Pre-registration:** `PREREGISTRATION-2026-09-18-P17.md`
**SHA-256:** `8936aa4359da190d602ed0732199a1e5c0ddfd5e0dde145fcc95de7ebd59eea1`
**Script:** `round5/control_floor.py` · **Results:** `results/control_floor.json`
**Desk:** Free (Miah J. Fry) & Claude

P-16 gave an ordering but not a size, because its floor estimate came in at twice its usual value.
A metric's floor has to be known before any percentage built on it means anything, so it was
measured properly: four times the shots, two independent ways of having no bond, bootstrap errors
on everything.

| Arm | Bond | Bootstrap SD |
|---|---|---|
| floor · one ship's own centre read | 0.0291 | ±0.0067 |
| floor · rims never entangled at all | 0.0313 | ±0.0070 |
| ceiling · shared reading, no wait | 0.2183 | ±0.0061 |
| signal · shared reading, 60 µs, centres-only echo | 0.0784 | ±0.0080 |

| Test | Prediction | Verdict |
|---|---|---|
| H1 | The two floors agree within 15% | **Holds** — 0.0291 and 0.0313, 7.2% apart |
| H2 | The signal stands clear of the floor by ≥ 5 SD | **Holds** — 5.1 SD |
| H3 | The surviving fraction at 60 µs lands between 15% and 35%, with an error bar | **Holds** — **25.6% ± 5.1%** |

## The number, at last quotable

**After 60 microseconds of waiting, with the echo timed against the neighbours rather than against
the clock, 26% ± 5% of the shared bond survives.** Two independent floors
agree to within seven percent, so the denominator is trustworthy, and P-16's floor-free ordering
now has a magnitude to go with it: the coupling echo roughly doubles what the old clock echo left.

## The accident, declared before it was tested

The first draft of this control used *two ships never linked* as its null: no link, so no shared
bond to find. **The simulator showed that is not a null at all.** Reading the parity of two unlinked
centres **swaps** the entanglement onto the two rims and produces a full bond, 0.26 where zero was
expected.

The shared reading does not only *reveal* a relationship. **It can create one between parts that
were never joined.**

That is standard entanglement swapping, known since the nineteen-nineties, and it is exactly the
kind of claim this desk does not get to slip in through a control arm. It was declared in P-17's
pre-registration, before the hardware run, and **it gets its own pre-registration and its own
measurement.** What is recorded here is only the date it was noticed and how.

For the framework the implication is worth stating carefully and then testing: if the centre of
both can be read into existence between two things that had no prior relationship, then the shared
centre is not merely a description of an existing bond — it is a way of making one. Free's reading
has always said the relationship is the primary thing. This would be the first place the hardware
offers to say it too.
