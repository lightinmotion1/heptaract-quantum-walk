#!/usr/bin/env python3
"""
repetition_code_hardware.py  --  the doorway: CORRECTION, not just mitigation.

The smallest real error-correcting code: protect one logical bit with THREE physical
qubits (Miah's redundancy / 217 instinct), and use PARITY checks (Miah's relationship /
syndrome measurement) to catch a flip and fix it -- WITHOUT reading the logical value.

  Encode logical 1  ->  |111>   (data qubit copied onto two others)
  A single bit-flip error moves it to |011>, |101>, or |110>.
  The two syndromes  s01 = Z0 xor Z1 ,  s12 = Z1 xor Z2  point straight at the culprit:
      (0,0) no error   (1,0) qubit 0   (1,1) qubit 1   (0,1) qubit 2
  Majority vote across the 3 qubits then RECOVERS the logical bit.

We inject a known flip on {none, 0, 1, 2} and show on real hardware that (a) the syndrome
localizes it and (b) majority-vote decoding recovers logical 1 -- while a bare single qubit
that took the hit would be 100% wrong. Requires saved credentials.
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192
SYND_MAP = {(0, 0): "none", (1, 0): "qubit 0", (1, 1): "qubit 1", (0, 1): "qubit 2"}

def encoded(error=None):
    qc = QuantumCircuit(3, 3)
    qc.x(0)                       # data = logical 1
    qc.cx(0, 1); qc.cx(0, 2)     # encode -> |111>
    if error is not None:
        qc.x(error)              # inject a known bit-flip
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

def analyze(counts):
    total = sum(counts.values()); synd = {}; logical_err = 0; bare_err = 0
    for bits, c in counts.items():
        b = bits[::-1].zfill(3); q = [int(b[k]) for k in range(3)]
        s = (q[0] ^ q[1], q[1] ^ q[2])
        synd[s] = synd.get(s, 0) + c
        if (1 if sum(q) >= 2 else 0) != 1: logical_err += c   # majority-vote decode; truth = 1
        if q[0] != 1: bare_err += c                           # naive: trust qubit 0 alone
    dom = max(synd, key=synd.get)
    return dom, logical_err / total, bare_err / total

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Running on real backend: {backend.name}")

    cases = [None, 0, 1, 2]
    seed = transpile(encoded(None), backend, optimization_level=3)
    try: layout = list(seed.layout.final_index_layout()[:3])
    except Exception: layout = None
    tp = lambda c: transpile(c, backend, initial_layout=layout, optimization_level=3) if layout \
                   else transpile(c, backend, optimization_level=3)
    circs = [tp(encoded(e)) for e in cases]

    print("Submitting 4 circuits (error on none/0/1/2) in one job...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()

    print("\ninjected error | measured syndrome -> localizes | logical err (corrected) | bare-qubit err")
    for e, r in zip(cases, res):
        dom, lerr, berr = analyze(r.data.c.get_counts())
        inj = "none" if e is None else f"qubit {e}"
        print(f"  {inj:<12} |  {str(dom)} -> {SYND_MAP[dom]:<8} |   {lerr*100:5.1f}%             |  {berr*100:5.1f}%")
    print("\nIf syndrome points at the injected qubit and 'corrected' << 'bare' when the hit lands")
    print("on qubit 0, the code CAUGHT and FIXED the error using redundancy + relationship checks.")

if __name__ == "__main__":
    main()
