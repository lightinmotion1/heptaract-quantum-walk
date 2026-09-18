# P-14 · How far can the shared centre reach?

**Run:** 2026-09-18, ibm_kingston, qubits [12, 13, 14, 15, 19] · 80 circuits · 1024 shots · **32 seconds of QPU time**
**Pre-registration:** `PREREGISTRATION-2026-09-18-P14.md`
**SHA-256:** `46161c324868ef4116ee34fb7a33a081fe66c4d245a319df30d7d0871d8ac67d`
**Script:** `round5/centre_reach.py` · **Results:** `results/centre_reach.json`
**Desk:** Free (Miah J. Fry) & Claude

P-12 and P-13 said the reach of the shared centre belongs to its carriers. This acted on that:
**two** carriers instead of six, a chain chosen for coherence (q12: 328.7 µs, q19: 241.0 µs),
and the wait spent silent or refocused.

| Wait | silent | echo-2 | echo-4 | echo-8 |
|---|---|---|---|---|
| **60 µs** | 13.1% | **24.5%** | 18.5% | 18.2% |
| **180 µs** | **9.9%** | 5.2% | 4.4% | 0.0% |

(as a share of the no-wait bond, with the noise floor of 0.0452 subtracted)

## The scoreboard, and it is mostly red

| Test | Prediction | Verdict |
|---|---|---|
| H1 | Two carriers keep ≥ 20% of the ceiling at 60 µs, silent | **Fails** — 13.1% |
| H2 | The bond keeps ≥ 10% at 180 µs with its best treatment | **Narrowly fails** — 9.9% |
| H3 | The best treatment is two or four pulses at **both** delays | **Fails** — two pulses win at 60 µs, and at 180 µs every pulse sequence is worse than silence |
| H4 | The silent decay sits within a factor of two of the two-body prediction (139.0 µs) | **Fails** — the 60 µs point implies ~30 µs, the 180 µs point implies ~78 µs; the decay is not one exponential and is faster than dephasing alone predicts |

## What is true anyway

**Fewer carriers reach much further.** Six carriers, by P-13's measured decay, would hold under 1%
of their bond at 60 µs. Two carriers hold **13% silent and 25% echoed**. The direction of the
sum-of-rates arithmetic is right even though its absolute rate is not.

**The echo helps early and hurts late.** At 60 µs one Hahn echo nearly doubles what survives
(13.1% → 24.5%). At 180 µs every sequence does worse than
silence, and eight pulses erase the bond entirely. Pulse error accumulates with the length of the
wait, so there is a crossing point, and on this chip it sits between 60 and 180 microseconds.

**Something beyond dephasing is eating the bond.** The chain's own T₂ values predict a two-body
lifetime of 139.0 µs; the measurement implies three to five times faster.
Pure dephasing does not account for it. The candidates are energy decay, always-on ZZ coupling
between neighbours during the idle, and crosstalk from the pulses themselves. **That is the next
thing to measure, and it is a machine question rather than a framework one.**

## Honest statistics

At 1,024 shots over eight phase points, the resolution of this metric is roughly ±10% of the
ceiling. Only the 60 µs echo advantage (24.5% against
13.1%) sits comfortably outside it; the gap between 13.1% and 9.9% does not.
Read the table as one clear effect and several suggestive ones, not as four measurements.

## Where this leaves the claim

The relationship still shows no decay of its own. What this round did was fail to extend its reach
as far as the arithmetic promised, and find out why: the carriers lose more than their dephasing
alone, and refocusing stops paying once the pulses outlast the noise. **Four predictions, four
misses, and a clearer machine.** The next test is a decay-channel measurement, not another
relationship test.
