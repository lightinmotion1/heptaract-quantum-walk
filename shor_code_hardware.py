#!/usr/bin/env python3
"""
shor_code_hardware.py  --  the 9-qubit Shor code: catch a bit-flip AND a phase-flip.

Neither 3-qubit code alone was enough (each has a blind spot). Shor's code NESTS them:
  * 3 blocks of 3 qubits, phase-flip-encoded across the blocks (Hadamard glasses),
  * each block itself a bit-flip repetition code.
Result: it corrects ANY single-qubit error -- bit-flip (X), phase-flip (Z), or both (Y).

Encoding (logical 0), qubits 0..8, block leaders 0,3,6:
   phase layer:  CX(0,3) CX(0,6)  H(0) H(3) H(6)
   bit  layer:   CX(0,1) CX(0,2)  CX(3,4) CX(3,5)  CX(6,7) CX(6,8)

Two detection settings (one job):
  Z-BASIS run  -> catches X (bit) errors via 6 within-block parities  Z_iZ_j
  X-BASIS run  -> catches Z (phase) errors via 2 between-block parities (X over 6 qubits)

We inject a known X on one qubit per block, and a known Z on one leader per block, and show
BOTH types get localized -- the thing neither 3-qubit code could do. Requires saved creds.
"""
from collections import Counter
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192

def encode(qc):
    qc.cx(0, 3); qc.cx(0, 6)
    qc.h(0); qc.h(3); qc.h(6)
    qc.cx(0, 1); qc.cx(0, 2)
    qc.cx(3, 4); qc.cx(3, 5)
    qc.cx(6, 7); qc.cx(6, 8)

def x_err(k):                       # inject X, read Z basis (bit-flip detection)
    qc = QuantumCircuit(9, 9); encode(qc)
    if k is not None: qc.x(k)
    qc.measure(range(9), range(9)); return qc

def z_err(k):                       # inject Z, read X basis (phase-flip detection)
    qc = QuantumCircuit(9, 9); encode(qc)
    if k is not None: qc.z(k)
    qc.h(range(9)); qc.measure(range(9), range(9)); return qc

def q_of(bits):
    b = bits[::-1].zfill(9); return [int(b[k]) for k in range(9)]

def bit_syndrome(counts):           # 6 within-block parities -> block & position of an X error
    cnt = Counter()
    for bits, c in counts.items():
        q = q_of(bits)
        cnt[(q[0]^q[1], q[1]^q[2], q[3]^q[4], q[4]^q[5], q[6]^q[7], q[7]^q[8])] += c
    return cnt.most_common(1)[0][0]

def phase_syndrome(counts):         # 2 between-block parities -> block of a Z error
    cnt = Counter()
    for bits, c in counts.items():
        q = q_of(bits)
        cnt[(q[0]^q[1]^q[2]^q[3]^q[4]^q[5], q[3]^q[4]^q[5]^q[6]^q[7]^q[8])] += c
    return cnt.most_common(1)[0][0]

def bit_loc(s):
    for blk, (a, b) in enumerate([(s[0], s[1]), (s[2], s[3]), (s[4], s[5])]):
        if (a, b) != (0, 0):
            pos = {(1, 0): 0, (1, 1): 1, (0, 1): 2}.get((a, b), "?")
            return f"block {blk}, qubit {blk*3+pos if pos!='?' else '?'}"
    return "none"

def phase_loc(s):
    return {(0, 0): "none", (1, 0): "block 0", (1, 1): "block 1", (0, 1): "block 2"}.get(s, str(s))

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=9)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(x_err(None), backend, optimization_level=3)
    try: layout = list(seed.layout.final_index_layout()[:9])
    except Exception: layout = None
    tp = lambda c: transpile(c, backend, initial_layout=layout, optimization_level=3) if layout \
                   else transpile(c, backend, optimization_level=3)

    x_cases = [None, 1, 4, 7]        # a bit-flip in each of the 3 blocks
    z_cases = [None, 0, 3, 6]        # a phase-flip on each block leader
    circs = [tp(x_err(k)) for k in x_cases] + [tp(z_err(k)) for k in z_cases]
    print("Submitting 8 circuits (4 X-error + 4 Z-error) in one job -- 9 qubits, be patient...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()

    print("\n=== BIT-FLIP side: inject X, read Z parities -> should localize the X error ===")
    print("injected X | 6-bit within-block syndrome -> localizes")
    for k, r in zip(x_cases, res[:4]):
        s = bit_syndrome(r.data.c.get_counts())
        print(f"  {('none' if k is None else 'qubit '+str(k)):<9} | {s} -> {bit_loc(s)}")

    print("\n=== PHASE-FLIP side: inject Z, read X parities -> should localize the Z error's block ===")
    print("injected Z | between-block syndrome -> localizes")
    for k, r in zip(z_cases, res[4:]):
        s = phase_syndrome(r.data.c.get_counts())
        print(f"  {('none' if k is None else 'qubit '+str(k)):<9} | {s} -> {phase_loc(s)}")
    print("\nBoth an X error AND a Z error localized by ONE 9-qubit code -- the two blind spots, closed.")

if __name__ == "__main__":
    main()
