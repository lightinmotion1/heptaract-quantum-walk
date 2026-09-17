#!/usr/bin/env python3
"""
HEPTARACT round 2, IBM hardware (pre-registered 2026-09-17).

  T-1.5  GHZ size scan n = 5..9 on the first n qubits of ONE fixed linear chain
  P-2    GHZ-7: every pair's <XX> and <YY> (shared by many, not by pairs)
  P-1    the fire read two ways: seven-qubit star-graph state, center read in X or in Z,
         rim six-body coherence conditioned on the center's outcome

Star-graph note: the star graph state (|0>|+..+> + |1>|-..->)/sqrt2 equals a GHZ-7 with a
Hadamard on each rim qubit. Reading the rim in its X basis undoes that Hadamard, so the
circuit prepares GHZ-7 grown outward from the center and reads the rim with the ordinary
parity oscillation. Same physics, shallower circuit.

  python3 round2_hardware.py submit   -> sends one job (uses QPU time), saves results/round2_hardware_pending.json
  python3 round2_hardware.py fetch    -> when the job is done, saves results/round2_hardware_counts.json
  python3 round2_hardware.py analyze  -> results/round2_hardware.json          (no QPU)
Requires a saved IBM Quantum account (save_creds.py).
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results"; RES.mkdir(exist_ok=True)
COUNTS = RES / "round2_hardware_counts.json"
SHOTS = 4096
SIZES = [5, 6, 7, 8, 9]


# ----------------------------------------------------------------- circuits
def ghz_chain(qc, qs):
    qc.h(qs[0])
    for a, b in zip(qs, qs[1:]):
        qc.cx(a, b)

def ghz_center_out(qc, qs, c):
    """GHZ grown outward from index c along the chain qs."""
    qc.h(qs[c])
    for i in range(c, 0, -1):
        qc.cx(qs[i], qs[i - 1])
    for i in range(c, len(qs) - 1):
        qc.cx(qs[i], qs[i + 1])

def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []
    for n in SIZES:
        q = list(range(n))
        qc = QuantumCircuit(n, n); ghz_chain(qc, q); qc.measure(q, q)
        circs.append(qc); meta.append({"kind": "pop", "n": n})
        for j in range(4):
            phi = 2 * math.pi * j / (4 * n)
            qc = QuantumCircuit(n, n); ghz_chain(qc, q)
            for k in q:
                qc.rz(phi, k); qc.h(k)
            qc.measure(q, q)
            circs.append(qc); meta.append({"kind": "par", "n": n, "j": j})
    # P-2: GHZ-7 in the X basis and in the Y basis
    for basis in ("X", "Y"):
        qc = QuantumCircuit(7, 7); ghz_chain(qc, list(range(7)))
        for k in range(7):
            if basis == "Y":
                qc.sdg(k)
            qc.h(k)
        qc.measure(range(7), range(7))
        circs.append(qc); meta.append({"kind": "pair", "basis": basis})
    # P-1: center = chain index 3; rim = the other six
    rim = [0, 1, 2, 4, 5, 6]
    for cb in ("X", "Z"):
        for j in range(4):
            phi = 2 * math.pi * j / (4 * 6)
            qc = QuantumCircuit(7, 7); ghz_center_out(qc, list(range(7)), 3)
            if cb == "X":
                qc.h(3)
            for k in rim:
                qc.rz(phi, k); qc.h(k)
            qc.measure(range(7), range(7))
            circs.append(qc); meta.append({"kind": "fire", "center_basis": cb, "j": j})
    return circs, meta


# ----------------------------------------------------------------- layout
def best_chain(backend, length=9):
    """Best simple path of `length` physical qubits by two-qubit and readout error."""
    t = backend.target
    two = None
    for name in ("cz", "ecr", "cx"):
        if name in t.operation_names:
            two = name; break
    err2 = {}
    for qargs, props in t[two].items():
        if props is not None and props.error is not None:
            err2[tuple(qargs)] = props.error
    ro = {}
    for (q,), props in t["measure"].items():
        ro[q] = props.error if props and props.error is not None else 0.05
    adj = {}
    for (a, b), e in err2.items():
        if e < 0.05:
            adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    def edge_err(a, b):
        return min(err2.get((a, b), 1), err2.get((b, a), 1))
    best, best_score = None, -1e9
    def dfs(path, score):
        nonlocal best, best_score
        if len(path) == length:
            if score > best_score:
                best, best_score = list(path), score
            return
        for nb in adj.get(path[-1], ()):
            if nb in path:
                continue
            s = score + math.log(1 - edge_err(path[-1], nb)) + math.log(1 - ro.get(nb, 0.05))
            path.append(nb); dfs(path, s); path.pop()
    for q in adj:
        dfs([q], math.log(1 - ro.get(q, 0.05)))
    return best, two


# ----------------------------------------------------------------- run
PENDING = RES / "round2_hardware_pending.json"

def submit():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=27)
    chain, two = best_chain(backend, 9)
    circs, meta = build()
    tcs = [transpile(qc, backend, initial_layout=chain[:qc.num_qubits], optimization_level=1, seed_transpiler=7)
           for qc in circs]
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"job_id": job.job_id(), "backend": backend.name, "chain": chain,
        "two_qubit_gate": two, "meta": meta, "twoq_counts": [tc.num_nonlocal_gates() for tc in tcs],
        "depths": [tc.depth() for tc in tcs],
        "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, "chain", chain)

def fetch():
    from qiskit_ibm_runtime import QiskitRuntimeService
    P = json.loads(PENDING.read_text())
    job = QiskitRuntimeService().job(P["job_id"])
    st = job.status()
    print("status", st)
    if str(st).upper().split(".")[-1] not in ("DONE",):
        return
    result = job.result()
    out = {"backend": P["backend"], "job_id": P["job_id"], "chain": P["chain"], "two_qubit_gate": P["two_qubit_gate"],
           "shots": SHOTS, "timestamp_utc": P["submitted_utc"], "twoq_counts": P["twoq_counts"],
           "depths": P["depths"], "items": []}
    for m, pub in zip(P["meta"], result):
        out["items"].append({**m, "counts": pub.data.c.get_counts()})
    try:
        out["qpu_seconds"] = job.usage()
    except Exception:
        pass
    COUNTS.write_text(json.dumps(out, indent=1))
    print("saved", COUNTS)


# ----------------------------------------------------------------- analyze
def bits(key, n):
    # qiskit bitstrings: rightmost char = clbit 0
    return [int(key[n - 1 - i]) for i in range(n)]

def parity_exp(counts, n, idx=None, cond=None):
    tot, s = 0, 0.0
    for k, v in counts.items():
        b = bits(k, n)
        sign = 1
        if cond is not None:
            ci, want = cond
            if b[ci] != want:
                continue
        for i in (idx if idx is not None else range(n)):
            sign *= (1 - 2 * b[i])
        s += sign * v; tot += v
    return s / tot if tot else 0.0

def resample(counts, rng):
    keys = list(counts); p = np.array([counts[k] for k in keys], float); N = int(p.sum())
    draw = rng.multinomial(N, p / N)
    return {k: int(c) for k, c in zip(keys, draw) if c}

def analyze(B=1000):
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    rng = np.random.default_rng(20260917)

    def ghz_f(n, getc):
        pop = getc(("pop", n))
        tot = sum(pop.values())
        p0 = pop.get("0" * n, 0) / tot; p1 = pop.get("1" * n, 0) / tot
        P = [parity_exp(getc(("par", n, j)), n) for j in range(4)]
        C = math.hypot(P[0] - P[2], P[1] - P[3]) / 2
        F = (p0 + p1) / 2 + C / 2
        return F, C, p0 + p1

    index = {}
    for it in items:
        if it["kind"] == "pop": index[("pop", it["n"])] = it["counts"]
        if it["kind"] == "par": index[("par", it["n"], it["j"])] = it["counts"]

    point = {n: ghz_f(n, lambda k: index[k]) for n in SIZES}
    f = {n: point[n][0] ** (1 / n) for n in SIZES}
    others = [5, 6, 8, 9]
    def trend_resid(fd):
        x = np.array(others, float); y = np.array([fd[n] for n in others])
        a, b = np.polyfit(x, y, 1)
        return fd[7] - (a * 7 + b)
    resid0 = trend_resid(f)
    boots = []
    for _ in range(B):
        rc = {k: resample(v, rng) for k, v in index.items()}
        fb = {n: ghz_f(n, lambda k: rc[k])[0] ** (1 / n) for n in SIZES}
        boots.append(trend_resid(fb))
    se = float(np.std(boots, ddof=1))
    t15 = {"by_n": {n: {"F": round(point[n][0], 4), "coherence": round(point[n][1], 4),
                        "population": round(point[n][2], 4), "per_qubit_f": round(f[n], 5)} for n in SIZES},
           "residual_7_vs_trend": round(resid0, 5), "bootstrap_se": round(se, 5),
           "z": round(resid0 / se, 2) if se else None,
           "verdict": "PASS" if resid0 > 2 * se else "FAIL",
           "rule": "PASS if f_7 sits above the line through n=5,6,8,9 by more than 2 bootstrap SE"}

    # P-2
    pc = {it["basis"]: it["counts"] for it in items if it["kind"] == "pair"}
    pairs = [(i, j) for i in range(7) for j in range(i + 1, 7)]
    xx = {f"{i}-{j}": round(parity_exp(pc["X"], 7, [i, j]), 4) for i, j in pairs}
    yy = {f"{i}-{j}": round(parity_exp(pc["Y"], 7, [i, j]), 4) for i, j in pairs}
    x7 = parity_exp(pc["X"], 7)
    maxpair = max(max(abs(v) for v in xx.values()), max(abs(v) for v in yy.values()))
    C7 = point[7][1]
    p2 = {"XX": xx, "YY": yy, "max_abs_pair": round(maxpair, 4), "seven_body_X_parity": round(x7, 4),
          "C7": round(C7, 4),
          "verdict": "PASS" if (maxpair <= 0.1 and C7 >= 0.5) else "FAIL"}

    # P-1
    fire = {}
    for cb in ("X", "Z"):
        cs = {it["j"]: it["counts"] for it in items if it["kind"] == "fire" and it["center_basis"] == cb}
        rim = [0, 1, 2, 4, 5, 6]
        branch = {}
        for outcome in (0, 1):
            P = [parity_exp(cs[j], 7, rim, cond=(3, outcome)) for j in range(4)]
            branch[outcome] = {"P": [round(p, 4) for p in P], "C6": math.hypot(P[0] - P[2], P[1] - P[3]) / 2}
        # weight by how often each outcome occurred
        w = []
        for outcome in (0, 1):
            tot = sum(v for k, v in cs[0].items() if bits(k, 7)[3] == outcome)
            w.append(tot)
        C6 = (branch[0]["C6"] * w[0] + branch[1]["C6"] * w[1]) / max(1, sum(w))
        fire[cb] = {"C6_weighted": round(C6, 4),
                    "by_outcome": {o: {"C6": round(branch[o]["C6"], 4), "P": branch[o]["P"], "shots": w[o]} for o in (0, 1)}}
    p1 = {"center_read_X": fire["X"], "center_read_Z": fire["Z"],
          "verdict": "PASS" if (fire["X"]["C6_weighted"] >= 0.5 and fire["Z"]["C6_weighted"] <= 0.1) else "FAIL"}

    out = {"backend": D["backend"], "job_id": D["job_id"], "chain": D["chain"], "timestamp_utc": D["timestamp_utc"],
           "shots": D["shots"], "T-1.5": t15, "P-2": p2, "P-1": p1,
           "twoq_counts": D.get("twoq_counts"), "depths": D.get("depths"), "qpu_usage": D.get("qpu_seconds")}
    (RES / "round2_hardware.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"T-1.5": {k: t15[k] for k in ("by_n", "residual_7_vs_trend", "bootstrap_se", "z", "verdict")},
                      "P-2": {k: p2[k] for k in ("max_abs_pair", "C7", "verdict")},
                      "P-1": {"X": fire["X"]["C6_weighted"], "Z": fire["Z"]["C6_weighted"], "verdict": p1["verdict"]}},
                     indent=1))


if __name__ == "__main__":
    {"submit": submit, "fetch": fetch, "analyze": analyze}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
