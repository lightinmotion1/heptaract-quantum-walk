#!/usr/bin/env python3
"""
noise_clean_cut_hardware.py  --  separate READOUT noise from ENTANGLING-CHAIN noise.

The 7-qubit fingerprint blended two things. This splits them, in one job:
  * Circuit CAL0: prepare |000...0>, measure  -> pure readout error for the "0" side
  * Circuit CAL1: prepare |111...1>, measure  -> pure readout error for the "1" side
       (these have NO entangling gates, so they see ONLY readout error)
  * Circuit GHZ : the 7-qubit GHZ            -> readout error PLUS chain error

Per qubit:
    f_readout  = 1 - P(read1|prep0) - P(read0|prep1)      (pure readout, from CAL0/CAL1)
    f_ghz      = solved from GHZ pair-distortions          (readout + chain, blended)
    chain_gap  = f_readout - f_ghz                         (what the entangling chain cost)

All three circuits are transpiled onto the SAME physical qubits so the per-qubit
comparison is apples-to-apples. Requires saved credentials (run save_creds.py once).
"""
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

N_QUBITS = 7
SHOTS = 8192

def ghz(n):
    qc = QuantumCircuit(n, n); qc.h(0)
    for k in range(n - 1): qc.cx(k, k + 1)
    qc.measure(range(n), range(n)); return qc

def prep(n, ones=False):
    qc = QuantumCircuit(n, n)
    if ones:
        for k in range(n): qc.x(k)
    qc.measure(range(n), range(n)); return qc

def p_read1(counts, n):
    total = sum(counts.values()); p1 = np.zeros(n)
    for bits, c in counts.items():
        b = bits[::-1].zfill(n)
        for k in range(n):
            if b[k] == '1': p1[k] += c
    return p1 / total

def ghz_fidelity(counts, n):
    total = sum(counts.values()); pairs = list(combinations(range(n), 2)); Zij = {p: 0.0 for p in pairs}
    zval = lambda bit: 1 if bit == '0' else -1
    for bits, c in counts.items():
        b = bits[::-1].zfill(n); w = c / total; v = [zval(b[k]) for k in range(n)]
        for (i, j) in pairs: Zij[(i, j)] += v[i] * v[j] * w
    A = np.zeros((len(pairs), n)); rhs = np.zeros(len(pairs))
    for r, (i, j) in enumerate(pairs):
        A[r, i] = 1; A[r, j] = 1; rhs[r] = np.log(max(Zij[(i, j)], 1e-6))
    x, *_ = np.linalg.lstsq(A, rhs, rcond=None); return np.exp(x)

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=N_QUBITS)
    print(f"Running on real backend: {backend.name}")

    tghz = transpile(ghz(N_QUBITS), backend, optimization_level=3)
    try:
        layout = list(tghz.layout.final_index_layout()[:N_QUBITS])   # same physical qubits
    except Exception:
        layout = None
    def tp(circ):
        return transpile(circ, backend, initial_layout=layout, optimization_level=1) if layout \
               else transpile(circ, backend, optimization_level=1)
    tcal0, tcal1 = tp(prep(N_QUBITS, False)), tp(prep(N_QUBITS, True))

    print("Submitting 3 circuits (CAL0, CAL1, GHZ) in one job...")
    job = Sampler(backend).run([tcal0, tcal1, tghz], shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()}")
    print("Waiting for results -- a few minutes in the free queue...")
    res = job.result()
    c0 = res[0].data.c.get_counts(); c1 = res[1].data.c.get_counts(); cg = res[2].data.c.get_counts()

    p1g0 = p_read1(c0, N_QUBITS)          # P(read 1 | prepped 0)
    p1g1 = p_read1(c1, N_QUBITS)          # P(read 1 | prepped 1)
    f_readout = 1 - p1g0 - (1 - p1g1)     # = 1 - P(1|0) - P(0|1)
    f_ghz = ghz_fidelity(cg, N_QUBITS)
    gap = f_readout - f_ghz

    print("\nqubit | readout-only | GHZ (blended) | chain gap")
    for k in range(N_QUBITS):
        print(f"  {k}   |    {f_readout[k]*100:5.1f}%   |    {f_ghz[k]*100:5.1f}%    | {gap[k]*100:+5.1f}%")
    print(f"\naverage readout-only fidelity : {f_readout.mean()*100:.1f}%")
    print(f"average GHZ (blended) fidelity: {f_ghz.mean()*100:.1f}%")
    print(f"average chain-attributable gap: {gap.mean()*100:.1f}%   <- cost of the entangling chain, isolated")

if __name__ == "__main__":
    main()
