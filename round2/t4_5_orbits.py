#!/usr/bin/env python3
"""
HEPTARACT test round 2 -- T-4.5 "Just ratios in planetary orbits".

Implements the pre-registered protocol in
    ../PREREGISTRATION-2026-09-17.md  (section "T-4.5")

Pipeline (end to end):
  1. Download hostname, pl_name, pl_orbper from the NASA Exoplanet Archive
     TAP service, table pscomppars (cached to ../data/pscomppars_periods.csv).
  2. Keep systems with >= 2 planets having non-null periods; sort each system
     by period; form adjacent pairs; r = P_out / P_in; keep 1 < r <= 3.2.
  3. Smooth expectation: Gaussian KDE on ln r, bandwidth h = 0.10 (ln units,
     set explicitly). Expected count in [a, b] (ln space) =
         N * mean_i [ Phi((b - x_i)/h) - Phi((a - x_i)/h) ].
  4. Enrichment E = observed / expected; one-sided Poisson
     p = P(X >= observed | mean = expected).
  5. Windows: primary [q, 1.03 q]; secondary [0.99 q, 1.01 q] (inclusive).
  6. Predictions (primary window only):
       (a) mean E(H) > mean E(first-order rivals)
       (b) E(7/4) > E of every same-order rival.
  7. Solar-system neighbours reported separately (not in N).
  8. Robustness (NOT pre-registered): bandwidth 0.05 and 0.20.

Usage:  python3 t4_5_orbits.py [--refresh]
Output: ../results/t4_5_orbits.json
"""
import hashlib
import io
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.stats import norm, poisson

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RES = ROOT / "results"
PREREG = ROOT / "PREREGISTRATION-2026-09-17.md"
CSV = DATA / "pscomppars_periods.csv"

TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
ADQL = "select hostname, pl_name, pl_orbper from pscomppars"

# ---- Pre-registered constants (do not edit) --------------------------------
R_MIN, R_MAX = 1.0, 3.2            # keep 1 < r <= 3.2
BANDWIDTH = 0.10                   # KDE bandwidth in ln r
PRIMARY = (1.00, 1.03)             # [q, 1.03 q]
SECONDARY = (0.99, 1.01)           # [0.99 q, 1.01 q]
SETS = {
    "H": ["9/8", "6/5", "5/4", "4/3", "3/2", "7/4", "2/1"],
    "first_order_rivals": ["7/6", "8/7", "10/9"],
    "same_order_rivals_of_7/4": ["5/2", "8/5", "10/7", "11/8"],
}
ROBUST_BW = [0.05, 0.20]           # robustness only, not part of verdict

# Standard sidereal periods (days), as specified by the desk.
SOLAR = [("Mercury", 87.969), ("Venus", 224.701), ("Earth", 365.256),
         ("Mars", 686.980), ("Jupiter", 4332.59), ("Saturn", 10759.22),
         ("Uranus", 30688.5), ("Neptune", 60182.0), ("Pluto", 90560.0)]


# ---- Data ------------------------------------------------------------------
def download(refresh=False):
    DATA.mkdir(parents=True, exist_ok=True)
    if CSV.exists() and not refresh:
        return CSV.read_text()
    url = TAP + "?" + urllib.parse.urlencode({"query": ADQL, "format": "csv"})
    with urllib.request.urlopen(url, timeout=120) as f:
        txt = f.read().decode("utf-8")
    CSV.write_text(txt)
    return txt


def load_pairs(txt):
    import csv
    rows = list(csv.DictReader(io.StringIO(txt)))
    systems = {}
    n_null = 0
    for row in rows:
        p = row["pl_orbper"].strip()
        if p == "":
            n_null += 1
            continue
        systems.setdefault(row["hostname"], []).append((float(p), row["pl_name"]))
    multi = {h: sorted(v) for h, v in systems.items() if len(v) >= 2}
    pairs_all, pairs = [], []
    for h, pl in multi.items():
        for (p1, n1), (p2, n2) in zip(pl[:-1], pl[1:]):
            r = p2 / p1
            pairs_all.append(r)
            if R_MIN < r <= R_MAX:
                pairs.append({"host": h, "inner": n1, "outer": n2,
                              "P_in": p1, "P_out": p2, "r": r})
    info = {
        "n_rows": len(rows),
        "n_rows_null_period": n_null,
        "n_systems_with_period": len(systems),
        "n_systems_multi": len(multi),
        "n_planets_in_multi": int(sum(len(v) for v in multi.values())),
        "n_adjacent_pairs_all": len(pairs_all),
        "n_pairs_r_eq_1": int(sum(1 for r in pairs_all if r <= 1.0)),
        "n_pairs_r_gt_3.2": int(sum(1 for r in pairs_all if r > R_MAX)),
        "N_pairs_used": len(pairs),
    }
    return pairs, info


# ---- Statistics ------------------------------------------------------------
def expected_count(x, lo, hi, h):
    """N * integral over [lo, hi] (ln space) of Gaussian KDE with bandwidth h."""
    return float(np.sum(norm.cdf((hi - x) / h) - norm.cdf((lo - x) / h)))


def window_stats(r, x, q, win, h):
    lo_r, hi_r = win[0] * q, win[1] * q
    obs = int(np.sum((r >= lo_r) & (r <= hi_r)))
    exp = expected_count(x, np.log(lo_r), np.log(hi_r), h)
    E = obs / exp if exp > 0 else float("nan")
    p = float(poisson.sf(obs - 1, exp)) if obs > 0 else 1.0
    return {"lo": lo_r, "hi": hi_r, "observed": obs, "expected": exp,
            "E": E, "p_poisson_ge": p}


def analyse(r, h):
    x = np.log(r)
    out = {}
    for sname, ratios in SETS.items():
        out[sname] = {}
        for s in ratios:
            q = float(Fraction(s))
            out[sname][s] = {
                "q": q,
                "primary": window_stats(r, x, q, PRIMARY, h),
                "secondary": window_stats(r, x, q, SECONDARY, h),
            }
    return out


def verdicts(tab):
    def E(sname, s, w="primary"):
        return tab[sname][s][w]["E"]
    mean_H = float(np.mean([E("H", s) for s in SETS["H"]]))
    mean_R1 = float(np.mean([E("first_order_rivals", s)
                             for s in SETS["first_order_rivals"]]))
    e74 = E("H", "7/4")
    so = {s: E("same_order_rivals_of_7/4", s)
          for s in SETS["same_order_rivals_of_7/4"]}
    a = mean_H > mean_R1
    b = all(e74 > v for v in so.values())
    # Secondary window values, reported for information (verdict = primary).
    mean_H2 = float(np.mean([E("H", s, "secondary") for s in SETS["H"]]))
    mean_R12 = float(np.mean([E("first_order_rivals", s, "secondary")
                              for s in SETS["first_order_rivals"]]))
    return {
        "a": {"statement": "mean E(H) > mean E(first-order rivals), primary window",
              "mean_E_H": mean_H, "mean_E_first_order_rivals": mean_R1,
              "verdict": "PASS" if a else "FAIL"},
        "b": {"statement": "E(7/4) > E of every same-order rival, primary window",
              "E_7/4": e74, "E_same_order_rivals": so,
              "verdict": "PASS" if b else "FAIL"},
        "secondary_window_info_only": {"mean_E_H": mean_H2,
                                       "mean_E_first_order_rivals": mean_R12,
                                       "E_7/4": E("H", "7/4", "secondary"),
                                       "E_same_order_rivals": {
                                           s: E("same_order_rivals_of_7/4", s, "secondary")
                                           for s in SETS["same_order_rivals_of_7/4"]}},
    }


def solar_system():
    named = [(s, float(Fraction(s)), k) for k, v in SETS.items() for s in v]
    rows = []
    for (n1, p1), (n2, p2) in zip(SOLAR[:-1], SOLAR[1:]):
        r = p2 / p1
        near = [{"ratio": s, "set": k, "rel_dev": r / q - 1,
                 "in_primary_window": bool(q <= r <= 1.03 * q),
                 "in_secondary_window": bool(0.99 * q <= r <= 1.01 * q)}
                for s, q, k in named if abs(r / q - 1) <= 0.03]
        rows.append({"pair": f"{n1}-{n2}", "r": r,
                     "in_range_1_to_3.2": bool(R_MIN < r <= R_MAX),
                     "named_within_3pct": near})
    return rows


def main():
    txt = download(refresh="--refresh" in sys.argv)
    pairs, info = load_pairs(txt)
    r = np.array([p["r"] for p in pairs])

    tab = analyse(r, BANDWIDTH)
    ver = verdicts(tab)

    robust = {}
    for h in ROBUST_BW:
        t = analyse(r, h)
        robust[str(h)] = {"table": t, "verdicts": verdicts(t)}

    res = {
        "test": "T-4.5 Just ratios in planetary orbits",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "prereg_file_sha256": hashlib.sha256(PREREG.read_bytes()).hexdigest(),
        "data_source": {"tap": TAP, "adql": ADQL,
                        "csv_sha256": hashlib.sha256(txt.encode()).hexdigest()},
        "selection": info,
        "r_summary": {"min": float(r.min()), "max": float(r.max()),
                      "median": float(np.median(r))},
        "kde_bandwidth_ln": BANDWIDTH,
        "windows": {"primary": "[q, 1.03q]", "secondary": "[0.99q, 1.01q]"},
        "table": tab,
        "predictions": ver,
        "solar_system": solar_system(),
        "robustness_NOT_preregistered": robust,
    }
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "t4_5_orbits.json").write_text(json.dumps(res, indent=2))

    # Console summary
    print(json.dumps(info, indent=1))
    for w in ("primary", "secondary"):
        print(f"\n== {w} window, bw={BANDWIDTH}")
        for sname, d in tab.items():
            for s, v in d.items():
                z = v[w]
                print(f"{sname:26s} {s:>5s} obs={z['observed']:4d} exp={z['expected']:7.2f} "
                      f"E={z['E']:.3f} p={z['p_poisson_ge']:.4g}")
    print(json.dumps(ver, indent=1))
    for h, d in robust.items():
        print(f"robust bw={h}: a={d['verdicts']['a']['verdict']} "
              f"({d['verdicts']['a']['mean_E_H']:.3f} vs {d['verdicts']['a']['mean_E_first_order_rivals']:.3f}), "
              f"b={d['verdicts']['b']['verdict']} (E74={d['verdicts']['b']['E_7/4']:.3f}, "
              f"{ {k: round(v, 3) for k, v in d['verdicts']['b']['E_same_order_rivals'].items()} })")
    for s in res["solar_system"]:
        print(s["pair"], round(s["r"], 4), [(n["ratio"], round(n["rel_dev"], 4), n["in_primary_window"]) for n in s["named_within_3pct"]])


if __name__ == "__main__":
    main()
