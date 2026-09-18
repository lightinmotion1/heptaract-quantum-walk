#!/usr/bin/env python3
"""
T-3.1 — Why E?  Scanning every center root against every root-step set.

The tree says: E sits at the center of the five-root climb, and the climb stands at F#. The test
asks whether that centering is FORCED by the from-center reading, or inherited from where the
naming of notes happens to start.

Method: port the Lab v0.2 radial module exactly (its locked self-check values are reproduced
first), then declare a criterion and scan.

  Criterion, declared before the scan:
    primary   — the largest axis magnitude among symmetric spreads
    secondary — an axis that lands exactly on a pitch class (zero cents)
    tertiary  — a spread that is symmetric at all

  python3 t3_1_why_e.py     ->  t3_1_why_e.json
"""
import json, itertools
import numpy as np

TUN = {
    "12tet":       [0, 2, 4, 5, 7, 9, 11],
    "pythagorean": [0, 2.0391, 4.0782, 4.98, 7.0195, 9.0586, 11.0977],
    "just":        [0, 2.0391, 3.8631, 4.98, 7.0195, 8.8436, 10.8827],
}
PN = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def md(a, n=12):
    return ((a % n) + n) % n


def read_from_centre(pcs, o=1):
    """Seven rays on the pitch circle, summed from the shared centre."""
    x = y = 0.0
    for p in pcs:
        a = o * 2 * np.pi * md(p) / 12
        x += np.cos(a); y += np.sin(a)
    m = float(np.hypot(x, y) / len(pcs))
    if m < 1e-9:
        return {"m": 0.0, "st": -1.0, "cents": 0.0, "name": None}
    st = float(md((o * np.arctan2(y, x)) / (2 * np.pi) * 12))
    return {"m": m, "st": st, "cents": float((st - round(st)) * 100), "name": PN[int(md(round(st)))]}


def scale(root, tuning):
    return [md(root + d) for d in TUN[tuning]]


def climb(centre, tuning="12tet", o=1, step=2, n=5):
    """n roots spaced `step` semitones apart, centred on `centre`; each read, then read again."""
    half = (n - 1) // 2
    roots = [md(centre + step * k) for k in range(-half, half + 1)]
    reads = [read_from_centre(scale(r, tuning), o) for r in roots]
    axis = read_from_centre([r["st"] for r in reads], o)
    spread = sorted(md(r["st"] - axis["st"] + 6) - 6 for r in reads)
    sym = all(abs(spread[i] + spread[n - 1 - i]) < 1e-6 for i in range(n // 2))
    return {"roots": [PN[int(md(round(r)))] for r in roots], "axis": axis,
            "spread": [round(s, 4) for s in spread], "symmetric": bool(sym)}


def main():
    out = {}

    # ---- the port is faithful: reproduce the Lab's locked values first
    a = read_from_centre(scale(0, "12tet"))
    b = read_from_centre(scale(0, "pythagorean"))
    c = read_from_centre(scale(0, "just"))
    e = read_from_centre([i * 12 / 7 for i in range(7)])
    f = climb(4, "12tet", 1, 2, 5)
    out["self_check"] = {
        "C major reads": a["name"], "cents_12tet": round(a["cents"], 2),
        "cents_pythagorean": round(b["cents"], 2), "cents_just": round(c["cents"], 2),
        "seven_even_rays_magnitude": round(e["m"], 12),
        "climb_on_E_axis": f["axis"]["name"], "climb_on_E_symmetric": f["symmetric"],
        "passes": (a["name"] == "D" and abs(a["cents"]) < .01 and abs(b["cents"] - 3.93) < .01
                   and abs(c["cents"] - 38.49) < .01 and f["axis"]["name"] == "F#"
                   and f["symmetric"] and e["m"] < 1e-12),
    }

    # ---- the scan the test asks for: every centre root x every root-step set
    rows = []
    for tuning in TUN:
        for o in (1, -1):
            for step in range(1, 7):
                for centre in range(12):
                    cl = climb(centre, tuning, o, step, 5)
                    rows.append({"tuning": tuning, "orientation": o, "step": step,
                                 "centre": PN[centre], "axis": cl["axis"]["name"],
                                 "axis_offset_semitones": round(md(cl["axis"]["st"] - centre + 6) - 6, 4),
                                 "magnitude": round(cl["axis"]["m"], 6),
                                 "cents": round(cl["axis"]["cents"], 4),
                                 "symmetric": cl["symmetric"]})
    out["scan_rows"] = len(rows)

    # does anything single out a centre?
    by_centre = {}
    for r in rows:
        by_centre.setdefault(r["centre"], []).append(r["magnitude"])
    spread_across_centres = {k: (round(min(v), 9), round(max(v), 9)) for k, v in by_centre.items()}
    mags_per_config = {}
    for r in rows:
        key = (r["tuning"], r["orientation"], r["step"])
        mags_per_config.setdefault(key, set()).add(round(r["magnitude"], 9))
    identical_across_centres = all(len(v) == 1 for v in mags_per_config.values())

    offsets = {}
    for r in rows:
        offsets.setdefault((r["tuning"], r["orientation"], r["step"]), set()).add(r["axis_offset_semitones"])
    offset_is_fixed = all(len(v) == 1 for v in offsets.values())

    best = max(rows, key=lambda r: (r["symmetric"], r["magnitude"]))
    winners = [r for r in rows if r["symmetric"] and abs(r["magnitude"] - best["magnitude"]) < 1e-9]
    winning_centres = sorted(set(r["centre"] for r in winners))
    winning_steps = sorted(set(r["step"] for r in winners))

    out["criterion"] = {
        "primary": "largest axis magnitude among symmetric spreads",
        "best_magnitude": round(best["magnitude"], 6),
        "how_many_configurations_tie": len(winners),
        "centres_that_tie": winning_centres,
        "steps_that_tie": winning_steps,
        "E_is_unique_maximiser": winning_centres == ["E"],
    }
    out["structure"] = {
        "magnitude_identical_across_centres": identical_across_centres,
        "axis_offset_from_centre_is_fixed_per_configuration": offset_is_fixed,
        "magnitude_range_per_centre": spread_across_centres,
    }

    # what the criterion DOES pick out, if not a centre
    by_step = {}
    for r in rows:
        if r["tuning"] == "12tet" and r["orientation"] == 1:
            by_step.setdefault(r["step"], []).append((r["magnitude"], r["symmetric"]))
    out["by_step_12tet"] = {str(s): {"magnitude": round(v[0][0], 6),
                                     "symmetric": bool(all(x[1] for x in v))}
                            for s, v in sorted(by_step.items())}

    # the five roots of the climb, for the record
    out["climb_examples"] = {PN[c]: climb(c, "12tet", 1, 2, 5)["roots"] for c in (0, 4, 7)}

    with open("t3_1_why_e.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("self_check", "criterion", "structure", "by_step_12tet",
                                          "climb_examples")}, indent=1))


if __name__ == "__main__":
    main()
