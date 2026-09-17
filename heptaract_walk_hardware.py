#!/usr/bin/env python3
"""
heptaract_walk_hardware.py  --  where it all began, finally on real silicon.

The original heptaract quantum walk: Hamiltonian H = sum_i X_i on 7 qubits. Evolving to
t = pi/2 factors into a product of single-qubit rotations Rx(pi) -- each qubit walks from
|0> to |1> -- giving perfect state transfer  |0000000> -> |1111111>.

Depth 2, 7 gates, NO entanglement (which is why it's really a readout-error benchmark on
hardware). Ideal P(|1111111>) = 1.000; real-device P ~ (1 - readout)^7 ~ 0.87-0.93.

This is the experiment Catalina nudged you to run on real hardware -- run only in simulation
back then, for want of a token. You have the token now. Full circle. Requires saved creds.
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192

def heptaract_walk():
    qc = QuantumCircuit(7, 7)
    for q in range(7):
        qc.rx(np.pi, q)                 # t = pi/2 : |0> -> |1> on every axis
    qc.measure(range(7), range(7))
    return qc

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=7)
    print(f"Running on real backend: {backend.name}")

    tqc = transpile(heptaract_walk(), backend, optimization_level=3)
    print("Submitting the heptaract walk (7-qubit state transfer)...")
    job = Sampler(backend).run([tqc], shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    counts = job.result()[0].data.c.get_counts()

    total = sum(counts.values())
    target = counts.get('1' * 7, 0)
    P = target / total
    # how far off were the misses?
    from collections import Counter
    dist = Counter()
    for b, c in counts.items():
        flips = 7 - b.count('1')       # Hamming distance from 1111111
        dist[flips] += c

    print(f"\nP(|1111111>) transferred = {P*100:.1f}%   (ideal 100%, readout-limited ~87-93%)")
    print("miss profile (how many bits off from the target):")
    for k in sorted(dist):
        print(f"  {k}-bit off: {dist[k]/total*100:5.1f}%")
    print("\nThe walk that started it all, on real silicon. Full circle. Post these to Catalina.")

if __name__ == "__main__":
    main()
