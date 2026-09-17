#!/usr/bin/env python3
"""
noise_fingerprint_7q_hardware.py  --  "measure and define the frontier."

Scales the relationship-measurement to 7 qubits (change N_QUBITS to 9 if you like)
and turns the pairwise DISTORTIONS into a full per-qubit NOISE FINGERPRINT of a
real IBM machine -- Miah's "predict the noise" idea, at scale.

HOW IT WORKS
  1. Prepare a 7-qubit GHZ state (all 7 entangled; shallow -- 1 H + 6 CNOTs).
  2. Measure all qubits in Z, many shots.
  3. Compute every individual <Z_i> (should be ~0) and every pairwise <Z_iZ_j>.
  4. All 21 pairs share ONE measurement setting (they commute), so this is cheap.
  5. Solve  log f_i + log f_j = log<Z_iZ_j>  (least squares) for each qubit's
     readout fidelity f_i.  21 equations, 7 unknowns = 3x OVER-DETERMINED:
     we solve the noise AND cross-check it. Leftover residuals = correlated noise.

Requires saved credentials (run save_creds.py once first).
"""
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

N_QUBITS = 7      # <-- change to 9 for the 9D version
SHOTS = 8192

def ghz(n):
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for k in range(n - 1):
        qc.cx(k, k + 1)
    qc.measure(range(n), range(n))
    return qc

def fingerprint(counts, n):
    total = sum(counts.values())
    zval = lambda bit: 1 if bit == '0' else -1
    Zi = np.zeros(n)
    pairs = list(combinations(range(n), 2))
    Zij = {p: 0.0 for p in pairs}
    for bits, c in counts.items():
        b = bits[::-1].zfill(n)          # qiskit is little-endian; qubit k -> b[k]
        w = c / total
        v = [zval(b[k]) for k in range(n)]
        for k in range(n):
            Zi[k] += v[k] * w
        for (i, j) in pairs:
            Zij[(i, j)] += v[i] * v[j] * w
    # least-squares solve for per-qubit readout fidelity
    A = np.zeros((len(pairs), n)); rhs = np.zeros(len(pairs))
    for r, (i, j) in enumerate(pairs):
        A[r, i] = 1; A[r, j] = 1
        rhs[r] = np.log(max(Zij[(i, j)], 1e-6))
    x, *_ = np.linalg.lstsq(A, rhs, rcond=None)
    f = np.exp(x)
    residuals = {p: f[p[0]] * f[p[1]] - Zij[p] for p in pairs}
    return Zi, Zij, f, residuals

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=N_QUBITS)
    print(f"Running on real backend: {backend.name}")

    tqc = transpile(ghz(N_QUBITS), backend, optimization_level=3)
    print(f"Transpiled {N_QUBITS}-qubit GHZ. Submitting...")
    job = Sampler(backend).run([tqc], shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()}")
    print("Waiting for results -- a few minutes in the free queue. Leave it running...")
    counts = job.result()[0].data.c.get_counts()

    Zi, Zij, f, resid = fingerprint(counts, N_QUBITS)
    print("\n--- INDIVIDUAL VALUES (want ~0) ---")
    print("  " + "  ".join(f"<Z{k}>={Zi[k]:+.3f}" for k in range(N_QUBITS)))
    print("\n--- NOISE FINGERPRINT: per-qubit readout fidelity (solved from the pair distortions) ---")
    for k in range(N_QUBITS):
        print(f"  qubit {k}: {f[k]*100:5.1f}%   (~{(1-f[k])*100:.1f}% error)")
    worst = int(np.argmin(f)); best = int(np.argmax(f))
    print(f"  noisiest qubit: {worst} ({f[worst]*100:.1f}%)   cleanest: {best} ({f[best]*100:.1f}%)")
    maxres = max(abs(v) for v in resid.values())
    print(f"\n--- CROSS-CHECK (21 pairs vs 7 solved singles) ---")
    print(f"  largest reconstruction residual = {maxres:.3f}")
    print("  small everywhere  -> noise is well-described as independent per-qubit readout.")
    print("  a few large ones  -> those pairs carry CORRELATED noise the simple model misses.")

if __name__ == "__main__":
    main()
