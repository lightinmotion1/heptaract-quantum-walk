#!/usr/bin/env python3
"""
phase_break_even_hardware.py  --  protect a LIVE SUPERPOSITION (its phase) vs a bare qubit.

Q12 protected a classical bit (|1>) against bit-flips and WON. This is the harder, quantum
version: protect the PHASE of a superposition |+> = (|0>+|1>)/sqrt(2) against DEPHASING (T2) --
the fragile, genuinely-quantum information. It's the phase-flip dual of Q12.

    BARE:  |+> , wait, measure in X basis (H then measure).  error = phase got scrambled (reads 1)
    CODE:  |+++> (3-qubit phase repetition), wait, measure all in X, majority vote.
           Majority vote corrects a single dephasing event; truth = 0.

Physics to expect:
  * dephasing randomizes phase, so both bare and code saturate toward 50% at long waits (max entropy).
  * in the MIDDLE regime the code should win -- majority vote suppresses independent dephasing,
    and there are NO entangling gates here (just H), so no correlated-gate error to fight.
If the code beats bare anywhere, that's redundancy protecting genuinely QUANTUM information.
(Single error type / single round. Full arbitrary-superposition, all-error, multi-round
protection = the Steane/live summit still ahead.) Requires saved credentials.
"""
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192
DELAYS_US = [0, 25, 50, 100]

def bare(d):
    qc = QuantumCircuit(1, 1); qc.h(0); qc.barrier()
    if d > 0: qc.delay(d, 0, unit="us")
    qc.barrier(); qc.h(0); qc.measure(0, 0); return qc

def code(d):
    qc = QuantumCircuit(3, 3); qc.h(0); qc.h(1); qc.h(2); qc.barrier()
    if d > 0:
        for q in range(3): qc.delay(d, q, unit="us")
    qc.barrier(); qc.h(0); qc.h(1); qc.h(2); qc.measure([0, 1, 2], [0, 1, 2]); return qc

def bare_err(counts):
    tot = sum(counts.values()); wrong = sum(c for b, c in counts.items() if b[::-1][0] != '0')
    return wrong / tot

def code_err(counts):
    tot = sum(counts.values()); wrong = 0
    for b, c in counts.items():
        q = [int(x) for x in b[::-1].zfill(3)][:3]
        if (1 if sum(q) >= 2 else 0) != 0: wrong += c   # truth for |+++> in X basis is 0
    return wrong / tot

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(code(0), backend, optimization_level=3)
    try: L = list(seed.layout.final_index_layout()[:3])
    except Exception: L = None
    tpc = lambda c: transpile(c, backend, initial_layout=L, optimization_level=3) if L else transpile(c, backend, optimization_level=3)
    tpb = lambda c: transpile(c, backend, initial_layout=[L[0]], optimization_level=3) if L else transpile(c, backend, optimization_level=3)

    circs = [tpb(bare(d)) for d in DELAYS_US] + [tpc(code(d)) for d in DELAYS_US]
    print(f"Submitting {len(circs)} circuits (bare |+> & phase-code at {len(DELAYS_US)} wait times)...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()
    n = len(DELAYS_US)
    bares = [bare_err(res[i].data.c.get_counts()) for i in range(n)]
    codes = [code_err(res[n + i].data.c.get_counts()) for i in range(n)]

    print("\n wait (us) | BARE phase-err | CODE phase-err | winner")
    crossover = None
    for i, d in enumerate(DELAYS_US):
        win = "CODE" if codes[i] < bares[i] else "bare"
        if win == "CODE" and crossover is None: crossover = d
        print(f"   {d:>5}   |    {bares[i]*100:5.1f}%     |    {codes[i]*100:5.1f}%     | {win}")
    print()
    if crossover is not None:
        print(f"CODE beats bare from ~{crossover} us -> redundancy protected the SUPERPOSITION'S PHASE.")
        print("Genuinely quantum information, shielded on real hardware.")
    else:
        print("Bare won everywhere -> phase protection is below threshold here; the encoding/readout")
        print("overhead outweighs the correction. The honest quantum-memory wall.")

if __name__ == "__main__":
    main()
