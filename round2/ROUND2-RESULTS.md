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

## Hardware round · run 2026-09-17 on ibm_marrakesh

**Job** `dam750tr85ps73fcblg0` · chain [12, 13, 14, 15, 19, 35, 34, 33, 32] · 4096 shots per circuit · **40 seconds of QPU time**
(of the 600 in the 28-day window). Pre-registered in `PREREGISTRATION-2026-09-17.md`
(SHA-256 8d9d804f…20fc) before the account existed; nothing was changed after the data arrived.

| Test | Prediction | Verdict |
|---|---|---|
| T-1.5 | f₇ sits above the trend through n = 5, 6, 8, 9 by more than two bootstrap SE | **Narrows** (residual 0.00091, z = 1.21) |
| P-1 | reading the center in X leaves the rim bonded; reading in Z does not | **Holds** (C₆ = 0.802 vs 0.018) |
| P-2 | the seven-body correlation survives where every pair carries nothing | **Holds** (max pair 0.036, C₇ = 0.806) |

### T-1.5 · Is anything special at seven qubits?

| n | GHZ fidelity | Coherence | Population | Per-qubit f |
|---|---|---|---|---|
| 5 | 0.9044 | 0.8809 | 0.9280 | 0.98011 |
| 6 | 0.8768 | 0.8400 | 0.9136 | 0.97833 |
| 7 | 0.8562 | 0.8064 | 0.9060 | 0.97807 |
| 8 | 0.8282 | 0.7704 | 0.8860 | 0.97671 |
| 9 | 0.7853 | 0.7219 | 0.8486 | 0.97350 |

Fidelity falls smoothly as the state grows. Seven sits 0.00091 above the line
through its neighbors, against a bootstrap standard error of 0.00075 — z = 1.21, well
inside the noise. **Seven is not special to the machine.** The decline is the machine's own: each added
member costs roughly two percent of per-qubit fidelity.

### P-1 · The fire read two ways

The center qubit is read in one basis, and the six around it are scored afterward.

| Center read in | Rim C₆ |
|---|---|
| X | 0.8018 |
| Z | 0.0177 |

Same state, same chip, same moment. Reading the center along X leaves the six holding a bonded state;
reading along Z leaves them holding nothing measurable. The rim's condition is not a property the rim
owns on its own — the center's manner of reading decides. That is the fire reading, on hardware.

### P-2 · Pairs versus the whole

Every one of the 21 pairs of a GHZ-7 was measured in XX and in YY. The largest correlation of any pair is
0.0356 — nothing. The seven-body parity is 0.7969, and C₇ = 0.8064.
**The bond lives in the whole and in no part of it.** Take one member away and the rest carry nothing;
this is the GHZ character computed in P-3, now measured.

### What the hardware round teaches

The two predictions that held are about *relationship*: how the whole is read, and where the bond lives.
The one that narrowed is about *the number itself*. Seven earns nothing from the machine for being seven.
This is the same lesson round 2 gave from orbits, brains and breath, now from the cleanest instrument we
have — and it points the remaining work at the algebra (𝔽₇, 𝔽₈, MUBs, [[7,1,4]]₇) rather than at
seven-ness in nature.

## Files

- **Scripts:** `scripts/t2_quantum_round2.py`, `t4_5_orbits.py`, `t4_1_alpha.py`, `t5_5_heart_breath.py`, `round2_hardware.py`
- **Results:** `results/*.json`
