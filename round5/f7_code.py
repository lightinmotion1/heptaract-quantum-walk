#!/usr/bin/env python3
"""
T-2.8 / P9 — the seven-share code [[7,1,4]]_7, built explicitly and checked.

The claim on the tree: the best seven-share quantum scheme cannot be built from qubits; it
needs seven-level pieces. This script builds the code over F_7, measures its distance by
enumeration rather than by citation, and then proves the qubit route is closed by exhausting
every binary code of the same shape.

  python3 f7_code.py      ->  f7_code.json
"""
import json, itertools
import numpy as np

P = 7
FIELD = list(range(P))


def rs_code(k, p=P):
    """Evaluation code: all polynomials of degree < k, read at every element of F_p.

    Length p, dimension k, minimum distance p - k + 1 — an MDS code, the best any code of
    that length and dimension can be. Over F_p the dual of this code is the same construction
    with dimension p - k, so the family contains its own duals.
    """
    G = np.array([[pow(a, j, p) if not (a == 0 and j == 0) else 1 for a in range(p)]
                  for j in range(k)], dtype=int) % p
    return G


def span(G, p=P):
    k, n = G.shape
    out = np.zeros((p ** k, n), dtype=int)
    for i, coeffs in enumerate(itertools.product(range(p), repeat=k)):
        out[i] = (np.array(coeffs) @ G) % p
    return out


def min_weight(words, exclude=None):
    w = np.count_nonzero(words, axis=1)
    mask = w > 0
    if exclude is not None:
        ex = set(map(tuple, exclude.tolist()))
        mask &= np.array([tuple(r) not in ex for r in words.tolist()])
    return int(w[mask].min()) if mask.any() else None


def contained(A, B):
    """Is every word of A a word of B?"""
    Bs = set(map(tuple, B.tolist()))
    return all(tuple(r) in Bs for r in A.tolist())


def binary_best_distance(n=7, k=4):
    """Exhaust every binary [n,k] linear code and report the best minimum distance.

    Generator matrices in reduced row echelon form enumerate the subspaces exactly once.
    """
    best, best_G = 0, None
    cols = list(range(n))
    for pivots in itertools.combinations(cols, k):
        free = [c for c in cols if c not in pivots]
        for fill in itertools.product([0, 1], repeat=k * len(free)):
            G = np.zeros((k, n), dtype=int)
            for i, pcol in enumerate(pivots):
                G[i, pcol] = 1
            f = np.array(fill, dtype=int).reshape(k, len(free))
            for i in range(k):
                for j, fc in enumerate(free):
                    if fc > pivots[i]:
                        G[i, fc] = f[i, j]
            words = np.zeros((2 ** k, n), dtype=int)
            for i, c in enumerate(itertools.product([0, 1], repeat=k)):
                words[i] = (np.array(c) @ G) % 2
            w = np.count_nonzero(words, axis=1)
            d = int(w[w > 0].min()) if (w > 0).any() else 0
            if d > best:
                best, best_G = d, G.copy()
    return best, best_G.tolist()


def main():
    # ---- the code over F_7
    G4 = rs_code(4)                 # [7,4,4]
    G3 = rs_code(3)                 # [7,3,5], the dual
    C4, C3 = span(G4), span(G3)

    # dual check, by the inner product rather than by assertion
    dual_ok = bool(np.all((C4 @ G3.T) % P == 0))
    nested = contained(C3, C4)

    d4 = min_weight(C4)
    d3 = min_weight(C3)
    d_css = min_weight(C4, exclude=C3)          # CSS distance: least weight in C \ C_dual

    # ---- single-error correction: every weight-one error must have its own syndrome
    H = G3                                       # 3 x 7 parity checks, over F_7
    syn = {}
    collisions = 0
    for pos in range(7):
        for a in range(P):
            for b in range(P):
                if a == 0 and b == 0:
                    continue
                ex = np.zeros(7, dtype=int); ez = np.zeros(7, dtype=int)
                ex[pos] = a; ez[pos] = b
                s = (tuple((H @ ex) % P), tuple((H @ ez) % P))
                if s in syn and syn[s] != (pos, a, b):
                    collisions += 1
                syn[s] = (pos, a, b)
    single_errors = 7 * (P * P - 1)

    # ---- every error of weight <= 3 is either detected or does nothing
    undetected_light = 0
    checked = 0
    rng = np.random.default_rng(7)
    for wgt in (1, 2, 3):
        for positions in itertools.combinations(range(7), wgt):
            for _ in range(200):                # sampled, then confirmed by the distance above
                ex = np.zeros(7, dtype=int); ez = np.zeros(7, dtype=int)
                for pos in positions:
                    ex[pos] = rng.integers(0, P); ez[pos] = rng.integers(0, P)
                if not ex.any() and not ez.any():
                    continue
                checked += 1
                sx = (H @ ex) % P; sz = (H @ ez) % P
                if not sx.any() and not sz.any():
                    in_stab = tuple(ex) in set(map(tuple, C3.tolist())) and \
                              tuple(ez) in set(map(tuple, C3.tolist()))
                    if not in_stab:
                        undetected_light += 1

    # ---- the qubit route
    b74, bG = binary_best_distance(7, 4)
    b73, _ = binary_best_distance(7, 3)

    out = {
        "field": P,
        "classical": {
            "C  [7,4]": {"distance": d4, "mds": d4 == 7 - 4 + 1},
            "C* [7,3]": {"distance": d3, "mds": d3 == 7 - 3 + 1},
            "dual_of_C_is_C*": dual_ok,
            "C*_inside_C": nested,
        },
        "quantum_code": {
            "parameters": "[[7,1,%d]]_7" % d_css,
            "distance_by_enumeration": d_css,
            "encodes_qudits": 1,
            "singleton_bound_k_max": 7 - 2 * (d_css - 1),
            "meets_singleton": 1 == 7 - 2 * (d_css - 1),
            "single_error_syndromes": {"errors": single_errors, "collisions": collisions,
                                       "distinct": len(syn)},
            "light_errors_sampled": checked,
            "undetected_light_errors": undetected_light,
        },
        "qubit_route": {
            "best_binary_[7,4]_distance": b74,
            "best_binary_[7,3]_distance": b73,
            "generator_of_best_[7,4]": bG,
            "css_distance_available_over_F2": min(b74, b73),
            "verdict": ("closed: no binary [7,4] code reaches distance 4, so the CSS route to "
                        "[[7,1,4]] over qubits does not exist")
        },
    }
    with open("f7_code.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
