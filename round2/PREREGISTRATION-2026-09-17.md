# HEPTARACT test round 2: pre-registration

**Declared:** 2026-09-17 05:15 UTC, before any data or run in this round was touched.
**Desk:** Free (Miah J. Fry) & Claude
**Rule for this round:** HEPTARACT has to beat a rival, not only the null.

- Where the framework says *seven*, the same test runs at the neighboring numbers.
- Where the framework says *the seven just ratios* (9/8, 6/5, 7/4, 3/2, 4/3, 2/1, 5/4), the same test runs on a matched set of control ratios the framework does not name.

A result counts only against the prediction, window and rival written here. Changing a window after seeing data voids that reading. The SHA-256 of this file is published in the tree's changelog.

---

## Quantum & base-7

### T-2.5 · The helix walk

**Geometry.** The helix of n-gons, H(n, L), is a spiral path of nL + 1 vertices, numbered 0 … nL. Two kinds of edges join them:
- **Path edges:** k ~ k+1.
- **Climb edges:** k ~ k+n. These encode "the eighth is the first, one climb up."

**Walk.** A continuous-time quantum walk on the adjacency matrix, starting at vertex 0.

**Metric.** The best transfer fidelity, max over t in [0, 60] of |⟨target| e^(−iAt) |0⟩|², sampled at Δt = 0.005. Two targets are scored:
- (a) vertex n, the same degree one climb up;
- (b) vertex nL, the top.

**Cases.** n ∈ {5, 6, 7, 8} and L ∈ {2, 3}.

**HEPTARACT prediction.** n = 7 gives the highest best-transfer fidelity among the four n, for both targets and both L.

**Wrong if.** Any other n matches (within 0.01) or beats n = 7 in the majority of the four (target, L) cells.

### T-2.6 · Reading from the hub (wheel graphs)

**Setup.** The wheel W_n is a hub joined to every vertex of an n-cycle. A quantum walk starts at the hub.

**Metric.** The largest share of the walk that ever leaves the hub.

**Prediction.** None specific to seven was ever written. The test is run as a check on whether "from center" singles out n = 7 in this simplest model.

**Wrong if.** Not applicable (exploratory, labeled as such).

### T-2.7 · Base-d break-even curves

**Setup.** For d = 2 … 16, compute:
- the readout break-even, f^(log₂ d), at f = 0.99;
- the gate-error break-even multiplier, (log₂ d)²;
- the embedding waste, 2^⌈log₂ d⌉ − d.

**HEPTARACT prediction.** d = 7 sits off the smooth curves in the framework's favor.

**Wrong if.** d = 7 lies on the smooth curves. In that case seven's only distinction is being prime and fitting inside three qubits with one spare level.

### T-1.5 · GHZ size scan on one chip (IBM hardware)

**Setup.**
- Prepare an n-qubit GHZ state on the first n qubits of one fixed linear chain on one IBM device, for n = 5, 6, 7, 8, 9, all in the same job.
- Fidelity: F_n = (P₀ + P₁)/2 + C_n/2.
  - P₀ and P₁ are the all-zero and all-one populations.
  - C_n is the parity-oscillation amplitude from four phase settings, φ_j = 2πj / (4n).
  - Each setting gets 4,096 shots.
- Per-qubit fidelity: f_n = F_n^(1/n).

**HEPTARACT prediction.** f_7 sits above the straight-line trend fitted through n = 5, 6, 8, 9 by more than two bootstrap standard errors.

**Wrong if.** f_7 lies within two standard errors of the trend.

---

## Particles of thought (models of the idea, not tests of minds)

### P-1 · The fire, read two ways (IBM hardware)

**Setup.** A seven-qubit star graph state: one center (the fire) and six rim qubits.
- Measure the center in X ("from the face") or in Z ("as a point").
- Then read the rim's six-body coherence, C₆, conditioned on the center's outcome.

**Physics prediction (standard quantum mechanics).**
- Center read in X: the rim stays one six-body whole, C₆ ≥ 0.5.
- Center read in Z: the rim falls into separate parts, |C₆| ≤ 0.1.

**Wrong if.** Either inequality fails.

### P-2 · Shared by many, not by pairs (IBM hardware)

**Setup.** On GHZ-7, read ⟨XᵢXⱼ⟩ and ⟨YᵢYⱼ⟩ for all 21 pairs (two circuits). Take the seven-body coherence C₇ from T-1.5.

**Prediction.**
- Every pair shows |⟨XX⟩| ≤ 0.1 and |⟨YY⟩| ≤ 0.1, meaning no pair holds entanglement on its own.
- C₇ ≥ 0.5, meaning the whole group does.

**Wrong if.** Either part fails.

### P-3 · W versus GHZ (computed)

**Setup.** Remove one member (trace out one qubit) from W₇ and from GHZ₇, then compute the entanglement left among the remaining six and between remaining pairs.

**Prediction (standard).**
- The GHZ bond needs every member.
- The W bond survives a departure.

This is the language for "dancing around the fire or not."

---

## Earth & sky

### T-4.5 · Just ratios in planetary orbits

**Data.** NASA Exoplanet Archive, table pscomppars.
- Keep every system with two or more planets that have orbital periods.
- For each pair of neighboring planets, take the period ratio r = P_outer / P_inner, keeping 1 < r ≤ 3.2.
- Add the solar-system neighbors, reported separately.

**Windows.**
- Primary: the just-wide window [q, 1.03q].
- Secondary: the symmetric window [0.99q, 1.01q].

**Sets.**
- H: 9/8, 6/5, 5/4, 4/3, 3/2, 7/4, 2/1.
- First-order rivals H omits: 7/6, 8/7, 10/9.
- Same-order rivals of 7/4 (third order): 5/2, 8/5, 10/7, 11/8.

**Expectation.** A smooth density of log r (Gaussian kernel, bandwidth 0.10 in natural log). Enrichment E = observed / expected. Poisson p-values.

**HEPTARACT predictions.**
- (a) The mean E of H exceeds the mean E of the first-order rivals, in the primary window.
- (b) E(7/4) exceeds E of every same-order rival, in the primary window.

**Wrong if.** (a) or (b) fails. Each is scored on its own.

### T-4.1 · Where alpha peaks sit

**Data.** PhysioNet EEG Motor Movement/Imagery, eyes-closed baseline (run R02) for every subject with that run.
- Channels O1, Oz, O2, averaged.
- Welch PSD with 8 s windows and 50% overlap.
- Individual alpha frequency (IAF) = the peak in 7–14 Hz, refined by parabolic interpolation.

**Bands.** Each is ±0.2 Hz.
- H1: 8.81 Hz (9/8 × 7.83).
- H2: 13.70 Hz (7/4 × 7.83).
- Rivals: 8.30, 9.30 and 10.30 Hz.

**Expectation.** A Gaussian fitted to all IAFs. Enrichment E = observed / expected in each band.

**HEPTARACT predictions.**
- H1: E(8.81) > 1 with Poisson p < 0.05, and E(8.81) exceeds every rival band's E.
- H2: E(13.70) > 1 with Poisson p < 0.05.

**Wrong if.** Each part fails on its own terms.

---

## Body & collective

### T-5.5 · Heart and breath at just ratios

**Data.** PhysioNet MIT-BIH Polysomnographic Database (slpdb), all records with ECG beat annotations and a respiration channel.
- In 60 s windows, compute heart rate from beat annotations and breathing rate from respiration peaks.
- Ratio ρ = f_heart / f_breath, folded into one octave: ρ′ = ρ / 2^⌊log₂ ρ⌋, so ρ′ ∈ [1, 2).
- The folding (octave equivalence) is itself a framework assumption, declared here.

**Sets and windows.** Each window is ±1% of the ratio.
- H: 9/8, 6/5, 5/4, 4/3, 3/2, 7/4.
- Rivals: 7/6, 8/7, 7/5, 8/5, 5/3, 9/5, 11/8, 13/8.

**Expectation.** A smooth density of ρ′ (Gaussian kernel, bandwidth 0.05).

**HEPTARACT prediction.** The mean E of H exceeds 1.2 and exceeds the mean E of the rivals.

**Wrong if.** Either fails.

### Protocols only (no data this round)

**T-6.1 · Tempo at a just ratio of the group's heart**
- A group sings or drums to a pulse set at 3/2 of the group's mean resting heart rate, versus a control ratio of 7/5.
- Order is counterbalanced, and HRV straps are worn throughout.
- Prediction: higher group HRV synchrony under the just ratio.
- Wrong if the difference is zero or reversed.

**T-6.2 · Does coupling grow faster than the group, at just ratios?**
- Groups of N = 2, 4, 8 and 16 people, under the T-6.1 conditions.
- Prediction: synchrony rises super-linearly in N, and only in the just-ratio condition.

**T-5.6 · The QpC center versus the center of mass (Book Eight, Ask #2)**
- Multi-sensor mapping of coherence under axis-specific load, such as sleep loss or isolation.
- Prediction: the coherence-weighted center moves away from the body's center of mass by more than the measurement error.
