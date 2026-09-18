#!/usr/bin/env python3
"""
P-14 — How far can the shared centre reach?

P-12 and P-13 said the reach of the shared centre is a property of its CARRIERS: the bond across
six died at the sum of six dephasing rates, and one echo gave a third of it back. So this asks the
engineering question the physics implies:

    hold the relationship with fewer, better-chosen carriers, refocus the wait, and how far does
    the centre of both reach?

Two ships, each a centre with ONE rim qubit instead of three, so the shared bond is carried by two
things rather than six. The chain is chosen by coherence. The wait is swept out to 180 microseconds
and spent four ways: silent, and refocused with two, four or eight pulses.

Pre-registered, from the sum-of-rates arithmetic: two carriers should last about three times longer
than six, and the best pulse count should be SMALL, because on this hardware pulse error outruns
the noise it cancels (P-13).

  python3 centre_reach.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "centre_reach_pending.json"
COUNTS = RES / "centre_reach_counts.json"
OUT = RES / "centre_reach.json"

RIM_A, C1, ANC, C2, RIM_B = 0, 1, 2, 3, 4
RIM = [RIM_A, RIM_B]
NQ = 5
ALL = list(range(NQ))
THETAS = 8
SHOTS = 1024
DELAYS = [0, 60, 180]                 # microseconds
TREATMENTS = ["none", "echo2", "echo4", "echo8"]


def prep(qc):
    qc.h(C1); qc.cx(C1, RIM_A)
    qc.h(C2); qc.cx(C2, RIM_B)
    qc.cz(C1, C2)


def idle(qc, us, treatment):
    if us == 0:
        return
    qc.barrier(ALL)
    n = {"none": 0, "echo2": 2, "echo4": 4, "echo8": 8}[treatment]
    if n == 0:
        for q in ALL:
            qc.delay(us, q, unit="us")
    else:
        seq = {2: ["x", "x"], 4: ["x", "y", "x", "y"],
               8: ["x", "y", "x", "y", "y", "x", "y", "x"]}[n]
        seg = us / float(n)
        for p in seq:
            for q in ALL:
                qc.delay(seg, q, unit="us")
            for q in ALL:
                getattr(qc, p)(q)
            qc.barrier(ALL)
    qc.barrier(ALL)


def arms():
    out = [("ours", 0, "none")]
    for us in DELAYS[1:]:
        for tr in TREATMENTS:
            out.append(("ours", us, tr))
    out.append(("private", DELAYS[1], "none"))
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
    floor = b["private/%dus/none" % DELAYS[1]]
    ceil = max(b["ours/0us/none"] - floor, 1e-9)
    corr = {k: round(max(v - floor, 0.0), 4) for k, v in b.items()}
    frac = {k: round(v / ceil, 3) for k, v in corr.items() if k.startswith("ours")}

    def tau(key, us):
        f = frac.get(key, 0)
        return round(us / math.log(1 / f), 1) if 0 < f < 1 else None

    coh = D.get("coherence") or {}
    ch = D.get("chain") or []
    rim_phys = [str(ch[i]) for i in (RIM_A, RIM_B)] if ch else []
    rim_t2 = [coh[q]["T2_us"] for q in rim_phys if q in coh]
    two_body = round(1.0 / sum(1.0 / x for x in rim_t2), 1) if rim_t2 else None

    best = {}
    for us in DELAYS[1:]:
        cands = {tr: frac.get("ours/%dus/%s" % (us, tr), 0) for tr in TREATMENTS}
        bt = max(cands, key=cands.get)
        best[str(us)] = {"treatment": bt, "fraction": cands[bt], "tau_us": tau("ours/%dus/%s" % (us, bt), us),
                         "all": cands}
    out.update({"floor": round(floor, 4), "ceiling_above_floor": round(ceil, 4),
                "fraction_of_ceiling": frac, "rim_T2_us": {q: coh[q]["T2_us"] for q in rim_phys if q in coh},
                "two_body_prediction_us": two_body, "best_by_delay": best})
    out["verdict"] = {
        "two_carriers_beat_six_at_matched_wait": None,     # filled by hand against P-13's 8.9%
        "echo_helps_at_every_delay": all(
            best[str(us)]["treatment"] != "none" for us in DELAYS[1:]),
        "small_pulse_count_wins": all(
            best[str(us)]["treatment"] in ("echo2", "echo4") for us in DELAYS[1:]),
        "reaches_180us": frac.get("ours/180us/%s" % best["180"]["treatment"], 0) >= 0.10,
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("bond", "floor", "fraction_of_ceiling",
                                          "rim_T2_us", "two_body_prediction_us",
                                          "best_by_delay", "verdict")}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
