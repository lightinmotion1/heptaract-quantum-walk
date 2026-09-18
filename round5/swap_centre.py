#!/usr/bin/env python3
"""
P-18 — Can reading the centre of both make them one?

The P-17 control turned up a state of affairs that deserves its own measurement. Two ships are
built that never touch: each a centre with its own rim qubit, no gate between them, ever. Then the
shared reading is taken — onto a third thing that belongs to neither ship, so neither ship's own
centre is ever learned, only what the two hold in common.

    Do the two rims, which have never interacted, end up bonded?

This is textbook entanglement swapping and has been known since the nineteen-nineties. Nothing here
is new physics. What is being tested is the framework's claim in the framework's own terms: that the
centre of both is not merely a description of an existing relationship but a way of making one.

A HALF reading is not enough, and the simulator said so before any hardware time was spent. Reading
only ONE parity of the two centres leaves the rims in an even mixture of two Bell states — correlated,
but separable. A bond metric alone would have called that a bond. So the shared reading here is
COMPLETE: the Z parity of the two centres is read onto the shared ancilla, the ancilla is reset, and
the X parity is read onto the same ancilla. Two readings, one shared thing, neither ship touched by
the other. Only then can a fidelity above one half be quoted, and above one half is the witness.

Four arms:

    SWAP      the complete shared reading, then the rims scored
    PRIVATE   one ship's own centre read twice instead — Z then X — the rims scored the same way
    NONE      the shared thing read twice with nothing connected to it; the rims scored the same way
    LINKED    the P-11 state, ships joined by a gate, complete shared reading — for scale

Each arm carries a phase sweep (for the coherence) and a population circuit (for the Z correlation),
and both are conditioned on the same branch of the shared reading.

  python3 swap_centre.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "swap_centre_pending.json"
COUNTS = RES / "swap_centre_counts.json"
OUT = RES / "swap_centre.json"

RIM_A, C1, ANC, C2, RIM_B = 0, 1, 2, 3, 4
RIM = [RIM_A, RIM_B]
NQ = 5

B_A, B_B, B_Z, B_X = 0, 1, 2, 3          # classical bits
NC = 4

THETAS = 8
SHOTS = 4096
ARMS = ["swap", "private", "none", "linked"]


def prep(qc, link=False):
    qc.h(C1); qc.cx(C1, RIM_A)
    qc.h(C2); qc.cx(C2, RIM_B)
    if link:
        qc.cz(C1, C2)


def reading(qc, arm):
    """Two readings onto the one shared ancilla, Z parity first then X parity."""
    if arm in ("swap", "linked"):
        src = [C1, C2]
    elif arm == "private":
        src = [C1]
    else:
        src = []
    qc.barrier(range(NQ))
    for q in src:                         # Z parity
        qc.cx(q, ANC)
    qc.measure(ANC, B_Z)
    qc.reset(ANC)
    qc.barrier(range(NQ))
    for q in src:                         # X parity
        qc.h(q)
    for q in src:
        qc.cx(q, ANC)
    qc.measure(ANC, B_X)
    qc.barrier(range(NQ))


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []
    for arm in ARMS:
        for kind in ["pop"] + ["par%d" % t for t in range(THETAS)]:
            qc = QuantumCircuit(NQ, NC)
            prep(qc, link=(arm == "linked"))
            reading(qc, arm)
            if kind != "pop":
                theta = 2 * math.pi * int(kind[3:]) / THETAS
                for r in RIM:
                    qc.rz(theta, r); qc.h(r)
            qc.measure(RIM_A, B_A); qc.measure(RIM_B, B_B)
            circs.append(qc)
            meta.append({"arm": arm, "kind": kind})
    return circs, meta


def best_line(backend, length=NQ):
    t = backend.target
    two = next(x for x in ("cz", "ecr", "cx") if x in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else .05) for q, p in t["measure"].items()}
    adj = {}
    for (a, b), e in err2.items():
        if e < .04:
            adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    def ee(a, b): return min(err2.get((a, b), 1.), err2.get((b, a), 1.))
    def score(q): return math.log(1 - ro.get(q, .05))
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


def sel(counts, z, x):
    out = {}
    for k, v in counts.items():
        b = bits(k)
        if b[B_Z] == z and b[B_X] == x:
            out[k] = out.get(k, 0) + v
    return out


def zz(counts):
    tot, s = 0, 0.0
    for k, v in counts.items():
        b = bits(k)
        s += (1 - 2 * b[B_A]) * (1 - 2 * b[B_B]) * v
        tot += v
    return (s / tot if tot else 0.0), tot


def amplitude(series):
    """The oscillation sits at a known frequency — two cycles across the sweep — so only that
    bin is read. Summing every bin adds the magnitude of the noise in each one, which inflates
    the signal AND the floor; on a noiseless simulator that bias showed up as a fidelity of 1.06
    for a state whose true fidelity is 1."""
    sp = np.abs(np.fft.rfft(np.array(series))) / len(series)
    return 2.0 * float(sp[2])                   # 1.0 for a perfect Bell state


def one(popc, parc):
    """Conditioned on the Z-parity branch 0; the two X branches averaged by magnitude."""
    cohs, sames, ns = [], [], []
    for x in (0, 1):
        series = [zz(sel(parc[t], 0, x))[0] for t in range(THETAS)]
        cohs.append(amplitude(series))
        v, n = zz(sel(popc, 0, x))
        sames.append(abs(v)); ns.append(n)
    coh = float(np.mean(cohs))
    same = float(np.mean(sames))
    return coh, same, (1.0 + same + 2.0 * coh) / 4.0, int(np.sum(ns))


def resample(counts, rng):
    keys = list(counts)
    p = np.array([counts[k] for k in keys], float)
    n = int(p.sum())
    draw = rng.multinomial(n, p / n)
    return {k: int(c) for k, c in zip(keys, draw) if c}


def stats(items, arm, rng, B=300):
    pop_c = next(it["counts"] for it in items if it["arm"] == arm and it["kind"] == "pop")
    par_c = {int(it["kind"][3:]): it["counts"] for it in items
             if it["arm"] == arm and it["kind"].startswith("par")}
    coh, same, fid, n = one(pop_c, par_c)
    boots = [one(resample(pop_c, rng), {t: resample(c, rng) for t, c in par_c.items()})[:3]
             for _ in range(B)]
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
           "qpu_usage": D.get("qpu_usage"), "arms": {}}
    for arm in ARMS:
        out["arms"][arm] = stats(items, arm, rng)
    a = out["arms"]
    floor = (a["private"]["bond"] + a["none"]["bond"]) / 2
    floor_sd = math.hypot(a["private"]["bond_sd"], a["none"]["bond_sd"]) / 2
    out["floor"] = {"value": round(floor, 4), "sd": round(floor_sd, 4)}
    out["swap_over_floor_sd"] = round((a["swap"]["bond"] - floor) / math.hypot(a["swap"]["bond_sd"], floor_sd), 1)
    out["swap_fidelity_over_half_sd"] = round((a["swap"]["fidelity"] - 0.5) / a["swap"]["fidelity_sd"], 1)
    out["verdict"] = {
        "reading_creates_a_bond": out["swap_over_floor_sd"] >= 5,
        "entanglement_witnessed": out["swap_fidelity_over_half_sd"] >= 3 and a["swap"]["fidelity"] > 0.5,
        "no_reading_no_bond": abs(a["none"]["bond"] - floor) <= 2 * floor_sd,
        "swap_vs_linked_ratio": round(a["swap"]["bond"] / max(a["linked"]["bond"], 1e-9), 2),
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("arms", "floor", "swap_over_floor_sd",
                                          "swap_fidelity_over_half_sd", "verdict")}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
