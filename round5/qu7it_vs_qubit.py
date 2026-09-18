#!/usr/bin/env python3
"""
T-2.9 — reading a seven-level state, natively or as three qubits, under real readout error.

The claim on the tree: a qu7it read in its eight mutually unbiased bases carries more than the
same information squeezed through qubits. The rival nobody names out loud: the advantage may
belong to MUBs rather than to seven, in which case qubits with good bases do just as well.

Four ways of reading the SAME seven-level state, at matched shots and matched readout error:

  A  qu7it · 8 MUBs           the framework's claim
  B  qu7it · 8 random bases   isolates MUBs from the dimension
  C  qubits · Pauli products  what anyone actually does on hardware today (27 settings)
  D  qubits · 8 random bases  the honest matched-effort rival

Readout error is matched by TOTAL probability of a wrong outcome, so no scheme is handed an
easier detector. Estimation is linear inversion followed by the nearest physical state.

  python3 qu7it_vs_qubit.py            -> qu7it_vs_qubit.json  (+ .png)
"""
import json, itertools
import numpy as np

D7, D8 = 7, 8
RNG = np.random.default_rng(20260918)
SHOT_BUDGETS = [2000, 8000, 32000]
SPAM_LEVELS = [0.0, 0.02, 0.05, 0.10]
N_STATES = 60


# ------------------------------------------------------------------ bases
def mubs_prime(d=D7):
    """The d+1 mutually unbiased bases of a prime-dimensional space."""
    w = np.exp(2j * np.pi / d)
    out = [np.eye(d, dtype=complex)]
    for k in range(d):
        B = np.zeros((d, d), dtype=complex)
        for j in range(d):
            for q in range(d):
                B[q, j] = w ** ((k * q * q + j * q) % d) / np.sqrt(d)
        out.append(B)
    return out


def random_bases(d, n, rng):
    out = []
    for _ in range(n):
        z = (rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))) / np.sqrt(2)
        q, r = np.linalg.qr(z)
        out.append(q * (np.diag(r) / abs(np.diag(r))))
    return out


def pauli_bases():
    """Every product of X, Y, Z on three qubits: 27 measurement settings on 8 levels."""
    ev = {
        'X': np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),
        'Y': np.array([[1, 1], [1j, -1j]], dtype=complex) / np.sqrt(2),
        'Z': np.eye(2, dtype=complex),
    }
    out = []
    for combo in itertools.product('XYZ', repeat=3):
        B = ev[combo[0]]
        for c in combo[1:]:
            B = np.kron(B, ev[c])
        out.append(B)
    return out


def embed(rho7):
    """A seven-level state sitting inside three qubits: the eighth level stays empty."""
    r = np.zeros((D8, D8), dtype=complex)
    r[:D7, :D7] = rho7
    return r


# ------------------------------------------------------------------ measurement
def projectors(bases):
    """Every basis becomes its rank-one projectors, stacked."""
    P = []
    for B in bases:
        for j in range(B.shape[1]):
            v = B[:, j:j+1]
            P.append(v @ v.conj().T)
    return np.array(P)


def confusion(d, eps):
    """A wrong outcome with total probability eps, spread evenly over the other levels."""
    C = np.full((d, d), eps / (d - 1))
    np.fill_diagonal(C, 1.0 - eps)
    return C


def measure(rho, bases, shots_per_basis, eps, rng):
    """Sample outcomes basis by basis, through the confusion matrix."""
    d = rho.shape[0]
    C = confusion(d, eps)
    freqs = []
    for B in bases:
        p = np.real(np.einsum('ij,jk,ki->i', B.conj().T, rho, B))
        p = np.clip(p, 0, None); p = p / p.sum()
        p_noisy = C @ p                                   # the detector's own confusion
        p_noisy = np.clip(p_noisy, 0, None); p_noisy /= p_noisy.sum()
        counts = rng.multinomial(shots_per_basis, p_noisy)
        freqs.append(counts / shots_per_basis)
    return np.concatenate(freqs)


def nearest_physical(M):
    """Closest density matrix: hermitian part, clipped eigenvalues, unit trace."""
    M = (M + M.conj().T) / 2
    w, v = np.linalg.eigh(M)
    w = np.clip(w, 0, None)
    if w.sum() <= 0:
        return np.eye(M.shape[0]) / M.shape[0]
    w = w / w.sum()
    return (v * w) @ v.conj().T


def reconstruct(freqs, P):
    """Linear inversion: least squares against the projector set, then made physical."""
    d = P.shape[1]
    A = P.reshape(P.shape[0], -1)
    A_real = np.concatenate([A.real, A.imag], axis=1)
    x, *_ = np.linalg.lstsq(A_real, freqs, rcond=None)
    M = (x[:d*d] + 1j * x[d*d:]).reshape(d, d)
    return nearest_physical(M)


def random_state(d, rng, purity=0.85):
    z = (rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    psi = q[:, 0:1]
    pure = psi @ psi.conj().T
    return purity * pure + (1 - purity) * np.eye(d) / d


def fidelity(a, b):
    """Uhlmann fidelity between two density matrices."""
    w, v = np.linalg.eigh(a)
    w = np.clip(w, 0, None)
    sa = (v * np.sqrt(w)) @ v.conj().T
    m = sa @ b @ sa
    ew = np.clip(np.linalg.eigvalsh((m + m.conj().T) / 2), 0, None)
    return float(np.sum(np.sqrt(ew)) ** 2)


# ------------------------------------------------------------------ the four readings
def schemes(rng):
    m7 = mubs_prime(D7)                       # 8 bases in 7 levels
    r7 = random_bases(D7, 8, rng)
    pauli = pauli_bases()                     # 27 bases in 8 levels
    r8 = random_bases(D8, 8, rng)
    return {
        "A qu7it · 8 MUBs":        {"bases": m7,   "d": D7, "P": projectors(m7)},
        "B qu7it · 8 random":      {"bases": r7,   "d": D7, "P": projectors(r7)},
        "C qubits · 27 Paulis":    {"bases": pauli,"d": D8, "P": projectors(pauli)},
        "D qubits · 8 random":     {"bases": r8,   "d": D8, "P": projectors(r8)},
    }


def run():
    S = schemes(RNG)
    results = {name: {} for name in S}
    for shots in SHOT_BUDGETS:
        for eps in SPAM_LEVELS:
            acc = {name: [] for name in S}
            for _ in range(N_STATES):
                rho7 = random_state(D7, RNG)
                rho8 = embed(rho7)
                for name, sc in S.items():
                    per = max(1, shots // len(sc["bases"]))       # the SAME total shot budget
                    truth = rho7 if sc["d"] == D7 else rho8
                    f = measure(truth, sc["bases"], per, eps, RNG)
                    est = reconstruct(f, sc["P"])
                    if sc["d"] == D8:
                        est = nearest_physical(est[:D7, :D7] / max(np.real(np.trace(est[:D7, :D7])), 1e-12))
                    acc[name].append(1.0 - fidelity(rho7, est))
            for name in S:
                a = np.array(acc[name])
                results[name]["shots%d_spam%.2f" % (shots, eps)] = {
                    "mean_infidelity": float(a.mean()),
                    "sem": float(a.std(ddof=1) / np.sqrt(len(a))),
                }
            print(shots, eps, {n: round(results[n]["shots%d_spam%.2f" % (shots, eps)]["mean_infidelity"], 5) for n in S}, flush=True)

    # verdicts, in the form the pre-registration asks for
    def val(n, s, e): return results[n]["shots%d_spam%.2f" % (s, e)]["mean_infidelity"]
    def sem(n, s, e): return results[n]["shots%d_spam%.2f" % (s, e)]["sem"]
    A, B, C, D = list(S)
    verdicts = {}
    for s in SHOT_BUDGETS:
        for e in SPAM_LEVELS:
            z_vs_pauli = (val(C, s, e) - val(A, s, e)) / np.hypot(sem(C, s, e), sem(A, s, e))
            z_vs_rand7 = (val(B, s, e) - val(A, s, e)) / np.hypot(sem(B, s, e), sem(A, s, e))
            z_vs_rand8 = (val(D, s, e) - val(A, s, e)) / np.hypot(sem(D, s, e), sem(A, s, e))
            verdicts["shots%d_spam%.2f" % (s, e)] = {
                "z_MUB_beats_pauli": round(float(z_vs_pauli), 2),
                "z_MUB_beats_random7": round(float(z_vs_rand7), 2),
                "z_MUB_beats_random8": round(float(z_vs_rand8), 2),
            }

    out = {"states_per_cell": N_STATES, "shot_budgets": SHOT_BUDGETS, "spam_levels": SPAM_LEVELS,
           "results": results, "verdicts": verdicts}
    with open("qu7it_vs_qubit.json", "w") as f:
        json.dump(out, f, indent=1)

    # ---------------------------------------------------------------- figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, GRID, BG = "#E8F0EE", "#1B2A2B", "#0A1112"
    COL = {A: "#2FA8A0", B: "#7FC24A", C: "#E8743B", D: "#B14FA8"}
    fig, axes = plt.subplots(1, len(SHOT_BUDGETS), figsize=(13, 4.2), facecolor=BG, sharey=True)
    for ax, shots in zip(axes, SHOT_BUDGETS):
        ax.set_facecolor(BG)
        for sp in ax.spines.values():
            sp.set_color(GRID)
        ax.tick_params(colors=INK, labelsize=8)
        ax.grid(True, color=GRID, lw=.6)
        for name in S:
            y = [val(name, shots, e) for e in SPAM_LEVELS]
            er = [sem(name, shots, e) for e in SPAM_LEVELS]
            ax.errorbar([e*100 for e in SPAM_LEVELS], y, yerr=er, color=COL[name], lw=1.7,
                        marker='o', ms=3.5, capsize=2, label=name)
        ax.set_yscale("log")
        ax.set_xlabel("readout error, % of outcomes wrong", color=INK, fontsize=9)
        ax.set_title("%s shots total" % f"{shots:,}", color=INK, fontsize=10)
    axes[0].set_ylabel("mean infidelity (lower is better)", color=INK, fontsize=9)
    axes[-1].legend(facecolor=BG, edgecolor=GRID, labelcolor=INK, fontsize=8)
    fig.suptitle("Reading a seven-level state: natively, or squeezed through qubits",
                 color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig("qu7it_vs_qubit.png", dpi=150, facecolor=BG)
    print(json.dumps(verdicts, indent=1))


if __name__ == "__main__":
    run()
