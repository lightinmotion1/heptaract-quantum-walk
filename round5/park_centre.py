#!/usr/bin/env python3
"""
P-20 — Was the diagnosis right? Parking the spent, or merely hurrying.

P-19 failed: two hops reached 6.7% of the ceiling where 42.2% was predicted, and the fidelity fell
below the one-half line. But the two-hop numbers did not fall together — the z-correlation survived
at 0.587 while the phase collapsed to 0.062, which is the signature of dephasing rather than decay.

A diagnosis was offered AFTER that data, which makes it a hypothesis and not a finding: the first
reading leaves its spent qubits alive in superposition beside the carriers, and P-15 measured that
neighbour coupling at 3.9 kHz while P-16 established what a neighbour in superposition does.

This run exists to give that hypothesis a chance to be WRONG, and the two candidate causes are
separated so they cannot hide behind each other:

    NEIGHBOURS   the spent qubits are left humming next to the carriers
    TIME         the second reading simply takes too long and the ends dephase while waiting

Six arms on the same 8-qubit line, everything scored the same way:

    none              no reading          -> ceiling on a,b  and a floor on a,f
    first             one reading         -> one hop on a,d
    naive             P-19 exactly        -> the replication. If this does not reproduce P-19,
                                            nothing else in this run means anything.
    parked            sequential + the spent qubits RESET after the first reading
                                          -> isolates NEIGHBOURS (same elapsed time as naive, plus
                                             the reset; the neighbours go quiet)
    parallel          readings concurrent, nothing parked
                                          -> isolates TIME (the neighbours still hum, but for
                                             roughly half as long)
    parked_parallel   both fixes together

If parking helps and hurrying does not, the diagnosis stands. If hurrying helps and parking does
not, the cause was elapsed time and the neighbour claim is retracted. If neither helps, the whole
diagnosis is wrong and P-19's failure is unexplained — which is a proper outcome and will be
written as one.

  python3 park_centre.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "park_centre_pending.json"
COUNTS = RES / "park_centre_counts.json"
OUT = RES / "park_centre.json"

#            a  b  ANC1  c  d  ANC2  e  f
A, B, ANC1, C, D, ANC2, E, F = 0, 1, 2, 3, 4, 5, 6, 7
NQ = 8
LIVE = [A, B, C, D, E, F]
CB = {q: i for i, q in enumerate(LIVE)}
Z1, X1, Z2, X2 = 6, 7, 8, 9
NC = 10

PAIRS = [(A, B), (C, D), (E, F)]
THETAS = 8
SHOTS = 4096
ARMS = ["none", "first", "naive", "parked", "parallel", "parked_parallel"]


def prep(qc):
    for u, v in PAIRS:
        qc.h(u); qc.cx(u, v)


def reading(qc, pair, anc, zbit, xbit):
    """A complete joint reading of two centres onto a shared thing: Z parity, reset, X parity.
    Barriers are held to the qubits involved, so two readings on disjoint qubits may overlap."""
    span = list(pair) + [anc]
    qc.barrier(span)
    for q in pair:
        qc.cx(q, anc)
    qc.measure(anc, zbit)
    qc.reset(anc)
    qc.barrier(span)
    for q in pair:
        qc.h(q)
    for q in pair:
        qc.cx(q, anc)
    qc.measure(anc, xbit)
    qc.barrier(span)


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []
    for arm in ARMS:
        for kind in ["pop"] + ["par%d" % t for t in range(THETAS)]:
            qc = QuantumCircuit(NQ, NC)
            prep(qc)

            if arm == "first":
                reading(qc, (B, C), ANC1, Z1, X1)
            elif arm in ("naive", "parked"):
                reading(qc, (B, C), ANC1, Z1, X1)
                if arm == "parked":
                    qc.reset(B); qc.reset(C)        # the spent go quiet before the long wait
                qc.barrier(range(NQ))               # sequential: the second waits for the first
                reading(qc, (D, E), ANC2, Z2, X2)
            elif arm in ("parallel", "parked_parallel"):
                reading(qc, (B, C), ANC1, Z1, X1)   # no full-width barrier: disjoint qubits,
                reading(qc, (D, E), ANC2, Z2, X2)   # so these may be scheduled together
                if arm == "parked_parallel":
                    qc.barrier(range(NQ))
                    for q in (B, C, D, E):
                        qc.reset(q)

            if kind != "pop":
                theta = 2 * math.pi * int(kind[3:]) / THETAS
                for q in LIVE:
                    qc.rz(theta, q); qc.h(q)
            for q in LIVE:
                qc.measure(q, CB[q])
            circs.append(qc)
            meta.append({"arm": arm, "kind": kind})
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
        nxt.sort(key=lambda x: -x[1]); beam = nxt[:600]
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
    # the durations are the whole point of the parallel arms, so they are recorded
    durs = {}
    for m, tc in zip(meta, tcs):
        if m["kind"] == "pop":
            try:
                durs[m["arm"]] = int(tc.duration) if tc.duration else None
            except Exception:
                durs[m["arm"]] = None
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"backend": backend.name, "chain": chain, "job_id": job.job_id(),
                                   "meta": meta, "shots": SHOTS, "coherence": props,
                                   "circuit_dt": durs,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, len(tcs), "circuits x", SHOTS)
    print("durations (dt):", json.dumps(durs))


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
                                  "circuit_dt": P.get("circuit_dt"), "qpu_usage": usage,
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
                                  "shots": SHOTS, "coherence": None, "circuit_dt": None,
                                  "qpu_usage": None, "timestamp_utc": "sim", "items": items}, indent=1))
    print("simulated", len(circs), "circuits")


# ------------------------------------------------------------------ analyze
def bits(key):
    b = key.replace(" ", "")
    return [int(b[len(b) - 1 - i]) for i in range(len(b))]


def sel(counts, zsum, xbits, xsum):
    out = {}
    for k, v in counts.items():
        b = bits(k)
        if zsum:
            z = 0
            for i in zsum:
                z ^= b[i]
            if z:
                continue
        x = 0
        for i in xbits:
            x ^= b[i]
        if x != xsum:
            continue
        out[k] = out.get(k, 0) + v
    return out


def zz(counts, pair):
    i, j = CB[pair[0]], CB[pair[1]]
    tot, s = 0, 0.0
    for k, v in counts.items():
        b = bits(k)
        s += (1 - 2 * b[i]) * (1 - 2 * b[j]) * v
        tot += v
    return (s / tot if tot else 0.0), tot


def amplitude(series):
    sp = np.abs(np.fft.rfft(np.array(series))) / len(series)
    return 2.0 * float(sp[2])


def score_one(popc, parc, pair, zsum, xbits):
    cohs, sames, ns = [], [], []
    for xs in ([0, 1] if xbits else [0]):
        series = [zz(sel(parc[t], zsum, xbits, xs), pair)[0] for t in range(THETAS)]
        cohs.append(abs(amplitude(series)))
        v, n = zz(sel(popc, zsum, xbits, xs), pair)
        sames.append(abs(v)); ns.append(n)
    coh = float(np.mean(cohs)); same = float(np.mean(sames))
    return coh, same, (1.0 + same + 2.0 * coh) / 4.0, int(np.sum(ns))


def resample(counts, rng):
    keys = list(counts)
    p = np.array([counts[k] for k in keys], float)
    n = int(p.sum())
    return {k: int(c) for k, c in zip(keys, rng.multinomial(n, p / n)) if c}


TWO = (Z1, Z2), (X1, X2)
VIEWS = {
    "ceiling_gate":    ("none",  (A, B), None,   ()),
    "floor_none":      ("none",  (A, F), None,   ()),
    "one_hop":         ("first", (A, D), (Z1,),  (X1,)),
    "floor_one_short": ("first", (A, F), (Z1,),  (X1,)),
    "naive":           ("naive",           (A, F), TWO[0], TWO[1]),
    "parked":          ("parked",          (A, F), TWO[0], TWO[1]),
    "parallel":        ("parallel",        (A, F), TWO[0], TWO[1]),
    "parked_parallel": ("parked_parallel", (A, F), TWO[0], TWO[1]),
}
FIXES = ["parked", "parallel", "parked_parallel"]


def stats(items, view, rng, B=300):
    arm, pair, zsum, xbits = VIEWS[view]
    pop_c = next(it["counts"] for it in items if it["arm"] == arm and it["kind"] == "pop")
    par_c = {int(it["kind"][3:]): it["counts"] for it in items
             if it["arm"] == arm and it["kind"].startswith("par")}
    coh, same, fid, n = score_one(pop_c, par_c, pair, zsum, xbits)
    boots = [score_one(resample(pop_c, rng), {t: resample(c, rng) for t, c in par_c.items()},
                       pair, zsum, xbits)[:3] for _ in range(B)]
    arr = np.array(boots)
    return {"bond": round(coh, 4), "bond_sd": round(float(arr[:, 0].std(ddof=1)), 4),
            "z_correlation": round(same, 4),
            "fidelity": round(fid, 4), "fidelity_sd": round(float(arr[:, 2].std(ddof=1)), 4),
            "shots_in_branch": n}


def analyze():
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    rng = np.random.default_rng(20260918)
    out = {"backend": D["backend"], "chain": D["chain"], "shots": D["shots"],
           "circuit_dt": D.get("circuit_dt"), "qpu_usage": D.get("qpu_usage"), "views": {}}
    for v in VIEWS:
        out["views"][v] = stats(items, v, rng)
    V = out["views"]

    nv, nv_sd = V["naive"]["bond"], V["naive"]["bond_sd"]
    ceil = max(V["ceiling_gate"]["bond"], 1e-9)
    one = V["one_hop"]["bond"]
    out["replicates_p19"] = {"naive_bond": nv, "p19_value": 0.0621,
                             "within_3sd": abs(nv - 0.0621) <= 3 * math.hypot(nv_sd, 0.0109),
                             "below_0p15": nv < 0.15}
    out["over_naive_sd"] = {f: round((V[f]["bond"] - nv) / math.hypot(V[f]["bond_sd"], nv_sd), 1)
                            for f in FIXES}
    out["of_ceiling"] = {k: round(V[k]["bond"] / ceil, 3)
                         for k in ["one_hop", "naive"] + FIXES}
    best = max(FIXES, key=lambda f: V[f]["bond"])
    out["best_fix"] = best
    out["multiplicative_target"] = round((one / ceil) ** 2, 3)
    parked_gain = V["parked"]["bond"] - nv
    parallel_gain = V["parallel"]["bond"] - nv
    out["mechanism"] = {
        "parked_gain": round(parked_gain, 4), "parallel_gain": round(parallel_gain, 4),
        "verdict": ("neighbours" if parked_gain > parallel_gain + 2 * nv_sd else
                    "time" if parallel_gain > parked_gain + 2 * nv_sd else "not separated"),
    }
    out["verdict"] = {
        "p19_replicated": out["replicates_p19"]["within_3sd"] and out["replicates_p19"]["below_0p15"],
        "a_fix_works": max(out["over_naive_sd"].values()) >= 5 and V[best]["bond"] >= 0.25,
        "entanglement_recovered": (V[best]["fidelity"] > 0.5
                                   and (V[best]["fidelity"] - 0.5) / V[best]["fidelity_sd"] >= 3),
        "diagnosis_stands": (out["mechanism"]["verdict"] == "neighbours"
                             and max(out["over_naive_sd"].values()) >= 5),
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("views", "replicates_p19", "over_naive_sd", "of_ceiling",
                                          "best_fix", "multiplicative_target", "mechanism",
                                          "verdict")}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
