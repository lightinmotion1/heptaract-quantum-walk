#!/usr/bin/env python3
"""
chsh_bell_test_hardware.py  --  put a NUMBER on "spooky action at a distance."

A CHSH Bell test measures how strongly two entangled particles' outcomes agree across
four combinations of measurement angles, combined into one number S:

    S = E(A,B) - E(A,B') + E(A',B) + E(A',B')

  * ANY classical theory -- where the particles carry definite properties set in advance
    (local realism) -- is mathematically forbidden from exceeding  S = 2.
  * Quantum mechanics reaches  S = 2*sqrt(2) ~ 2.828.

So if your Bell pair scores S > 2 on real hardware, you've shown -- by direct measurement --
that the relationship between the two qubits is stronger than any classical explanation allows.
That is Einstein's "spooky action," quantified. Optimal angles baked in. Requires saved creds.
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192
A, Ap = 0.0, np.pi / 2          # Alice's two measurement angles
B, Bp = np.pi / 4, 3 * np.pi / 4  # Bob's two measurement angles

def meas(thA, thB):
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)         # Bell pair |Phi+>
    qc.ry(-thA, 0); qc.ry(-thB, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def corr(counts):               # E = <Z0 Z1> = P(agree) - P(disagree)
    tot = sum(counts.values()); e = 0
    for b, c in counts.items():
        q = b[::-1].zfill(2)
        e += (c if q[0] == q[1] else -c)
    return e / tot

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(meas(A, B), backend, optimization_level=3)
    try: L = list(seed.layout.final_index_layout()[:2])
    except Exception: L = None
    tp = lambda c: transpile(c, backend, initial_layout=L, optimization_level=3) if L else transpile(c, backend, optimization_level=3)

    settings = [("A,B", A, B), ("A,B'", A, Bp), ("A',B", Ap, B), ("A',B'", Ap, Bp)]
    circs = [tp(meas(a, b)) for _, a, b in settings]
    print("Submitting 4 CHSH circuits...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()

    Es = [corr(res[i].data.c.get_counts()) for i in range(4)]
    for (name, _, _), e in zip(settings, Es):
        print(f"  E({name}) = {e:+.3f}")
    S = Es[0] - Es[1] + Es[2] + Es[3]
    sigma = np.sqrt(4.0 / SHOTS)          # rough stat. uncertainty on S
    print(f"\n  S = {S:.3f}   (classical limit 2.000, quantum max 2.828)")
    if S > 2:
        print(f"  --> S beats the classical bound by {(S-2)/sigma:.0f} sigma.")
        print("  Local realism VIOLATED on real hardware: the bond is stronger than any classical theory.")
    else:
        print("  S <= 2 this run -- noise washed out the violation (deep/noisy qubits).")

if __name__ == "__main__":
    main()
