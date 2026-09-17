#!/usr/bin/env python3
"""
ramsey_scan_hardware.py  --  Miah's fine-timestamp idea = the Ramsey experiment.

Q14's coarse waits (25/50/75/100 us) ALIASED the coherent spin -- strobe-light effect.
Sample the wait FINELY instead, and two real things fall out of the fringes:
  * the FREQUENCY the qubit is humming at (its detuning) -- a live read of a quantum
    structure's frequency, the local seed of the 200 mph dream;
  * roughly how long its phase stays coherent (T2*-ish, from how fast the fringes fade).

    |+> , wait t (fine steps) , H , measure   ->   P(1) oscillates as sin^2 of the spin angle.
Signal <X> = 1 - 2*P(1) ~ cos(2*pi*f*t) * e^{-t/T2}.  We FFT it to pull out f. Requires creds.
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192
DT_US = 2
TIMES_US = list(range(0, 61, DT_US))      # 0, 2, ..., 60 us  (fine, evenly stepped for the FFT)

def ramsey(t):
    qc = QuantumCircuit(1, 1); qc.h(0); qc.barrier()
    if t > 0: qc.delay(t, 0, unit="us")
    qc.barrier(); qc.h(0); qc.measure(0, 0); return qc

def p1(counts):
    tot = sum(counts.values()); return sum(c for b, c in counts.items() if b[::-1][0] == '1') / tot

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=1)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(ramsey(0), backend, optimization_level=3)
    try: L = list(seed.layout.final_index_layout()[:1])
    except Exception: L = None
    tp = lambda c: transpile(c, backend, initial_layout=L, optimization_level=3) if L else transpile(c, backend, optimization_level=3)

    circs = [tp(ramsey(t)) for t in TIMES_US]
    print(f"Submitting {len(circs)} fine-timestamp circuits (0 -> {TIMES_US[-1]} us, step {DT_US} us)...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()

    P1 = np.array([p1(res[i].data.c.get_counts()) for i in range(len(TIMES_US))])
    sig = 1 - 2 * P1                                   # <X>(t), oscillating & decaying

    print("\n t(us) | P(1)  | <X>")
    for t, p, s in zip(TIMES_US, P1, sig):
        bar = "#" * int(round((s + 1) * 20))
        print(f"  {t:>4} | {p*100:4.0f}% | {s:+.2f} {bar}")

    # FFT to find the humming frequency
    s0 = sig - sig.mean()
    spec = np.abs(np.fft.rfft(s0))
    freqs = np.fft.rfftfreq(len(sig), d=DT_US * 1e-6)  # Hz
    k = int(np.argmax(spec[1:]) + 1)                   # skip DC
    f = freqs[k]
    print(f"\nDominant fringe frequency (the qubit's 'hum' / detuning): {f/1e3:.1f} kHz")
    if f > 0: print(f"  -> one full phase turn every {1e6/f:.1f} us")
    print("Fine timestamps beat aliasing -- and hand you the frequency the qubit is humming at.")

if __name__ == "__main__":
    main()
