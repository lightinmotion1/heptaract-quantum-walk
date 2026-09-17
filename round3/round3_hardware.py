#!/usr/bin/env python3
"""
HEPTARACT round 3, IBM hardware.  Seven as a rest and as a building block.

  P-4  The fire read at seven angles.  A GHZ-7 grown from the center; the center is read
       along the axis  n = sin(phi) X + cos(phi) Z  for phi = 0, 15, 30, 45, 60, 75, 90 degrees;
       the six around it are scored by parity oscillation, conditioned on the center's outcome.
       Ideal theory: C6(phi) = A sin(phi).  Rivals: a straight ramp, and a step at 45 degrees.

  P-5  Blocks fused into a whole.  Two GHZ blocks are prepared side by side, then fused with one
       CX and a measurement of the joining qubit (the branch is conditioned in post-processing,
       so no feed-forward is needed).  Cuts 7+7, 6+8, 5+9 all leave a 13-qubit whole and use the
       same number of two-qubit gates; the shorter block is padded with idle time so every cut
       has the same duration.  A monolithic GHZ-13 is built as a control.
       Prediction: the 7+7 cut carries the largest 13-body coherence.

  python3 round3_hardware.py sim       Aer check, no QPU
  python3 round3_hardware.py submit    one job on the least busy QPU
  python3 round3_hardware.py fetch     counts + reported QPU seconds
  python3 round3_hardware.py analyze   results/round3_hardware.json
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "round3_hardware_pending.json"
COUNTS = RES / "round3_hardware_counts.json"
OUT = RES / "round3_hardware.json"

SHOTS = 4096
ANGLES = [0, 15, 30, 45, 60, 75, 90]        # degrees from Z toward X
CUTS = [(7, 7), (6, 8), (5, 9)]
NTOT = 14                                    # qubits used by P-5 before fusion
NWHOLE = NTOT - 1                            # 13 remain after the joining qubit is measured


# ------------------------------------------------------------------ circuits
def ghz_center_out(qc, qs, c):
    qc.h(qs[c])
    for i in range(c, 0, -1):
        qc.cx(qs[i], qs[i - 1])
    for i in range(c, len(qs) - 1):
        qc.cx(qs[i], qs[i + 1])


def build(pad_dt=0):
    """Returns (circuits, meta).  pad_dt = duration of one two-qubit layer in dt units."""
    from qiskit import QuantumCircuit
    circs, meta = [], []

    # ---- P-4: seven angles of the fire
    rim = [0, 1, 2, 4, 5, 6]
    for a in ANGLES:
        phi = math.radians(a)
        for j in range(4):
            theta = 2 * math.pi * j / (4 * 6)
            qc = QuantumCircuit(NTOT, NTOT)
            ghz_center_out(qc, list(range(7)), 3)
            qc.ry(-phi, 3)                       # measures sin(phi) X + cos(phi) Z on the center
            for k in rim:
                qc.rz(theta, k)
                qc.h(k)
            qc.measure(range(7), range(7))
            circs.append(qc)
            meta.append({"kind": "fire7", "angle": a, "j": j})

    # ---- P-5: blocks fused into a whole
    def blocks(qc, k1, k2):
        """Block A = 0..k1-1 (seed at 0), block B = k1..13 (seed at k1). Both grow rightward."""
        qc.h(0)
        for i in range(0, k1 - 1):
            qc.cx(i, i + 1)
        qc.h(k1)
        for i in range(k1, k1 + k2 - 1):
            qc.cx(i, i + 1)
        # idle padding so every cut lasts as long as the slowest one
        if pad_dt:
            slow = max(max(c) for c in CUTS) - 1
            for side, (start, size) in enumerate(((0, k1), (k1, k2))):
                idle = (slow - (size - 1)) * pad_dt
                if idle > 0:
                    for q in range(start, start + size):
                        qc.delay(idle, q, unit="dt")

    def fuse_and_read(k1, k2, kind, j=None, pop=False):
        from qiskit import QuantumCircuit
        qc = QuantumCircuit(NTOT, NTOT)
        if kind == "mono":
            qc.h(0)
            for i in range(NTOT - 2):            # 13 qubits, 0..12
                qc.cx(i, i + 1)
            whole = list(range(NWHOLE))
            fuse_q = None
        else:
            blocks(qc, k1, k2)
            qc.cx(k1 - 1, k1)                    # the fuse
            qc.measure(k1, k1)                   # joining qubit is read out and leaves the whole
            whole = [q for q in range(NTOT) if q != k1]
            fuse_q = k1
        if not pop:
            theta = 2 * math.pi * j / (4 * NWHOLE)
            for q in whole:
                qc.rz(theta, q)
                qc.h(q)
        qc.measure(whole, whole)
        return qc, whole, fuse_q

    for (k1, k2) in CUTS + [("mono", "mono")]:
        kind = "mono" if k1 == "mono" else "cut"
        tag = "mono" if kind == "mono" else f"{k1}+{k2}"
        qc, whole, fq = fuse_and_read(k1, k2, kind, pop=True)
        circs.append(qc)
        meta.append({"kind": "blockpop", "cut": tag, "whole": whole, "fuse_q": fq})
        for j in range(4):
            qc, whole, fq = fuse_and_read(k1, k2, kind, j=j)
            circs.append(qc)
            meta.append({"kind": "blockpar", "cut": tag, "j": j, "whole": whole, "fuse_q": fq})
    return circs, meta


# ------------------------------------------------------------------ layout
def best_chain(backend, length):
    """Beam search for a good simple path of `length` physical qubits."""
    t = backend.target
    two = next(n for n in ("cz", "ecr", "cx") if n in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else 0.05) for q, p in t["measure"].items()}
    adj = {}
    for (a, b), e in err2.items():
        if e < 0.05:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)

    def edge_err(a, b):
        return min(err2.get((a, b), 1.0), err2.get((b, a), 1.0))

    beam = [([q], math.log(1 - ro.get(q, 0.05))) for q in adj]
    for _ in range(length - 1):
        nxt = []
        for path, score in beam:
            for nb in adj.get(path[-1], ()):
                if nb in path:
                    continue
                nxt.append((path + [nb],
                            score + math.log(1 - edge_err(path[-1], nb)) + math.log(1 - ro.get(nb, 0.05))))
        if not nxt:
            break
        nxt.sort(key=lambda x: -x[1])
        beam = nxt[:400]
    beam.sort(key=lambda x: -x[1])
    return beam[0][0], two


# ------------------------------------------------------------------ run
def submit():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=NTOT + 5)
    chain, two = best_chain(backend, NTOT)
    # one two-qubit layer, in dt, for the idle padding
    durs = [p.duration for q, p in backend.target[two].items() if p is not None and p.duration is not None]
    layer_s = float(np.median(durs)) if durs else 6.6e-7
    pad_dt = int(round(layer_s / backend.dt / 16) * 16)
    circs, meta = build(pad_dt=pad_dt)
    tcs = [transpile(c, backend, initial_layout=chain, optimization_level=1, seed_transpiler=7) for c in circs]
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"job_id": job.job_id(), "backend": backend.name, "chain": chain,
                                   "two_qubit_gate": two, "pad_dt": pad_dt, "meta": meta,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, "\nchain", chain, "\npad_dt", pad_dt,
          "\ncircuits", len(tcs), "shots", SHOTS)


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
            name = list(d.keys())[0]
            counts = d[name].get_counts()
        items.append({**m, "counts": counts})
    usage = None
    try:
        usage = job.metrics().get("usage", {})
    except Exception:
        pass
    COUNTS.write_text(json.dumps({"backend": P["backend"], "job_id": P["job_id"], "chain": P["chain"],
                                  "pad_dt": P["pad_dt"], "shots": SHOTS, "qpu_usage": usage,
                                  "timestamp_utc": P["submitted_utc"], "items": items}, indent=1))
    print("saved", COUNTS, "usage", usage)


def simulate():
    """Noiseless Aer run of the same circuits, to check the analysis recovers the ideal curve."""
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    sim = AerSimulator()
    circs, meta = build(pad_dt=0)
    tcs = transpile(circs, sim, optimization_level=1)
    res = sim.run(tcs, shots=8192, seed_simulator=7).result()
    items = [{**m, "counts": res.get_counts(i)} for i, m in enumerate(meta)]
    COUNTS.write_text(json.dumps({"backend": "aer", "job_id": "sim", "chain": list(range(NTOT)),
                                  "pad_dt": 0, "shots": 8192, "qpu_usage": None,
                                  "timestamp_utc": "sim", "items": items}, indent=1))
    print("simulated", len(circs), "circuits")


# ------------------------------------------------------------------ analyze
def bits(key, n):
    key = key.replace(" ", "")
    return [int(key[len(key) - 1 - i]) for i in range(n)]


def parity_exp(counts, nbits, idx, cond=None, flip=()):
    tot, s = 0, 0.0
    for k, v in counts.items():
        b = bits(k, nbits)
        if cond is not None and b[cond[0]] != cond[1]:
            continue
        sign = 1
        for i in idx:
            sign *= (1 - 2 * b[i])
        for i in flip:
            sign *= -1
        s += sign * v
        tot += v
    return (s / tot if tot else 0.0), tot


def resample(counts, rng):
    keys = list(counts)
    p = np.array([counts[k] for k in keys], float)
    N = int(p.sum())
    draw = rng.multinomial(N, p / N)
    return {k: int(c) for k, c in zip(keys, draw) if c}


def _fire_curve(index, rng=None):
    rim = [0, 1, 2, 4, 5, 6]
    out = {}
    for a in ANGLES:
        num, den = 0.0, 0
        for outcome in (0, 1):
            P, w = [], 0
            for j in range(4):
                c = index[("fire7", a, j)]
                p, tot = parity_exp(c, NTOT, rim, cond=(3, outcome))
                P.append(p)
                w = max(w, tot)
            C6 = math.hypot(P[0] - P[2], P[1] - P[3]) / 2
            num += C6 * w
            den += w
        out[a] = num / max(1, den)
    return out


def _block_coh(index, cut, meta_by_cut):
    """13-body coherence for one cut.

    The fused state comes in two branches. Branch 0 (joining qubit reads 0) is an ordinary
    GHZ-13; branch 1 carries an X on every qubit of block B, which shifts the parity
    oscillation to a different frequency. Only branch 0 is kept, by design, which is why the
    shot count per cut is about half the shots of the job.
    """
    whole = meta_by_cut[cut]["whole"]
    fq = meta_by_cut[cut]["fuse_q"]
    cond = None if fq is None else (fq, 0)

    popc = index[("blockpop", cut)]
    ok, tot = 0, 0
    for k, v in popc.items():
        b = bits(k, NTOT)
        if cond is not None and b[cond[0]] != cond[1]:
            continue
        tot += v
        vals = [b[q] for q in whole]
        if all(x == vals[0] for x in vals):
            ok += v
    population = ok / max(1, tot)

    Ps = []
    for j in range(4):
        p, _ = parity_exp(index[("blockpar", cut, j)], NTOT, whole, cond=cond)
        Ps.append(p)
    C = math.hypot(Ps[0] - Ps[2], Ps[1] - Ps[3]) / 2
    return C, population, Ps


def analyze(B=400):
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    index, meta_by_cut = {}, {}
    for it in items:
        if it["kind"] == "fire7":
            index[("fire7", it["angle"], it["j"])] = it["counts"]
        elif it["kind"] == "blockpop":
            index[("blockpop", it["cut"])] = it["counts"]
            meta_by_cut[it["cut"]] = {"whole": it["whole"], "fuse_q": it["fuse_q"]}
        elif it["kind"] == "blockpar":
            index[("blockpar", it["cut"], it["j"])] = it["counts"]

    rng = np.random.default_rng(20260918)

    # ---- P-4
    curve = _fire_curve(index)
    x = np.array([math.radians(a) for a in ANGLES])
    y = np.array([curve[a] for a in ANGLES])

    def sse(shape):
        s = np.array(shape, float)
        A = float(np.dot(s, y) / np.dot(s, s)) if np.dot(s, s) else 0.0
        return float(np.sum((y - A * s) ** 2)), A

    shapes = {"sin": np.sin(x),
              "ramp": x / (math.pi / 2),
              "step": np.array([0.0 if a < 45 else 1.0 for a in ANGLES])}
    fits = {k: sse(v) for k, v in shapes.items()}
    best = min(fits, key=lambda k: fits[k][0])
    boots = []
    for _ in range(B):
        idx = {k: resample(v, rng) for k, v in index.items() if k[0] == "fire7"}
        cb = _fire_curve(idx)
        yb = np.array([cb[a] for a in ANGLES])
        r = {}
        for k, s in shapes.items():
            A = float(np.dot(s, yb) / np.dot(s, s))
            r[k] = float(np.sum((yb - A * s) ** 2))
        boots.append(min(r, key=lambda k: r[k]) == "sin")
    p4 = {"curve": {a: round(curve[a], 4) for a in ANGLES},
          "fits": {k: {"sse": round(v[0], 6), "amplitude": round(v[1], 4)} for k, v in fits.items()},
          "best_shape": best,
          "sin_wins_fraction_of_bootstraps": round(float(np.mean(boots)), 3),
          "verdict": "PASS" if (best == "sin" and np.mean(boots) >= 0.95) else "FAIL",
          "rule": "PASS if the sine shape fits better than both rivals in at least 95% of bootstraps"}

    # ---- P-5
    blocks = {}
    for cut in list(meta_by_cut):
        C, pop, Ps = _block_coh(index, cut, meta_by_cut)
        blocks[cut] = {"C13": round(C, 4), "population": round(pop, 4),
                       "F13": round(pop / 2 + C / 2, 4), "P": [round(p, 4) for p in Ps]}
    bse = {}
    for cut in list(meta_by_cut):
        vals = []
        for _ in range(B):
            idx = {k: resample(v, rng) for k, v in index.items() if k[0] in ("blockpop", "blockpar") and k[1] == cut}
            vals.append(_block_coh(idx, cut, meta_by_cut)[0])
        bse[cut] = float(np.std(vals, ddof=1))
        blocks[cut]["bootstrap_se"] = round(bse[cut], 4)
    cuts = [c for c in blocks if c != "mono"]
    winner = max(cuts, key=lambda c: blocks[c]["C13"])
    margins = {c: round((blocks["7+7"]["C13"] - blocks[c]["C13"]) / math.hypot(bse["7+7"], bse[c]), 2)
               for c in cuts if c != "7+7"}
    p5 = {"by_cut": blocks, "winner": winner, "z_of_7+7_over": margins,
          "verdict": "PASS" if (winner == "7+7" and all(z >= 2 for z in margins.values())) else "FAIL",
          "rule": "PASS if 7+7 carries the largest C13 and beats each rival cut by at least 2 SE"}

    out = {"backend": D["backend"], "job_id": D["job_id"], "chain": D["chain"], "shots": D["shots"],
           "qpu_usage": D.get("qpu_usage"), "timestamp_utc": D["timestamp_utc"], "P-4": p4, "P-5": p5}
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({"P-4": {k: p4[k] for k in ("curve", "best_shape", "sin_wins_fraction_of_bootstraps", "verdict")},
                      "P-5": {"by_cut": {c: {"C13": v["C13"], "se": v["bootstrap_se"]} for c, v in blocks.items()},
                              "winner": winner, "z": margins, "verdict": p5["verdict"]}}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
