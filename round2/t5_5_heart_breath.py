#!/usr/bin/env python3
"""
HEPTARACT round 2 -- T-5.5 . Heart and breath at just ratios
Pre-registration: /mnt/user-data/outputs/heptaract-tests/PREREGISTRATION-2026-09-17.md

End-to-end, rerunnable:
  1. download PhysioNet slpdb v1.0.0 (.hea/.dat/.ecg) to /home/claude/hx-data/slpdb, verify SHA-256
  2. per record: 60 s non-overlapping windows; heart rate from 'ecg' beat annotations,
     breathing rate from the respiration channel (priority nasal > chest > abdomen > sum)
  3. rho = f_heart / f_breath, octave-folded rho' = rho / 2^floor(log2 rho) in [1, 2)
  4. reflected Gaussian KDE (bw 0.05, reflection at 1 and 2); +-1% windows; E = obs/exp;
     Poisson p = P(X >= obs)
  5. verdict: PASS iff mean E(H) > 1.2 AND mean E(H) > mean E(rivals)
  6. NOT part of verdict: per-record breakdown, record-level bootstrap (2000 draws),
     exploratory unfolded-rho analysis.

All cleaning thresholds below were fixed before any ratio was computed.
"""
import hashlib
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction

import numpy as np
import wfdb
from scipy.signal import butter, find_peaks, sosfiltfilt
from scipy.special import ndtr
from scipy.stats import poisson

BASE_URL = "https://physionet.org/files/slpdb/1.0.0/"
DATA_DIR = "/home/claude/hx-data/slpdb"
OUT_DIR = "/mnt/user-data/outputs/heptaract-tests/results"
OUT_JSON = os.path.join(OUT_DIR, "t5_5_heart_breath.json")
OUT_CSV = os.path.join(OUT_DIR, "t5_5_heart_breath_windows.csv")

# ---- fixed parameters (pre-registered / fixed by the task brief before data) ----
WIN_S = 60.0
RR_MIN, RR_MAX = 0.3, 2.0            # s
BP_LO, BP_HI, BP_ORDER = 0.1, 0.7, 2  # Hz, zero-phase Butterworth
PEAK_MIN_SPACING_S = 1.5
PEAK_PROM_FRAC = 0.3                 # x window std of the band-passed signal
MIN_BREATHS = 4                      # detected breath peaks per window
FB_MIN, FB_MAX = 0.1, 0.7            # Hz
FH_MIN, FH_MAX = 0.6, 2.5            # Hz
KDE_BW = 0.05                        # rho' units
WIN_HALF = 0.01                      # +-1 %
# slpdb spells the abdominal channel both "Resp (abdomen)" and "Resp (abdominal)"; both are
# treated as the same (third-priority) channel. Only slp61 is affected (its only resp channel).
RESP_PRIORITY = ["Resp (nasal)", "Resp (chest)", ("Resp (abdomen)", "Resp (abdominal)"), "Resp (sum)"]
H_SET = ["9/8", "6/5", "5/4", "4/3", "3/2", "7/4"]
RIVALS = ["7/6", "8/7", "7/5", "8/5", "5/3", "9/5", "11/8", "13/8"]
N_BOOT = 2000
SEED = 20260917
# exploratory (not pre-registered): unfolded rho near integers
EXPL_INTS = [3, 4, 5]
EXPL_LOG_BW = 0.05                   # Gaussian KDE bandwidth in ln(rho)

BEAT_SYMBOLS = set("NLRBAaJSVrFejnE/fQ?")


def q(s):
    return float(Fraction(s))


# ------------------------------------------------------------------ download
def fetch(url, dest):
    tmp = dest + ".part"
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            os.replace(tmp, dest)
            return
        except Exception as e:  # noqa
            err = e
    raise RuntimeError(f"download failed {url}: {err}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    with urllib.request.urlopen(BASE_URL + "RECORDS", timeout=60) as r:
        records = r.read().decode().split()
    with urllib.request.urlopen(BASE_URL + "SHA256SUMS.txt", timeout=60) as r:
        sums = {}
        for line in r.read().decode().splitlines():
            parts = line.split()
            if len(parts) == 2:
                sums[parts[1]] = parts[0]
    needed = [f"{rec}.{ext}" for rec in records for ext in ("hea", "ecg", "dat")]
    needed = [n for n in needed if n in sums]  # only files that exist in the release
    todo = []
    for n in needed:
        p = os.path.join(DATA_DIR, n)
        if not (os.path.exists(p) and sha256(p) == sums[n]):
            todo.append(n)
    if todo:
        print(f"downloading {len(todo)} files ...", flush=True)
        with ThreadPoolExecutor(8) as ex:
            list(ex.map(lambda n: fetch(BASE_URL + n, os.path.join(DATA_DIR, n)), todo))
    bad = [n for n in needed if sha256(os.path.join(DATA_DIR, n)) != sums[n]]
    if bad:
        raise RuntimeError(f"SHA-256 mismatch: {bad}")
    return records, len(needed)


# ------------------------------------------------------------------ per record
def process_record(rec):
    path = os.path.join(DATA_DIR, rec)
    info = {"record": rec}
    if not os.path.exists(path + ".ecg"):
        info["excluded"] = "no ecg annotation file"
        return info, []
    hdr = wfdb.rdheader(path)
    resp = None
    for pr in RESP_PRIORITY:
        names = pr if isinstance(pr, tuple) else (pr,)
        hit = [c for c in names if c in hdr.sig_name]
        if hit:
            resp = hit[0]
            break
    info["resp_channel"] = resp
    info["all_channels"] = hdr.sig_name
    if resp is None:
        info["excluded"] = "no respiration channel"
        return info, []
    fs = float(hdr.fs)
    sig = wfdb.rdrecord(path, channel_names=[resp]).p_signal[:, 0].astype(float)
    n = len(sig)
    info["fs"] = fs
    info["duration_h"] = n / fs / 3600

    # invalid samples (NaN) -> linear interpolation only for filtering; windows containing
    # any invalid raw sample are dropped.
    bad = ~np.isfinite(sig)
    info["n_invalid_resp_samples"] = int(bad.sum())
    if bad.all():
        info["excluded"] = "respiration all invalid"
        return info, []
    if bad.any():
        idx = np.arange(n)
        sig = sig.copy()
        sig[bad] = np.interp(idx[bad], idx[~bad], sig[~bad])
    sos = butter(BP_ORDER, [BP_LO, BP_HI], btype="bandpass", fs=fs, output="sos")
    filt = sosfiltfilt(sos, sig)

    ann = wfdb.rdann(path, "ecg")
    samp = np.asarray(ann.sample)
    sym = np.asarray(ann.symbol)
    isbeat = np.array([s in BEAT_SYMBOLS for s in sym])
    samp, sym = samp[isbeat], sym[isbeat]
    info["beat_symbol_counts"] = {str(s): int((sym == s).sum()) for s in sorted(set(sym))}
    # RR between consecutive beats where both are normal ('N'); assigned by ending beat
    rr = np.diff(samp) / fs
    both_n = (sym[:-1] == "N") & (sym[1:] == "N")
    rr_end = samp[1:]
    ok = both_n & (rr >= RR_MIN) & (rr <= RR_MAX)
    rr, rr_end = rr[ok], rr_end[ok]

    wlen = int(round(WIN_S * fs))
    nwin = n // wlen
    dist = int(round(PEAK_MIN_SPACING_S * fs))
    drops = {"invalid_resp": 0, "no_valid_rr": 0, "flat_resp": 0, "lt4_breaths": 0,
             "f_breath_range": 0, "f_heart_range": 0}
    rows = []
    rr_win = rr_end // wlen
    for k in range(nwin):
        a, b = k * wlen, (k + 1) * wlen
        if bad[a:b].any():
            drops["invalid_resp"] += 1
            continue
        rrk = rr[rr_win == k]
        if len(rrk) == 0:
            drops["no_valid_rr"] += 1
            continue
        fh = 1.0 / rrk.mean()
        seg = filt[a:b]
        sd = seg.std()
        if not np.isfinite(sd) or sd == 0:
            drops["flat_resp"] += 1
            continue
        pk, _ = find_peaks(seg, distance=dist, prominence=PEAK_PROM_FRAC * sd)
        if len(pk) < MIN_BREATHS:
            drops["lt4_breaths"] += 1
            continue
        fb = (len(pk) - 1) / ((pk[-1] - pk[0]) / fs)
        if not (FB_MIN <= fb <= FB_MAX):
            drops["f_breath_range"] += 1
            continue
        if not (FH_MIN <= fh <= FH_MAX):
            drops["f_heart_range"] += 1
            continue
        rows.append((rec, k, fh, fb, len(rrk), len(pk)))
    info["n_windows_total"] = int(nwin)
    info["drops"] = drops
    info["n_windows_kept"] = len(rows)
    return info, rows


# ------------------------------------------------------------------ statistics
def fold(rho):
    return rho / 2.0 ** np.floor(np.log2(rho))


def kde_mass(x, lo, hi, bw=KDE_BW):
    """Mass of reflected KDE (reflection at 1 and 2) in [lo, hi], times N (i.e. expected count)."""
    pts = np.concatenate([x, 2.0 - x, 4.0 - x])
    return float(np.sum(ndtr((hi - pts) / bw) - ndtr((lo - pts) / bw)))


def enrichment(x, ratios):
    out = []
    for r in ratios:
        qv = q(r)
        lo, hi = (1 - WIN_HALF) * qv, (1 + WIN_HALF) * qv
        obs = int(np.sum((x >= lo) & (x <= hi)))
        exp = kde_mass(x, lo, hi)
        out.append({"ratio": r, "value": qv, "window": [lo, hi], "obs": obs,
                    "exp": exp, "E": obs / exp if exp > 0 else float("nan"),
                    "p_poisson_ge": float(poisson.sf(obs - 1, exp)) if exp > 0 else float("nan")})
    return out


def mean_E(tab):
    return float(np.mean([t["E"] for t in tab]))


def main():
    records, nfiles = ensure_data()
    infos, rows = [], []
    for rec in records:
        info, r = process_record(rec)
        infos.append(info)
        rows.extend(r)
        print(rec, info.get("resp_channel"), info.get("n_windows_kept"), info.get("excluded", ""),
              flush=True)

    rec_arr = np.array([r[0] for r in rows])
    fh = np.array([r[2] for r in rows])
    fb = np.array([r[3] for r in rows])
    rho = fh / fb
    rhof = fold(rho)
    N = len(rhof)
    used = sorted(set(rec_arr))

    with open(OUT_CSV, "w") as f:
        f.write("record,window_index,start_s,f_heart_hz,f_breath_hz,n_rr,n_breath_peaks,rho,rho_folded\n")
        for (rec, k, h, b, nrr, npk), r_, rf in zip(rows, rho, rhof):
            f.write(f"{rec},{k},{k*WIN_S:.0f},{h:.6f},{b:.6f},{nrr},{npk},{r_:.6f},{rf:.6f}\n")

    # ---- pre-registered test
    tabH = enrichment(rhof, H_SET)
    tabR = enrichment(rhof, RIVALS)
    mH, mR = mean_E(tabH), mean_E(tabR)
    verdict = "PASS" if (mH > 1.2 and mH > mR) else "FAIL"

    # ---- NOT part of verdict: per record
    per_rec = []
    for rec in used:
        x = rhof[rec_arr == rec]
        tH, tR = enrichment(x, H_SET), enrichment(x, RIVALS)
        info = next(i for i in infos if i["record"] == rec)
        per_rec.append({"record": rec, "resp_channel": info["resp_channel"], "n_windows": int(len(x)),
                        "median_rho": float(np.median(rho[rec_arr == rec])),
                        "obs_H_total": int(sum(t["obs"] for t in tH)),
                        "exp_H_total": float(sum(t["exp"] for t in tH)),
                        "obs_R_total": int(sum(t["obs"] for t in tR)),
                        "exp_R_total": float(sum(t["exp"] for t in tR)),
                        "mean_E_H": mean_E(tH), "mean_E_rivals": mean_E(tR),
                        "diff": mean_E(tH) - mean_E(tR)})

    # ---- NOT part of verdict: record-level bootstrap
    rng = np.random.default_rng(SEED)
    groups = {rec: rhof[rec_arr == rec] for rec in used}
    boot_diff, boot_mH = [], []
    for _ in range(N_BOOT):
        pick = rng.choice(used, size=len(used), replace=True)
        x = np.concatenate([groups[p] for p in pick])
        bh, br = mean_E(enrichment(x, H_SET)), mean_E(enrichment(x, RIVALS))
        boot_diff.append(bh - br)
        boot_mH.append(bh)
    boot_diff, boot_mH = np.array(boot_diff), np.array(boot_mH)

    # ---- exploratory: unfolded rho
    lr = np.log(rho)
    expl_int = []
    for k in EXPL_INTS:
        lo, hi = (1 - WIN_HALF) * k, (1 + WIN_HALF) * k
        obs = int(np.sum((rho >= lo) & (rho <= hi)))
        exp = float(np.sum(ndtr((np.log(hi) - lr) / EXPL_LOG_BW) - ndtr((np.log(lo) - lr) / EXPL_LOG_BW)))
        expl_int.append({"integer": k, "window": [lo, hi], "obs": obs, "exp": exp, "E": obs / exp,
                         "p_poisson_ge": float(poisson.sf(obs - 1, exp))})
    octs = np.floor(np.log2(rho)).astype(int)
    oct_counts = {int(o): int((octs == o).sum()) for o in sorted(set(octs))}
    hist_edges = np.linspace(1, 2, 41)
    hist = np.histogram(rhof, bins=hist_edges)[0]

    drops_total = {}
    for i in infos:
        for kk, v in i.get("drops", {}).items():
            drops_total[kk] = drops_total.get(kk, 0) + v

    res = {
        "test": "T-5.5 Heart and breath at just ratios",
        "preregistration": "/mnt/user-data/outputs/heptaract-tests/PREREGISTRATION-2026-09-17.md",
        "preregistration_sha256": sha256("/mnt/user-data/outputs/heptaract-tests/PREREGISTRATION-2026-09-17.md"),
        "data": {"source": BASE_URL, "n_records_in_db": len(records), "n_files_sha256_verified": nfiles,
                 "n_records_used": len(used), "n_windows_used": int(N),
                 "n_windows_total": int(sum(i.get("n_windows_total", 0) for i in infos)),
                 "drops_total": drops_total},
        "parameters": {
            "window_s": WIN_S, "rr_valid_s": [RR_MIN, RR_MAX], "rr_rule": "consecutive beat annotations both 'N'; RR assigned to window of its ending beat",
            "bandpass_hz": [BP_LO, BP_HI], "butter_order": BP_ORDER,
            "bandpass_note": "scipy butter(2, band) -> 4th-order band-pass, applied with sosfiltfilt (zero-phase) to the whole record",
            "peak_min_spacing_s": PEAK_MIN_SPACING_S, "peak_prominence": "0.3 x std of band-passed signal in the window",
            "min_breath_peaks": MIN_BREATHS,
            "f_breath_rule": "(n_peaks - 1) / (t_last_peak - t_first_peak)",
            "f_breath_hz": [FB_MIN, FB_MAX], "f_heart_hz": [FH_MIN, FH_MAX],
            "resp_priority": RESP_PRIORITY, "kde_bandwidth": KDE_BW,
            "kde_boundary": "reflection at rho'=1 and rho'=2 (data augmented with 2-x and 4-x, normalised by N)",
            "window_half_width": WIN_HALF, "poisson_p": "P(X >= obs | mean = exp)",
            "n_boot": N_BOOT, "seed": SEED},
        "records": infos,
        "enrichment_H": tabH,
        "enrichment_rivals": tabR,
        "mean_E_H": mH, "mean_E_rivals": mR,
        "verdict_rule": "PASS iff mean E(H) > 1.2 AND mean E(H) > mean E(rivals)",
        "verdict": verdict,
        "not_part_of_verdict": {
            "per_record": per_rec,
            "bootstrap_records": {
                "stat": "mean E(H) - mean E(rivals), records resampled with replacement, KDE refit per draw",
                "point": mH - mR,
                "mean": float(boot_diff.mean()),
                "ci95": [float(np.percentile(boot_diff, 2.5)), float(np.percentile(boot_diff, 97.5))],
                "frac_gt_0": float((boot_diff > 0).mean()),
                "mean_E_H_ci95": [float(np.percentile(boot_mH, 2.5)), float(np.percentile(boot_mH, 97.5))],
                "frac_mean_E_H_gt_1.2": float((boot_mH > 1.2).mean())},
        },
        "exploratory": {
            "rho_unfolded": {"median": float(np.median(rho)),
                             "q25": float(np.percentile(rho, 25)), "q75": float(np.percentile(rho, 75)),
                             "min": float(rho.min()), "max": float(rho.max())},
            "f_heart_hz_median": float(np.median(fh)), "f_breath_hz_median": float(np.median(fb)),
            "octave_counts_floor_log2_rho": oct_counts,
            "near_integers": {"window": "+-1%", "expectation": f"Gaussian KDE of ln(rho), bandwidth {EXPL_LOG_BW}, no reflection",
                              "table": expl_int},
            "rho_folded_histogram": {"edges": hist_edges.tolist(), "counts": hist.tolist()},
        },
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(res, f, indent=1)

    print(f"\nN windows = {N}, records = {len(used)}")
    for lab, tab in (("H", tabH), ("rival", tabR)):
        for t in tab:
            print(f"{lab:6s} {t['ratio']:>6s} obs={t['obs']:5d} exp={t['exp']:8.2f} E={t['E']:.3f} p={t['p_poisson_ge']:.3g}")
    print(f"mean E(H) = {mH:.4f}  mean E(rivals) = {mR:.4f}  -> {verdict}")
    print("bootstrap:", res["not_part_of_verdict"]["bootstrap_records"])
    print("exploratory:", json.dumps(res["exploratory"]["rho_unfolded"]), json.dumps(expl_int))
    print("octaves:", oct_counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
