# HEPTARACT round 4: the return at seven

**Run:** 2026-09-18 UTC, ibm_marrakesh, job `dam81778gn2s739kvg7g` · qubits [98, 91, 92] · 4096 shots per circuit
**QPU time:** 41 seconds
**Pre-registration:** `PREREGISTRATION-2026-09-17c.md`
**SHA-256:** `428405b7a8207c51716c4724b4e2138ea0cff1eeb9e1520ef29fedbaace14b6e`
**Desk:** Free (Miah J. Fry) & Claude

The first test built on Free's own framing rather than adapted to it: seven is a rest, and the
eighth is the return home and the first step of the next round at once. Over three bits, 𝔽₈ says
the same in algebra — the seven nonzero elements form one cycle and α⁷ = α⁰.

| Test | Prediction | Verdict |
|---|---|---|
| P-6 | The 𝔽₈ cycle comes home at seven and nowhere before, and its return beats the counter's return at eight | **Holds** (0.996 at seven vs 0.697 at eight, z = 41.13) |
| P-7 | The 𝔽₈ orbit reads seven distinct states — every nonzero state, once | **Holds** (7 of 7, weakest reading 0.9373) |

## P-6 · The return

A three-qubit register is prepared as (|000⟩ + |011⟩)/√2, stepped k times, then unprepared.
Reading 000 is likely only when the map has come home. Away from home the ideal value is 0.25.

| Steps k | 𝔽₈ cycle reads 000 | Counter mod 8 reads 000 |
|---|---|---|
| 1 | 0.2559 | 0.0125 |
| 2 | 0.2668 | 0.0073 |
| 3 | 0.2830 | 0.2734 |
| 4 | 0.2312 | 0.0320 |
| 5 | 0.2332 | 0.2397 |
| 6 | 0.2266 | 0.0222 |
| 7 | 0.9956 | 0.0354 |
| 8 | — | 0.6973 |

- **𝔽₈ comes home at seven: 0.9956.** Nowhere before: the worst wandering value is
  0.283, against an ideal 0.25.
- **The counter comes home at eight: 0.6973.** Its own return, on its own period,
  on the same three qubits, in the same job — and a third of the coherence is already gone.
- Two-qubit gates at the return: **0 for the seven-cycle**, 90 for the eight-counter.

**Reading.** The seven-cycle is the return three bits give away for free. Because 𝔽₈'s
multiplication is linear over 𝔽₂, every step is CNOTs alone; the counter needs a Toffoli each step
and pays for the extra number. This was declared before the run: the win is structure over cost,
and the point is precisely that seven's return costs nothing extra.

## P-7 · The complete cycle

Starting from a state whose orbit is as long as each map allows:

- **𝔽₈, period 7:** 001 → 010 → 100 → 011 → 110 → 111 → 101 → home. Seven distinct states, every nonzero state exactly
  once, the weakest read at 0.9373.
- **Linear map, period 4:** four states. **Bit rotation, period 3:** three states.

Seven is the longest complete return three bits allow, and the eighth reading is the first of the
next turn — arrival and departure in one step, measured.

## What round 4 teaches

Rounds 2 and 3 asked seven to be a summit and a building block, and hardware declined both. This
round asked seven to be **a period** — a rest that closes a cycle — and hardware answered yes,
decisively and cheaply. The lesson is not that seven is magic; the lesson is that seven's claim
lives in **structure and return**, not in height or in counts of parts. Where the framework says
cycle, modulus, orbit and return, the machine agrees. Where the framework said summit, the machine
said no.

Next in this direction: the same return on qudits rather than qubits, the eight MUBs of a qu7it,
and the seven-share code [[7,1,4]]₇.

## Files

- **Script:** `round4/round4_hardware.py` (sim / submit / fetch / analyze)
- **Results:** `results/round4_hardware.json`, counts in `results/round4_hardware_counts.json`
