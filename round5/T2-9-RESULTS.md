# T-2.9 · Reading a seven-level state under real readout error

**Run:** 2026-09-18, simulation on a laptop. 60 random states per cell, purity 0.85.
**Pre-registration:** `PREREGISTRATION-2026-09-18-T2-9.md`
**SHA-256:** `36a1bc83150dd08ad95c4422e8996fe56328e797b889325ec1b8ae6fb42332b3`
**Script:** `round5/qu7it_vs_qubit.py` · **Results:** `results/qu7it_vs_qubit.json`, chart `results/qu7it_vs_qubit.png`
**Desk:** Free (Miah J. Fry) & Claude

One seven-level state, read four ways, at matched total shots and matched total readout error.
Lower infidelity is better.

| Test | Prediction | Verdict |
|---|---|---|
| H1 | The qu7it in its 8 MUBs beats three qubits read in all 27 Pauli products | **Holds** (worst margin 5.33σ) |
| H2 | The qu7it in its 8 MUBs beats the qu7it in 8 random bases | **Holds** (worst margin 15.7σ) |
| H3 | The qu7it in its 8 MUBs beats three qubits in 8 random bases | **Holds** (worst margin 18.53σ) |

| Shots | Readout error | A qu7it · 8 MUBs | C qubits · 27 Paulis | B qu7it · 8 random | D qubits · 8 random | z vs C | z vs B | z vs D |
|---|---|---|---|---|---|---|---|---|
| 2,000 | 0% | 0.0893 | 0.1034 | 0.3238 | 0.2249 | 5.33 | 18.68 | 20.93 |
| 2,000 | 2% | 0.0897 | 0.1064 | 0.3214 | 0.2207 | 6.6 | 17.75 | 18.53 |
| 2,000 | 5% | 0.0932 | 0.1120 | 0.3377 | 0.2381 | 7.79 | 18.8 | 20.4 |
| 2,000 | 10% | 0.0993 | 0.1201 | 0.3275 | 0.2454 | 7.42 | 22.0 | 23.2 |
| 8,000 | 0% | 0.0497 | 0.0612 | 0.1819 | 0.1694 | 6.53 | 17.44 | 22.14 |
| 8,000 | 2% | 0.0480 | 0.0606 | 0.2000 | 0.1639 | 6.73 | 17.35 | 23.16 |
| 8,000 | 5% | 0.0468 | 0.0589 | 0.2058 | 0.1681 | 6.5 | 17.82 | 28.63 |
| 8,000 | 10% | 0.0475 | 0.0657 | 0.2056 | 0.1725 | 10.14 | 21.16 | 26.78 |
| 32,000 | 0% | 0.0166 | 0.0288 | 0.1125 | 0.1316 | 8.78 | 15.7 | 26.27 |
| 32,000 | 2% | 0.0132 | 0.0270 | 0.1079 | 0.1363 | 11.03 | 19.02 | 32.04 |
| 32,000 | 5% | 0.0129 | 0.0217 | 0.1222 | 0.1355 | 9.55 | 18.44 | 33.91 |
| 32,000 | 10% | 0.0189 | 0.0256 | 0.1237 | 0.1405 | 10.62 | 18.74 | 36.81 |

## Reading

- **Every cell, every margin, one direction.** The qu7it read in its eight mutually unbiased bases
  gives the most faithful reconstruction at every shot budget and every level of readout error.
- **The win is the unbiasedness, not the roominess.** Eight *random* bases in the same seven
  levels lose badly. Seven levels alone buy nothing; seven levels read in the right eight bases
  buy a great deal.
- **The win is not the number of settings.** Pauli tomography uses 27 settings against the MUBs'
  8, and still loses. More looks do not beat better-placed looks.
- **The advantage grows with the error.** At 32,000 shots the margin over Paulis widens as readout
  error rises from 0% to 10%. The worse the detector, the more the structure pays — which is the
  practical claim, since real detectors are the error-prone part.

## What this is, honestly

A simulation of measurement statistics, not a hardware result: nobody reads a native qu7it for us
yet. What is compared is how much a given number of reads through a given detector tells you about
the state — an information claim. Estimation is linear inversion followed by the nearest physical
state, identical for every scheme, and the qubit schemes are given the benefit of reconstructing in
eight dimensions and then being restricted to the seven that matter.

## Where this sits

The eight MUBs exist because seven is prime. This is the fourth receipt in a row landing in the
same place — the algebra of sevens and the reading of relationships — after the hardware declined
seven as a summit (round 2) and as a building block (round 3), and agreed to seven as a period
(round 4) and as an alphabet (T-2.8).
