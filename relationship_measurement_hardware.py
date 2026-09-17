#!/usr/bin/env python3
"""
relationship_measurement_hardware.py
------------------------------------
Miah's short-term goal, on real IBM hardware:

    Measure the RELATIONSHIP between qubits (a-b, b-c, ...) so the measurement
    does not change --- instead of measuring the individual VALUES, which would
    collapse the superposition.

This is the honest, lab-real version of the idea. Its proper names are
quantum non-demolition (QND) measurement and stabilizer / syndrome measurement
--- the core trick of quantum error correction.

WHAT IT DOES
  1. Prepares a 3-qubit GHZ state  (|000> + |111>)/sqrt(2)  on a real device.
  2. Measures all three in the Z basis over many shots.
  3. From the counts it computes:
        <Z_a>, <Z_b>, <Z_c>        the INDIVIDUAL values   -> should be ~0  (unpredictable)
        <Z_aZ_b>, <Z_bZ_c>, <Z_aZ_c>  the RELATIONSHIPS    -> should be ~+1 (certain)
     and checks the cross-check consistency:
        <Z_aZ_b> * <Z_bZ_c>  should predict  <Z_aZ_c>.
  The point: on real hardware the individual bits are coin-flips, but the
  RELATIONSHIPS are locked --- and the pairwise cross-checks agree. That is the
  receipt: you can know a-b, b-c, a-c without ever pinning a, b, or c.

SETUP  (current IBM Quantum Platform — verified against IBM docs 2026-08-11)
  1. pip install qiskit qiskit-ibm-runtime
  2. On quantum.cloud.ibm.com: your free "open-instance" is created. Now make an
     API key:  Home dashboard  ->  "API key"  ->  Create.  Copy the 44-char key.
  3. Copy your instance CRN:  Instances page  ->  hover the CRN  ->  click copy icon.
  4. Run this ONCE, locally, to save your credentials (keeps the secret OUT of this
     file and out of any chat):

       from qiskit_ibm_runtime import QiskitRuntimeService
       QiskitRuntimeService.save_account(
           token="<your-44-char-API-key>",
           instance="<your-open-instance-CRN>",
           set_as_default=True,
           overwrite=True,
       )

  After that, this script just calls QiskitRuntimeService() and loads them.
  Your API key is confidential — never paste it into shared code or chat.
"""

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = 4096

def analyze(counts):
    """counts: dict like {'000': n, '111': m, ...}; bit order c[0]c[1]c[2] = a b c."""
    total = sum(counts.values())
    # map bit '0'->+1, '1'->-1 for Z eigenvalues
    def z(bit): return 1 if bit == '0' else -1
    exp = {"Za":0,"Zb":0,"Zc":0,"ZaZb":0,"ZbZc":0,"ZaZc":0}
    for bits, n in counts.items():
        b = bits[::-1] if len(bits) == 3 else bits   # qiskit little-endian guard
        a_, bq, c_ = z(b[0]), z(b[1]), z(b[2])
        w = n/total
        exp["Za"]  += a_*w;      exp["Zb"]  += bq*w;      exp["Zc"]  += c_*w
        exp["ZaZb"]+= a_*bq*w;   exp["ZbZc"]+= bq*c_*w;   exp["ZaZc"]+= a_*c_*w
    return exp

def main():
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()   # loads your saved default account (see SETUP at top)
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Running on real backend: {backend.name}")

    qc = QuantumCircuit(3, 3)
    qc.h(0); qc.cx(0, 1); qc.cx(1, 2)     # GHZ: a-b-c all entangled
    qc.measure([0, 1, 2], [0, 1, 2])

    print("Transpiling circuit for the device...")
    tqc = transpile(qc, backend, optimization_level=3)
    sampler = Sampler(backend)
    job = sampler.run([tqc], shots=SHOTS)
    print(f"Submitted. Job ID: {job.job_id()}")
    print("Waiting for results -- can take a few minutes in the free queue. Leave it running...")
    result = job.result()
    counts = result[0].data.c.get_counts()

    print("\nraw counts:", counts)
    e = analyze(counts)
    print("\n--- INDIVIDUAL VALUES (want ~0: unpredictable) ---")
    print(f"  <Z_a>={e['Za']:+.3f}   <Z_b>={e['Zb']:+.3f}   <Z_c>={e['Zc']:+.3f}")
    print("--- RELATIONSHIPS (want ~+1: certain) ---")
    print(f"  <Z_aZ_b>={e['ZaZb']:+.3f}   <Z_bZ_c>={e['ZbZc']:+.3f}   <Z_aZ_c>={e['ZaZc']:+.3f}")
    print("--- CROSS-CHECK CONSISTENCY ---")
    pred = e['ZaZb']*e['ZbZc']
    print(f"  <Z_aZ_b>*<Z_bZ_c> = {pred:+.3f}   vs measured <Z_aZ_c> = {e['ZaZc']:+.3f}")
    print(f"  agreement gap = {abs(pred - e['ZaZc']):.3f}  (small = the relationships close consistently)")

if __name__ == "__main__":
    main()
