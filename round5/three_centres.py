#!/usr/bin/env python3
"""
P-11 — Three centres: mine, yours, ours.

Free's reading: there cannot be two centres of one thing. Two centres means two objects — and the
moment there are two, a third centre appears that belongs to neither, the centre of both shared.

Two ships, each a centre with its own three, joined by one relationship gate:

    ship A:  C1 + rim A (3 qubits)      ship B:  C2 + rim B (3 qubits)      link: CZ(C1, C2)

Three readings of the same state:

    MINE    read ship A's own centre           (X basis on C1)
    YOURS   read ship B's own centre           (X basis on C2)
    OURS    read only the relationship         (the parity of C1 and C2, onto an ancilla,
                                                so neither ship's own centre is ever learned)

and after each, three bonds are measured by phase sweep:

    bond A      the three of ship A among themselves
    bond B      the three of ship B among themselves
    bond A+B    the six across both ships — the thing that only exists between them

  python3 three_centres.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "three_centres_pending.json"
COUNTS = RES / "three_centres_counts.json"
OUT = RES / "three_centres.json"

# qubit roles on a 9-qubit line: rimA(3) C1 ANC C2 rimB(3)
RIM_A = [0, 1, 2]
C1 = 3
ANC = 4
C2 = 5
RIM_B = [6, 7, 8]
NQ = 9
THETAS = 8
SHOTS = 2048
READINGS = ["mine", "yours", "ours"]


def prep(qc):
    """Each ship: a centre in superposition writing itself onto its own three. Then one link."""
    qc.h(C1)
    for r in RIM_A:
        qc.cx(C1, r)
    qc.h(C2)
    for r in RIM_B:
        qc.cx(C2, r)
    qc.cz(C1, C2)                      # the relationship, and the only thing joining them


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []
    for reading in READINGS:
        for t in range(THETAS):
            theta = 2 * math.pi * t / THETAS
            qc = QuantumCircuit(NQ, NQ)
            prep(qc)
            if reading == "mine":
                qc.h(C1)
                qc.measure(C1, C1)
            elif reading == "yours":
                qc.h(C2)
                qc.measure(C2, C2)
            else:
                # the shared centre: the parity of the two, written onto an ancilla and read there,
                # so neither ship's own centre is ever learned
                qc.h(C1); qc.h(C2)
                qc.cx(C1, ANC)
                qc.cx(C2, ANC)
                qc.measure(ANC, ANC)
                qc.h(C1); qc.h(C2)     # put the centres back where they were
            for r in RIM_A + RIM_B:
                qc.rz(theta, r)
                qc.h(r)
            qc.measure(RIM_A + RIM_B, RIM_A + RIM_B)
            circs.append(qc)
            meta.append({"reading": reading, "t": t})
    return circs, meta


def best_line(backend, length=NQ):
    t = backend.target
    two = next(x for x in ("cz", "ecr", "cx") if x in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else .05) for q, p in t["measure"].items()}
    adj = {}
    for (a, b), e in err2.items():
        if e < .05:
            adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    def ee(a, b): return min(err2.get((a, b), 1.), err2.get((b, a), 1.))
    beam = [([q], math.log(1 - ro.get(q, .05))) for q in adj]
    for _ in range(length - 1):
        nxt = []
        for path, sc in beam:
            for nb in adj.get(path[-1], ()):
                if nb in path: continue
                nxt.append((path + [nb], sc + math.log(1 - ee(path[-1], nb)) + math.log(1 - ro.get(nb, .05))))
        nxt.sort(key=lambda x: -x[1]); beam = nxt[:400]
    beam.sort(key=lambda x: -x[1])
    return beam[0][0], two


def submit():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    svc = QiskitRuntimeService()
    backend = svc.least_busy(operational=True, simulator=False, min_num_qubits=NQ + 4)
    chain, two = best_line(backend, NQ)
    circs, meta = build()
    tcs = [transpile(c, backend, initial_layout=chain, optimization_level=3, seed_transpiler=7) for c in circs]
    for m, tc in zip(meta, tcs):
        m["twoq"] = sum(1 for i in tc.data if i.operation.num_qubits == 2)
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"backend": backend.name, "chain": chain, "job_id": job.job_id(),
                                   "meta": meta, "shots": SHOTS,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, len(tcs), "circuits")
    print("two-qubit gates:", sorted(set(m["twoq"] for m in meta)))


def fetch():
    from qiskit_ibm_runtime import QiskitRuntimeService
    P = json.loads(PENDING.read_text())
    job = QiskitRuntimeService().job(P["job_id"])
    print("status", job.status())
    res = job.result()
    items = []
    for m, r in zip(P["meta"], res):
        d = r.data
        try:
            counts = d.c.get_counts()
        except AttributeError:
            counts = d[list(d.keys())[0]].get_counts()
        items.append({**m, "counts": counts})
    usage = None
    try:
        usage = job.metrics().get("usage", {})
    except Exception:
        pass
    COUNTS.write_text(json.dumps({"backend": P["backend"], "chain": P["chain"], "job_id": P["job_id"],
                                  "shots": P["shots"], "qpu_usage": usage,
                                  "timestamp_utc": P["submitted_utc"], "items": items}, indent=1))
    print("saved", COUNTS, usage)


def simulate():
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    sim = AerSimulator()
    circs, meta = build()
    tcs = transpile(circs, sim, optimization_level=1)
    res = sim.run(tcs, shots=8192, seed_simulator=7).result()
    items = [{**m, "twoq": 0, "counts": res.get_counts(i)} for i, m in enumerate(meta)]
    COUNTS.write_text(json.dumps({"backend": "aer", "chain": list(range(NQ)), "job_id": "sim",
                                  "shots": 8192, "qpu_usage": None, "timestamp_utc": "sim",
                                  "items": items}, indent=1))
    print("simulated", len(circs), "circuits")


# ------------------------------------------------------------------ analyze
def bits(key):
    b = key.replace(" ", "")
    return [int(b[len(b) - 1 - i]) for i in range(len(b))]


def parity(counts, idx, cond=None):
    """Parity of the given clbits, conditioned on the reading's own outcome.

    The centre's outcome flips the sign of the oscillation, so averaging over it cancels the
    signal: every bond here is read inside one branch of the reading, then averaged as magnitude.
    """
    tot, s = 0, 0.0
    for k, v in counts.items():
        b = bits(k)
        if cond is not None and b[cond[0]] != cond[1]:
            continue
        sign = 1
        for i in idx:
            sign *= (1 - 2 * b[i])
        s += sign * v; tot += v
    return (s / tot if tot else 0.0), tot


def bond(series):
    sp = np.abs(np.fft.rfft(np.array(series))) / len(series)
    return round(float(np.sum(sp[1:])), 4)


def analyze():
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    out = {"backend": D["backend"], "job_id": D["job_id"], "shots": D["shots"],
           "qpu_usage": D.get("qpu_usage"), "by_reading": {}}
    where = {"mine": C1, "yours": C2, "ours": ANC}
    for reading in READINGS:
        by_t = {it["t"]: it["counts"] for it in items if it["reading"] == reading}
        cbit = where[reading]
        per = {}
        for outcome in (0, 1):
            sA = [parity(by_t[t], RIM_A, (cbit, outcome))[0] for t in range(THETAS)]
            sB = [parity(by_t[t], RIM_B, (cbit, outcome))[0] for t in range(THETAS)]
            sAB = [parity(by_t[t], RIM_A + RIM_B, (cbit, outcome))[0] for t in range(THETAS)]
            per[outcome] = {"A": bond(sA), "B": bond(sB), "across": bond(sAB),
                            "series_across": [round(x, 4) for x in sAB]}
        out["by_reading"][reading] = {
            "bond_A": round((per[0]["A"] + per[1]["A"]) / 2, 4),
            "bond_B": round((per[0]["B"] + per[1]["B"]) / 2, 4),
            "bond_across": round((per[0]["across"] + per[1]["across"]) / 2, 4),
            "by_outcome": per,
            "two_qubit_gates": sorted(set(it.get("twoq", 0) for it in items if it["reading"] == reading)),
        }
    m, y, o = (out["by_reading"][r] for r in READINGS)
    out["verdict"] = {
        "shared_reading_keeps_the_bond_across": o["bond_across"] > 2 * max(m["bond_across"], y["bond_across"]),
        "private_readings_keep_their_own": min(m["bond_A"], y["bond_B"]) > 0.15,
        "ratio_ours_over_mine": round(o["bond_across"] / max(m["bond_across"], 1e-6), 2),
        "ratio_ours_over_yours": round(o["bond_across"] / max(y["bond_across"], 1e-6), 2),
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({"by_reading": {k: {kk: v[kk] for kk in ("bond_A", "bond_B", "bond_across", "two_qubit_gates")}
                                     for k, v in out["by_reading"].items()},
                      "verdict": out["verdict"]}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
