#!/usr/bin/env python3
"""
P-15 — Which channel eats the shared bond?

P-14 found the bond dying three to five times faster than the chain's published dephasing allows.
This measures the suspects separately, on the same qubits, in the same idle conditions:

    T1          energy decay          prepare |1>, wait, read
    T2*         free dephasing        Ramsey fringe through the wait
    T2 echo     refocused dephasing   the same with one pulse at the middle
    ZZ          the neighbours        Ramsey on a rim qubit with its centre held in |0> and in |1>;
                                      the fringe shifts by the always-on coupling between them

Then the arithmetic: does a model built from the MEASURED numbers account for the bond decay P-14
saw, and how much of the gap does the neighbours' coupling close?

  python3 decay_channels.py sim | submit | fetch | analyze
"""
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "decay_channels_pending.json"
COUNTS = RES / "decay_channels_counts.json"
OUT = RES / "decay_channels.json"

# the same five-qubit shape as P-14: rimA, C1, ANC, C2, rimB
RIM_A, C1, ANC, C2, RIM_B = 0, 1, 2, 3, 4
PAIRS = [(RIM_A, C1), (RIM_B, C2)]        # (rim qubit, its own centre = its nearest neighbour)
NQ = 5
DELAYS = [0, 60, 180]
PHASES = 4
ZZ_PHASES = 8
ZZ_DELAY = 60
SHOTS = 1024


def build():
    from qiskit import QuantumCircuit
    circs, meta = [], []

    # ---- T1: how fast the excitation leaks away
    for rim, _ in PAIRS:
        for us in DELAYS:
            qc = QuantumCircuit(NQ, NQ)
            qc.x(rim)
            if us:
                qc.delay(us, rim, unit="us")
            qc.measure(rim, rim)
            circs.append(qc); meta.append({"kind": "t1", "q": rim, "delay_us": us})

    # ---- T2* and T2 echo: how fast the phase is forgotten, free and refocused
    for kind in ("ramsey", "echo"):
        for rim, _ in PAIRS:
            for us in DELAYS:
                for p in range(PHASES):
                    phi = 2 * math.pi * p / PHASES
                    qc = QuantumCircuit(NQ, NQ)
                    qc.h(rim)
                    if us:
                        if kind == "ramsey":
                            qc.delay(us, rim, unit="us")
                        else:
                            qc.delay(us / 2.0, rim, unit="us")
                            qc.x(rim)
                            qc.delay(us / 2.0, rim, unit="us")
                            qc.x(rim)
                    qc.rz(phi, rim)
                    qc.h(rim)
                    qc.measure(rim, rim)
                    circs.append(qc)
                    meta.append({"kind": kind, "q": rim, "delay_us": us, "p": p})

    # ---- ZZ: the same Ramsey, with the neighbour held in |0> and in |1>
    for rim, centre in PAIRS:
        for nb in (0, 1):
            for p in range(ZZ_PHASES):
                phi = 2 * math.pi * p / ZZ_PHASES
                qc = QuantumCircuit(NQ, NQ)
                if nb:
                    qc.x(centre)
                qc.h(rim)
                qc.delay(ZZ_DELAY, rim, unit="us")
                qc.delay(ZZ_DELAY, centre, unit="us")
                qc.rz(phi, rim)
                qc.h(rim)
                qc.measure(rim, rim)
                circs.append(qc)
                meta.append({"kind": "zz", "q": rim, "centre": centre, "neighbour": nb, "p": p})
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
    print("published coherence:", json.dumps(props))


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
def p1(counts, q):
    tot = sum(counts.values())
    one = 0
    for k, v in counts.items():
        b = k.replace(" ", "")
        if b[len(b) - 1 - q] == "1":
            one += v
    return one / tot if tot else 0.0


def analyze():
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    chain = D["chain"]
    out = {"backend": D["backend"], "chain": chain, "published": D.get("coherence"),
           "qpu_usage": D.get("qpu_usage"), "measured": {}}

    for rim, centre in PAIRS:
        phys = str(chain[rim])
        row = {}

        # T1
        pops = {it["delay_us"]: p1(it["counts"], rim) for it in items if it["kind"] == "t1" and it["q"] == rim}
        row["excited_population"] = {str(k): round(v, 4) for k, v in sorted(pops.items())}
        p0, pL = pops[DELAYS[0]], pops[DELAYS[-1]]
        row["T1_us"] = round(DELAYS[-1] / math.log(p0 / pL), 1) if pL > 0 and pL < p0 else None

        # T2* and echo, from fringe amplitude
        for kind, label in (("ramsey", "T2_star_us"), ("echo", "T2_echo_us")):
            amps = {}
            for us in DELAYS:
                sub = {it["p"]: it["counts"] for it in items
                       if it["kind"] == kind and it["q"] == rim and it["delay_us"] == us}
                series = np.array([1 - 2 * p1(sub[p], rim) for p in range(PHASES)])
                amps[us] = float(np.hypot(series[0] - series[2], series[1] - series[3]) / 2)
            row[label.replace("_us", "_amplitude")] = {str(k): round(v, 4) for k, v in amps.items()}
            a0, aL = amps[DELAYS[0]], amps[DELAYS[-1]]
            row[label] = round(DELAYS[-1] / math.log(a0 / aL), 1) if 0 < aL < a0 else None

        # ZZ: the fringe phase with the neighbour down and up
        ph = {}
        for nb in (0, 1):
            sub = {it["p"]: it["counts"] for it in items
                   if it["kind"] == "zz" and it["q"] == rim and it["neighbour"] == nb}
            series = np.array([1 - 2 * p1(sub[p], rim) for p in range(ZZ_PHASES)])
            f = np.fft.rfft(series)
            ph[nb] = float(np.angle(f[1]))
        dphi = (ph[1] - ph[0] + math.pi) % (2 * math.pi) - math.pi
        row["zz_phase_shift_rad"] = round(dphi, 4)
        row["zz_coupling_kHz"] = round(abs(dphi) / (2 * math.pi * ZZ_DELAY * 1e-6) / 1e3, 2)
        out["measured"][phys] = row

    # ---- does a model from the measured numbers account for P-14?
    meas = out["measured"]
    inv = lambda x: (1.0 / x) if x else 0.0
    t2star_model = 1.0 / sum(inv(v.get("T2_star_us")) for v in meas.values()) if meas else None
    pub = D.get("coherence") or {}
    pub_model = (1.0 / sum(inv(pub[q]["T2_us"]) for q in meas if q in pub)) if pub else None
    zz_rate_kHz = sum(v.get("zz_coupling_kHz") or 0 for v in meas.values())
    # an always-on coupling of zeta dephases an unknown-neighbour superposition on ~1/(2 pi zeta)
    zz_time_us = round(1e3 / (2 * math.pi * zz_rate_kHz), 1) if zz_rate_kHz else None
    combined = (1.0 / (inv(t2star_model) + inv(zz_time_us))) if (t2star_model and zz_time_us) else None
    out["model"] = {
        "published_two_body_us": round(pub_model, 1) if pub_model else None,
        "measured_T2star_two_body_us": round(t2star_model, 1) if t2star_model else None,
        "zz_total_kHz": round(zz_rate_kHz, 2),
        "zz_dephasing_time_us": zz_time_us,
        "measured_plus_zz_us": round(combined, 1) if combined else None,
        "observed_bond_decay_us_from_P14": 30.0,
        "note": "P-14's 60 us point implies a bond decay near 30 us; the models above are what "
                "each measured channel predicts for a two-carrier bond",
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({"measured": out["measured"], "model": out["model"]}, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
