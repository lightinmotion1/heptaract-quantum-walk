# Perimeter Institute — Quantum Information Group
# Email to: quantuminfo@perimeterinstitute.ca

**Subject:** Heptaract quantum walk — geometric invariance result and open questions

---

Dear Perimeter Quantum Information Group,

I'm writing with a result that sits at the boundary between quantum walk algorithms and geometric/harmonic structure — the kind of question that feels more at home at Perimeter than anywhere else.

**The short version:**

The continuous-time quantum walk on the 7-dimensional hypercube (heptaract) achieves perfect corner-to-corner state transfer at t = π/2 via a depth-2, zero-entanglement circuit. That part is clean and verifiable. But the structure has an additional property that I don't know how to explain:

When the 7 axes are assigned the seven fundamental just-intonation pitch ratios (the 7-limit intervals: 2/1, 3/2, 4/3, 5/4, 6/5, 7/4, 9/8), the 128 vertices collapse to 32 pitch classes. The most consonant vertex — the tonic, ratio 1/1 — is invariant under all 5040 permutations of axis labels. The spectral gap that drives the quantum transfer (Δ = 2) maps precisely to the perfect fifth (3:2), which is also the interval that anchors every minimal triangular neighborhood in the graph.

This may be a known result in algebraic graph theory or spectral combinatorics. If so, I'd genuinely like to know the reference. If not, it raises a question I find hard to dismiss:

*If the heptaract's 7 axes correspond to physical commuting observables, does the spectral structure constrain which transitions are energetically favored — and does the "home" ground state appear there for the same reason it appears in the pitch system?*

I'm not claiming a physical theory. I'm asking whether the geometry is pointing at one.

**What's attached / linked:**
- Full reproducible code (numpy + Qiskit 2.4)
- Benchmark results (64x speedup at n=7, O(n) vs O(n·2^n) scaling)
- Draft note: [arXiv link]

I'd welcome a conversation, a pointer to relevant prior work, or a correction if I've missed something obvious.

Thank you for your time.

[Name]
[Contact]
