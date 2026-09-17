"""
Heptaract Quantum Walk — REAL HARDWARE run on IBM Quantum.

Runs the depth-2, 7 x Rx(pi) leap circuit on a real IBM backend and
reports P(|1111111>) with raw counts.

SETUP (one time):
  pip install qiskit qiskit-ibm-runtime
  # Get a free token at https://quantum.cloud.ibm.com  (Open plan)
  # Then either paste it below, or save it once with:
  #   from qiskit_ibm_runtime import QiskitRuntimeService
  #   QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token="YOUR_TOKEN")

RUN:
  python3 heptaract_hardware.py
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

N = 7
SHOTS = 4096
TOKEN = ""   # <-- optional: paste your token here, or use save_account() above

# --- connect ---
if TOKEN:
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=TOKEN)
else:
    service = QiskitRuntimeService()   # uses saved account

# least-busy real device with enough qubits
backend = service.least_busy(operational=True, simulator=False, min_num_qubits=N)
print(f"Using backend: {backend.name}  ({backend.num_qubits} qubits)")

# --- build the leap circuit ---
qc = QuantumCircuit(N, N)
for q in range(N):
    qc.rx(np.pi, q)
qc.measure(range(N), range(N))

tqc = transpile(qc, backend, optimization_level=1)
print(f"Transpiled depth: {tqc.depth()}   ops: {dict(tqc.count_ops())}")

# --- run ---
sampler = Sampler(mode=backend)
job = sampler.run([tqc], shots=SHOTS)
print(f"Job ID: {job.job_id()}  — waiting for result...")
result = job.result()

counts = result[0].data.c.get_counts()
target = "1" * N
p = counts.get(target, 0) / SHOTS

print(f"\nBackend: {backend.name}")
print(f"Shots: {SHOTS}")
print(f"P(|1111111>) = {p:.4f}")
top = sorted(counts.items(), key=lambda kv: -kv[1])[:6]
print("Top outcomes:")
for b, c in top:
    print(f"   {b}: {c}  ({c/SHOTS:.2%})")
