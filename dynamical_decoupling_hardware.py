#!/usr/bin/env python3
"""
dynamical_decoupling_hardware.py  --  cancel the coherent spin with a spin echo.

Q14 revealed the idle phase error is COHERENT (the |+> Bloch vector spinning around Z),
not random -- the giveaway was bare error swinging past 50% (81%) and back (29%).
Correction can't fix a systematic rotation. Dynamical decoupling CANCELS it:

    IDLE:  |+> , wait d ,           H, measure     (coherent spin accumulates -> oscillates)
    ECHO:  |+> , wait d/2, X, wait d/2, H, measure (X flips the qubit mid-wait, so the phase
                                                    gained in the 2nd half undoes the 1st half)

Because |+> is an eigenstate of X, the pulse leaves the state itself alone but reverses the
sign of the accumulating phase -> the coherent rotation refocuses to ~0. What's left is only
the slow, genuine decoherence. Expect: ECHO error stays low and smooth while IDLE oscillates.
Requires saved credentials.
"""
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 8192
DELAYS_US = [0, 25, 50, 100]

def idle(d):
    qc = QuantumCircuit(1, 1); qc.h(0); qc.barrier()
    if d > 0: qc.delay(d, 0, unit="us")
    qc.barrier(); qc.h(0); qc.measure(0, 0); return qc

def echo(d):
    qc = QuantumCircuit(1, 1); qc.h(0); qc.barrier()
    if d > 0: qc.delay(d // 2, 0, unit="us")
    qc.x(0)
    if d > 0: qc.delay(d - d // 2, 0, unit="us")
    qc.barrier(); qc.h(0); qc.measure(0, 0); return qc

def err(counts):   # truth for |+> in X basis (with |+> preserved by X) is 0
    tot = sum(counts.values()); wrong = sum(c for b, c in counts.items() if b[::-1][0] != '0')
    return wrong / tot

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=1)
    print(f"Running on real backend: {backend.name}")

    seed = transpile(idle(0), backend, optimization_level=3)
    try: L = list(seed.layout.final_index_layout()[:1])
    except Exception: L = None
    tp = lambda c: transpile(c, backend, initial_layout=L, optimization_level=3) if L else transpile(c, backend, optimization_level=3)

    circs = [tp(idle(d)) for d in DELAYS_US] + [tp(echo(d)) for d in DELAYS_US]
    print(f"Submitting {len(circs)} circuits (idle & spin-echo at {len(DELAYS_US)} waits)...")
    job = Sampler(backend).run(circs, shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()} -- waiting...")
    res = job.result()
    n = len(DELAYS_US)
    idles = [err(res[i].data.c.get_counts()) for i in range(n)]
    echos = [err(res[n + i].data.c.get_counts()) for i in range(n)]

    print("\n wait (us) | IDLE phase-err | ECHO phase-err | echo helps?")
    for i, d in enumerate(DELAYS_US):
        print(f"   {d:>5}   |    {idles[i]*100:5.1f}%     |    {echos[i]*100:5.1f}%     | {'YES' if echos[i] < idles[i] else 'no'}")
    swing_idle = max(idles) - min(idles); swing_echo = max(echos) - min(echos)
    print(f"\nIDLE swings over {swing_idle*100:.0f} points (the coherent spin); ECHO swings {swing_echo*100:.0f}.")
    print("A flat, low ECHO row = the spin was refocused -> the RIGHT tool for a coherent error.")

if __name__ == "__main__":
    main()
