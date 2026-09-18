# P-11 · Three centres: mine, yours, ours

**Run:** 2026-09-18, ibm_marrakesh, job `dam9r0o2fm4c73f2keig` · 24 circuits · 2048 shots · **15 seconds of QPU time**
**Pre-registration:** `PREREGISTRATION-2026-09-18-P11.md`
**SHA-256:** `1aee5faaac9117fc373f5ebc82d7dc61f7478800cfbac0cc8238529648c9fc5c`
**Script:** `round5/three_centres.py` · **Results:** `results/three_centres.json`
**Desk:** Free (Miah J. Fry) & Claude

Free's reading, in his words: *there cannot be more than one centre unless you measure two
distinct objects — and then it becomes a relationship conversation: the centre of one ship, the
centre of the other ship, and the centre of both shared.*

Two ships were built — each a centre writing itself onto its own three — and joined by a single
gate. Then the three centres were read.

| Reading | bond A (ship A's three) | bond B (ship B's three) | bond across (all six) |
|---|---|---|---|
| MINE — ship A's own centre | 0.0427 | 0.0370 | **0.0404** |
| YOURS — ship B's own centre | 0.0608 | 0.0360 | **0.0383** |
| OURS — only the relationship | 0.0544 | 0.0281 | **0.1906** |

| Test | Prediction | Verdict |
|---|---|---|
| H1 | Only the shared reading keeps the shared thing: OURS ≥ 2× either private reading | **Holds** — 4.72× over MINE, 4.98× over YOURS |
| H2 | The shared bond is really there on hardware: ≥ 0.10 | **Holds** — 0.1906 |
| H3 | After the link, neither ship owns a bond of its own (≤ 0.10 everywhere) | **Holds** — 0.028 to 0.061 |

## Reading

**The centre of both is a real measurement.** Asking only for the relationship — the parity of the
two centres, written onto an ancilla so that neither ship's own centre is ever learned — leaves the
six across both ships bonded at 0.19. Asking either ship *what are you* destroys that, five times
over. The shared centre can be read without dissolving what is between them; a private centre
cannot be read without dissolving it.

**And neither ship kept a bond of its own.** Once the link was made, ship A's three had no
coherence among themselves under any reading, and neither did ship B's. **The bond does not sit in
either ship. It sits between them, and only the shared reading can hold it.** That was H3, declared
in advance, and the hardware agreed at every reading.

**So the philosophy stands, measured.** One object has one centre. Two objects have three: yours,
mine, and the one that belongs to neither and exists only because both do. The third is not a way
of speaking — it is the only reading that leaves the relationship whole.

## The honest edges

- Both private readings cost 25 two-qubit gates and the shared reading 30, so OURS runs the
  *deeper* circuit and still wins by five times. The result is not bought with shallower work.
- The link here is one gate between two centres. A stronger or weaker link would move the
  numbers; what is pre-registered is the ordering, not the magnitude.
- Noiseless simulation gives 0.262 against 0.025 and 0.018 — ten- and fourteen-fold. The chip
  returns five-fold, which is the same statement through this machine's noise.

## Where this sits

With P-1 and P-4 (the centre's manner of reading governs the six, by a sine law), P-2 (the bond
lives in the whole, not the pairs) and P-10 (one fire may carry more levels without spending the
bond), the relationship claims now hold four for four on hardware — while every claim that asked
seven to be a **size** has narrowed. The framework's measurable content is relationship and
structure, and this is the cleanest statement of the first half yet: **what is between two things
is its own thing, and it answers only to a question about both.**
