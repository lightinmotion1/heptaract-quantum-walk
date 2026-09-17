#!/usr/bin/env python3
"""
HEPTARACT test round 2 -- T-4.1 "Where alpha peaks sit".

Implements the pre-registered protocol in
    ../PREREGISTRATION-2026-09-17.md  (section "T-4.1")

Pipeline (end to end):
  1. Download run R02 (eyes-closed baseline) for S001..S109 from PhysioNet
     eegmmidb v1.0.0 into /home/claude/hx-data/eegmmidb/ (raw data > 50 MB,
     so kept outside the outputs folder). Missing files are skipped.
  2. Read EDF with mne; pick O1, Oz, O2 (labels like 'O1..' -> strip dots);
     average the three signals sample by sample.
  3. Welch PSD: Hann window, 8 s segments, 50 % overlap (nperseg = 8*fs).
  4. IAF = argmax of the PSD over bins with 7 <= f <= 14 Hz, refined by
     parabolic interpolation on log10(PSD) using bins k-1, k, k+1.
     Implementation detail (not in the protocol text): the parabolic offset is
     clipped to [-0.5, +0.5] bin, and if the three points are not concave
     (possible only when the argmax sits on a band edge) no refinement is
     applied. Peaks whose argmax bin is 7.0 Hz or 14.0 Hz are flagged as
     edge peaks; they are kept (the protocol says "every subject").
  5. Fit a Gaussian (ML mean, sd) to all IAFs. Expected count in band
     [lo, hi] = N * (Phi(hi) - Phi(lo)). E = obs/exp; one-sided Poisson
     p = P(X >= obs | exp).
  6. Bands (+-0.2 Hz, inclusive): H1 8.81, H2 13.70, rivals 8.30, 9.30, 10.30.
     H1 PASS iff E(8.81) > 1 and p < 0.05 and E(8.81) > E of every rival.
     H2 PASS iff E(13.70) > 1 and p < 0.05.

Usage:  python3 t4_1_alpha.py
Output: ../results/t4_1_alpha.json (+ ../data/t4_1_iaf_per_subject.csv)
"""
import csv
import hashlib
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.signal import welch
from scipy.stats import norm, poisson

import mne

mne.set_log_level("ERROR")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RES = ROOT / "results"
PREREG = ROOT / "PREREGISTRATION-2026-09-17.md"
RAW = Path("/home/claude/hx-data/eegmmidb")
BASE = "https://physionet.org/files/eegmmidb/1.0.0"

# ---- Pre-registered constants (do not edit) --------------------------------
SUBJECTS = [f"S{i:03d}" for i in range(1, 110)]
RUN = "R02"
CHANNELS = ["O1", "Oz", "O2"]
SEG_SEC = 8.0
OVERLAP = 0.5
FMIN, FMAX = 7.0, 14.0
HALF_BAND = 0.2
BANDS = {"H1": 8.81, "H2": 13.70, "rival_8.30": 8.30,
         "rival_9.30": 9.30, "rival_10.30": 10.30}
RIVALS = ["rival_8.30", "rival_9.30", "rival_10.30"]
ALPHA_P = 0.05


# ---- Download --------------------------------------------------------------
def fetch(subj):
    dest = RAW / subj / f"{subj}{RUN}.edf"
    if dest.exists() and dest.stat().st_size > 0:
        return subj, dest, None
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{BASE}/{subj}/{subj}{RUN}.edf"
    err = None
    for attempt in range(6):  # retry transient network errors with backoff
        try:
            with urllib.request.urlopen(url, timeout=120) as f:
                data = f.read()
            err = None
            break
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
            if e.code == 404:
                break
        except Exception as e:  # connection reset etc.
            err = repr(e)
        time.sleep(2 * (attempt + 1))
    if err is not None:
        return subj, None, err
    tmp = dest.with_suffix(".part")
    tmp.write_bytes(data)
    tmp.rename(dest)
    return subj, dest, None


# ---- Signal processing -----------------------------------------------------
def iaf_for_file(path):
    raw = mne.io.read_raw_edf(path, preload=True, verbose="ERROR")
    fs = float(raw.info["sfreq"])
    names = {ch.replace(".", ""): ch for ch in raw.ch_names}
    missing = [c for c in CHANNELS if c not in names]
    if missing:
        raise ValueError(f"missing channels {missing}")
    sig = raw.get_data(picks=[names[c] for c in CHANNELS]).mean(axis=0)
    nper = int(round(SEG_SEC * fs))
    f, pxx = welch(sig, fs=fs, window="hann", nperseg=nper,
                   noverlap=int(round(nper * OVERLAP)), detrend="constant",
                   scaling="density")
    band = np.where((f >= FMIN - 1e-9) & (f <= FMAX + 1e-9))[0]
    k = band[np.argmax(pxx[band])]
    df = f[1] - f[0]
    edge = "low" if k == band[0] else ("high" if k == band[-1] else None)
    # Parabolic interpolation on log-PSD around the peak bin.
    y0, y1, y2 = np.log10(pxx[k - 1: k + 2])
    denom = y0 - 2 * y1 + y2
    if denom < 0:  # concave: a true local maximum of the parabola
        delta = float(np.clip(0.5 * (y0 - y2) / denom, -0.5, 0.5))
    else:
        delta = 0.0
    return {"fs": fs, "n_samples": int(sig.size), "duration_s": sig.size / fs,
            "n_welch_segments": int(1 + (sig.size - nper) // (nper - int(round(nper * OVERLAP)))),
            "df": float(df), "peak_bin_hz": float(f[k]), "iaf": float(f[k] + delta * df),
            "delta_bins": delta, "edge": edge}


# ---- Statistics ------------------------------------------------------------
def band_stats(iaf, mu, sd, c):
    lo, hi = c - HALF_BAND, c + HALF_BAND
    n = len(iaf)
    obs = int(np.sum((iaf >= lo) & (iaf <= hi)))
    exp = float(n * (norm.cdf(hi, mu, sd) - norm.cdf(lo, mu, sd)))
    E = obs / exp if exp > 0 else float("nan")
    p = float(poisson.sf(obs - 1, exp)) if obs > 0 else 1.0
    return {"center": c, "lo": lo, "hi": hi, "observed": obs,
            "expected": exp, "E": E, "p_poisson_ge": p}


def main():
    with ThreadPoolExecutor(max_workers=3) as ex:
        dl = list(ex.map(fetch, SUBJECTS))
    skipped = {s: err for s, p, err in dl if p is None}

    per = []
    for subj, path, err in dl:
        if path is None:
            continue
        try:
            d = iaf_for_file(path)
        except Exception as e:
            skipped[subj] = f"read/process error: {e!r}"
            continue
        d["subject"] = subj
        d["file_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        per.append(d)

    iaf = np.array([d["iaf"] for d in per])
    n = len(iaf)
    mu, sd = norm.fit(iaf)  # maximum-likelihood mean and sd (ddof=0)

    bands = {k: band_stats(iaf, mu, sd, c) for k, c in BANDS.items()}
    h1, h2 = bands["H1"], bands["H2"]
    h1_parts = {
        "E_gt_1": h1["E"] > 1,
        "p_lt_0.05": h1["p_poisson_ge"] < ALPHA_P,
        "E_exceeds_every_rival": all(h1["E"] > bands[r]["E"] for r in RIVALS),
    }
    h2_parts = {"E_gt_1": h2["E"] > 1, "p_lt_0.05": h2["p_poisson_ge"] < ALPHA_P}

    # 0.25 Hz bins aligned to 7.0 Hz, widened to cover every IAF (the
    # interpolation can move an edge peak slightly outside 7-14 Hz).
    lo_e = FMIN - 0.25 * np.ceil(max(0.0, FMIN - iaf.min()) / 0.25)
    hi_e = FMAX + 0.25 * np.ceil(max(0.0, iaf.max() - FMAX) / 0.25 + 1e-9)
    edges = np.arange(lo_e, hi_e + 1e-9, 0.25)
    hist, _ = np.histogram(iaf, bins=edges)
    fs_counts = {}
    for d in per:
        fs_counts[str(d["fs"])] = fs_counts.get(str(d["fs"]), 0) + 1

    res = {
        "test": "T-4.1 Where alpha peaks sit",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "prereg_file_sha256": hashlib.sha256(PREREG.read_bytes()).hexdigest(),
        "data_source": f"{BASE}/SxxxR02.edf",
        "N_subjects_used": n,
        "skipped_subjects": skipped,
        "sampling_rates": fs_counts,
        "method": {"channels": CHANNELS, "average": "time-domain mean of O1, Oz, O2",
                   "welch": {"window": "hann", "segment_s": SEG_SEC, "overlap": OVERLAP,
                             "detrend": "constant", "nperseg": "8*fs"},
                   "iaf": "argmax PSD in [7,14] Hz + parabolic interpolation on log10 PSD "
                          "(offset clipped to +-0.5 bin; no refinement if not concave)",
                   "gaussian_fit": "ML (numpy std ddof=0)"},
        "iaf_summary": {"mean": float(mu), "sd_ml": float(sd),
                        "sd_ddof1": float(np.std(iaf, ddof=1)),
                        "median": float(np.median(iaf)),
                        "min": float(iaf.min()), "max": float(iaf.max()),
                        "n_edge_low_7Hz": int(sum(d["edge"] == "low" for d in per)),
                        "n_edge_high_14Hz": int(sum(d["edge"] == "high" for d in per)),
                        "edge_subjects": {d["subject"]: d["edge"] for d in per if d["edge"]},
                        "histogram_0.25Hz": [{"lo": float(a), "hi": float(b), "count": int(c)}
                                             for a, b, c in zip(edges[:-1], edges[1:], hist)]},
        "bands": bands,
        "predictions": {
            "H1": {"statement": "E(8.81) > 1 with Poisson p < 0.05, and E(8.81) exceeds every rival band's E",
                   "parts": h1_parts,
                   "rival_E": {r: bands[r]["E"] for r in RIVALS},
                   "verdict": "PASS" if all(h1_parts.values()) else "FAIL"},
            "H2": {"statement": "E(13.70) > 1 with Poisson p < 0.05",
                   "parts": h2_parts,
                   "verdict": "PASS" if all(h2_parts.values()) else "FAIL"},
        },
        "per_subject": per,
    }
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "t4_1_alpha.json").write_text(json.dumps(res, indent=2))
    with open(DATA / "t4_1_iaf_per_subject.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["subject", "fs", "duration_s", "peak_bin_hz", "iaf", "edge"])
        for d in per:
            w.writerow([d["subject"], d["fs"], round(d["duration_s"], 3),
                        d["peak_bin_hz"], round(d["iaf"], 4), d["edge"] or ""])

    # Console summary
    print("N =", n, "skipped:", skipped, "fs:", fs_counts)
    print({k: v for k, v in res["iaf_summary"].items() if k != "histogram_0.25Hz"})
    for h in res["iaf_summary"]["histogram_0.25Hz"]:
        print(f"  {h['lo']:6.2f}-{h['hi']:6.2f} {'#' * h['count']} {h['count']}")
    for k, b in bands.items():
        print(f"{k:12s} [{b['lo']:.2f},{b['hi']:.2f}] obs={b['observed']:3d} "
              f"exp={b['expected']:6.2f} E={b['E']:.3f} p={b['p_poisson_ge']:.4g}")
    print(json.dumps(res["predictions"], indent=1))


if __name__ == "__main__":
    main()
