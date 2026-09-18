#!/usr/bin/env python3
"""
P-17 — Settling the floor, so the magnitudes can be quoted.

P-16 established an ordering but not a size, because its private control returned about twice the
noise floor the same control gave in two earlier runs. A metric's floor has to be known before any
percentage built on it means anything.

Four arms, at high shots, on one chain:

    FLOOR-private   the private reading — one ship's own centre — which cannot hold a shared bond
    FLOOR-product   the shared reading on a state whose rims were never entangled with their own
                    centres, so no bond can exist anywhere. A second, independent estimate of the
                    same floor.

    (An earlier design used "no link between the ships" as the null. The simulator showed that is
    NOT a null: reading the parity of two unlinked centres SWAPS the entanglement onto the two
    rims and produces a full bond. That is a real effect worth its own test, not a floor.)
    CEILING         the shared reading with no wait at all
    SIGNAL          the shared reading after 60 microseconds with the centres-only echo

Everything carries a bootstrap error bar this time.

  python3 control_floor.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "control_floor_pending.json"
COUNTS = RES / "control_floor_counts.json"
OUT = RES / "control_floor.json"

RIM_A, C1, ANC, C2, RIM_B = 0, 1, 2, 3, 4
RIM = [RIM_A, RIM_B]
CENTRES = [C1, C2]
NQ = 5
ALL = list(range(NQ))
THETAS = 8
SHOTS = 4096
WAIT = 60
ARMS = ["floor_private", "floor_product", "ceiling", "signal"]


def prep(qc, rims=True):
    qc.h(C1)
    if rims:
        qc.cx(C1, RIM_A)
    qc.h(C2)
    if rims:
        qc.cx(C2, RIM_B)
    qc.cz(C1, C2)


def centres_echo(qc, us):
    qc.barrier(ALL)
    for _ in range(2):
        for q in ALL:
            qc.delay(us / 2.0, q, unit="us")
        for q in CENTRES:
            qc.x(q)
        qc.barrier(ALL)


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []
    for arm in ARMS:
        for t in range(THETAS):
            theta = 2 * math.pi * t / THETAS
            qc = QuantumCircuit(NQ, NQ)
            prep(qc, rims=(arm != "floor_product"))
            if arm == "signal":
                centres_echo(qc, WAIT)
            elif arm == "floor_private":
                qc.barrier(ALL)
                for q in ALL:
                    qc.delay(WAIT, q, unit="us")
                qc.barrier(ALL)
            if arm == "floor_private":
                qc.h(C1); qc.measure(C1, C1)
            else:
                qc.h(C1); qc.h(C2)
                qc.cx(C1, ANC); qc.cx(C2, ANC)
                qc.measure(ANC, ANC)
                qc.h(C1); qc.h(C2)
            for r in RIM:
                qc.rz(theta, r); qc.h(r)
            qc.measure(RIM, RIM)
            circs.append(qc)
            meta.append({"arm": arm, "t": t})
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
    circs, meta = build()
    tcs = [transpile(c, backend, initial_layout=chain, optimization_level=1, seed_transpiler=7) for c in circs]
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"backend": backend.name, "chain": chain, "job_id": job.job_id(),
                                   "meta": meta, "shots": SHOTS,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, len(tcs), "circuits x", SHOTS, "shots")


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
    res = sim.run(tcs, shots=SHOTS, seed_simulator=7).result()
    items = [{**m, "counts": res.get_counts(i)} for i, m in enumerate(meta)]
    COUNTS.write_text(json.dumps({"backend": "aer", "chain": list(range(NQ)), "job_id": "sim",
                                  "shots": SHOTS, "qpu_usage": None, "timestamp_utc": "sim",
                                  "items": items}, indent=1))
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
    return float(np.mean(vals))


def resample(counts, rng):
    keys = list(counts)
    p = np.array([counts[k] for k in keys], float)
    n = int(p.sum())
    draw = rng.multinomial(n, p / n)
    return {k: int(c) for k, c in zip(keys, draw) if c}


def analyze(B=400):
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    rng = np.random.default_rng(20260918)
    out = {"backend": D["backend"], "chain": D["chain"], "shots": D["shots"],
           "qpu_usage": D.get("qpu_usage"), "arms": {}}
    raw = {}
    for arm in ARMS:
        by_t = {it["t"]: it["counts"] for it in items if it["arm"] == arm}
        cbit = C1 if arm == "floor_private" else ANC
        val = bond_of(by_t, cbit)
        boots = []
        for _ in range(B):
            rb = {t: resample(c, rng) for t, c in by_t.items()}
            boots.append(bond_of(rb, cbit))
        sd = float(np.std(boots, ddof=1))
        raw[arm] = (val, sd)
        out["arms"][arm] = {"bond": round(val, 4), "bootstrap_sd": round(sd, 4)}

    fp, fp_sd = raw["floor_private"]
    fn, fn_sd = raw["floor_product"]
    agree = abs(fp - fn) / max((fp + fn) / 2, 1e-9)
    floor = (fp + fn) / 2
    floor_sd = math.hypot(fp_sd, fn_sd) / 2
    ce, ce_sd = raw["ceiling"]
    sg, sg_sd = raw["signal"]
    frac = (sg - floor) / max(ce - floor, 1e-9)
    frac_sd = abs(frac) * math.hypot(math.hypot(sg_sd, floor_sd) / max(sg - floor, 1e-9),
                                     math.hypot(ce_sd, floor_sd) / max(ce - floor, 1e-9))
    out["floor"] = {"private": round(fp, 4), "product": round(fn, 4),
                    "relative_difference": round(agree, 3), "pooled": round(floor, 4),
                    "pooled_sd": round(floor_sd, 4)}
    out["signal_over_floor_sd"] = round((sg - floor) / math.hypot(sg_sd, floor_sd), 1)
    out["surviving_fraction_at_60us"] = {"value": round(frac, 3), "sd": round(frac_sd, 3)}
    out["verdict"] = {
        "two_floor_estimates_agree_within_15pc": agree <= 0.15,
        "signal_above_floor_by_5sd": (sg - floor) / math.hypot(sg_sd, floor_sd) >= 5,
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("arms", "floor", "signal_over_floor_sd",
                                          "surviving_fraction_at_60us", "verdict")}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
