#!/usr/bin/env python3
"""
entanglement_swap_hardware.py  --  WRITE a relationship between two strangers.

Entanglement swapping: two Bell pairs (q0-q1) and (q2-q3). q0 and q3 have NEVER interacted.
We do a Bell measurement on the two middle partners (q1,q2) -- and that act forces q0 and q3
into an entangled relationship. A bond written between particles that never touched.

To PROVE the new bond is genuinely quantum (not a classical correlation), we measure q0 & q3
two ways and apply an entanglement witness, conditioned on the (q1,q2) Bell outcome:
    W = |<Z0 Z3>| + |<X0 X3>|
A separable (classical) state obeys W <= 1.  A Bell state reaches W = 2.
Two measurement settings (Z and X on q0,q3), one job. Requires saved credentials.
"""
from collections import defaultdict
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192

def swap(basis):
    qc = QuantumCircuit(4, 4)
    qc.h(0); qc.cx(0, 1)          # Bell pair q0-q1
    qc.h(2); qc.cx(2, 3)          # Bell pair q2-q3
    qc.barrier()
    qc.cx(1, 2); qc.h(1)          # Bell-measurement rotation on the middle pair
    if basis == 'X':
        qc.h(0); qc.h(3)          # read q0,q3 in the X basis
    qc.measure(range(4), range(4))
    return qc

def cond_corr(counts):
    acc = defaultdict(float); cnt = defaultdict(int)
    for bits, c in counts.items():
        b = bits[::-1].zfill(4)                       # q0,q1,q2,q3
        q0 = 1 - 2*int(b[0]); q3 = 1 - 2*int(b[3])
        key = (int(b[1]), int(b[2]))                  # (q1,q2) Bell outcome
        acc[key] += q0*q3*c; cnt[key] += c
    return {k: acc[k]/cnt[k] for k in cnt}, cnt

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=4)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(swap('Z'), backend, optimization_level=3)
    try: L = list(seed.layout.final_index_layout()[:4])
    except Exception: L = None
    tp = lambda c: transpile(c, backend, initial_layout=L, optimization_level=3) if L else transpile(c, backend, optimization_level=3)

    print("Submitting 2 circuits (Z and X readout of the swapped bond)...")
    job = Sampler(backend).run([tp(swap('Z')), tp(swap('X'))], shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()
    zz, nz = cond_corr(res[0].data.c.get_counts())
    xx, nx = cond_corr(res[1].data.c.get_counts())

    print("\n (q1,q2) outcome | <Z0Z3> | <X0X3> | witness |ZZ|+|XX| | entangled?")
    for k in sorted(zz):
        if k not in xx: continue
        W = abs(zz[k]) + abs(xx[k])
        print(f"     {k}        | {zz[k]:+.2f}  | {xx[k]:+.2f}  |    {W:.2f}      | {'YES (>1)' if W > 1 else 'no'}")
    print("\nEvery outcome with W>1 = q0 and q3 hold a genuinely quantum bond -- written between")
    print("two particles that never interacted. Classical relationships can't exceed 1.")

if __name__ == "__main__":
    main()
