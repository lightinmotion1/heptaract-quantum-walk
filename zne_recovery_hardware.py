#!/usr/bin/env python3
"""
zne_recovery_hardware.py  --  fight the chain noise with Zero-Noise Extrapolation.

We proved we can't out-SHAPE the ~2.4% chain gap (linear chain is depth-optimal on a
line). So now we push it back the only honest way left: turn the noise deliberately UP,
measure, and extrapolate back to zero.

  Zero-Noise Extrapolation (ZNE): run the circuit at noise factors 1x, 3x, 5x
  (each gate folded with its own inverse -- does nothing ideally, but multiplies the
  real noise), then extrapolate the measured correlation back to the 0x (noiseless) point.

We measure the average pairwise <Z_iZ_j> of the 7-qubit GHZ (ideal = +1.0) TWO ways:
    RAW  (resilience_level=0)  -- no mitigation, what the machine actually gives
    ZNE  (resilience_level=2)  -- IBM's built-in zero-noise extrapolation
and watch ZNE lift the number back toward 1.0. Requires saved credentials.
"""
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator

N_QUBITS = 7

def ghz_prep(n):                       # NO measurement (Estimator measures observables itself)
    qc = QuantumCircuit(n); qc.h(0)
    for k in range(n - 1): qc.cx(k, k + 1)
    return qc

def zz(i, j, n):                       # observable Z_i Z_j as an n-qubit Pauli
    s = ['I'] * n; s[n - 1 - i] = 'Z'; s[n - 1 - j] = 'Z'
    return SparsePauliOp(''.join(s))

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=N_QUBITS)
    print(f"Running on real backend: {backend.name}")

    isa = transpile(ghz_prep(N_QUBITS), backend, optimization_level=3)
    pairs = list(combinations(range(N_QUBITS), 2))
    obs = [zz(i, j, N_QUBITS).apply_layout(isa.layout) for (i, j) in pairs]

    def run(level, label):
        est = Estimator(mode=backend)
        est.options.resilience_level = level
        if level == 2:  # nudge ZNE to 1x,3x,5x with a linear extrapolation
            try:
                est.options.resilience.zne.noise_factors = (1, 3, 5)
                est.options.resilience.zne.extrapolator = "linear"
            except Exception:
                pass
        print(f"Submitting {label} (resilience_level={level})...")
        job = est.run([(isa, obs)])
        print(f"  Job ID: {job.job_id()} -- waiting...")
        evs = np.asarray(job.result()[0].data.evs, dtype=float)
        return evs

    raw = run(0, "RAW")
    zne = run(2, "ZNE")

    print("\n--- average pairwise <Z_iZ_j>  (ideal = +1.000) ---")
    print(f"  RAW (no mitigation): {raw.mean():+.3f}")
    print(f"  ZNE (extrapolated) : {zne.mean():+.3f}")
    lift = zne.mean() - raw.mean()
    print(f"\n  ZNE lifted the correlation by {lift*100:+.1f} points, "
          f"closing {100*lift/max(1-raw.mean(),1e-6):.0f}% of the gap to the ideal 1.0.")
    print("  (If ZNE lands well above RAW and near 1.0, the noise was 'un-eaten' without any")
    print("   error-correcting hardware -- prediction's cousin, correction's doorway.)")

if __name__ == "__main__":
    main()
