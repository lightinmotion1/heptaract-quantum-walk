#!/usr/bin/env python3
"""
ghz_shape_showdown_hardware.py  --  can we BEAT the 2.6% chain gap by reshaping the entanglement?

We just learned the noise lives in the entangling chain, and it grows with DEPTH.
So: build the same 7-qubit GHZ two ways and race them on real hardware.

  LINEAR:  H(0), CX(0,1), CX(1,2), ... CX(5,6)      -> 6 CNOTs, logical depth ~6
  TREE:    binary-doubling cascade                   -> 6 CNOTs, logical depth ~3

Same gate count, half the logical depth. BUT the tree needs long-range CNOTs, and on
real (heavy-hex) hardware the transpiler inserts SWAPs to route them -- which adds gates.
So this is an honest race: does the tree's shallower depth survive the connectivity tax?
We report each construction's transpiled 2-qubit-gate count, depth, and measured chain gap.

Plus CAL0/CAL1 for the shared readout baseline. All circuits in one job. Needs saved creds.
"""
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

N_QUBITS = 7
SHOTS = 8192

def ghz_linear(n):
    qc = QuantumCircuit(n, n); qc.h(0)
    for k in range(n - 1): qc.cx(k, k + 1)
    qc.measure(range(n), range(n)); return qc

def ghz_tree(n):
    qc = QuantumCircuit(n, n); qc.h(0)
    step = 1
    while step < n:
        for q in range(step):
            if q + step < n: qc.cx(q, q + step)
        step *= 2
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

def avg_corr_and_fid(counts, n):
    total = sum(counts.values()); pairs = list(combinations(range(n), 2)); Zij = {p: 0.0 for p in pairs}
    zval = lambda bit: 1 if bit == '0' else -1
    for bits, c in counts.items():
        b = bits[::-1].zfill(n); w = c / total; v = [zval(b[k]) for k in range(n)]
        for (i, j) in pairs: Zij[(i, j)] += v[i] * v[j] * w
    A = np.zeros((len(pairs), n)); rhs = np.zeros(len(pairs))
    for r, (i, j) in enumerate(pairs):
        A[r, i] = 1; A[r, j] = 1; rhs[r] = np.log(max(Zij[(i, j)], 1e-6))
    f = np.exp(np.linalg.lstsq(A, rhs, rcond=None)[0])
    return np.mean(list(Zij.values())), f.mean()

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=N_QUBITS)
    print(f"Running on real backend: {backend.name}\n")

    # Pin ALL circuits to the SAME physical qubits so cal + linear + tree are apples-to-apples.
    seed = transpile(ghz_linear(N_QUBITS), backend, optimization_level=3)
    try:
        line = list(seed.layout.final_index_layout()[:N_QUBITS])   # the physical qubits the chain chose
    except Exception:
        line = None
    def tp(circ, opt):
        return transpile(circ, backend, initial_layout=line, optimization_level=opt) if line \
               else transpile(circ, backend, optimization_level=opt)
    tlin  = tp(ghz_linear(N_QUBITS), 3)                 # native on the line
    ttree = tp(ghz_tree(N_QUBITS), 3)                   # routed onto the SAME line (SWAP tax shows here)
    tc0, tc1 = tp(prep(N_QUBITS), 1), tp(prep(N_QUBITS, True), 1)   # readout on the SAME qubits
    print(f"LINEAR transpiled: {tlin.num_nonlocal_gates()} two-qubit gates, depth {tlin.depth()}")
    print(f"TREE   transpiled: {ttree.num_nonlocal_gates()} two-qubit gates, depth {ttree.depth()}")

    print("\nSubmitting 4 circuits (CAL0, CAL1, LINEAR, TREE) in one job...")
    job = Sampler(backend).run([tc0, tc1, tlin, ttree], shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()}\nWaiting for results...")
    r = job.result()
    c0, c1, clin, ctree = (r[i].data.c.get_counts() for i in range(4))

    readout = (1 - p_read1(c0, N_QUBITS) - (1 - p_read1(c1, N_QUBITS))).mean()
    corr_lin, fid_lin = avg_corr_and_fid(clin, N_QUBITS)
    corr_tree, fid_tree = avg_corr_and_fid(ctree, N_QUBITS)

    print(f"\nshared readout baseline: {readout*100:.1f}%\n")
    print(f"{'construction':<8} | {'2q gates':>8} | {'depth':>5} | {'avg <ZZ>':>8} | {'chain gap':>9}")
    print(f"{'LINEAR':<8} | {tlin.num_nonlocal_gates():>8} | {tlin.depth():>5} | {corr_lin:>8.3f} | {(readout-fid_lin)*100:>+8.1f}%")
    print(f"{'TREE':<8} | {ttree.num_nonlocal_gates():>8} | {ttree.depth():>5} | {corr_tree:>8.3f} | {(readout-fid_tree)*100:>+8.1f}%")
    winner = "TREE" if fid_tree > fid_lin else "LINEAR"
    print(f"\nWinner (smaller chain gap / higher correlation): {winner}")
    print("If TREE wins -> shallower depth beat the routing tax. If LINEAR wins -> connectivity ruled.")

if __name__ == "__main__":
    main()
