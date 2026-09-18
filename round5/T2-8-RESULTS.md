# T-2.8 · The seven-share code, built and measured

**Run:** 2026-09-18, by enumeration on a laptop. No quantum hardware, no citation: every number
below was counted.
**Script:** `round5/f7_code.py` · **Results:** `results/f7_code.json`
**Desk:** Free (Miah J. Fry) & Claude

The tree has long claimed that the best seven-share quantum scheme cannot be built from qubits.
This test builds the thing and then closes the qubit route by exhaustion.

## What was built

Over 𝔽₇, read polynomials of degree under k at all seven field elements:

| Code | Parameters | Distance | MDS? |
|---|---|---|---|
| C | [7, 4] | **4** | yes (7 − 4 + 1) |
| C* = C^⊥ | [7, 3] | **5** | yes (7 − 3 + 1) |

C* sits inside C — checked word by word, not assumed — so the CSS construction applies and gives

**[[7, 1, 4]]₇ — seven qu7its carrying one, correcting any single error, detecting any three.**

- Distance **measured by enumerating the code**: the lightest word of C that is not in C* has
  weight 4. Not quoted from a table.
- **Meets the quantum Singleton bound exactly**: k ≤ n − 2(d − 1) gives k ≤ 1, and k = 1. Nothing
  of length seven can do better at distance four.
- **All 336 single-qudit errors have distinct syndromes.** Zero collisions.
- **12,572 sampled errors of weight one, two and three: none undetected.**

## The qubit route, closed

Every binary [7,4] linear code was generated and measured — all 11,811 of them, by reduced row
echelon form so each subspace appears exactly once.

| Over 𝔽₂ | Best distance found |
|---|---|
| [7,4] | **3** (the Hamming code) |
| [7,3] | 4 |

The CSS distance available over qubits at this length is therefore **3**, which is the Steane code
[[7,1,3]]₂. **No binary [7,4] code reaches distance 4**, so the route that produces [[7,1,4]] over
𝔽₇ does not exist over 𝔽₂. Seven levels give the seven-share code its extra distance; two levels
cannot, at any arrangement.

## Why this one counts

Rounds 2 and 3 asked seven to be a summit and a building block; hardware declined both. Round 4
asked seven to be a period and hardware agreed. This test asks seven to be **an alphabet** — the
size of the field the arithmetic lives in — and the answer is a clean separation: a scheme that
exists over seven levels and provably does not over two.

Every result that has held for HEPTARACT now sits in the same place: **the algebra of sevens, and
the reading of relationships.** Not seven as a count, not seven as a height.

## Next in this direction

- The eight MUBs of a qu7it, constructed and checked the same way (T-2.2 follow-on).
- Tomography under real readout error, comparing the qu7it against its qubit encoding (T-2.9).
- The same seven-share code run on hardware once native qudits are reachable.
