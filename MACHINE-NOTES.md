# Machine notes — what we know about the chips themselves

**Read this before choosing a backend. Add to it after every run.**

The schematic and the built thing are not the same object. IBM publishes calibration; the chip does
something else; and the difference only shows up when a circuit you understand runs on it. This file
is where that difference gets written down, so it accumulates instead of being rediscovered.

Standing rule: **the backend is a declared variable.** Choose it by published criteria before
submitting and say so in the seal. `least_busy()` selects on queue depth, which has no relationship
to the experiment — that is how P-19 ended up on a chip nobody had characterised, produced a
collapse, and had that collapse published and then retracted.

---

## The three we use

### `ibm_kingston` — the one our long circuits belong on
Calibration 2026-09-18: worst readout **0.0335** · median T2 **323.9 µs** · worst T2 on line 152.1 µs · 2q **0.00195**

Best coherence and lowest two-qubit error of the three, with mid-range readout. Every two-hop success
we have is from this machine: P-20 (0.627 of ceiling) and P-21 (0.600), plus P-12, P-14 and P-18.
Queue is usually short. **Default choice for anything with an 8-qubit line or long idles.**

### `ibm_marrakesh` — the one with the cleanest measurement
Calibration 2026-09-18: worst readout **0.0135** · median T2 207.5 µs · **worst T2 on line 35.7 µs** · 2q 0.00266

By far the best readout — a fifth of fez's, a third of kingston's. But its best 8-in-a-row contains a
qubit at **35.7 µs**, against circuits that idle 16 µs, so roughly a third of that qubit's coherence
is gone before the reading. **Good for short, measurement-heavy 5-qubit work** (P-1, P-2, P-4, P-6,
P-7, P-10, P-11, P-13, P-15, P-16, P-17 all ran here and held). **Risky for 8-qubit lines.**

### `ibm_fez` — the one to characterise before trusting
Calibration 2026-09-18: **worst readout 0.0781** · median T2 **152.2 µs** · worst T2 on line 88.0 µs · 2q 0.00221

Worst readout of the three by a wide margin — 2.3× kingston, 5.8× marrakesh — on a line our two-hop
circuits fire ten measurements through, four of them mid-circuit. Lowest coherence too. Our only
two-hop collapse (P-19, 0.062) happened here and has never been reproduced elsewhere.

**This is a suspicion, not a finding.** Inventing a mechanism from a suggestive number is exactly the
error P-20 forced us to retract, and this number is suggestive in exactly that way. P-21's fez leg
recorded its calibration at submission, so when it returns the bond can be read against readout error
across all three machines. Until then fez is *uncharacterised*, not *bad*.

Queue is chronically deep — 65 to 106 pending while kingston sat at 2. Budget wall-clock accordingly.

---

## Open questions this file exists to close

1. **Does the two-hop bond track readout error across machines?** Three points when fez lands. Not
   pre-registered — exploratory, and it must be labelled that way until it earns a seal of its own.
2. **Is between-machine spread larger than within-machine drift?** If one chip wanders as much as the
   chips differ, then a single-day reading does not characterise a chip, and every single-backend
   result in the ledger needs re-reading. `calib_log.py report` answers this once there is a
   fortnight of data.
3. **Which metric actually predicts our failures?** We have one collapse and several successes. The
   honest answer today is that we do not know, and the log is how that changes.

## The tools

```
python3 calib_log.py            # daily snapshot, append-only, no QPU. Step zero of the daily scan.
python3 calib_log.py report     # between-machine spread vs within-machine drift
python3 calib_log.py watch      # flags a machine drifting out of its OWN baseline (needs 4 days)
python3 choose_backend.py --seal  # scores the chips, prints a line for the pre-registration
```

`choose_backend.py` prints a single composite "quality" number. **Trust the component columns over
the composite** — the weighting is ours, and it already disagrees with its own stated priority once:
it says readout dominates, yet marrakesh has the best readout and ranks last, because the ranking is
really driven by worst-T2.

`watch` is the one aimed at prediction. Comparing a chip to other chips only says chips differ;
comparing a chip to its own history is what can warn that something changed — the reading that would
have told us, on the evening P-19 ran, whether that machine was itself.
