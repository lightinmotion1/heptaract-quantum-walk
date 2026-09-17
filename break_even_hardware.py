#!/usr/bin/env python3
"""
break_even_hardware.py  --  the field's central question: does the code BEAT a bare qubit?

Fair fight, on real hardware. Store logical 1 for a variable WAIT time, then check if it
survived -- two ways:
    BARE:  one qubit in |1>, wait, measure.            error = P(measure 0)
    CODE:  |111> (3-qubit repetition), wait, measure,  error = P(majority-vote != 1)
           majority vote at the end corrects a single bit that flipped during the wait.

Sweep the wait. Prediction:
  * short wait  -> BARE wins (code's encoding + 3x readout overhead dominates)
  * long  wait  -> errors accumulate; the code can fix ONE, the bare qubit can't ->
                   IF a crossover appears, that's the code earning its keep (local break-even).
  * no crossover -> we're BELOW THRESHOLD on this hardware: the honest NISQ reality, and
                    exactly why real fault tolerance needs better qubits + many QEC rounds.

Single-round protection only (one correction at the end), so don't expect a dramatic win --
the result itself is the lesson. Requires saved credentials.
"""
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192
DELAYS_US = [0, 25, 50, 100]     # wait times in microseconds

def bare(d):
    qc = QuantumCircuit(1, 1); qc.x(0); qc.barrier()
    if d > 0: qc.delay(d, 0, unit="us")
    qc.barrier(); qc.measure(0, 0); return qc

def code(d):
    qc = QuantumCircuit(3, 3); qc.x(0); qc.cx(0, 1); qc.cx(0, 2); qc.barrier()
    if d > 0:
        for q in range(3): qc.delay(d, q, unit="us")
    qc.barrier(); qc.measure([0, 1, 2], [0, 1, 2]); return qc

def bare_err(counts):
    tot = sum(counts.values()); wrong = sum(c for b, c in counts.items() if b[::-1][0] != '1')
    return wrong / tot

def code_err(counts):
    tot = sum(counts.values()); wrong = 0
    for b, c in counts.items():
        q = [int(x) for x in b[::-1].zfill(3)][:3]
        if (1 if sum(q) >= 2 else 0) != 1: wrong += c
    return wrong / tot

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(code(0), backend, optimization_level=3)
    try: L = list(seed.layout.final_index_layout()[:3])
    except Exception: L = None
    tpc = lambda c: transpile(c, backend, initial_layout=L, optimization_level=3) if L else transpile(c, backend, optimization_level=3)
    tpb = lambda c: transpile(c, backend, initial_layout=[L[0]], optimization_level=3) if L else transpile(c, backend, optimization_level=3)

    circs = [tpb(bare(d)) for d in DELAYS_US] + [tpc(code(d)) for d in DELAYS_US]
    print(f"Submitting {len(circs)} circuits (bare & code at {len(DELAYS_US)} wait times)...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()
    n = len(DELAYS_US)
    bares = [bare_err(res[i].data.c.get_counts()) for i in range(n)]
    codes = [code_err(res[n + i].data.c.get_counts()) for i in range(n)]

    print("\n wait (us) | BARE error | CODE error | winner")
    crossover = None
    for i, d in enumerate(DELAYS_US):
        win = "CODE" if codes[i] < bares[i] else "bare"
        if win == "CODE" and crossover is None: crossover = d
        print(f"   {d:>5}   |   {bares[i]*100:5.1f}%   |   {codes[i]*100:5.1f}%   | {win}")
    print()
    if crossover is not None:
        print(f"CROSSOVER at ~{crossover} us: beyond this wait, the code beats the bare qubit -- local break-even.")
    else:
        print("No crossover: the bare qubit won at every wait -> we're BELOW THRESHOLD on this chip.")
        print("That's the honest NISQ wall: single-round codes can't yet beat a good bare qubit here.")

if __name__ == "__main__":
    main()
