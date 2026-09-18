# HEPTARACT round 4 — pre-registration · The return at seven

**Written:** 2026-09-17, before any circuit was sent to a quantum processor.
**Desk:** Free (Miah J. Fry) & Claude
**Script:** `round4/round4_hardware.py` (simulator check run first; no hardware data seen)

## The claim being tested

Free's reading: seven is a rest — the close of a cycle — and **the eighth is the return home and
the first step of the next round at once**. Over three bits, 𝔽₈ says this in algebra: the seven
nonzero elements form a single cycle and α⁷ = α⁰, arrival and departure in one step. This round
asks whether a real machine shows that return, and whether seven is the longest complete return
three bits allow.

## P-6 · The return

A three-qubit register is prepared as (|000⟩ + |011⟩)/√2, stepped k times by a map, then
unprepared. Reading 000 is likely only when the map has come home. Ideal values: 0.25 away from
home, 1.00 at home (confirmed on the noiseless simulator).

Maps: the 𝔽₈ cycle (period 7, CNOTs only), a linear map of period 4, a bit rotation of period 3,
and the ordinary counter mod 8 (period 8, needs a Toffoli each step).

- **Prediction:** the 𝔽₈ cycle reads 000 with probability **≥ 0.70 at k = 7**, stays **≤ 0.45 for
  k = 1…6**, and its return **beats the counter's own return at k = 8 by at least two standard
  errors**.
- **Why the counter is the rival that matters:** eight is the neighbour of seven and the counter
  is the obvious eight-cycle. If the eighth step is arrival and departure together, the cheap
  complete return should be the seven-cycle, not the eight-counter.
- **Declared in advance:** the counter costs a Toffoli per step and the 𝔽₈ cycle costs CNOTs only.
  A win for 𝔽₈ is therefore partly a win of structure over cost — which is the claim, not a
  confound: the point is that seven's return is the one three bits give away for free.

## P-7 · The complete cycle

Starting from a state whose orbit is as long as each map allows, the register is stepped and read.

- **Prediction:** the 𝔽₈ orbit reads **seven distinct states**, each identified with probability
  ≥ 0.60 — every nonzero state, once — while the period-4 and period-3 rivals read four and three.
- Seven is then the longest complete return available on three bits, and the eighth reading is the
  start again.

## Bookkeeping

- Nothing above moves after data arrives. A null is published like a pass.
- Shots: 4,096 per circuit, one job, least busy IBM Heron processor at submission.
