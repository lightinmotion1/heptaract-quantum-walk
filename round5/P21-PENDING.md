# P-21 — IN FLIGHT (do not claim anything until both chips are in)

**Pre-registration:** `PREREGISTRATION-2026-09-18-P21.md`
**SHA-256:** `b4835412f84f8d4926351e50004659b82599436d6144f8066acfd09c5e0f89f0`
**Rule from the seal:** H1, H2 and H3 are claimed **only if they hold on BOTH chips**. A pass on one
and a failure on the other is a **split**, reported as chip-dependence, not as a pass.

| chip | job id | state | QPU |
|---|---|---|---|
| `ibm_kingston` | `damc0v5r85ps73fcj3k0` | **DONE, analyzed** | 25 s |
| `ibm_fez` | `damc10o2fm4c73f2og90` | **QUEUED** behind ~65 jobs as of 04:57 UTC | ~25 s expected |

## Kingston, already in hand

two hops **0.551 ± 0.010**, z-correlation 0.637, fidelity **0.685 ± 0.007**
- 42.5 SD over the pooled floor (needs 5) — H1 passes here
- 26.0 SD over the ½ line (needs 3) — H2 passes here
- of ceiling: one hop 0.806, two hops 0.600; multiplicative target 0.649, gap **0.05** (needs ≤0.10) — H3 passes here

Independently replicates P-20's 0.627 of ceiling.

## To finish, in a later session if needed

```
cd ~/Documents/heptaract-quantum-walk/round5
$HOME/qenv/bin/python3 cross_chip.py fetch   ibm_fez
$HOME/qenv/bin/python3 cross_chip.py analyze ibm_fez
$HOME/qenv/bin/python3 cross_chip.py combine
```

Then write `P21-RESULTS.md`, add the receipt to `site/tree.json`, add
`PREREGISTRATION-2026-09-18-P21.md` and `P21-RESULTS.md` to `build_room.py` SOURCES, rebuild, re-seal
with `HEPTARACT_ROOM_PASS`, publish, commit and push. Delete this file when done.

**H4 — the fez reading, already fixed in advance:** below 0.15 = P-19's collapse reproduced and is a
real property of that chip; above 0.40 = it does not reproduce and P-19 was one bad evening; between
the two = ambiguous, and it gets reported as ambiguous with no story attached.
