#!/usr/bin/env python3
"""
P-9 — the MUB reading on a machine that was never built for it.

T-2.9 showed, in simulation, that a seven-level state read in its eight mutually unbiased bases
is reconstructed better than the same state read through twenty-seven Pauli settings, at matched
shots and matched readout error. That comparison assumed the readings themselves cost nothing.

On a qubit processor they do not. A Pauli setting is one single-qubit rotation per qubit and no
entangling gates at all. A MUB of dimension seven, embedded in three qubits, is a generic
three-qubit unitary and compiles to a long chain of two-qubit gates. So this test asks the
question the simulation could not:

    does the information advantage of the eight MUBs survive the cost of performing them
    on hardware that has no native seven-level piece?

Either answer is worth having, and the pre-registration says so before the run.

  python3 mub_hardware.py sim | submit | fetch | analyze
"""
import json, itertools, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results" if (HERE.parent / "results").exists() else HERE / "results"
RES.mkdir(exist_ok=True)
PENDING = RES / "mub_hardware_pending.json"
COUNTS = RES / "mub_hardware_counts.json"
OUT = RES / "mub_hardware.json"

D7, D8, NQ = 7, 8, 3
SHOTS_MUB = 1024        # 8 bases  x 1024 = 8,192 shots
SHOTS_PAULI = 304       # 27 bases x  304 = 8,208 shots — matched within 0.2%


# ------------------------------------------------------------------ the states we read
def test_states():
    rng = np.random.default_rng(7)
    states = {}
    v = np.zeros(D7, dtype=complex); v[0] = 1
    states["level 0"] = v
    states["uniform"] = np.ones(D7, dtype=complex) / np.sqrt(D7)
    v = np.zeros(D7, dtype=complex); v[0] = v[6] = 1/np.sqrt(2)
    states["ends"] = v
    z = rng.normal(size=D7) + 1j*rng.normal(size=D7)
    states["random"] = z / np.linalg.norm(z)
    return states


def embed_vec(v7):
    v8 = np.zeros(D8, dtype=complex); v8[:D7] = v7
    return v8


# ------------------------------------------------------------------ bases
def mubs7():
    w = np.exp(2j*np.pi/D7)
    out = [np.eye(D7, dtype=complex)]
    for k in range(D7):
        B = np.zeros((D7, D7), dtype=complex)
        for j in range(D7):
            for q in range(D7):
                B[q, j] = w ** ((k*q*q + j*q) % D7) / np.sqrt(D7)
        out.append(B)
    return out


def mub_unitaries():
    """Each MUB basis, embedded in eight dimensions, as the unitary that rotates it to Z."""
    U = []
    for B in mubs7():
        M = np.eye(D8, dtype=complex)
        M[:D7, :D7] = B
        U.append(M.conj().T)          # apply U, then read in the computational basis
    return U


PAULI_1Q = {
    'X': np.array([[1, 1], [1, -1]], dtype=complex)/np.sqrt(2),
    'Y': np.array([[1, -1j], [1, 1j]], dtype=complex)/np.sqrt(2),
    'Z': np.eye(2, dtype=complex),
}


def pauli_unitaries():
    out = []
    for combo in itertools.product('XYZ', repeat=NQ):
        M = PAULI_1Q[combo[0]]
        for c in combo[1:]:
            M = np.kron(M, PAULI_1Q[c])
        out.append(M)
    return out


def projector_set(unitaries):
    """The POVM each reading implements, in the eight-dimensional space."""
    P = []
    for U in unitaries:
        for j in range(D8):
            v = U.conj().T[:, j:j+1]
            P.append(v @ v.conj().T)
    return np.array(P)


# ------------------------------------------------------------------ circuits
def build():
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import StatePreparation, UnitaryGate
    circs, meta = [], []
    for name, v7 in test_states().items():
        prep = StatePreparation(embed_vec(v7))
        for tag, unis, shots in (("mub", mub_unitaries(), SHOTS_MUB),
                                 ("pauli", pauli_unitaries(), SHOTS_PAULI)):
            for i, U in enumerate(unis):
                qc = QuantumCircuit(NQ, NQ)
                qc.append(prep, range(NQ))
                qc.append(UnitaryGate(U), range(NQ))
                qc.measure(range(NQ), range(NQ))
                circs.append(qc)
                meta.append({"state": name, "scheme": tag, "setting": i, "shots": shots})
    return circs, meta


# ------------------------------------------------------------------ layout
def best_line(backend, length=NQ):
    import math
    t = backend.target
    two = next(n for n in ("cz", "ecr", "cx") if n in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else .05) for q, p in t["measure"].items()}
    adj = {}
    for (a, b), e in err2.items():
        if e < .05:
            adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    def ee(a, b): return min(err2.get((a, b), 1.), err2.get((b, a), 1.))
    beam = [([q], math.log(1-ro.get(q, .05))) for q in adj]
    for _ in range(length-1):
        nxt = []
        for path, sc in beam:
            for nb in adj.get(path[-1], ()):
                if nb in path: continue
                nxt.append((path+[nb], sc + math.log(1-ee(path[-1], nb)) + math.log(1-ro.get(nb, .05))))
        nxt.sort(key=lambda x: -x[1]); beam = nxt[:400]
    beam.sort(key=lambda x: -x[1])
    return beam[0][0], two


# ------------------------------------------------------------------ run
def submit():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=NQ+5)
    chain, two = best_line(backend, NQ)
    circs, meta = build()
    tcs = [transpile(c, backend, initial_layout=chain, optimization_level=3, seed_transpiler=7)
           for c in circs]
    twoq = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in tcs]
    for m, n in zip(meta, twoq):
        m["twoq"] = n
    # one job per shot count, since the sampler takes a single shots value
    jobs = {}
    for tag, shots in (("mub", SHOTS_MUB), ("pauli", SHOTS_PAULI)):
        idx = [i for i, m in enumerate(meta) if m["scheme"] == tag]
        job = Sampler(mode=backend).run([tcs[i] for i in idx], shots=shots)
        jobs[tag] = {"job_id": job.job_id(), "index": idx}
        print("submitted", tag, job.job_id(), len(idx), "circuits x", shots, "shots")
    PENDING.write_text(json.dumps({"backend": backend.name, "chain": chain, "jobs": jobs,
                                   "meta": meta,
                                   "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    print("two-qubit gates per reading — mub:",
          sorted(set(m["twoq"] for m in meta if m["scheme"] == "mub")),
          "pauli:", sorted(set(m["twoq"] for m in meta if m["scheme"] == "pauli")))


def fetch():
    from qiskit_ibm_runtime import QiskitRuntimeService
    P = json.loads(PENDING.read_text())
    svc = QiskitRuntimeService()
    items, usage = [], {}
    for tag, j in P["jobs"].items():
        job = svc.job(j["job_id"])
        print(tag, job.status())
        res = job.result()
        try:
            usage[tag] = job.metrics().get("usage", {})
        except Exception:
            pass
        for k, r in zip(j["index"], res):
            d = r.data
            try:
                counts = d.c.get_counts()
            except AttributeError:
                counts = d[list(d.keys())[0]].get_counts()
            items.append({**P["meta"][k], "counts": counts})
    COUNTS.write_text(json.dumps({"backend": P["backend"], "chain": P["chain"], "jobs": P["jobs"],
                                  "qpu_usage": usage, "timestamp_utc": P["submitted_utc"],
                                  "items": items}, indent=1))
    print("saved", COUNTS, usage)


def simulate():
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    sim = AerSimulator()
    circs, meta = build()
    tcs = transpile(circs, sim, optimization_level=1)
    items = []
    for tag, shots in (("mub", SHOTS_MUB), ("pauli", SHOTS_PAULI)):
        idx = [i for i, m in enumerate(meta) if m["scheme"] == tag]
        res = sim.run([tcs[i] for i in idx], shots=shots, seed_simulator=7).result()
        for n, i in enumerate(idx):
            items.append({**meta[i], "twoq": 0, "counts": res.get_counts(n)})
    COUNTS.write_text(json.dumps({"backend": "aer", "chain": [0, 1, 2], "jobs": {},
                                  "qpu_usage": None, "timestamp_utc": "sim", "items": items}, indent=1))
    print("simulated", len(circs), "circuits")


# ------------------------------------------------------------------ analyze
def nearest_physical(M):
    M = (M + M.conj().T)/2
    w, v = np.linalg.eigh(M)
    w = np.clip(w, 0, None)
    if w.sum() <= 0:
        return np.eye(M.shape[0])/M.shape[0]
    w = w/w.sum()
    return (v * w) @ v.conj().T


def reconstruct(freqs, P):
    d = P.shape[1]
    A = P.reshape(P.shape[0], -1)
    A_real = np.concatenate([A.real, A.imag], axis=1)
    x, *_ = np.linalg.lstsq(A_real, freqs, rcond=None)
    return nearest_physical((x[:d*d] + 1j*x[d*d:]).reshape(d, d))


def fidelity(a, b):
    w, v = np.linalg.eigh(a); w = np.clip(w, 0, None)
    sa = (v*np.sqrt(w)) @ v.conj().T
    m = sa @ b @ sa
    ew = np.clip(np.linalg.eigvalsh((m + m.conj().T)/2), 0, None)
    return float(np.sum(np.sqrt(ew))**2)


def bits_to_index(k):
    return int(k.replace(" ", ""), 2)


def analyze(B=400):
    D = json.loads(COUNTS.read_text())
    items = D["items"]
    P_mub = projector_set(mub_unitaries())
    P_pau = projector_set(pauli_unitaries())
    states = test_states()
    rng = np.random.default_rng(20260918)

    by = {}
    for it in items:
        by.setdefault((it["state"], it["scheme"]), {})[it["setting"]] = it["counts"]

    def freq_vector(counts_by_setting, n_settings, shots):
        f = []
        for i in range(n_settings):
            c = counts_by_setting[i]
            tot = sum(c.values())
            row = np.zeros(D8)
            for k, v in c.items():
                row[bits_to_index(k)] = v/tot
            f.append(row)
        return np.concatenate(f)

    def resample(counts, rng):
        keys = list(counts)
        p = np.array([counts[k] for k in keys], float); N = int(p.sum())
        draw = rng.multinomial(N, p/N)
        return {k: int(c) for k, c in zip(keys, draw) if c}

    out = {"backend": D["backend"], "chain": D["chain"], "qpu_usage": D.get("qpu_usage"),
           "two_qubit_gates": {}, "by_state": {}}
    for m in items:
        out["two_qubit_gates"].setdefault(m["scheme"], set()).add(m.get("twoq", 0))
    out["two_qubit_gates"] = {k: sorted(v) for k, v in out["two_qubit_gates"].items()}

    infid = {"mub": [], "pauli": []}
    for name, v7 in states.items():
        truth = np.outer(embed_vec(v7), embed_vec(v7).conj())
        row = {}
        for scheme, P, n, shots in (("mub", P_mub, len(mub_unitaries()), SHOTS_MUB),
                                    ("pauli", P_pau, len(pauli_unitaries()), SHOTS_PAULI)):
            cbs = by[(name, scheme)]
            est = reconstruct(freq_vector(cbs, n, shots), P)
            f = fidelity(truth, est)
            boots = []
            for _ in range(B):
                rc = {i: resample(c, rng) for i, c in cbs.items()}
                boots.append(1 - fidelity(truth, reconstruct(freq_vector(rc, n, shots), P)))
            row[scheme] = {"infidelity": round(1-f, 5),
                           "bootstrap_sd": round(float(np.std(boots, ddof=1)), 5),
                           "leak_to_level_7": round(float(np.real(est[7, 7])), 5)}
            infid[scheme].append(1-f)
        row["z_mub_better"] = round(float((row["pauli"]["infidelity"] - row["mub"]["infidelity"]) /
                                          np.hypot(row["pauli"]["bootstrap_sd"], row["mub"]["bootstrap_sd"])), 2)
        out["by_state"][name] = row

    mm, pm = float(np.mean(infid["mub"])), float(np.mean(infid["pauli"]))
    out["mean_infidelity"] = {"mub": round(mm, 5), "pauli": round(pm, 5)}
    out["verdict"] = ("MUB reading survives the hardware cost" if mm < pm else
                      "the hardware cost of the MUB readings eats the advantage")
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"sim": simulate, "submit": submit, "fetch": fetch, "analyze": analyze}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
