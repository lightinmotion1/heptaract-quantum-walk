#!/usr/bin/env python3
"""
P-19 — Does the centre compose?

P-18 settled that reading the centre of both MAKES a bond between two things that never touched.
This asks whether that act stacks — whether the shared centre is a structure and not only an event.

    Three ships in a row, six qubits, three relationships:  a=b   c=d   e=f

    Read the centre of b and c.  Now a and d are bonded, though they never touched.
    Read the centre of d and e.  Now a and f are bonded — and a and f were never touched,
                                 never linked, and never even read together.

If the bond reaches all the way, the centre of both is associative: it composes, and one fire on
one level is the same act as one fire on the next. If the bond dies at the first hop, the centre
is an event and not a structure, and the tree has to say so.

This is a two-hop entanglement-swapping chain — the bones of a quantum repeater, and thirty years
old. Nothing here is new physics. What is being measured is the COST PER HOP, which is the number
that decides whether the structure is worth anything.

One circuit family, three arms, and the phase sweep applied to every live qubit — so the ceiling,
the one-hop bond, the two-hop bond and two matched floors all come out of the same shots:

    NONE    no reading taken      -> score a,b : the CEILING, a bond made directly by a gate
                                  -> score a,f : a floor
    FIRST   one reading taken     -> score a,d : ONE HOP
                                  -> score a,f : the floor that matters, structurally identical
                                     to the signal and one reading short of it
    BOTH    both readings taken   -> score a,f : TWO HOPS

  python3 chain_centre.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "chain_centre_pending.json"
COUNTS = RES / "chain_centre_counts.json"
OUT = RES / "chain_centre.json"

#            a  b  ANC1  c  d  ANC2  e  f
A, B, ANC1, C, D, ANC2, E, F = 0, 1, 2, 3, 4, 5, 6, 7
NQ = 8
LIVE = [A, B, C, D, E, F]
CB = {q: i for i, q in enumerate(LIVE)}          # qubit -> classical bit
Z1, X1, Z2, X2 = 6, 7, 8, 9
NC = 10

PAIRS = [(A, B), (C, D), (E, F)]
THETAS = 8
SHOTS = 4096
ARMS = ["none", "first", "both"]


def prep(qc):
    for u, v in PAIRS:
        qc.h(u); qc.cx(u, v)


def reading(qc, pair, anc, zbit, xbit):
    """A complete joint reading of two centres onto a shared thing: Z parity, reset, X parity.
    Neither centre is ever learned on its own."""
    qc.barrier(range(NQ))
    for q in pair:
        qc.cx(q, anc)
    qc.measure(anc, zbit)
    qc.reset(anc)
    qc.barrier(range(NQ))
    for q in pair:
        qc.h(q)
    for q in pair:
        qc.cx(q, anc)
    qc.measure(anc, xbit)
    qc.barrier(range(NQ))


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
    # two rounds of mid-circuit measurement and reset make coherence matter as much as readout
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
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"backend": backend.name, "chain": chain, "job_id": job.job_id(),
                                   "meta": meta, "shots": SHOTS, "coherence": props,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, len(tcs), "circuits x", SHOTS)


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
                                  "shots": P["shots"], "coherence": P.get("coherence"), "qpu_usage": usage,
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


def sel(counts, zsum, xbits, xsum):
    """Keep shots whose reading outcomes sum (mod 2) to the named branch. Two readings compose by
    Pauli frame: the pair ends in the Bell state indexed by the XOR of the two outcomes."""
    out = {}
    for k, v in counts.items():
        b = bits(k)
        if zsum is not None:
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
    """Only the known frequency bin is read. Summing every bin adds the magnitude of the noise in
    each one, which inflates the signal and the floor together."""
    sp = np.abs(np.fft.rfft(np.array(series))) / len(series)
    return 2.0 * float(sp[2])


def score_one(popc, parc, pair, zsum, xbits):
    cohs, sames, ns = [], [], []
    branches = [0, 1] if xbits else [0]
    for xs in branches:
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


# name -> (arm, pair, z bits to XOR, x bits to XOR)
VIEWS = {
    "ceiling_gate":  ("none",  (A, B), None,       ()),
    "floor_none":    ("none",  (A, F), None,       ()),
    "one_hop":       ("first", (A, D), (Z1,),      (X1,)),
    "floor_one_short": ("first", (A, F), (Z1,),    (X1,)),
    "two_hops":      ("both",  (A, F), (Z1, Z2),   (X1, X2)),
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


def analyze():
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    rng = np.random.default_rng(20260918)
    out = {"backend": D["backend"], "chain": D["chain"], "shots": D["shots"],
           "qpu_usage": D.get("qpu_usage"), "views": {}}
    for v in VIEWS:
        out["views"][v] = stats(items, v, rng)
    V = out["views"]
    floor = (V["floor_none"]["bond"] + V["floor_one_short"]["bond"]) / 2
    floor_sd = math.hypot(V["floor_none"]["bond_sd"], V["floor_one_short"]["bond_sd"]) / 2
    out["floor"] = {"value": round(floor, 4), "sd": round(floor_sd, 4)}
    two, two_sd = V["two_hops"]["bond"], V["two_hops"]["bond_sd"]
    one, one_sd = V["one_hop"]["bond"], V["one_hop"]["bond_sd"]
    ceil = V["ceiling_gate"]["bond"]
    out["two_hops_over_floor_sd"] = round((two - floor) / math.hypot(two_sd, floor_sd), 1)
    out["two_hops_fidelity_over_half_sd"] = round(
        (V["two_hops"]["fidelity"] - 0.5) / V["two_hops"]["fidelity_sd"], 1)
    out["cost_per_hop"] = {
        "hop1_of_ceiling": round(one / max(ceil, 1e-9), 3),
        "hop2_of_hop1": round(two / max(one, 1e-9), 3),
        "hop2_of_ceiling": round(two / max(ceil, 1e-9), 3),
        "multiplicative": round(abs((one / max(ceil, 1e-9)) ** 2 - two / max(ceil, 1e-9)), 3),
    }
    out["verdict"] = {
        "centre_composes": out["two_hops_over_floor_sd"] >= 5,
        "second_hop_still_entangled": (out["two_hops_fidelity_over_half_sd"] >= 3
                                       and V["two_hops"]["fidelity"] > 0.5),
        "floors_agree_within_2sd": abs(V["floor_none"]["bond"] - V["floor_one_short"]["bond"]) <= 2 * floor_sd * 2,
        "cost_is_multiplicative_within_0p1": out["cost_per_hop"]["multiplicative"] <= 0.10,
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("views", "floor", "two_hops_over_floor_sd",
                                          "two_hops_fidelity_over_half_sd", "cost_per_hop",
                                          "verdict")}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
