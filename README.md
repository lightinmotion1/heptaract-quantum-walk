# Heptaract Quantum Walk

**Perfect state transfer across the 7-dimensional hypercube — depth-2 circuit, zero entanglement, P=1.0**

## The Result

The continuous-time quantum walk on the 7-cube (heptaract) transfers a state from one corner `|0000000⟩` to the opposite corner `|1111111⟩` with probability 1.0, using only 7 single-qubit gates at circuit depth 2.

```
q0: ──[Rx(π)]──[M]──
q1: ──[Rx(π)]──[M]──
q2: ──[Rx(π)]──[M]──
q3: ──[Rx(π)]──[M]──
q4: ──[Rx(π)]──[M]──
q5: ──[Rx(π)]──[M]──
q6: ──[Rx(π)]──[M]──
```

The Hamiltonian factors exactly because the 7 axis terms commute:

```
H = Σᵢ Xᵢ  →  exp(-iHt) = ⊗ᵢ Rx(2t)
```

At t = π/2: P(|1111111⟩) = 1.0

## Benchmark

| Method | Operations | P(success) |
|--------|-----------|------------|
| **Quantum walk (this work)** | **7 gates** | **1.0000** |
| Classical random walk | ~165 steps avg | eventual |
| Classical exhaustive | up to 128 checks | eventual |

**64x speedup at n=7. Scales as O(n) quantum vs O(n·2^n) classical.**

| n | Quantum gates | Classical steps | Speedup |
|---|--------------|----------------|---------|
| 7 | 7 | 448 | 64x |
| 13 | 13 | 53,248 | 4,096x |
| 50 | 50 | ~2.8 × 10¹⁶ | ~10¹⁴x |

## Bonus Finding: Pitch-Class Invariance

When the 7 axes are assigned just-intonation ratios (2/1, 3/2, 4/3, 5/4, 6/5, 7/4, 9/8), the 128 vertices collapse to 32 distinct pitch classes. The tonic (1/1) is invariant under all 5040 axis-label permutations — any system wiring these 7 intervals into a 7-cube finds the same natural ground state.

The spectral gap driving the quantum transfer (Δ=2) maps to the perfect fifth (3:2) — the same interval anchoring every minimal triangular neighborhood in the graph.

## Files

| File | Description |
|------|-------------|
| `heptaract_qiskit.py` | Qiskit circuit + full benchmark |
| `qleap.py` | Quantum walk simulation (numpy) |
| `heptaract.py` | Pitch-class analysis + invariance test |
| `paper/heptaract_note.md` | Technical write-up (arXiv draft) |
| `heptaract_subatomic.py` | Sub-atomic relationship structure — SO(10)/SO(14) spinors as hypercube parity classes, anomaly cancellation, Fano/octonion axis algebra (no dependencies) |
| `heptaract_frequency.py` | Sound science — the heptaract spectrum as a harmonic ladder, roughness-model consonance, Schumann correction, body-axis coupling audit (no dependencies) |
| `paper/The Heptaract Papers v3.9.md` | Full framework document — Book Thirteen is the sub-atomic discussion, Q&A, and R&D |
| `results/` | Pre-generated output from all scripts |

## Requirements

```bash
pip install qiskit qiskit-aer numpy
```

## Run It

```bash
python3 heptaract_qiskit.py   # circuit + benchmark
python3 qleap.py               # quantum walk sweep
python3 heptaract.py           # pitch analysis
python3 heptaract_subatomic.py # sub-atomic receipts (stdlib only)
python3 heptaract_frequency.py # sound / frequency receipts (stdlib only)
```

## Hardware Verification

This circuit runs on any current 7-qubit NISQ device. Circuit depth 2 is well within fidelity range. If you run it on real hardware, open an issue with your results.

## Open Questions

1. Is the pitch-class invariance a known result in algebraic graph theory?
2. The 7/4 vertex has identical path-multiplicity (6) to the 1/1 home vertex — is there a symmetry group mapping one to the other?
3. If physical observables map to heptaract axes, does spectral gap Δ=2 correspond to a measurable transition energy?

## Sub-Atomic Structure

`heptaract_subatomic.py` runs the same hypercube machinery one floor below the atom, and prints the receipts. Standard library only — no numpy, no qiskit.

- **The settled hypercube of matter has five axes, not seven.** One generation of fermions is exactly the 16 even-parity vertices of a 5-cube — the SO(10) spinor weights. Every Standard Model charge is a linear function of the vertex, and **all four gauge anomalies cancel as a parity condition** (Σ Y = Σ Y³ = 0, computed, nothing assumed). This is the honest lead, and it is a penteract.
- **The heptaract's rung is SO(14).** The 128 vertices split by parity into 64 + 64 — the two Weyl spinors of SO(14). Under SO(10) × SO(4) the 64 branches as **2 generations + 2 mirror generations**. The mirror problem is real, unsolved, and printed rather than buried.
- **Parity is chirality, and seven is odd.** Home vertex and far shore lie in opposite parity classes, so the depth-2 perfect-transfer walk carries 64 → 64-bar. `t = ±π/2` is a chirality exchange, and Hamming distance from home is an exact U(1) charge, X = 7/2 − k.
- **The seven axes carry an algebra.** Fano plane → octonion multiplication, verified numerically (norm-multiplicative to 9e−15, alternative, associative exactly on the seven lines). G₂ = Aut(𝕆) is the holonomy group of the 7-manifolds M-theory compactifies on. That seven is not ours — Furey 2018, Acharya & Witten 2001, Freund–Rubin — which is why it is the one worth chasing.

**Not claimed:** no new force, no new particle, no mass prediction, and **no energy scale** — Δ = 2 is dimensionless and stays UNASSIGNED. The just-intonation axis ratios and the Schumann band carry **no** sub-atomic claim and are marked DO NOT COUPLE.

Full discussion, a twelve-question Q&A, a three-track R&D programme, and five named kill conditions: **Book Thirteen** of `paper/The Heptaract Papers v3.9.md`.

**Cheapest way to refute it:** show the bit-to-sign identification behind the chirality reading cannot be made canonical. That is an afternoon's work and it takes out the load-bearing section. Open an issue.

## Sound & Frequency

`heptaract_frequency.py` — same discipline, applied to the frequency claims. Standard library only.

- **The spectrum is a harmonic ladder.** H = Σ Xᵢ has eigenvalues 7, 5, 3, 1, −1, −3, −5, −7 with binomial multiplicities — every gap exactly **Δ = 2**. Evenly spaced is the condition for **full revival**, so P = 1.0 at t = π/2 is what a harmonic spectrum does, not a coincidence of seven. Seven only decides *where* the revival lands.
- **The walk is a chord.** Cross-checked two independent ways — a 128-mode Fourier sum against the closed product form — agreeing to 1e−15. At t = π/4 every vertex sits at exactly 1/128.
- **Consonance from roughness, not mysticism.** A Plomp–Levelt/Sethares sweep puts 5 of 5 minima on simple ratios within a quarter-cent. And **7/4 only becomes a consonance once the seventh partial enters the timbre** — a six-partial world hears the heart axis as out of tune.
- **Schumann, corrected.** The ideal-cavity formula overestimates every mode by ~20% (10.59 Hz vs the measured 7.83). 7.83 Hz is **measured, not derived** — the lossy-ionosphere correction does the work.
- **The audit we ran on ourselves.** The published body-axis coupling claim lands in its own bands on **3 of 7** axes as written; 7 of 7 under octave equivalence — but four bands are wider than an octave and *cannot fail*, so passing was ~15% likely by chance. Downgraded to **PROPOSED — NOT YET SCORED**, with the experiment that would settle it.

**Where sound stops:** a 7.83 Hz phonon carries ~3e−14 eV against ~0.027 eV of thermal energy at body temperature — twelve orders of magnitude. Low-frequency effects act through classical channels (piezoelectricity, PIEZO1/2 mechanotransduction, otoacoustic emission), not quantum ones. Sub-atomic **DO NOT COUPLE** stands.

Full treatment: **Book Fourteen** of `paper/The Heptaract Papers v3.9.md`.

---

*Seeking hardware verification and theoretical context. Reach out via issues or discussions.*
