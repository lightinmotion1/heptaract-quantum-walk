#!/usr/bin/env python3
"""
HEPTARACT round 4, IBM hardware.  The return at seven.

Free's reading: seven is a rest — the close of a cycle — and the eighth is the return home
and the first step of the next round at once.  Over three bits, 𝔽₈ says the same in algebra:
the seven nonzero elements form one cycle, and the eighth step is α⁷ = α⁰, arrival and
departure together.

  P-6  The return.  A three-qubit register is prepared in a superposition, stepped k times by a
       map, then unprepared.  The chance of reading 000 is high only when the map has come home.
       Maps: the 𝔽₈ cycle (period 7), a linear map of period 4, a bit rotation of period 3, and
       the ordinary counter mod 8 (period 8).
       Prediction: the 𝔽₈ cycle stays away from home for k = 1..6 and returns at k = 7, and its
       return is cleaner than the counter's return at k = 8.

  P-7  The complete cycle.  Starting from one nonzero state, the 𝔽₈ cycle visits all seven
       nonzero states, each once, in seven steps; the rivals of period 4 and 3 visit four and
       three.  Seven is the longest complete return three bits allow.

  python3 round4_hardware.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "round4_hardware_pending.json"
COUNTS = RES / "round4_hardware_counts.json"
OUT = RES / "round4_hardware.json"

SHOTS = 4096
N = 3

# ---- the maps, as binary matrices over F2 acting on (b0, b1, b2) ------------
# 𝔽₈ multiplication by α with x³ = x + 1:  (b0,b1,b2) -> (b2, b0+b2, b1)
F8 = np.array([[0, 0, 1],
               [1, 0, 1],
               [0, 1, 0]], dtype=int)
# unitriangular, period 4:  b0 += b1 ; b1 += b2
ORD4 = np.array([[1, 1, 0],
                 [0, 1, 1],
                 [0, 0, 1]], dtype=int)
# bit rotation, period 3
ORD3 = np.array([[0, 0, 1],
                 [1, 0, 0],
                 [0, 1, 0]], dtype=int)
LINEAR = {"F8_period7": (F8, 7), "linear_period4": (ORD4, 4), "rotate_period3": (ORD3, 3)}
COUNTER_PERIOD = 8


def matpow(m, k):
    out = np.eye(N, dtype=int)
    for _ in range(k):
        out = (out @ m) % 2
    return out


def longest_orbit_start(mat, period):
    """A start vector whose orbit under `mat` has the full period."""
    best, best_len = None, 0
    for v in range(1, 2 ** N):
        vec = np.array([(v >> i) & 1 for i in range(N)], dtype=int)
        seen, cur = [], vec.copy()
        for _ in range(period):
            seen.append(tuple(cur))
            cur = (mat @ cur) % 2
        L = len(set(seen))
        if L > best_len:
            best, best_len = vec, L
    return best


def linear_gate(mat):
    from qiskit.circuit.library import LinearFunction
    return LinearFunction(mat.tolist()).definition


def counter_step(qc):
    """|j> -> |j+1 mod 8>, little endian (q0 = least significant)."""
    qc.ccx(0, 1, 2)
    qc.cx(0, 1)
    qc.x(0)


def prep(qc):
    """|000> -> (|000> + |011>)/sqrt(2):  the zero element and the element 3."""
    qc.h(0)
    qc.cx(0, 1)


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []

    # ---- P-6: prepare, step k times, unprepare, read 000
    for name, (mat, period) in LINEAR.items():
        for k in range(1, period + 1):
            qc = QuantumCircuit(N, N)
            prep(qc)
            qc.compose(linear_gate(matpow(mat, k)), inplace=True)
            qc.cx(0, 1)
            qc.h(0)
            qc.measure(range(N), range(N))
            circs.append(qc)
            meta.append({"kind": "return", "map": name, "k": k, "period": period})
    for k in range(1, COUNTER_PERIOD + 1):
        qc = QuantumCircuit(N, N)
        prep(qc)
        for _ in range(k):
            counter_step(qc)
        qc.cx(0, 1)
        qc.h(0)
        qc.measure(range(N), range(N))
        circs.append(qc)
        meta.append({"kind": "return", "map": "counter_period8", "k": k, "period": COUNTER_PERIOD})

    # ---- P-7: the orbit, from a start whose orbit is as long as the map allows
    for name, (mat, period) in LINEAR.items():
        start = longest_orbit_start(mat, period)
        for k in range(0, period):
            qc = QuantumCircuit(N, N)
            for b in range(N):
                if start[b]:
                    qc.x(b)
            if k:
                qc.compose(linear_gate(matpow(mat, k)), inplace=True)
            qc.measure(range(N), range(N))
            circs.append(qc)
            meta.append({"kind": "orbit", "map": name, "k": k, "period": period})
    return circs, meta


# ------------------------------------------------------------------ layout
def best_line(backend, length=N):
    t = backend.target
    two = next(n for n in ("cz", "ecr", "cx") if n in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else 0.05) for q, p in t["measure"].items()}
    adj = {}
    for (a, b), e in err2.items():
        if e < 0.05:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)

    def edge_err(a, b):
        return min(err2.get((a, b), 1.0), err2.get((b, a), 1.0))

    beam = [([q], math.log(1 - ro.get(q, 0.05))) for q in adj]
    for _ in range(length - 1):
        nxt = []
        for path, score in beam:
            for nb in adj.get(path[-1], ()):
                if nb in path:
                    continue
                nxt.append((path + [nb], score + math.log(1 - edge_err(path[-1], nb)) + math.log(1 - ro.get(nb, 0.05))))
        nxt.sort(key=lambda x: -x[1])
        beam = nxt[:400]
    beam.sort(key=lambda x: -x[1])
    return beam[0][0], two


# ------------------------------------------------------------------ run
def submit():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=N + 5)
    chain, two = best_line(backend, N)
    circs, meta = build()
    tcs = [transpile(c, backend, initial_layout=chain, optimization_level=1, seed_transpiler=7) for c in circs]
    twoq = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in tcs]
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"job_id": job.job_id(), "backend": backend.name, "chain": chain,
                                   "meta": meta, "twoq": twoq,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, "chain", chain, "circuits", len(tcs))


def fetch():
    from qiskit_ibm_runtime import QiskitRuntimeService
    P = json.loads(PENDING.read_text())
    job = QiskitRuntimeService().job(P["job_id"])
    print("status", job.status())
    res = job.result()
    items = []
    for m, r, nq in zip(P["meta"], res, P["twoq"]):
        d = r.data
        try:
            counts = d.c.get_counts()
        except AttributeError:
            counts = d[list(d.keys())[0]].get_counts()
        items.append({**m, "twoq": nq, "counts": counts})
    usage = None
    try:
        usage = job.metrics().get("usage", {})
    except Exception:
        pass
    COUNTS.write_text(json.dumps({"backend": P["backend"], "job_id": P["job_id"], "chain": P["chain"],
                                  "shots": SHOTS, "qpu_usage": usage, "timestamp_utc": P["submitted_utc"],
                                  "items": items}, indent=1))
    print("saved", COUNTS, "usage", usage)


def simulate():
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    sim = AerSimulator()
    circs, meta = build()
    tcs = transpile(circs, sim, optimization_level=1)
    res = sim.run(tcs, shots=8192, seed_simulator=7).result()
    items = [{**m, "twoq": 0, "counts": res.get_counts(i)} for i, m in enumerate(meta)]
    COUNTS.write_text(json.dumps({"backend": "aer", "job_id": "sim", "chain": [0, 1, 2], "shots": 8192,
                                  "qpu_usage": None, "timestamp_utc": "sim", "items": items}, indent=1))
    print("simulated", len(circs), "circuits")


# ------------------------------------------------------------------ analyze
def analyze():
    D = json.loads(COUNTS.read_text())
    ret, orb, twoq = {}, {}, {}
    for it in D["items"]:
        tot = sum(it["counts"].values())
        if it["kind"] == "return":
            ret.setdefault(it["map"], {})[it["k"]] = it["counts"].get("000", 0) / tot
            twoq.setdefault(it["map"], {})[it["k"]] = it["twoq"]
        else:
            top = max(it["counts"].items(), key=lambda kv: kv[1])
            orb.setdefault(it["map"], {})[it["k"]] = {"state": top[0], "p": round(top[1] / tot, 4)}

    se = lambda p, n: math.sqrt(max(p * (1 - p), 1e-9) / n)
    n = D["shots"]
    f8 = ret["F8_period7"]
    away = max(f8[k] for k in range(1, 7))
    home = f8[7]
    ctr = ret["counter_period8"][8]
    z = (home - ctr) / math.hypot(se(home, n), se(ctr, n))
    p6 = {"by_map": {m: {str(k): round(v, 4) for k, v in sorted(d.items())} for m, d in ret.items()},
          "two_qubit_gates": {m: {str(k): v for k, v in sorted(d.items())} for m, d in twoq.items()},
          "F8_home_at_7": round(home, 4), "F8_worst_away_1_to_6": round(away, 4),
          "counter_home_at_8": round(ctr, 4), "z_F8_over_counter": round(z, 2),
          "verdict": "PASS" if (home >= 0.7 and away <= 0.45 and z >= 2) else "FAIL",
          "rule": "PASS if the F8 cycle reads 000 at least 0.70 at k=7, stays at or under 0.45 for k=1..6, "
                  "and beats the counter's own return by at least 2 SE"}

    cov = {}
    for m, d in orb.items():
        states = [d[k]["state"] for k in sorted(d)]
        cov[m] = {"visited": states, "distinct": len(set(states)),
                  "min_confidence": round(min(d[k]["p"] for k in d), 4)}
    p7 = {"orbits": cov,
          "verdict": "PASS" if (cov["F8_period7"]["distinct"] == 7 and cov["F8_period7"]["min_confidence"] >= 0.6
                                and cov["linear_period4"]["distinct"] == 4
                                and cov["rotate_period3"]["distinct"] == 3) else "FAIL",
          "rule": "PASS if the F8 orbit reads seven distinct states, each identified with at least 0.60, "
                  "and the rivals read four and three"}

    out = {"backend": D["backend"], "job_id": D["job_id"], "chain": D["chain"], "shots": D["shots"],
           "qpu_usage": D.get("qpu_usage"), "timestamp_utc": D["timestamp_utc"], "P-6": p6, "P-7": p7}
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({"P-6": {k: p6[k] for k in ("by_map", "F8_home_at_7", "F8_worst_away_1_to_6",
                                                 "counter_home_at_8", "z_F8_over_counter", "verdict")},
                      "P-7": {"orbits": cov, "verdict": p7["verdict"]}}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
