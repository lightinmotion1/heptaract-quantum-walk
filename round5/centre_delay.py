#!/usr/bin/env python3
"""
P-12 — Does the shared centre survive the wait?

P-11 showed the centre of both is a real reading: ask only for the relationship and the six across
two ships stay bonded; ask either ship what it is and the bond is gone. This asks whether that
survives time, and separates two things that the word "delay" hides:

  WAITING          idle time. The state decays at the qubits' own coherence time whether or not
                   anyone reads it. Nothing exotic is claimed; the question is the RATE.

  SPANNING         the two halves of the relationship taken at two different moments. Quantum
                   mechanics says correlations do not care which reading came first, so the
                   honest prediction is that spanning the wait costs nothing BEYOND the waiting.
                   If it costs more, that is real news about relationship and time.

Three arms, at each delay:

  TOGETHER   link, wait, then take the whole relationship at once   (the P-11 reading, delayed)
  SPANNED    link, take half the relationship, wait, take the other half, then read it
  PRIVATE    link, wait, then read one ship's own centre             (the control)

  python3 centre_delay.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "centre_delay_pending.json"
COUNTS = RES / "centre_delay_counts.json"
OUT = RES / "centre_delay.json"

RIM_A = [0, 1, 2]
C1, ANC, C2 = 3, 4, 5
RIM_B = [6, 7, 8]
NQ = 9
ALL = list(range(NQ))
THETAS = 8
SHOTS = 1024
DELAYS_US = [0, 30, 90]              # microseconds of idle, against a Heron T2 of order 100 us
ARMS = ["together", "spanned", "private"]


def prep(qc):
    qc.h(C1)
    for r in RIM_A:
        qc.cx(C1, r)
    qc.h(C2)
    for r in RIM_B:
        qc.cx(C2, r)
    qc.cz(C1, C2)


def wait(qc, us):
    if us:
        qc.barrier(ALL)
        for q in ALL:
            qc.delay(us, q, unit="us")
        qc.barrier(ALL)


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []
    for arm in ARMS:
        for us in DELAYS_US:
            for t in range(THETAS):
                theta = 2 * math.pi * t / THETAS
                qc = QuantumCircuit(NQ, NQ)
                prep(qc)
                if arm == "together":
                    wait(qc, us)
                    qc.h(C1); qc.h(C2)
                    qc.cx(C1, ANC)
                    qc.cx(C2, ANC)
                    qc.measure(ANC, ANC)
                    qc.h(C1); qc.h(C2)
                elif arm == "spanned":
                    qc.h(C1)
                    qc.cx(C1, ANC)          # half the relationship, taken now
                    qc.h(C1)
                    wait(qc, us)            # the third qubit carries it through the wait
                    qc.h(C2)
                    qc.cx(C2, ANC)          # the other half, taken after
                    qc.h(C2)
                    qc.measure(ANC, ANC)
                else:
                    wait(qc, us)
                    qc.h(C1)
                    qc.measure(C1, C1)
                for r in RIM_A + RIM_B:
                    qc.rz(theta, r)
                    qc.h(r)
                qc.measure(RIM_A + RIM_B, RIM_A + RIM_B)
                circs.append(qc)
                meta.append({"arm": arm, "delay_us": us, "t": t})
    return circs, meta


def best_line(backend, length=NQ):
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
    backend = svc.least_busy(operational=True, simulator=False, min_num_qubits=NQ + 4)
    chain, two = best_line(backend, NQ)
    props = {}
    try:
        for q in chain:
            props[str(q)] = {"T1_us": round(backend.qubit_properties(q).t1 * 1e6, 1),
                             "T2_us": round(backend.qubit_properties(q).t2 * 1e6, 1)}
    except Exception as e:
        props = {"error": str(e)}
    circs, meta = build()
    tcs = [transpile(c, backend, initial_layout=chain, optimization_level=1, seed_transpiler=7) for c in circs]
    for m, tc in zip(meta, tcs):
        m["twoq"] = sum(1 for i in tc.data if i.operation.num_qubits == 2)
    job = Sampler(mode=backend).run(tcs, shots=SHOTS)
    PENDING.write_text(json.dumps({"backend": backend.name, "chain": chain, "job_id": job.job_id(),
                                   "meta": meta, "shots": SHOTS, "coherence": props,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("submitted", job.job_id(), "on", backend.name, len(tcs), "circuits")
    print("coherence of the chain:", json.dumps(props))


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
    items = [{**m, "twoq": 0, "counts": res.get_counts(i)} for i, m in enumerate(meta)]
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
        series = [parity(by_t[t], RIM_A + RIM_B, (cbit, outcome))[0] for t in range(THETAS)]
        sp = np.abs(np.fft.rfft(np.array(series))) / THETAS
        vals.append(float(np.sum(sp[1:])))
    return round(float(np.mean(vals)), 4)


def analyze():
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    out = {"backend": D["backend"], "chain": D["chain"], "shots": D["shots"],
           "coherence": D.get("coherence"), "qpu_usage": D.get("qpu_usage"), "by_arm": {}}
    for arm in ARMS:
        cbit = C1 if arm == "private" else ANC
        row = {}
        for us in DELAYS_US:
            by_t = {it["t"]: it["counts"] for it in items if it["arm"] == arm and it["delay_us"] == us}
            row[str(us)] = bond_of(by_t, cbit)
        out["by_arm"][arm] = row

    # ---- the decay, done honestly
    # The metric has a floor: uncorrelated noise still returns a small non-zero bond. The private
    # arm sits at that floor once its own coherence is gone, so it measures the floor directly.
    tog = out["by_arm"]["together"]
    priv = out["by_arm"]["private"]
    floor = float(np.mean([priv[str(u)] for u in DELAYS_US[1:]])) if len(DELAYS_US) > 1 else 0.0
    corr = {str(u): max(tog[str(u)] - floor, 0.0) for u in DELAYS_US}
    b0 = corr[str(DELAYS_US[0])]
    tau, tau_bound = None, None
    for u in DELAYS_US[1:]:
        if corr[str(u)] > 0.005 and b0 > 0:
            tau = round(u / math.log(b0 / corr[str(u)]), 1)
            break
    if tau is None and b0 > 0:
        # the bond was already at the floor by the first non-zero delay: an upper bound only
        u = DELAYS_US[1]
        tau_bound = round(u / math.log(b0 / 0.01), 1)

    coh = D.get("coherence") or {}
    t2 = {k: v["T2_us"] for k, v in coh.items() if isinstance(v, dict) and "T2_us" in v}
    chain = D.get("chain") or []
    rim_phys = [str(chain[i]) for i in (RIM_A + RIM_B)] if chain else []
    rim_t2 = [t2[q] for q in rim_phys if q in t2]
    six_body = round(1.0 / sum(1.0 / x for x in rim_t2), 1) if rim_t2 else None
    out["decay"] = {
        "noise_floor": round(floor, 4),
        "floor_corrected_bond": {k: round(v, 4) for k, v in corr.items()},
        "shared_bond_decay_us": tau,
        "shared_bond_decay_upper_bound_us": tau_bound,
        "rim_T2_us": {q: t2[q] for q in rim_phys if q in t2},
        "six_body_prediction_us": six_body,
        "chain_mean_T2_us": round(float(np.mean(list(t2.values()))), 1) if t2 else None,
        "measured_over_six_body": (round((tau or tau_bound) / six_body, 2)
                                   if (tau or tau_bound) and six_body else None),
        "note": ("a six-body coherence decays at the SUM of its carriers' rates, so the yardstick "
                 "is the six-body prediction, not a single qubit's T2"),
    }
    span = out["by_arm"]["spanned"]
    out["verdict"] = {
        "shared_beats_private_at_zero_delay": tog[str(DELAYS_US[0])] > 1.5 * priv[str(DELAYS_US[0])],
        "shared_beats_private_at_every_delay": all(
            tog[str(u)] > 1.5 * priv[str(u)] for u in DELAYS_US),
        "spanning_costs_nothing_extra": all(
            span[str(u)] > 0.6 * tog[str(u)] for u in DELAYS_US),
        "decays_no_faster_than_its_carriers": (
            out["decay"]["measured_over_six_body"] is not None
            and out["decay"]["measured_over_six_body"] >= 0.33),
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("by_arm", "decay", "verdict")}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
