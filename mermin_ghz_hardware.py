#!/usr/bin/env python3
"""
mermin_ghz_hardware.py  --  the all-or-nothing refutation of classical reality.

CHSH beat local realism on AVERAGE. GHZ/Mermin beats it with CERTAINTY, in principle in a
single shot. Three entangled qubits, four joint measurements:

    M = <XXX> - <XYY> - <YXY> - <YYX>

  * Local realism (each qubit has predefined X,Y values):  |M| <= 2.
  * Quantum mechanics on the GHZ state:  M = 4.

Why it's sharper than CHSH: if the three "one-X-two-Y" terms each read -1 (they do), then any
theory of predefined properties FORCES <XXX> = -1. Quantum -- and the chip -- give +1. A flat
contradiction, not a statistical margin. Requires saved credentials.
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192

def ghz_meas(bases):
    qc = QuantumCircuit(3, 3)
    qc.h(0); qc.cx(0, 1); qc.cx(1, 2)     # GHZ
    for q, b in enumerate(bases):
        if b == 'X': qc.h(q)
        elif b == 'Y': qc.sdg(q); qc.h(q) # measure Y
    qc.measure(range(3), range(3))
    return qc

def parity_E(counts):
    tot = sum(counts.values()); e = 0
    for bits, c in counts.items():
        b = bits[::-1].zfill(3)
        e += ((-1) ** sum(int(x) for x in b[:3])) * c
    return e / tot

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(ghz_meas("XXX"), backend, optimization_level=3)
    try: L = list(seed.layout.final_index_layout()[:3])
    except Exception: L = None
    tp = lambda c: transpile(c, backend, initial_layout=L, optimization_level=3) if L else transpile(c, backend, optimization_level=3)

    bases = ["XXX", "XYY", "YXY", "YYX"]
    circs = [tp(ghz_meas(b)) for b in bases]
    print("Submitting 4 GHZ/Mermin circuits...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()

    E = {b: parity_E(res[i].data.c.get_counts()) for i, b in enumerate(bases)}
    for b in bases: print(f"  <{b}> = {E[b]:+.3f}")
    M = E["XXX"] - E["XYY"] - E["YXY"] - E["YYX"]
    sigma = np.sqrt(4.0 / SHOTS)
    print(f"\n  M = {M:.3f}   (classical limit 2, quantum max 4)")
    if M > 2:
        print(f"  --> M beats the classical bound by {(M-2)/sigma:.0f} sigma.")
        print("  Local realism REFUTED -- the all-or-nothing way -- on real hardware.")
    else:
        print("  M <= 2 this run -- noise washed out the contradiction.")

if __name__ == "__main__":
    main()
