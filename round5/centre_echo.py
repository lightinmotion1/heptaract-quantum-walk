#!/usr/bin/env python3
"""
P-13 — The echo: does the shared centre come back?

P-12 found the bond across six gone by 30 microseconds, at exactly the rate its six carriers
dephase. That leaves one question open, and it is the one that matters:

    did the RELATIONSHIP decay, or did the WIRE holding it get noisy?

Dephasing from slow noise is reversible. Put refocusing pulses inside the wait — the same wait,
the same reading, the same everything — and slow dephasing unwinds itself. If the bond comes back,
what died at 30 microseconds was the carriers' phase memory, not the thing between the ships.

Four treatments of the identical 30 microsecond wait, all read the shared way:

    NONE      the wait left silent                     (the P-12 point, reproduced)
    ECHO-2    two pulses, Hahn style                    X at the middle, X at the end
    ECHO-8    eight pulses, XY8                         the standard refocusing sequence
    ZERO      no wait at all                            (the ceiling, for scale)

plus a private reading with and without the echo, as controls.

  python3 centre_echo.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "centre_echo_pending.json"
COUNTS = RES / "centre_echo_counts.json"
OUT = RES / "centre_echo.json"

RIM_A = [0, 1, 2]
C1, ANC, C2 = 3, 4, 5
RIM_B = [6, 7, 8]
NQ = 9
ALL = list(range(NQ))
THETAS = 8
SHOTS = 1024
WAIT_US = 30
ARMS = [("ours", "zero"), ("ours", "none"), ("ours", "echo2"), ("ours", "echo8"),
        ("private", "none"), ("private", "echo8")]


def prep(qc):
    qc.h(C1)
    for r in RIM_A:
        qc.cx(C1, r)
    qc.h(C2)
    for r in RIM_B:
        qc.cx(C2, r)
    qc.cz(C1, C2)


def idle(qc, treatment):
    """The same 30 microseconds, spent four ways. Every sequence composes to the identity."""
    if treatment == "zero":
        return
    qc.barrier(ALL)
    if treatment == "none":
        for q in ALL:
            qc.delay(WAIT_US, q, unit="us")
    elif treatment == "echo2":
        seg = WAIT_US / 2.0
        for _ in range(2):
            for q in ALL:
                qc.delay(seg, q, unit="us")
            for q in ALL:
                qc.x(q)
            qc.barrier(ALL)
    elif treatment == "echo8":
        seg = WAIT_US / 8.0
        pulses = ["x", "y", "x", "y", "y", "x", "y", "x"]     # XY8
        for p in pulses:
            for q in ALL:
                qc.delay(seg, q, unit="us")
            for q in ALL:
                getattr(qc, p)(q)
            qc.barrier(ALL)
    qc.barrier(ALL)


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []
    for reading, treatment in ARMS:
        for t in range(THETAS):
            theta = 2 * math.pi * t / THETAS
            qc = QuantumCircuit(NQ, NQ)
            prep(qc)
            idle(qc, treatment)
            if reading == "ours":
                qc.h(C1); qc.h(C2)
                qc.cx(C1, ANC)
                qc.cx(C2, ANC)
                qc.measure(ANC, ANC)
                qc.h(C1); qc.h(C2)
            else:
                qc.h(C1)
                qc.measure(C1, C1)
            for r in RIM_A + RIM_B:
                qc.rz(theta, r)
                qc.h(r)
            qc.measure(RIM_A + RIM_B, RIM_A + RIM_B)
            circs.append(qc)
            meta.append({"reading": reading, "treatment": treatment, "t": t})
    return circs, meta


def best_line(backend, length=NQ):
    t = backend.target
    two = next(x for x in ("cz", "ecr", "cx") if x in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else .05) for q, p in t["measure"].items()}
    t2 = {}
    for q in range(backend.num_qubits):
        try:
            t2[q] = backend.qubit_properties(q).t2 or 0
        except Exception:
            t2[q] = 0
    adj = {}
    for (a, b), e in err2.items():
        if e < .05:
            adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    def ee(a, b): return min(err2.get((a, b), 1.), err2.get((b, a), 1.))
    # this test lives or dies on coherence, so the chain is chosen by T2 as well as by gate error
    def score(q): return math.log(1 - ro.get(q, .05)) + 0.35 * math.log(max(t2.get(q, 1e-6), 1e-6))
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
                                   "meta": meta, "shots": SHOTS, "coherence": props, "wait_us": WAIT_US,
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
                                  "wait_us": P.get("wait_us"), "qpu_usage": usage,
                                  "timestamp_utc": P["submitted_utc"], "items": items}, indent=1))
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
                                  "shots": 4096, "coherence": None, "wait_us": WAIT_US,
                                  "qpu_usage": None, "timestamp_utc": "sim", "items": items}, indent=1))
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
        series = [parity(by_t[t], RIM_A + RIM_B, (cbit, outcome))[0] for t in range(THETAS)]
        sp = np.abs(np.fft.rfft(np.array(series))) / THETAS
        vals.append(float(np.sum(sp[1:])))
    return round(float(np.mean(vals)), 4)


def analyze():
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    out = {"backend": D["backend"], "chain": D["chain"], "shots": D["shots"], "wait_us": D.get("wait_us"),
           "coherence": D.get("coherence"), "qpu_usage": D.get("qpu_usage"), "bond": {}}
    for reading, treatment in ARMS:
        by_t = {it["t"]: it["counts"] for it in items
                if it["reading"] == reading and it["treatment"] == treatment}
        cbit = ANC if reading == "ours" else C1
        out["bond"]["%s/%s" % (reading, treatment)] = bond_of(by_t, cbit)
    b = out["bond"]
    floor = b["private/none"]
    out["floor"] = floor
    out["recovered"] = {k: round(max(v - floor, 0.0), 4) for k, v in b.items()}
    zero = out["recovered"]["ours/zero"]
    out["verdict"] = {
        "echo_beats_silence": b["ours/echo8"] > 2 * b["ours/none"] or b["ours/echo2"] > 2 * b["ours/none"],
        "echo_recovers_fraction_of_ceiling": round(max(out["recovered"]["ours/echo8"],
                                                       out["recovered"]["ours/echo2"]) / zero, 3) if zero else None,
        "eight_beats_two": b["ours/echo8"] >= b["ours/echo2"],
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("bond", "floor", "recovered", "verdict")}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
