#!/usr/bin/env python3
"""
teleportation_hardware.py  --  WRITE a quantum state across an entangled relationship.

The purest form of "writing the relationship aspect of quantum particles": quantum
teleportation moves an arbitrary state from qubit q0 onto qubit q2 -- which q0 never
touches -- using only their shared ENTANGLEMENT as the channel. The relationship is
the wire; the state is what we write down it.

  q0: the message  (Ry(theta)|0> -- any state on the Bloch meridian)
  q1,q2: a shared Bell pair (the relationship)
  Bell-rotate q0,q1, apply the deferred corrections -> q2 now carries the message.
  Verify by un-preparing on q2 (Ry(-theta)) and measuring: |0> means it arrived.

Fidelity = P(q2 reads 0). Ideal 1.000; on hardware, less, by the depth (~4 CNOTs).
Requires saved credentials.
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192
THETAS = [i * np.pi / 4 for i in range(8)]   # 8 message states around the meridian

def teleport(theta):
    qc = QuantumCircuit(3, 1)
    qc.ry(theta, 0)                 # message on q0
    qc.h(1); qc.cx(1, 2)            # Bell pair q1-q2 (the relationship)
    qc.cx(0, 1); qc.h(0)            # Bell-basis rotation on q0,q1
    qc.cx(1, 2); qc.cz(0, 2)        # deferred corrections -> q2 receives the message
    qc.ry(-theta, 2)               # un-prepare on q2 to verify
    qc.measure(2, 0)               # 0 => the message wrote across
    return qc

def fidelity(counts):
    tot = sum(counts.values()); return sum(c for b, c in counts.items() if b[::-1][0] == '0') / tot

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(teleport(0.0), backend, optimization_level=3)
    try: L = list(seed.layout.final_index_layout()[:3])
    except Exception: L = None
    tp = lambda c: transpile(c, backend, initial_layout=L, optimization_level=3) if L else transpile(c, backend, optimization_level=3)

    circs = [tp(teleport(t)) for t in THETAS]
    print(f"Submitting {len(circs)} teleportations (8 message states)...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()

    print("\n message state (theta) | teleport fidelity (want ~1.0)")
    fids = []
    for t, r in zip(THETAS, res):
        f = fidelity(r.data.c.get_counts()); fids.append(f)
        bar = "#" * int(round(f * 30))
        print(f"   {t:5.2f} rad            |  {f*100:5.1f}%  {bar}")
    print(f"\naverage teleportation fidelity: {np.mean(fids)*100:.1f}%")
    print("Every state that lands near |0> = a quantum state WRITTEN across the entangled link.")
    print("(A bare, unentangled channel could not exceed ~66.7% -- the classical limit.)")

if __name__ == "__main__":
    main()
