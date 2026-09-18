#!/usr/bin/env python3
"""
P-10 — One fire, many levels.

Free's reading: the fire is one, on an unbounded number of levels. So the question is not what
two fires do to each other; it is what happens to the six around ONE fire as that fire is read at
more levels.

The state: a centre of k qubits (d = 2^k levels) in equal superposition, each level writing its
own pattern onto the same six rim qubits —

    |Psi_d> = (1/sqrt d) SUM_c |c>_centre (x) |M c>_rim

so every level of the fire names a different world for the six, and the six hold all of those
worlds at once.

Two readings of the same state:
  Z        the fire read as levels      — the six should fall into one world, sorted, no bond left
  Fourier  the fire read across levels  — the six should keep the bond, all worlds at once

Two quantities:
  sorting   I(centre outcome ; rim pattern), in bits — how many worlds the fire can tell apart
  bond      the rim's own coherence, from a phase sweep, conditioned on the fire's outcome

  python3 one_fire_levels.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "one_fire_pending.json"
COUNTS = RES / "one_fire_counts.json"
OUT = RES / "one_fire.json"

RIM = 6
KS = [1, 2, 3]                 # centre qubits -> 2, 4 and 8 levels
THETAS = 8                     # phase points in the rim sweep
SHOTS = 2048

# each centre qubit writes one pattern across the six; the patterns are independent
MASKS = [
    [1, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 1, 0, 1, 0, 1],
]


def n_qubits(k):
    return k + RIM


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []
    for k in KS:
        n = n_qubits(k)
        centre = list(range(k))
        rim = list(range(k, n))

        def prep(qc):
            for c in centre:
                qc.h(c)
            for j, c in enumerate(centre):
                for i, bit in enumerate(MASKS[j]):
                    if bit:
                        qc.cx(c, rim[i])

        # ---- sorting: fire read as levels, six read as patterns
        qc = QuantumCircuit(n, n)
        prep(qc)
        qc.measure(range(n), range(n))
        circs.append(qc); meta.append({"k": k, "kind": "sort"})

        # ---- bond: the rim swept in phase, under each reading of the fire
        for reading in ("Z", "F"):
            for t in range(THETAS):
                theta = 2 * math.pi * t / THETAS
                qc = QuantumCircuit(n, n)
                prep(qc)
                if reading == "F":
                    for c in centre:
                        qc.h(c)
                for r in rim:
                    qc.rz(theta, r)
                    qc.h(r)
                qc.measure(range(n), range(n))
                circs.append(qc)
                meta.append({"k": k, "kind": "bond", "reading": reading, "t": t})
    return circs, meta


# ------------------------------------------------------------------ layout
def best_line(backend, length):
    t = backend.target
    two = next(x for x in ("cz", "ecr", "cx") if x in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else .05) for q, p in t["measure"].items()}
    adj = {}
    for (a, b), e in err2.items():
        if e < .05:
            adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    def ee(a, b): return min(err2.get((a, b), 1.), err2.get((b, a), 1.))
    beam = [([q], math.log(1 - ro.get(q, .05))) for q in adj]
    for _ in range(length - 1):
        nxt = []
        for path, sc in beam:
            for nb in adj.get(path[-1], ()):
                if nb in path: continue
                nxt.append((path + [nb], sc + math.log(1 - ee(path[-1], nb)) + math.log(1 - ro.get(nb, .05))))
        nxt.sort(key=lambda x: -x[1]); beam = nxt[:400]
    beam.sort(key=lambda x: -x[1])
    return beam[0][0], two


def submit():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    svc = QiskitRuntimeService()
    backend = svc.least_busy(operational=True, simulator=False, min_num_qubits=n_qubits(max(KS)) + 4)
    chain, two = best_line(backend, n_qubits(max(KS)))
    circs, meta = build()
    tcs = []
    for c, m in zip(circs, meta):
        layout = chain[:c.num_qubits]
        tc = transpile(c, backend, initial_layout=layout, optimization_level=3, seed_transpiler=7)
        m["twoq"] = sum(1 for i in tc.data if i.operation.num_qubits == 2)
        tcs.append(tc)
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"backend": backend.name, "chain": chain, "job_id": job.job_id(),
                                   "meta": meta, "shots": SHOTS,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, len(tcs), "circuits")
    for k in KS:
        print("  k =", k, "two-qubit gates:", sorted(set(m["twoq"] for m in meta if m["k"] == k)))


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
    res = sim.run(tcs, shots=8192, seed_simulator=7).result()
    items = [{**m, "twoq": 0, "counts": res.get_counts(i)} for i, m in enumerate(meta)]
    COUNTS.write_text(json.dumps({"backend": "aer", "chain": list(range(9)), "job_id": "sim",
                                  "shots": 8192, "qpu_usage": None, "timestamp_utc": "sim",
                                  "items": items}, indent=1))
    print("simulated", len(circs), "circuits")


# ------------------------------------------------------------------ analyze
def split(key, k):
    """qiskit bitstrings: clbit 0 is rightmost. Returns (centre bits, rim bits) as tuples."""
    b = key.replace(" ", "")
    bits = [int(b[len(b) - 1 - i]) for i in range(len(b))]
    return tuple(bits[:k]), tuple(bits[k:k + RIM])


def mutual_information(counts, k):
    tot = sum(counts.values())
    pj, pc, pr = {}, {}, {}
    for key, v in counts.items():
        c, r = split(key, k)
        pj[(c, r)] = pj.get((c, r), 0) + v
        pc[c] = pc.get(c, 0) + v
        pr[r] = pr.get(r, 0) + v
    I = 0.0
    for (c, r), v in pj.items():
        p = v / tot
        I += p * math.log2(p / ((pc[c] / tot) * (pr[r] / tot)))
    return I


def rim_parity(counts, k, centre_outcome=None):
    tot, s = 0, 0.0
    for key, v in counts.items():
        c, r = split(key, k)
        if centre_outcome is not None and c != centre_outcome:
            continue
        sign = 1
        for bit in r:
            sign *= (1 - 2 * bit)
        s += sign * v; tot += v
    return (s / tot if tot else 0.0), tot


def bond_spectrum(items_for, k, reading):
    """Sweep the rim's phase and take the spectrum of its parity, per fire outcome."""
    by_t = {}
    for it in items_for:
        if it["kind"] == "bond" and it["reading"] == reading:
            by_t[it["t"]] = it["counts"]
    outcomes = sorted({split(key, k)[0] for c in by_t.values() for key in c})
    per_outcome = {}
    for oc in outcomes:
        series, weight = [], 0
        for t in range(THETAS):
            p, w = rim_parity(by_t[t], k, oc)
            series.append(p); weight = max(weight, w)
        sp = np.abs(np.fft.rfft(np.array(series))) / THETAS
        per_outcome["".join(map(str, oc))] = {"series": [round(x, 4) for x in series],
                                              "spectrum": [round(float(x), 4) for x in sp],
                                              "bond": round(float(np.sum(sp[1:])), 4),
                                              "shots": int(weight)}
    total = float(np.mean([v["bond"] for v in per_outcome.values()])) if per_outcome else 0.0
    return {"per_outcome": per_outcome, "mean_bond": round(total, 4)}


def analyze():
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    out = {"backend": D["backend"], "job_id": D["job_id"], "shots": D["shots"],
           "qpu_usage": D.get("qpu_usage"), "by_levels": {}}
    for k in KS:
        sub = [it for it in items if it["k"] == k]
        srt = next(it for it in sub if it["kind"] == "sort")
        levels = 2 ** k
        I = mutual_information(srt["counts"], k)
        fourier = bond_spectrum(sub, k, "F")
        zread = bond_spectrum(sub, k, "Z")
        out["by_levels"][str(levels)] = {
            "centre_qubits": k,
            "sorting_bits": round(I, 4),
            "sorting_ideal_bits": round(math.log2(levels), 4),
            "sorting_fraction": round(I / math.log2(levels), 4),
            "bond_fire_read_across_levels": fourier["mean_bond"],
            "bond_fire_read_as_levels": zread["mean_bond"],
            "ratio": round(fourier["mean_bond"] / max(zread["mean_bond"], 1e-6), 2),
            "two_qubit_gates": sorted(set(it.get("twoq", 0) for it in sub)),
            "detail_fourier": fourier["per_outcome"],
        }
    ok = all(v["bond_fire_read_across_levels"] > 2 * v["bond_fire_read_as_levels"]
             for v in out["by_levels"].values())
    grows = all(out["by_levels"][str(2 ** k)]["sorting_bits"] >
                out["by_levels"][str(2 ** (k - 1))]["sorting_bits"] for k in KS[1:])
    out["verdict"] = {
        "bond_survives_every_level_count": bool(ok),
        "sorting_grows_with_levels": bool(grows),
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({"by_levels": {k: {kk: v[kk] for kk in
                                        ("sorting_bits", "sorting_ideal_bits",
                                         "bond_fire_read_across_levels", "bond_fire_read_as_levels",
                                         "ratio", "two_qubit_gates")}
                                    for k, v in out["by_levels"].items()},
                      "verdict": out["verdict"]}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
