# HEPTARACT round 2: results

**Run:** 2026-09-17
**Desk:** Free (Miah J. Fry) & Claude
**Pre-registration:** `PREREGISTRATION-2026-09-17.md`
**SHA-256 of the pre-registration:** `8d9d804f718cb5c085c82f469468cb83380d4f4dd7c86f25663fd6954b3620fc`

**Timing note.** The header of the pre-registration says 05:15 UTC. The file itself was written at 05:11:28 UTC, and the first data download began at 05:13:17 UTC. The declaration came before any data was touched. The header simply shows a later time than the true one, and the file was left unedited so that the hash above still matches.

**The rule for this round:** each prediction had to beat a rival, not only the null hypothesis.

## Scoreboard

| Test | Prediction | Verdict |
|---|---|---|
| T-2.5 | The helix of 7-gons carries a state better than helices of 5-, 6- and 8-gons | **Narrows** (5-gons won 3 of the 4 cells) |
| T-2.7 | d = 7 sits off the smooth break-even curves | **Narrows** (the curves are smooth and 7 lies on them) |
| T-4.5 (a) | The seven just ratios beat the first-order ratios HEPTARACT omits, in exoplanet orbits | **Holds** (mean E 1.049 vs 0.355) |
| T-4.5 (b) | 7/4 beats every same-order rival | **Narrows** (E(7/4) = 0.719, the lowest of the five) |
| T-4.1 H1 | Alpha peaks cluster at 8.81 Hz (9/8 × 7.83) | **Narrows** (E = 0.996, p = 0.55) |
| T-4.1 H2 | Alpha peaks cluster at 13.70 Hz (7/4 × 7.83) | **Narrows** (0 of 109 peaks landed there) |
| T-5.5 | Heart:breath ratio locks at the just ratios | **Narrows** (mean E 0.994 vs 1.032 for the rivals) |
| P-3 | GHZ bonds need every member; W bonds survive a departure | **Holds** (standard physics, now computed) |
| T-1.5, P-1, P-2 | IBM hardware: GHZ size scan, the fire read two ways, pairs versus the whole | **Built and simulated.** Not run yet: the saved IBM key no longer matches an instance. |

## T-2.5 · The helix walk

Setup: a continuous-time quantum walk starting at vertex 0, scored by the best transfer fidelity over t ∈ [0, 60].

| L | Target | n = 5 | n = 6 | n = 7 | n = 8 |
|---|---|---|---|---|---|
| 2 | vertex n | **0.463** | 0.333 | 0.296 | 0.336 |
| 2 | top | **0.655** | 0.450 | 0.453 | 0.399 |
| 3 | vertex n | 0.347 | 0.252 | **0.348** | 0.230 |
| 3 | top | 0.512 | **0.587** | 0.407 | 0.328 |

- Seven wins one cell, and only by 0.0008, which is below the pre-registered 0.01 margin.
- None of these helices transfers perfectly.
- The perfect transfer seen on the 7-cube comes from the hypercube structure, not from the helix.

## T-2.6 · Reading from the hub (exploratory)

- The hub talks only to the even rim state.
- The most that ever leaves the hub is n/(n+1). That rises smoothly with n: 7/8 at n = 7.
- Nothing singles out seven.

## T-2.7 · Base-d break-even

| d | Bits per read | Readout target at 0.99 | Gate multiplier | Spare levels |
|---|---|---|---|---|
| 5 | 2.322 | 0.9769 | 5.39 | 3 |
| 6 | 2.585 | 0.9744 | 6.68 | 2 |
| 7 | 2.807 | 0.9722 | 7.88 | 1 |
| 8 | 3.000 | 0.9703 | 9.00 | 0 |
| 11 | 3.459 | 0.9658 | 11.97 | 5 |

- Both curves are smooth functions of log₂ d.
- What sets seven apart: seven is prime, which gives the full set of eight MUBs, and seven is the largest prime that fits inside three qubits.

## T-4.5 · Just ratios in planetary orbits

**Data:** NASA Exoplanet Archive (pscomppars), 1,045 multi-planet systems. N = 1,041 neighboring pairs with 1 < r ≤ 3.2.

Primary window [q, 1.03q]. E is the observed count divided by the expected count.

| Set | Ratio | Observed / expected | E | p |
|---|---|---|---|---|
| H | 9/8 | 0 / 3.87 | 0.00 | 1 |
| H | 6/5 | 1 / 8.51 | 0.12 | 0.9998 |
| H | 5/4 | 14 / 12.77 | 1.10 | 0.40 |
| H | 4/3 | 28 / 21.15 | 1.32 | 0.088 |
| H | 3/2 | 84 / 35.43 | 2.37 | 2.9e-12 |
| H | 7/4 | 29 / 40.35 | 0.72 | 0.97 |
| H | 2/1 | 71 / 41.39 | 1.72 | 1.8e-5 |
| First-order rival | 7/6 | 4 / 6.18 | 0.65 | 0.86 |
| First-order rival | 8/7 | 2 / 4.78 | 0.42 | 0.95 |
| First-order rival | 10/9 | 0 / 3.26 | 0.00 | 1 |
| Same-order rival | 5/2 | 30 / 28.81 | 1.04 | 0.44 |
| Same-order rival | 8/5 | 31 / 38.97 | 0.80 | 0.92 |
| Same-order rival | 10/7 | 25 / 30.42 | 0.82 | 0.86 |
| Same-order rival | 11/8 | 20 / 25.43 | 0.79 | 0.88 |

**Reading.**
- Prediction (a) holds, but 3:2 and 2:1 carry it. Those are the known first-order resonances, and orbital dynamics already favors them.
- 9/8 and 6/5 are depleted.
- 7/4 is depleted, and it loses to every same-order rival.
- The verdicts hold at kernel bandwidths 0.05 and 0.20.

**Solar system.**
- Neptune–Pluto: 3/2, +0.3%.
- Venus–Earth: 8/5, +1.6%.
- Mercury–Venus: 5/2, +2.2%.
- Jupiter–Saturn: 5/2, −0.7%.
- No pair lands near 7/4.

**Caveats.**
- Detection selection effects.
- Planets that exist but haven't been detected turn some counted "neighbors" into non-neighbors.
- Six of the seven ratios in H are themselves first-order ratios.

## T-4.1 · Where alpha peaks sit

**Data:** PhysioNet EEGMMIDB, run R02 (eyes closed), all 109 subjects. O1, Oz and O2 averaged; Welch PSD with 8 s windows.

- **Peak frequencies (IAF):** mean 10.08 Hz, sd 1.06 Hz. The two largest bins are 9.75–10.25 Hz.

| Band | Observed | Expected | E | p |
|---|---|---|---|---|
| 8.81 ± 0.2 | 8 | 8.03 | 1.00 | 0.55 |
| 13.70 ± 0.2 | 0 | 0.05 | 0 | 1 |
| Rival 8.30 | 3 | 4.05 | 0.74 | 0.77 |
| Rival 9.30 | 9 | 12.49 | 0.72 | 0.88 |
| Rival 10.30 | 25 | 15.97 | 1.57 | 0.022 |

- **H1 and H2 both fail.**
- **13.7 Hz sits in the beta band.** The test had almost no power there, because resting alpha peaks rarely land that high.
- **The 10.30 excess was not pre-registered.** It probably reflects a Gaussian that fits this distribution poorly.

## T-5.5 · Heart and breath at just ratios

**Data:** PhysioNet slpdb, all 18 records, 5,117 one-minute windows. Median heart rate 1.169 Hz, median breath rate 0.237 Hz. Heart:breath ratios folded into one octave; ±1% windows.

| Set | Ratio | Observed / expected | E |
|---|---|---|---|
| H | 9/8 | 151 / 164.7 | 0.92 |
| H | 6/5 | 162 / 156.0 | 1.04 |
| H | 5/4 | 139 / 146.5 | 0.95 |
| H | 4/3 | 156 / 153.2 | 1.02 |
| H | 3/2 | 166 / 162.1 | 1.02 |
| H | 7/4 | 121 / 118.9 | 1.02 |
| Rival | 7/6 | 184 / 162.2 | 1.13 |
| Rival | 8/7 | 166 / 164.4 | 1.01 |
| Rival | 7/5 | 184 / 170.3 | 1.08 |
| Rival | 8/5 | 131 / 129.1 | 1.02 |
| Rival | 5/3 | 97 / 115.0 | 0.84 |
| Rival | 9/5 | 134 / 124.3 | 1.08 |
| Rival | 11/8 | 168 / 164.6 | 1.02 |
| Rival | 13/8 | 132 / 122.7 | 1.08 |

- **Record-level bootstrap** (not part of the verdict): mean E(H) − mean E(rivals) = −0.038, 95% interval [−0.093, +0.013].
- **Population caveat:** these are sleep-lab patients, mostly men with sleep apnea, recorded while asleep.

## P-3 · W versus GHZ (7 qubits)

| State | Pair concurrence | Negativity across a 3 : 3 cut after one member leaves |
|---|---|---|
| GHZ₇ | 0 | 0 |
| W₇ | 0.286 (= 2/7) | 0.363 |

## What round 2 teaches

The framework's quantitative content concentrates in two places:
- the algebra of 𝔽₇ and 𝔽₈: MUBs, the seven-share code, and frames;
- the hypercube's dynamics.

The number seven, or the seven just ratios, attached directly to orbits, brains or breath, did not stand out against rivals. That still leaves the Resonance reading intact as philosophy. The Receipts now point to where the next hard tests belong:
- native qudit hardware;
- [[7,1,4]]₇;
- tomography under real error;
- frame-invariant fingerprints.

## Files

- **Scripts:** `scripts/t2_quantum_round2.py`, `t4_5_orbits.py`, `t4_1_alpha.py`, `t5_5_heart_breath.py`, `round2_hardware.py`
- **Results:** `results/*.json`
