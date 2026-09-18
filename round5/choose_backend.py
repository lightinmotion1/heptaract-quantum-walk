#!/usr/bin/env python3
"""
Backend chooser — so the chip stops being an accident.

Until now every hardware test picked its machine with `least_busy()`. That selects on QUEUE DEPTH,
which has nothing to do with the experiment. P-19 ran on ibm_fez for no reason other than that fez
happened to be empty, produced a collapse, and that collapse was published and then retracted. The
backend was an uncontrolled variable that got reasoned about as though it were a finding.

This scores the machines on what our circuits actually lean on, and prints a line meant to be pasted
into a pre-registration BEFORE the run — so the chip is a declared choice with a stated reason, and a
later disagreement between machines is data rather than a confound.

What the two-hop circuits lean on, in order:

    mid-circuit measurement and reset   the element P-19/P-20 disagreed over; readout error is the
                                        best proxy the API exposes
    T2 along the line                   the carriers idle through both readings
    two-qubit gate error                three Bell pairs plus four parity gates
    an 8-in-a-row line that has all three at once

  python3 choose_backend.py            score every operational machine
  python3 choose_backend.py --seal     also print the pre-registration line
"""
import json, math, sys

NQ = 8


def best_line(backend, length=NQ):
    t = backend.target
    two = next(x for x in ("cz", "ecr", "cx") if x in t.operation_names)
    err2 = {tuple(q): p.error for q, p in t[two].items() if p is not None and p.error is not None}
    ro = {q[0]: (p.error if p and p.error is not None else .05) for q, p in t["measure"].items()}
    t2 = {}
    for q in range(backend.num_qubits):
        try:
            t2[q] = (backend.qubit_properties(q).t2 or 1e-6) * 1e6
        except Exception:
            t2[q] = 1.0
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
    line = beam[0][0]
    return {
        "line": line,
        "median_T2_us": round(sorted(t2[q] for q in line)[len(line) // 2], 1),
        "worst_T2_us": round(min(t2[q] for q in line), 1),
        "median_readout": round(sorted(ro.get(q, .05) for q in line)[len(line) // 2], 4),
        "worst_readout": round(max(ro.get(q, .05) for q in line), 4),
        "median_2q_err": round(sorted(ee(line[i], line[i + 1])
                                     for i in range(len(line) - 1))[len(line) // 2], 5),
    }


def score(m):
    """One number, weighted the way the circuits are. Readout dominates because the whole test
    turns on two rounds of mid-circuit measurement and reset."""
    return round(
        2.0 * math.log(1 - m["worst_readout"])          # the weakest measurement sets the ceiling
        + 1.0 * math.log(1 - m["median_readout"])
        + 0.6 * math.log(max(m["worst_T2_us"], 1) / 100.0)
        + 1.2 * math.log(1 - m["median_2q_err"]) * 7, 4)


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    rows = []
    for b in svc.backends(operational=True, simulator=False, min_num_qubits=NQ + 4):
        try:
            m = best_line(b)
            st = b.status()
            m.update({"backend": b.name, "pending": st.pending_jobs, "quality": score(m)})
            rows.append(m)
        except Exception as e:
            print("skip", b.name, type(e).__name__)
    rows.sort(key=lambda r: -r["quality"])

    print("%-16s %8s %8s %9s %9s %9s %7s" %
          ("backend", "quality", "pending", "medT2us", "worstRO", "med2q", "line"))
    for r in rows:
        print("%-16s %8.4f %8d %9.1f %9.4f %9.5f  %s" %
              (r["backend"], r["quality"], r["pending"], r["median_T2_us"],
               r["worst_readout"], r["median_2q_err"], r["line"][:3]))

    if rows:
        best = rows[0]
        fastest = min(rows, key=lambda r: r["pending"])
        print()
        print("BEST QUALITY :", best["backend"], "· quality", best["quality"],
              "· queue", best["pending"])
        print("SHORTEST WAIT:", fastest["backend"], "· quality", fastest["quality"],
              "· queue", fastest["pending"])
        if best["backend"] != fastest["backend"]:
            print()
            print("These disagree. Pick on QUALITY and say so in the seal; the queue is not a reason.")
        if "--seal" in sys.argv:
            print()
            print("--- paste into the pre-registration, before submitting ---")
            print("**Backend, chosen in advance and why.** `%s`, selected by a fixed published"
                  % best["backend"])
            print("criterion rather than by queue depth: worst readout error %.4f along the chosen"
                  % best["worst_readout"])
            print("8-qubit line, median T2 %.1f us, median two-qubit error %.5f. The line is %s."
                  % (best["median_T2_us"], best["median_2q_err"], best["line"]))
            print("Queue depth was %d and played no part in the choice." % best["pending"])
        json.dump(rows, open("backend_scores.json", "w"), indent=1)


if __name__ == "__main__":
    main()
