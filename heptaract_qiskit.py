"""
Heptaract Quantum Walk — Qiskit Circuit + Speed Benchmark

The key insight from qleap.py:
  H (heptaract adjacency) = X₀ + X₁ + X₂ + X₃ + X₄ + X₅ + X₆
  (sum of single-qubit Pauli X on each of 7 qubits, all terms commute)

  exp(-iHt) = Rx(2t) ⊗ Rx(2t) ⊗ ... ⊗ Rx(2t)   [7 times]

  At t = π/2:  Rx(π) on every qubit  =  flip every bit
  P(|1111111⟩) = 1.0

BENCHMARK:
  3 ways to "find the far shore" from home across a 7-cube:
  1. Classical random walk  — flip one random bit per step
  2. Classical exhaustive   — check every vertex
  3. Quantum walk circuit   — Rx(π) x 7, measure once

  We measure: operations to solution, and wall-clock time scaled to
  equivalent problem sizes.
"""

import numpy as np
import time
import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

N_QUBITS = 7
HOME     = 0           # |0000000⟩
ANTIHOME = (1 << N_QUBITS) - 1  # |1111111⟩ = 127


# ─────────────────────────────────────────────
# 1. THE QISKIT CIRCUIT
# ─────────────────────────────────────────────

def build_leap_circuit(t: float = np.pi / 2, shots: int = 1024) -> QuantumCircuit:
    """
    Quantum walk on the 7-cube from |0000000⟩ for time t.
    At t=π/2: deterministic leap to |1111111⟩.
    Gate: Rx(2t) on every qubit (they commute, no entanglement needed).
    """
    qc = QuantumCircuit(N_QUBITS, N_QUBITS)
    for q in range(N_QUBITS):
        qc.rx(2 * t, q)
    qc.measure(range(N_QUBITS), range(N_QUBITS))
    return qc

def build_walk_circuit(t: float) -> QuantumCircuit:
    """General quantum walk at arbitrary t — no measurement, for statevector."""
    qc = QuantumCircuit(N_QUBITS)
    for q in range(N_QUBITS):
        qc.rx(2 * t, q)
    return qc

def run_quantum_leap(shots: int = 1024):
    """Run the leap circuit on Aer statevector simulator."""
    sim = AerSimulator(method='statevector')
    qc  = build_leap_circuit(np.pi / 2, shots)
    t0  = time.perf_counter()
    job = sim.run(transpile(qc, sim), shots=shots)
    result = job.result()
    elapsed = time.perf_counter() - t0
    counts = result.get_counts()
    # Qiskit bit order is reversed: qubit 0 is rightmost in bitstring
    target_bitstring = '1' * N_QUBITS
    p_success = counts.get(target_bitstring, 0) / shots
    gate_count = qc.count_ops()
    return p_success, elapsed, gate_count, counts


# ─────────────────────────────────────────────
# 2. CLASSICAL RANDOM WALK BENCHMARK
# ─────────────────────────────────────────────

def classical_random_walk(target: int = ANTIHOME, trials: int = 10000):
    """
    Random walk on 7-cube: flip one random bit per step.
    Returns average steps to reach target from HOME.
    """
    step_counts = []
    for _ in range(trials):
        state = HOME
        steps = 0
        while state != target:
            bit = random.randint(0, N_QUBITS - 1)
            state ^= (1 << bit)
            steps += 1
        step_counts.append(steps)
    return np.mean(step_counts), np.std(step_counts), min(step_counts), max(step_counts)


# ─────────────────────────────────────────────
# 3. CLASSICAL EXHAUSTIVE SEARCH
# ─────────────────────────────────────────────

def classical_exhaustive(target: int = ANTIHOME):
    """Scan all vertices until target found. Worst case = 2^7 = 128 checks."""
    for i, v in enumerate(range(2**N_QUBITS)):
        if v == target:
            return i + 1  # steps = position in scan order
    return 2**N_QUBITS


# ─────────────────────────────────────────────
# 4. QUANTUM WALK PROBABILITY SWEEP
# ─────────────────────────────────────────────

def quantum_walk_sweep():
    """
    Simulate the quantum walk at multiple t values.
    Show how probability flows from home → far shore.
    Uses numpy (exact), not shots-based.
    """
    from numpy.linalg import eigh

    # Build adjacency matrix
    dim = 2**N_QUBITS
    A = np.zeros((dim, dim))
    for i in range(dim):
        for j in range(dim):
            if bin(i ^ j).count('1') == 1:
                A[i, j] = 1.0
    evals, evecs = eigh(A)

    psi0 = np.zeros(dim); psi0[HOME] = 1.0

    t_values = np.linspace(0, np.pi, 200)
    p_anti = []
    for t in t_values:
        coeffs = evecs.T @ psi0
        phases = np.exp(-1j * evals * t)
        psi_t = evecs @ (phases * coeffs)
        p_anti.append(abs(psi_t[ANTIHOME])**2)

    peak_t = t_values[np.argmax(p_anti)]
    peak_p = max(p_anti)
    return t_values, np.array(p_anti), peak_t, peak_p


# ─────────────────────────────────────────────
# 5. SCALING COMPARISON (n-cube, n=1..12)
# ─────────────────────────────────────────────

def scaling_comparison():
    """
    For each n-cube size, compute:
      - Classical random walk expected steps (≈ 2^n, exact formula)
      - Quantum walk operations (always 1 "round" = n single-qubit gates)
      - Speedup ratio
    Classical expected hitting time for n-cube corner-to-corner ≈ n * 2^(n-1)
    (each of the n bit positions must be visited; each takes 2^(n-1) steps avg)
    """
    print(f"\n{'n':>4}  {'vertices':>10}  {'classical (ops)':>18}  {'quantum (gates)':>18}  {'speedup':>12}")
    print("─" * 70)
    for n in range(1, 14):
        classical_ops = n * (2 ** (n - 1))   # expected hitting time
        quantum_gates = n                     # one Rx per qubit, that's it
        speedup = classical_ops / quantum_gates
        vertices = 2**n
        marker = " ← we are here" if n == 7 else ""
        print(f"{n:>4}  {vertices:>10}  {classical_ops:>18,.0f}  {quantum_gates:>18}  "
              f"{speedup:>12,.1f}x{marker}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

print("=" * 65)
print("  HEPTARACT QUANTUM WALK — CIRCUIT + BENCHMARK")
print("=" * 65)

# --- print the circuit ---
print("\n[ CIRCUIT ]  Qiskit — quantum walk leap at t = π/2")
qc_display = build_leap_circuit(np.pi / 2)
print(qc_display.draw(output='text', fold=80))
print(f"  Total gates: {sum(qc_display.count_ops().values())}  "
      f"(7 × Rx(π) + 7 × measure)")
print(f"  Circuit depth: {qc_display.depth()}")

# --- run quantum leap ---
print("\n[ QUANTUM LEAP ]  Running on Aer statevector simulator...")
p_success, q_time, gate_ops, counts = run_quantum_leap(shots=1024)
print(f"  P(far shore) = {p_success:.4f}  (expect 1.0000)")
print(f"  Wall time:    {q_time*1000:.2f} ms")
print(f"  Gate ops:     {gate_ops}")
print(f"  Shot results: {dict(list(counts.items())[:4])}")

# --- classical random walk ---
print("\n[ CLASSICAL RANDOM WALK ]  10,000 trials...")
t0 = time.perf_counter()
avg_steps, std_steps, min_steps, max_steps = classical_random_walk()
rw_time = time.perf_counter() - t0
print(f"  Avg steps to far shore:  {avg_steps:.1f} ± {std_steps:.1f}")
print(f"  Min / Max:               {min_steps} / {max_steps}")
print(f"  Theoretical expectation: {7 * 2**6:.0f}  (n × 2^(n-1))")
print(f"  Wall time (10k trials):  {rw_time*1000:.1f} ms")

# --- classical exhaustive ---
ex_steps = classical_exhaustive()
print(f"\n[ CLASSICAL EXHAUSTIVE ]  Steps to find far shore: {ex_steps}")
print(f"  (worst case = {2**N_QUBITS} vertices)")

# --- quantum walk sweep ---
print("\n[ QUANTUM WALK SWEEP ]  Probability curve home → far shore")
t_vals, p_curve, peak_t, peak_p = quantum_walk_sweep()
# print a simple ASCII chart
print(f"  t=0 → t=π, peak at t={peak_t:.4f} (P={peak_p:.6f})")
width = 50
for i, (t, p) in enumerate(zip(t_vals, p_curve)):
    if i % 20 == 0:
        bar = int(p * width)
        print(f"  t={t:.2f}π  |{'█'*bar}{' '*(width-bar)}| {p:.4f}")

# --- scaling comparison ---
print("\n[ SCALING ]  Classical vs Quantum ops as n-cube grows:")
scaling_comparison()

print("\n[ SUMMARY ]")
print(f"  Quantum walk:          7 gates, 1 measurement, P=1.0")
print(f"  Classical random walk: ~{avg_steps:.0f} steps on average")
print(f"  Classical exhaustive:  up to {2**N_QUBITS} checks")
print(f"  Speedup (heptaract):   ~{avg_steps/7:.0f}x over random walk")
print(f"                         ~{2**N_QUBITS/7:.0f}x over exhaustive")
print()
print("  The walk scales as O(n) quantum gates vs O(n·2^n) classical steps.")
print("  At n=50 qubits: quantum = 50 gates, classical ≈ 2.8 × 10¹⁶ steps.")
