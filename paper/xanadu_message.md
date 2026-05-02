# Xanadu / PennyLane Community — Discord / GitHub Issue

**Subject:** Quantum walk on the heptaract — depth-2 perfect state transfer, looking for hardware verification

---

Hey PennyLane community —

Built something I'd love eyes on and ideally a hardware run.

**What it is:** A continuous-time quantum walk on the 7-cube (heptaract) that achieves perfect state transfer from |0000000⟩ to |1111111⟩ using a depth-2 circuit — 7 Rx(π) gates, zero entanglement, P=1.0.

The Hamiltonian factors cleanly because the 7 axis terms commute:

```
H = Σᵢ Xᵢ  →  exp(-iHt) = ⊗ᵢ Rx(2t)
```

At t = π/2 that's just 7 X-rotations. Verified 1024/1024 shots on Qiskit Aer.

**The benchmark:** 7 gates vs ~448 classical expected steps on the same graph. Scales as O(n) quantum vs O(n·2^n) classical. 64x at n=7, exponential beyond.

**The weird extra finding:** When you map the 7 axes to just-intonation pitch ratios (2/1, 3/2, 4/3, 5/4, 6/5, 7/4, 9/8), the 128 vertices collapse to 32 pitch classes, and the tonic (1/1) is invariant under all 5040 axis-label permutations. The spectral gap driving the transfer (Δ=2) maps to the perfect fifth. Not sure what to make of that yet but it feels like it's pointing at something.

**What I'm asking:**
1. Does anyone want to run this on real hardware? Should be clean on any current 7-qubit device — depth 2 is well within NISQ fidelity range.
2. Is the pitch-invariance result known? Feels like it might connect to something in algebraic graph theory I'm not aware of.

**Code:** [github link]
**arXiv:** [link once posted]

Happy to discuss either angle — the algorithm or the geometry.

Thanks
