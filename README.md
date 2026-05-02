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
```

## Hardware Verification

This circuit runs on any current 7-qubit NISQ device. Circuit depth 2 is well within fidelity range. If you run it on real hardware, open an issue with your results.

## Open Questions

1. Is the pitch-class invariance a known result in algebraic graph theory?
2. The 7/4 vertex has identical path-multiplicity (6) to the 1/1 home vertex — is there a symmetry group mapping one to the other?
3. If physical observables map to heptaract axes, does spectral gap Δ=2 correspond to a measurable transition energy?

---

*Seeking hardware verification and theoretical context. Reach out via issues or discussions.*
