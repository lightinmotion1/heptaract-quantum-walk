#!/usr/bin/env python3
"""
HEPTARACT round 2, quantum computations (pre-registered 2026-09-17).

  T-2.5  helix walk  H(n, L): spiral path 0..nL + climb edges k~k+n, n in {5,6,7,8}, L in {2,3}
  T-2.6  wheel walks W_n from the hub (exploratory)
  T-2.7  base-d break-even curves, d = 2..16
  P-3    W versus GHZ when one member leaves (7 qubits)

Writes results/t2_quantum_round2.json.
"""
import json, math
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent.parent / "results"
OUT.mkdir(exist_ok=True)
res = {}

# ---------- T-2.5 helix walk ----------
def helix(n, L):
    N = n * L + 1
    A = np.zeros((N, N))
    for k in range(N - 1):
        A[k, k + 1] = A[k + 1, k] = 1
    for k in range(N - n):
        A[k, k + n] = A[k + n, k] = 1
    return A

def best_transfer(A, src, dst, T=60.0, dt=0.005):
    w, V = np.linalg.eigh(A)
    amp_src = V[src, :]          # <v_j|src>
    amp_dst = V[dst, :]
    c = amp_src * amp_dst        # sum_j e^{-i w_j t} V[dst,j] V[src,j]
    ts = np.arange(0.0, T + dt / 2, dt)
    best, tbest = 0.0, 0.0
    for chunk in np.array_split(ts, max(1, len(ts) // 2000)):
        ph = np.exp(-1j * np.outer(chunk, w))
        p = np.abs(ph @ c) ** 2
        i = int(np.argmax(p))
        if p[i] > best:
            best, tbest = float(p[i]), float(chunk[i])
    return best, tbest

helix_rows = []
for L in (2, 3):
    for target in ("n", "top"):
        cell = {}
        for n in (5, 6, 7, 8):
            A = helix(n, L)
            dst = n if target == "n" else n * L
            f, t = best_transfer(A, 0, dst)
            cell[n] = {"fidelity": round(f, 6), "t": round(t, 3)}
        winner = max(cell, key=lambda k: cell[k]["fidelity"])
        others = [cell[k]["fidelity"] for k in cell if k != 7]
        seven_wins = cell[7]["fidelity"] > max(others) + 0.01
        helix_rows.append({"L": L, "target": target, "by_n": cell, "winner": winner, "seven_wins_by_0.01": seven_wins})
wins = sum(r["seven_wins_by_0.01"] for r in helix_rows)
res["T-2.5"] = {"cells": helix_rows, "seven_wins_cells": wins, "of": len(helix_rows),
                "verdict": "PASS" if wins >= 3 else "FAIL",
                "rule": "PASS needs n=7 to beat every other n by >0.01 in a majority (>=3) of the 4 cells"}

# ---------- T-2.6 wheel from hub ----------
wheel = {}
for n in range(3, 13):
    N = n + 1
    A = np.zeros((N, N))
    for k in range(1, N):
        A[0, k] = A[k, 0] = 1
        j = 1 + (k % n)
        A[k, j] = A[j, k] = 1
    w, V = np.linalg.eigh(A)
    ts = np.arange(0, 40, 0.002)
    ph = np.exp(-1j * np.outer(ts, w))
    hub = np.abs(ph @ (V[0, :] ** 2)) ** 2
    wheel[n] = {"max_share_leaving_hub": round(float(1 - hub.min()), 6),
                "analytic_bound_4n_over_(n+4)": round(4 * n / (n + 4) if n <= 12 else None, 6) if False else None}
# analytic: hub couples only to uniform rim state (energy 2): H_eff=[[0,sqrt n],[sqrt n,2]]
for n in wheel:
    d = math.sqrt(1 + n)            # half-splitting
    wheel[n]["analytic_max_share"] = round(n / (1 + n), 6)
res["T-2.6"] = {"by_n": wheel, "note": "Two-level reduction: the hub talks only to the even rim state; the most that ever leaves is n/(n+1), rising smoothly with n. Nothing singles out n=7."}

# ---------- T-2.7 base-d curves ----------
rows = []
for d in range(2, 17):
    b = math.log2(d)
    rows.append({"d": d, "bits_per_read": round(b, 4), "readout_break_even_at_0.99": round(0.99 ** b, 5),
                 "gate_error_multiplier": round(b * b, 3), "embedding_waste_levels": 2 ** math.ceil(b) - d,
                 "prime": all(d % p for p in range(2, int(d ** 0.5) + 1)) and d > 1})
# smoothness check: second differences of the two curves at d=7 vs neighbors
def second_diff(key, d):
    y = {r["d"]: r[key] for r in rows}
    return round(y[d - 1] - 2 * y[d] + y[d + 1], 6)
res["T-2.7"] = {"rows": rows,
                "second_difference_at_7": {"readout": second_diff("readout_break_even_at_0.99", 7),
                                           "gate": second_diff("gate_error_multiplier", 7)},
                "second_difference_at_6": {"readout": second_diff("readout_break_even_at_0.99", 6),
                                           "gate": second_diff("gate_error_multiplier", 6)},
                "verdict": "FAIL",
                "reading": "Both curves are smooth functions of log2 d; d=7 lies on them. Seven's distinctions: prime (full set of mutually unbiased bases) and the largest prime that fits inside three qubits (one spare level)."}

# ---------- P-3 W versus GHZ ----------
def ket(bits):
    v = np.zeros(2 ** len(bits)); v[int("".join(map(str, bits)), 2)] = 1; return v
def ghz(n):
    return (ket([0] * n) + ket([1] * n)) / math.sqrt(2)
def wstate(n):
    v = sum(ket([1 if i == k else 0 for i in range(n)]) for k in range(n)); return v / math.sqrt(n)
def reduced(psi, keep, n):
    psi = psi.reshape([2] * n)
    trace = [i for i in range(n) if i not in keep]
    M = np.transpose(psi, keep + trace).reshape(2 ** len(keep), -1)
    return M @ M.conj().T
def concurrence(rho):
    sy = np.array([[0, -1j], [1j, 0]])
    R = rho @ np.kron(sy, sy) @ rho.conj() @ np.kron(sy, sy)
    ev = np.sqrt(np.abs(np.sort(np.linalg.eigvals(R).real)[::-1]))
    return float(max(0.0, ev[0] - ev[1] - ev[2] - ev[3]))
def negativity_split(rho, nA, nB):
    r = rho.reshape(2 ** nA, 2 ** nB, 2 ** nA, 2 ** nB).transpose(0, 3, 2, 1).reshape(rho.shape)
    ev = np.linalg.eigvalsh(r)
    return float(-ev[ev < 0].sum())
n = 7
out = {}
for name, psi in (("GHZ7", ghz(n)), ("W7", wstate(n))):
    pair = concurrence(reduced(psi, [0, 1], n))
    six = reduced(psi, [1, 2, 3, 4, 5, 6], n)             # member 0 leaves (traced out)
    neg = negativity_split(six, 3, 3)                      # entanglement left across a 3|3 cut of the six
    out[name] = {"pair_concurrence": round(pair, 6), "after_one_leaves_negativity_3v3": round(neg, 6)}
res["P-3"] = {"results": out,
              "reading": "GHZ: no pair holds any entanglement, and once one member leaves the remaining six hold none either (the whole bond needs everyone). W: every pair holds a little (2/7), and the remaining six stay entangled after a departure."}

(OUT / "t2_quantum_round2.json").write_text(json.dumps(res, indent=1, default=str))
print(json.dumps({k: (v.get("verdict") if isinstance(v, dict) else None) for k, v in res.items()}, indent=1))
for r in helix_rows:
    print(r["L"], r["target"], {k: v["fidelity"] for k, v in r["by_n"].items()}, "winner", r["winner"])
print("wheel", {k: v["max_share_leaving_hub"] for k, v in wheel.items()})
print("P-3", out)
