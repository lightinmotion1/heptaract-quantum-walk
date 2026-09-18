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


def snapshot():
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    n = 0
    with open(LOG, "a") as fh:
        for b in svc.backends(operational=True, simulator=False, min_num_qubits=NQ + 4):
            try:
                row = {"utc": stamp, "backend": b.name, "pending": b.status().pending_jobs}
                row.update(line_stats(b))
                fh.write(json.dumps(row) + "\n")
                n += 1
                print("%-16s worstRO %.4f  medT2 %6.1f  med2q %.5f" %
                      (b.name, row["worst_readout"], row["median_T2_us"], row["median_2q_err"]))
            except Exception as e:
                print("skip", b.name, type(e).__name__)
    print("appended", n, "rows to", LOG)


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


if __name__ == "__main__":
    report() if len(sys.argv) > 1 and sys.argv[1] == "report" else snapshot()
