#!/usr/bin/env python3
"""
P-21 — Does the centre compose? Asked of two chips under one seal.

P-19 ran the two-hop chain on ibm_fez and got 0.062 — a collapse — and a mechanism was published
to explain it. P-20 ran the SAME schedule on the SAME chain shape on ibm_kingston and got 0.577.
The mechanism was retracted. The circuits were identical and the failing one was the shorter, so
neither barriers nor idle time could account for the gap. What differed was the chip.

That left the real question unsealed. P-20's two-hop number is a clean observation, but it came
from a run whose own H0 failed, so it cannot be claimed. This run seals it properly — and asks it
of two chips at once, because the lesson we paid for twice is that A SINGLE-CHIP NULL IS NOT A NULL,
and a single-chip PASS is worth no more.

    Three Bell pairs on a line:  a=b   c=d   e=f
    Read the centre of b and c.  Read the centre of d and e.
    Do a and f — which never touched, were never linked, and were never read together — end bonded?

Three arms, scored the same way on each chip:

    none    no reading   -> ceiling on a,b  and a floor on a,f
    first   one reading  -> one hop on a,d
    both    two readings -> TWO HOPS on a,f

Composition is claimed only if it holds on BOTH chips independently. Both jobs are submitted before
either result is fetched, so nothing can be tuned between them.

  python3 cross_chip.py submit <backend> | fetch <backend> | analyze <backend> | combine | sim
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)

#            a  b  ANC1  c  d  ANC2  e  f
A, B, ANC1, C, D, ANC2, E, F = 0, 1, 2, 3, 4, 5, 6, 7
NQ = 8
LIVE = [A, B, C, D, E, F]
CB = {q: i for i, q in enumerate(LIVE)}
Z1, X1, Z2, X2 = 6, 7, 8, 9
NC = 10

PAIRS = [(A, B), (C, D), (E, F)]
THETAS = 8
SHOTS = 3072
ARMS = ["none", "first", "both"]
CHIPS = ["ibm_kingston", "ibm_fez"]


def pend(bk): return RES / ("cross_%s_pending.json" % bk)
def cnts(bk): return RES / ("cross_%s_counts.json" % bk)
def outf(bk): return RES / ("cross_%s.json" % bk)


def prep(qc):
    for u, v in PAIRS:
        qc.h(u); qc.cx(u, v)


def reading(qc, pair, anc, zbit, xbit):
    """A complete joint reading of two centres onto a shared thing: Z parity, reset, X parity.
    Neither centre is ever learned on its own."""
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
            if arm in ("first", "both"):
                reading(qc, (B, C), ANC1, Z1, X1)
            if arm == "both":
                qc.barrier(range(NQ))
                reading(qc, (D, E), ANC2, Z2, X2)
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


def calibration(backend, chain):
    """Recorded at submission, so that if the two chips disagree the reason is on file."""
    t = backend.target
    ro = {q[0]: p.error for q, p in t["measure"].items() if p and p.error is not None}
    snap = {}
    for q in chain:
        row = {"readout_err": round(ro.get(q, float("nan")), 5)}
        try:
            row["T1_us"] = round(backend.qubit_properties(q).t1 * 1e6, 1)
            row["T2_us"] = round(backend.qubit_properties(q).t2 * 1e6, 1)
        except Exception:
            pass
        snap[str(q)] = row
    return snap


def submit(bk_name):
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    svc = QiskitRuntimeService()
    backend = svc.backend(bk_name)
    chain, two = best_line(backend, NQ)
    circs, meta = build()
    tcs = [transpile(c, backend, initial_layout=chain, optimization_level=1, seed_transpiler=7)
           for c in circs]
    dur = None
    try:
        sc = transpile(circs[-1], backend, initial_layout=chain, optimization_level=1,
                       seed_transpiler=7, scheduling_method="alap")
        dur = round(sc.duration * backend.dt * 1e6, 2)
    except Exception:
        pass
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    pend(bk_name).write_text(json.dumps(
        {"backend": bk_name, "chain": chain, "job_id": job.job_id(), "meta": meta,
         "shots": SHOTS, "calibration": calibration(backend, chain),
         "two_hop_duration_us": dur,
         "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", bk_name, len(tcs), "circuits x", SHOTS,
          "| two-hop schedule", dur, "us")


def fetch(bk_name):
    from qiskit_ibm_runtime import QiskitRuntimeService
    P = json.loads(pend(bk_name).read_text())
    job = QiskitRuntimeService().job(P["job_id"])
    print(bk_name, "status", job.status())
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
    cnts(bk_name).write_text(json.dumps(
        {**{k: P[k] for k in ("backend", "chain", "job_id", "shots", "calibration",
                              "two_hop_duration_us", "submitted_utc")},
         "qpu_usage": usage, "items": items}, indent=1))
    print("saved", cnts(bk_name), usage)


def simulate():
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    sim = AerSimulator()
    circs, meta = build()
    tcs = transpile(circs, sim, optimization_level=1)
    res = sim.run(tcs, shots=SHOTS, seed_simulator=7).result()
    items = [{**m, "counts": res.get_counts(i)} for i, m in enumerate(meta)]
    cnts("aer").write_text(json.dumps({"backend": "aer", "chain": list(range(NQ)), "job_id": "sim",
                                       "shots": SHOTS, "calibration": None,
                                       "two_hop_duration_us": None, "submitted_utc": "sim",
                                       "qpu_usage": None, "items": items}, indent=1))
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


VIEWS = {
    "ceiling_gate":    ("none",  (A, B), None,        ()),
    "floor_none":      ("none",  (A, F), None,        ()),
    "one_hop":         ("first", (A, D), (Z1,),       (X1,)),
    "floor_one_short": ("first", (A, F), (Z1,),       (X1,)),
    "two_hops":        ("both",  (A, F), (Z1, Z2),    (X1, X2)),
}


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


def analyze(bk_name):
    D = json.loads(cnts(bk_name).read_text())
    items = D["items"]
    rng = np.random.default_rng(20260918)
    out = {"backend": D["backend"], "chain": D["chain"], "shots": D["shots"],
           "calibration": D.get("calibration"), "two_hop_duration_us": D.get("two_hop_duration_us"),
           "qpu_usage": D.get("qpu_usage"), "views": {}}
    for v in VIEWS:
        out["views"][v] = stats(items, v, rng)
    V = out["views"]
    floor = (V["floor_none"]["bond"] + V["floor_one_short"]["bond"]) / 2
    floor_sd = math.hypot(V["floor_none"]["bond_sd"], V["floor_one_short"]["bond_sd"]) / 2
    two, two_sd = V["two_hops"]["bond"], V["two_hops"]["bond_sd"]
    ceil = max(V["ceiling_gate"]["bond"], 1e-9)
    one = V["one_hop"]["bond"]
    out["floor"] = {"value": round(floor, 4), "sd": round(floor_sd, 4)}
    out["two_over_floor_sd"] = round((two - floor) / math.hypot(two_sd, floor_sd), 1)
    out["two_fidelity_over_half_sd"] = round(
        (V["two_hops"]["fidelity"] - 0.5) / V["two_hops"]["fidelity_sd"], 1)
    out["of_ceiling"] = {"one_hop": round(one / ceil, 3), "two_hops": round(two / ceil, 3)}
    out["multiplicative"] = {"target": round((one / ceil) ** 2, 3),
                             "observed": round(two / ceil, 3),
                             "gap": round(abs((one / ceil) ** 2 - two / ceil), 3)}
    out["p19_collapse_reproduced"] = two < 0.15
    out["clearly_works"] = two > 0.40
    out["verdict"] = {
        "composes_here": out["two_over_floor_sd"] >= 5,
        "entangled_here": (V["two_hops"]["fidelity"] > 0.5
                           and out["two_fidelity_over_half_sd"] >= 3),
        "multiplicative_here": out["multiplicative"]["gap"] <= 0.10,
    }
    outf(bk_name).write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("views", "floor", "two_over_floor_sd",
                                          "two_fidelity_over_half_sd", "of_ceiling",
                                          "multiplicative", "p19_collapse_reproduced",
                                          "clearly_works", "verdict")}, indent=1))


def combine():
    got = {}
    for c in CHIPS:
        if outf(c).exists():
            got[c] = json.loads(outf(c).read_text())
    res = {"chips": {}, "n_chips": len(got)}
    for c, d in got.items():
        res["chips"][c] = {
            "two_hop_bond": d["views"]["two_hops"]["bond"],
            "two_hop_bond_sd": d["views"]["two_hops"]["bond_sd"],
            "two_hop_fidelity": d["views"]["two_hops"]["fidelity"],
            "two_hop_fidelity_sd": d["views"]["two_hops"]["fidelity_sd"],
            "of_ceiling": d["of_ceiling"], "multiplicative": d["multiplicative"],
            "two_over_floor_sd": d["two_over_floor_sd"],
            "two_fidelity_over_half_sd": d["two_fidelity_over_half_sd"],
            "schedule_us": d.get("two_hop_duration_us"),
            "qpu_usage": d.get("qpu_usage"), "verdict": d["verdict"],
            "p19_collapse_reproduced": d["p19_collapse_reproduced"],
        }
    v = [d["verdict"] for d in res["chips"].values()]
    res["verdict"] = {
        "composes_on_every_chip": bool(v) and all(x["composes_here"] for x in v),
        "entangled_on_every_chip": bool(v) and all(x["entangled_here"] for x in v),
        "multiplicative_on_every_chip": bool(v) and all(x["multiplicative_here"] for x in v),
        "fez_reproduced_p19_collapse": res["chips"].get("ibm_fez", {}).get("p19_collapse_reproduced"),
    }
    (RES / "cross_chip_combined.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    a = sys.argv[1:] or [""]
    if a[0] == "sim":
        simulate()
    elif a[0] == "combine":
        combine()
    elif a[0] in ("submit", "fetch", "analyze") and len(a) > 1:
        {"submit": submit, "fetch": fetch, "analyze": analyze}[a[0]](a[1])
    else:
        print(__doc__)
