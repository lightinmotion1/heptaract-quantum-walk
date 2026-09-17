#!/usr/bin/env python3
"""
phase_flip_code_hardware.py  --  catch the OTHER error: the phase-flip (Z).

The bit-flip code (Q9) is blind to phase errors. The phase-flip code is its mirror image:
the same 3-qubit repetition idea, but rotated into the X basis with Hadamards, so its
parity checks see Z errors instead of X errors.

  Phase-flip code:  logical 1 = |--->   (H applied to |111>)
  A Z error flips one qubit  |-> -> |+>.  Read parity in the X basis (H, then measure)
  and the syndrome localizes it exactly like before:
      (0,0) none   (1,0) qubit 0   (1,1) qubit 1   (0,1) qubit 2

To make the point vivid we run TWO views of the SAME injected phase error:
  * X-BASIS checks (phase-flip code)  -> should CATCH and localize it
  * Z-BASIS checks (bit-flip code)    -> should be BLIND (syndrome stays 'none')

That blindness is exactly why neither 3-qubit code is enough, and why Shor's 9-qubit code
(next) nests both. Requires saved credentials.
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192
SYND = {(0, 0): "none", (1, 0): "qubit 0", (1, 1): "qubit 1", (0, 1): "qubit 2"}

def phaseflip(error=None):                 # phase-flip code, X-basis readout -> catches Z errors
    qc = QuantumCircuit(3, 3)
    qc.x(0); qc.cx(0, 1); qc.cx(0, 2)      # |111>
    qc.h([0, 1, 2])                        # -> |--->  (logical 1 of the phase code)
    if error is not None: qc.z(error)      # inject a phase-flip
    qc.h([0, 1, 2])                        # rotate back -> measure in the X basis
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

def bitflip_blind(error=None):             # bit-flip code, Z-basis readout -> blind to Z errors
    qc = QuantumCircuit(3, 3)
    qc.x(0); qc.cx(0, 1); qc.cx(0, 2)      # |111>
    if error is not None: qc.z(error)      # same phase-flip error...
    qc.measure([0, 1, 2], [0, 1, 2])       # ...but Z measurement can't see it
    return qc

def analyze(counts):
    total = sum(counts.values()); synd = {}; logical_err = 0
    for bits, c in counts.items():
        b = bits[::-1].zfill(3); q = [int(b[k]) for k in range(3)]
        s = (q[0] ^ q[1], q[1] ^ q[2]); synd[s] = synd.get(s, 0) + c
        if (1 if sum(q) >= 2 else 0) != 1: logical_err += c
    return max(synd, key=synd.get), logical_err / total

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(phaseflip(None), backend, optimization_level=3)
    try: layout = list(seed.layout.final_index_layout()[:3])
    except Exception: layout = None
    tp = lambda c: transpile(c, backend, initial_layout=layout, optimization_level=3) if layout \
                   else transpile(c, backend, optimization_level=3)

    pf_cases = [None, 0, 1, 2]
    blind_cases = [None, 1]
    circs = [tp(phaseflip(e)) for e in pf_cases] + [tp(bitflip_blind(e)) for e in blind_cases]
    print("Submitting 6 circuits (4 phase-flip code + 2 blindness controls)...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()

    print("\n=== PHASE-FLIP CODE  (X-basis parity -> should CATCH the Z error) ===")
    print("injected phase error | syndrome -> localizes | logical err")
    for e, r in zip(pf_cases, res[:4]):
        dom, lerr = analyze(r.data.c.get_counts())
        inj = "none" if e is None else f"qubit {e}"
        print(f"  {inj:<18} |  {str(dom)} -> {SYND[dom]:<8} |  {lerr*100:5.1f}%")

    print("\n=== BIT-FLIP CODE on the SAME phase error  (Z-basis parity -> should be BLIND) ===")
    print("injected phase error | syndrome (stays 'none' = didn't see it)")
    for e, r in zip(blind_cases, res[4:]):
        dom, _ = analyze(r.data.c.get_counts())
        inj = "none" if e is None else f"qubit {e}"
        print(f"  {inj:<18} |  {str(dom)} -> {SYND[dom]}")
    print("\nPhase code localizes the Z error; bit code reads 'all clear' on the very same error.")
    print("Two blind spots, each covering the other -> nest them = Shor's 9-qubit code (next).")

if __name__ == "__main__":
    main()
