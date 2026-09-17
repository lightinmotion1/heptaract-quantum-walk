#!/usr/bin/env python3
"""
steane_code_hardware.py  --  the 7-qubit code that protects a SUPERPOSITION.

Shor used 9 qubits. The Steane [[7,1,3]] code does the same job -- correct ANY single-qubit
error (bit-flip OR phase-flip) on one logical qubit -- in exactly SEVEN qubits, using the
Hamming(7,4) structure (the Fano-plane geometry underneath the heptaract).

Its magic: the 3-bit syndrome is the BINARY ADDRESS of the flipped qubit.
  Stabilizers (qubit i is in stabilizer j iff bit j of (i+1) is 1):
    S1 = .. on qubits 0,2,4,6     S2 = .. on 1,2,5,6     S3 = .. on 3,4,5,6
  X error read in Z basis -> syndrome = binary(k+1)  ->  names qubit k.
  Z error read in X basis -> same Hamming address.    Same structure, both error types.

We encode logical |0>_L, inject single X and Z errors, and show the Hamming syndrome
points at the exact qubit -- for BOTH error types, on 7 qubits. Requires saved creds.

(Detection/localization demo. Protecting a LIVE superposition through correction rounds and
beating break-even for a logical qubit is the summit beyond this -- threshold-limited today.)
"""
from collections import Counter
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192

def encode(qc):                      # standard Steane encoder for logical |0>
    qc.h(0); qc.h(1); qc.h(3)
    qc.cx(0, 2); qc.cx(0, 4); qc.cx(0, 6)
    qc.cx(1, 2); qc.cx(1, 5); qc.cx(1, 6)
    qc.cx(3, 4); qc.cx(3, 5); qc.cx(3, 6)

def x_err(k):                        # inject X, read Z basis -> Z-stabilizers catch bit-flips
    qc = QuantumCircuit(7, 7); encode(qc)
    if k is not None: qc.x(k)
    qc.measure(range(7), range(7)); return qc

def z_err(k):                        # inject Z, read X basis -> X-stabilizers catch phase-flips
    qc = QuantumCircuit(7, 7); encode(qc)
    if k is not None: qc.z(k)
    qc.h(range(7)); qc.measure(range(7), range(7)); return qc

def hamming(counts):                 # dominant 3-bit Hamming syndrome
    cnt = Counter()
    for bits, c in counts.items():
        q = [int(x) for x in bits[::-1].zfill(7)][:7]
        cnt[(q[0]^q[2]^q[4]^q[6], q[1]^q[2]^q[5]^q[6], q[3]^q[4]^q[5]^q[6])] += c
    return cnt.most_common(1)[0][0]

def loc(s):
    idx = s[0] + 2*s[1] + 4*s[2]
    return "none" if idx == 0 else f"qubit {idx-1}"

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=7)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(x_err(None), backend, optimization_level=3)
    try: L = list(seed.layout.final_index_layout()[:7])
    except Exception: L = None
    tp = lambda c: transpile(c, backend, initial_layout=L, optimization_level=3) if L else transpile(c, backend, optimization_level=3)

    x_cases = [None, 0, 3, 6]
    z_cases = [None, 0, 3, 6]
    circs = [tp(x_err(k)) for k in x_cases] + [tp(z_err(k)) for k in z_cases]
    print("Submitting 8 circuits (X errors + Z errors) on the 7-qubit Steane code...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()

    print("\n=== BIT-FLIP: inject X, read Z basis -> Hamming address of the error ===")
    print("injected X | syndrome (s1,s2,s3) -> localizes")
    for k, r in zip(x_cases, res[:4]):
        s = hamming(r.data.c.get_counts())
        print(f"  {('none' if k is None else 'qubit '+str(k)):<9} | {s} -> {loc(s)}")

    print("\n=== PHASE-FLIP: inject Z, read X basis -> Hamming address of the error ===")
    print("injected Z | syndrome (s1,s2,s3) -> localizes")
    for k, r in zip(z_cases, res[4:]):
        s = hamming(r.data.c.get_counts())
        print(f"  {('none' if k is None else 'qubit '+str(k)):<9} | {s} -> {loc(s)}")
    print("\nSeven qubits, one protected logical qubit, both error types addressed by Hamming syndrome.")

if __name__ == "__main__":
    main()
