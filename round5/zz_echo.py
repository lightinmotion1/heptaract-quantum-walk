#!/usr/bin/env python3
"""
P-16 — The echo timed against the neighbours, not against the clock.

P-15 named the channel: an always-on coupling of about 3.9 kHz between each rim qubit and its own
centre. A neighbour in superposition dephases whatever it is coupled to.

And it carries a consequence the earlier echoes missed. The coupling term is a PRODUCT of the two
qubits' phases, so flipping BOTH members at the same moment flips the sign twice and leaves the
coupling exactly where it was. Every echo in P-13 and P-14 flipped all nine qubits together — which
refocuses each qubit's own dephasing and does nothing at all to the neighbours.

Four treatments of the same wait:

    SILENT      nothing
    CLOCK       X on every qubit at the middle and the end   (P-13's echo: local yes, neighbours no)
    ZZ          X on the CENTRES only                        (neighbours yes, local no)
    BOTH        rim flipped at the quarters, centres at the halves — staggered, so each pair sees
                an odd number of relative flips in each interval, and each qubit sees an even
                number overall                               (neighbours yes, local yes)

  python3 zz_echo.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "zz_echo_pending.json"
COUNTS = RES / "zz_echo_counts.json"
OUT = RES / "zz_echo.json"

RIM_A, C1, ANC, C2, RIM_B = 0, 1, 2, 3, 4
RIM = [RIM_A, RIM_B]
CENTRES = [C1, C2]
NQ = 5
ALL = list(range(NQ))
THETAS = 8
SHOTS = 1024
DELAYS = [0, 60, 180]
TREATMENTS = ["silent", "clock", "zz", "both"]

SCHEDULES = {
    "silent": [(1.0, [])],
    "clock":  [(0.5, ALL), (0.5, ALL)],
    "zz":     [(0.5, CENTRES), (0.5, CENTRES)],
    "both":   [(0.25, RIM), (0.25, CENTRES), (0.25, RIM), (0.25, CENTRES)],
}


def prep(qc):
    qc.h(C1); qc.cx(C1, RIM_A)
    qc.h(C2); qc.cx(C2, RIM_B)
    qc.cz(C1, C2)


def idle(qc, us, treatment):
    if us == 0:
        return
    qc.barrier(ALL)
    for frac, flips in SCHEDULES[treatment]:
        seg = us * frac
        for q in ALL:
            qc.delay(seg, q, unit="us")
        for q in flips:
            qc.x(q)
        qc.barrier(ALL)


def arms():
    out = [("ours", 0, "silent")]
    for us in DELAYS[1:]:
        for tr in TREATMENTS:
            out.append(("ours", us, tr))
    out.append(("private", DELAYS[1], "silent"))
    return out


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []
    for reading, us, tr in arms():
        for t in range(THETAS):
            theta = 2 * math.pi * t / THETAS
            qc = QuantumCircuit(NQ, NQ)
            prep(qc)
            idle(qc, us, tr)
            if reading == "ours":
                qc.h(C1); qc.h(C2)
                qc.cx(C1, ANC); qc.cx(C2, ANC)
                qc.measure(ANC, ANC)
                qc.h(C1); qc.h(C2)
            else:
                qc.h(C1); qc.measure(C1, C1)
            for r in RIM:
                qc.rz(theta, r); qc.h(r)
            qc.measure(RIM, RIM)
            circs.append(qc)
            meta.append({"reading": reading, "delay_us": us, "treatment": tr, "t": t})
    return circs, meta


def best_line(backend, length=NQ):
    t = backend.target
    two = next(x for x in ("cz", "ecr", "cx") if x in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else .05) for q, p in t["measure"].items()}
    t2 = {}
    for q in range(backend.num_qubits):
        try:
            t2[q] = (backend.qubit_properties(q).t2 or 1e-6) * 1e6
        except Exception:
            t2[q] = 1.0
    adj = {}
    for (a, b), e in err2.items():
        if e < .04:
            adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    def ee(a, b): return min(err2.get((a, b), 1.), err2.get((b, a), 1.))
    def score(q): return math.log(1 - ro.get(q, .05)) + 0.8 * math.log(max(t2.get(q, 1.), 1.))
    beam = [([q], score(q)) for q in adj]
    for _ in range(length - 1):
        nxt = []
        for path, sc in beam:
            for nb in adj.get(path[-1], ()):
                if nb in path: continue
                nxt.append((path + [nb], sc + math.log(1 - ee(path[-1], nb)) + score(nb)))
        nxt.sort(key=lambda x: -x[1]); beam = nxt[:400]
    beam.sort(key=lambda x: -x[1])
    return beam[0][0], two


def submit():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    svc = QiskitRuntimeService()
    backend = svc.least_busy(operational=True, simulator=False, min_num_qubits=NQ + 4)
    chain, two = best_line(backend, NQ)
    props = {}
    for q in chain:
        try:
            props[str(q)] = {"T1_us": round(backend.qubit_properties(q).t1 * 1e6, 1),
                             "T2_us": round(backend.qubit_properties(q).t2 * 1e6, 1)}
        except Exception:
            pass
    circs, meta = build()
    tcs = [transpile(c, backend, initial_layout=chain, optimization_level=1, seed_transpiler=7) for c in circs]
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"backend": backend.name, "chain": chain, "job_id": job.job_id(),
                                   "meta": meta, "shots": SHOTS, "coherence": props,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, len(tcs), "circuits")
    print("chain coherence:", json.dumps(props))


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
                                  "shots": P["shots"], "coherence": P.get("coherence"),
                                  "qpu_usage": usage, "timestamp_utc": P["submitted_utc"],
                                  "items": items}, indent=1))
    print("saved", COUNTS, usage)


def simulate():
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    sim = AerSimulator()
    circs, meta = build()
    tcs = transpile(circs, sim, optimization_level=1)
    res = sim.run(tcs, shots=4096, seed_simulator=7).result()
    items = [{**m, "counts": res.get_counts(i)} for i, m in enumerate(meta)]
    COUNTS.write_text(json.dumps({"backend": "aer", "chain": list(range(NQ)), "job_id": "sim",
                                  "shots": 4096, "coherence": None, "qpu_usage": None,
                                  "timestamp_utc": "sim", "items": items}, indent=1))
    print("simulated", len(circs), "circuits")


# ------------------------------------------------------------------ analyze
def bits(key):
    b = key.replace(" ", "")
    return [int(b[len(b) - 1 - i]) for i in range(len(b))]


def parity(counts, idx, cond):
    tot, s = 0, 0.0
    for k, v in counts.items():
        b = bits(k)
        if b[cond[0]] != cond[1]:
            continue
        sign = 1
        for i in idx:
            sign *= (1 - 2 * b[i])
        s += sign * v; tot += v
    return (s / tot if tot else 0.0), tot


def bond_of(by_t, cbit):
    vals = []
    for outcome in (0, 1):
        series = [parity(by_t[t], RIM, (cbit, outcome))[0] for t in range(THETAS)]
        sp = np.abs(np.fft.rfft(np.array(series))) / THETAS
        vals.append(float(np.sum(sp[1:])))
    return round(float(np.mean(vals)), 4)


def analyze():
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    out = {"backend": D["backend"], "chain": D["chain"], "shots": D["shots"],
           "coherence": D.get("coherence"), "qpu_usage": D.get("qpu_usage"), "bond": {}}
    for reading, us, tr in arms():
        by_t = {it["t"]: it["counts"] for it in items
                if it["reading"] == reading and it["delay_us"] == us and it["treatment"] == tr}
        cbit = ANC if reading == "ours" else C1
        out["bond"]["%s/%dus/%s" % (reading, us, tr)] = bond_of(by_t, cbit)

    b = out["bond"]
    floor = b["private/%dus/silent" % DELAYS[1]]
    ceil = max(b["ours/0us/silent"] - floor, 1e-9)
    frac = {k: round(max(v - floor, 0.0) / ceil, 3) for k, v in b.items() if k.startswith("ours")}
    out["floor"] = round(floor, 4)
    out["fraction_of_ceiling"] = frac

    def f(us, tr): return frac.get("ours/%dus/%s" % (us, tr), 0.0)
    best = {}
    for us in DELAYS[1:]:
        cands = {tr: f(us, tr) for tr in TREATMENTS}
        bt = max(cands, key=cands.get)
        tau = round(us / math.log(1 / cands[bt]), 1) if 0 < cands[bt] < 1 else None
        best[str(us)] = {"treatment": bt, "fraction": cands[bt], "tau_us": tau, "all": cands}
    out["best_by_delay"] = best
    out["verdict"] = {
        "staggered_beats_clock_at_60us": f(60, "both") >= 1.3 * max(f(60, "clock"), 1e-9),
        "centre_only_beats_silence_at_60us": f(60, "zz") >= 1.5 * max(f(60, "silent"), 1e-9),
        "best_keeps_15pc_at_180us": max(f(180, t) for t in TREATMENTS) >= 0.15,
        "ratio_both_over_clock_60us": round(f(60, "both") / max(f(60, "clock"), 1e-9), 2),
        "ratio_zz_over_silent_60us": round(f(60, "zz") / max(f(60, "silent"), 1e-9), 2),
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("bond", "floor", "fraction_of_ceiling",
                                          "best_by_delay", "verdict")}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
