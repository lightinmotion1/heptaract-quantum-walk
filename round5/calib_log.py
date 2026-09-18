#!/usr/bin/env python3
"""
Daily calibration snapshot — building the variance picture for free.

Pulling calibration costs no QPU. Run this once a day and by the time the allowance replenishes there
is a month of drift data to correlate against every hardware result in the ledger.

The point is not to rank the machines. It is to answer questions the ledger cannot currently answer:

    How much does one machine move between two days?
    Is the spread BETWEEN machines larger than the spread WITHIN one machine over time?
    When two runs of the same circuit disagree, was the chip different that day, or is the chip
        always that way?

That last one is the question P-19 and P-20 could not settle, because nobody was writing the
calibration down.

Appends one row per backend per run to calib_log.jsonl — append-only, never rewritten.

  python3 calib_log.py          snapshot every operational machine
  python3 calib_log.py report   summarise drift so far
  python3 calib_log.py watch    flag any machine drifting out of its OWN baseline
  python3 calib_log.py cadence  how often each machine is actually recalibrated
"""
import json, math, sys, time
from pathlib import Path

NQ = 8
HERE = Path(__file__).resolve().parent
LOG = (HERE.parent / "results" if (HERE.parent / "results").exists() else HERE) / "calib_log.jsonl"


def line_stats(backend, length=NQ):
    t = backend.target
    two = next(x for x in ("cz", "ecr", "cx") if x in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else .05) for q, p in t["measure"].items()}
    t1, t2 = {}, {}
    for q in range(backend.num_qubits):
        try:
            p = backend.qubit_properties(q)
            t1[q] = (p.t1 or 1e-6) * 1e6
            t2[q] = (p.t2 or 1e-6) * 1e6
        except Exception:
            t1[q] = t2[q] = 1.0
    adj = {}
    for (a, b), e in err2.items():
        if e < .04:
            adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    def ee(a, b): return min(err2.get((a, b), 1.), err2.get((b, a), 1.))
    def sc(q): return math.log(1 - ro.get(q, .05)) + 0.8 * math.log(max(t2.get(q, 1.), 1.))
    beam = [([q], sc(q)) for q in adj]
    for _ in range(length - 1):
        nxt = []
        for path, s in beam:
            for nb in adj.get(path[-1], ()):
                if nb in path: continue
                nxt.append((path + [nb], s + math.log(1 - ee(path[-1], nb)) + sc(nb)))
        nxt.sort(key=lambda x: -x[1]); beam = nxt[:600]
    beam.sort(key=lambda x: -x[1])
    ln = beam[0][0]
    med = lambda v: sorted(v)[len(v) // 2]
    return {
        "line": ln,
        "worst_readout": round(max(ro.get(q, .05) for q in ln), 5),
        "median_readout": round(med([ro.get(q, .05) for q in ln]), 5),
        "worst_T2_us": round(min(t2[q] for q in ln), 1),
        "median_T2_us": round(med([t2[q] for q in ln]), 1),
        "median_T1_us": round(med([t1[q] for q in ln]), 1),
        "median_2q_err": round(med([ee(ln[i], ln[i + 1]) for i in range(len(ln) - 1)]), 6),
        # the whole-chip view too, so a bad line is distinguishable from a bad chip
        "chip_median_readout": round(med(list(ro.values())), 5),
        "chip_median_T2_us": round(med(list(t2.values())), 1),
    }


def _last_rows():
    """Most recent logged row per backend, for de-duplication."""
    out = {}
    if LOG.exists():
        for l in open(LOG):
            if l.strip():
                r = json.loads(l)
                out[r["backend"]] = r
    return out


def _calibrated_at(b):
    """IBM's own calibration timestamp, when the API exposes one. This is the field that says
    whether a run sat early or late in a calibration cycle."""
    try:
        pr = b.properties()
        d = getattr(pr, "last_update_date", None)
        if d:
            return d.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        pass
    return None


# fields that define "the machine is unchanged"; utc and pending deliberately excluded
FINGERPRINT = ("line", "worst_readout", "median_readout", "worst_T2_us", "median_T2_us",
               "median_T1_us", "median_2q_err", "chip_median_readout", "chip_median_T2_us")
HEARTBEAT_HOURS = 12


def snapshot(force=False):
    """Append only when a machine has actually moved, plus a heartbeat every HEARTBEAT_HOURS.

    IBM's published numbers change only on recalibration, so sampling faster than that cadence would
    write duplicate rows and bury the signal. Skipping the duplicates means every row in the log is
    either a real change or a proof of steadiness, and the gap between rows measures the cadence
    itself."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    now = time.time()
    prev = _last_rows()
    n = skipped = 0
    with open(LOG, "a") as fh:
        for b in svc.backends(operational=True, simulator=False, min_num_qubits=NQ + 4):
            try:
                row = {"utc": stamp, "backend": b.name, "pending": b.status().pending_jobs,
                       "calibrated_at": _calibrated_at(b)}
                row.update(line_stats(b))
                old = prev.get(b.name)
                same = old is not None and all(old.get(k) == row.get(k) for k in FINGERPRINT)
                stale = True
                if old:
                    try:
                        age = now - time.mktime(time.strptime(old["utc"], "%Y-%m-%dT%H:%M:%SZ"))
                        stale = age >= HEARTBEAT_HOURS * 3600
                    except Exception:
                        stale = True
                if same and not stale and not force:
                    skipped += 1
                    print("%-16s unchanged" % b.name)
                    continue
                row["changed"] = (not same)
                fh.write(json.dumps(row) + "\n")
                n += 1
                print("%-16s %-9s worstRO %.4f  medT2 %6.1f  med2q %.5f" %
                      (b.name, "CHANGED" if not same else "heartbeat",
                       row["worst_readout"], row["median_T2_us"], row["median_2q_err"]))
            except Exception as e:
                print("skip", b.name, type(e).__name__)
    print("appended %d row(s), %d unchanged, to %s" % (n, skipped, LOG))
    return n


def report():
    if not LOG.exists():
        print("no log yet"); return
    rows = [json.loads(l) for l in open(LOG) if l.strip()]
    by = {}
    for r in rows:
        by.setdefault(r["backend"], []).append(r)
    print("%-16s %5s %22s %22s" % ("backend", "days", "worst_readout", "median_T2_us"))
    print("%-16s %5s %22s %22s" % ("", "", "min..max  (spread)", "min..max  (spread)"))
    summary = {}
    for bk, rs in sorted(by.items()):
        ro = [r["worst_readout"] for r in rs]
        t2 = [r["median_T2_us"] for r in rs]
        summary[bk] = {"n": len(rs), "readout_spread": round(max(ro) - min(ro), 5),
                       "T2_spread_us": round(max(t2) - min(t2), 1)}
        print("%-16s %5d  %.4f..%.4f (%.4f)  %6.1f..%6.1f (%5.1f)" %
              (bk, len(rs), min(ro), max(ro), max(ro) - min(ro),
               min(t2), max(t2), max(t2) - min(t2)))
    if len(by) > 1 and all(v["n"] >= 2 for v in summary.values()):
        within = max(v["readout_spread"] for v in summary.values())
        latest = {bk: rs[-1]["worst_readout"] for bk, rs in by.items()}
        between = max(latest.values()) - min(latest.values())
        print()
        print("widest drift WITHIN one machine : %.4f" % within)
        print("spread BETWEEN machines, latest : %.4f" % between)
        print(">> the machines differ more than any one of them drifts"
              if between > within else
              ">> one machine drifts as much as the machines differ — a single-day"
              " reading of a chip does not characterise that chip")
    else:
        print("\n(need at least two snapshots per machine before drift means anything)")


def cadence():
    """How often does each machine actually move? Written so that next month's tests can be aimed
    at a machine whose recalibration rhythm is known rather than guessed."""
    if not LOG.exists():
        print("no log yet"); return
    rows = [json.loads(l) for l in open(LOG) if l.strip()]
    by = {}
    for r in rows:
        by.setdefault(r["backend"], []).append(r)
    print("%-16s %7s %9s %28s" % ("backend", "rows", "changes", "mean hours between changes"))
    for bk, rs in sorted(by.items()):
        ch = [r for r in rs if r.get("changed")]
        gaps = []
        for a, b in zip(ch, ch[1:]):
            try:
                ta = time.mktime(time.strptime(a["utc"], "%Y-%m-%dT%H:%M:%SZ"))
                tb = time.mktime(time.strptime(b["utc"], "%Y-%m-%dT%H:%M:%SZ"))
                gaps.append((tb - ta) / 3600.0)
            except Exception:
                pass
        mean = ("%.1f" % (sum(gaps) / len(gaps))) if gaps else "-"
        print("%-16s %7d %9d %28s" % (bk, len(rs), len(ch), mean))
    print()
    print("A run is read against the calibration in force when it ran; 'calibrated_at' carries")
    print("IBM's own timestamp where the API exposes one.")


def _mad(v):
    if not v:
        return 0.0
    m = sorted(v)[len(v) // 2]
    d = sorted(abs(x - m) for x in v)
    return d[len(d) // 2] or 1e-9


METRICS = ["worst_readout", "median_readout", "worst_T2_us", "median_T2_us",
           "median_2q_err", "chip_median_readout", "chip_median_T2_us"]
WORSE_WHEN_HIGH = {"worst_readout", "median_readout", "median_2q_err", "chip_median_readout"}


def watch(k=3.0):
    """Flag a machine drifting out of its OWN baseline.

    Comparing a chip to other chips says only that chips differ. Comparing a chip to its own history
    is what can warn that something changed - which is the reading that would have told us, on the
    evening P-19 ran, that the machine was not itself."""
    if not LOG.exists():
        print("no log yet"); return
    rows = [json.loads(l) for l in open(LOG) if l.strip()]
    by = {}
    for r in rows:
        by.setdefault(r["backend"], []).append(r)
    any_flag = False
    for bk, rs in sorted(by.items()):
        if len(rs) < 4:
            print("%-16s %d snapshot(s) - need 4 before a baseline means anything" % (bk, len(rs)))
            continue
        hist, now = rs[:-1], rs[-1]
        flags = []
        for m in METRICS:
            v = [r[m] for r in hist if m in r]
            if not v or m not in now:
                continue
            med = sorted(v)[len(v) // 2]
            z = (now[m] - med) / (1.4826 * _mad(v))
            if abs(z) >= k:
                worse = (z > 0) if m in WORSE_WHEN_HIGH else (z < 0)
                flags.append("%s %.4g -> %.4g (%+.1f MAD, %s)"
                             % (m, med, now[m], z, "WORSE" if worse else "better"))
        if flags:
            any_flag = True
            print("%-16s DRIFTED" % bk)
            for f in flags:
                print("                 " + f)
        else:
            print("%-16s steady across %d snapshots" % (bk, len(rs)))
    if any_flag:
        print()
        print("A drifted machine is not disqualified - it is a machine whose result must be read")
        print("against its condition that day. Record the flag in the pre-registration.")


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    {"report": report, "watch": watch, "cadence": cadence}.get(a, snapshot)()
