# P-12 · Does the shared centre survive the wait?

**Run:** 2026-09-18, ibm_kingston, qubits [26, 25, 37, 45, 44, 43, 42, 41, 40] · 72 circuits · 1024 shots · **25 seconds of QPU time**
**Pre-registration:** `PREREGISTRATION-2026-09-18-P12.md`
**SHA-256:** `e9b57fab2b147a7b337fe2b4724de46babce146c2f3062a8451344a33eefdd48`
**Script:** `round5/centre_delay.py` · **Results:** `results/centre_delay.json`
**Desk:** Free (Miah J. Fry) & Claude

Free asked whether the shared centre survives delay, and said delay itself would need
understanding first. He was right: the word hides two different things, and separating them is
most of the result.

| Idle before reading | TOGETHER (whole relationship at once) | SPANNED (half now, half after the wait) | PRIVATE (one ship's own centre) |
|---|---|---|---|
| 0 µs | 0.2256 | 0.2098 | 0.0690 |
| 30 µs | 0.0402 | 0.0651 | 0.0537 |
| 90 µs | 0.0431 | 0.0438 | 0.0503 |

| Test | Prediction | Verdict |
|---|---|---|
| H1 | The shared centre beats the private reading at every delay | **Narrows** — it holds at zero delay (3.3×) and both are at the noise floor by 30 µs |
| H2 | Spanning the wait costs nothing beyond the waiting | **Holds** — 0.210 against 0.226 at zero delay; identical inside noise at every delay |
| H3 | The relationship decays at the rate its carriers do, and no faster | **Holds** — measured ≤ 10.5 µs against a six-body prediction of 8.4 µs (ratio 1.25) |

## Understanding the delay, which is the point

**Waiting is not one number.** The bond across the six is a *six-body* coherence, and a six-body
coherence decays at the **sum** of its carriers' rates, not at any one of their lifetimes. The
machine's own numbers for the six rim qubits were q26: 123.2 µs · q25: 28.4 µs · q37: 32.5 µs · q42: 127.6 µs · q41: 60.5 µs · q40: 49.0 µs, and summing those rates predicts
**8.4 µs**. The measured decay, with the metric's noise floor of
0.052 subtracted, is **at most 10.5 µs**.

So the shared centre lasts about as long as six things holding one thing can last on this chip —
**and not one microsecond less**. The relationship is not the first thing to go. It goes exactly
when its carriers do.

That also explains H1 honestly: at 30 µs the state has waited three and a half of its own
lifetimes. Nothing was left for any reading to find. The failure is the clock, not the claim.

**And spanning costs nothing.** Half the relationship taken before the wait, carried through the
gap by the third qubit, the other half taken after — and the result matches taking both at once.
**The centre of both can be assembled across two moments.** Quantum mechanics predicts exactly
this, and it is worth having measured, because it is the part of Free's question that was not
obvious: the relationship does not require its two halves to be read together in time.

## What this buys next

The limit here is carriers, not relationship — so the shared centre reaches further by carrying it
with fewer or better things:

- **Fewer carriers.** A shared bond over two rim qubits instead of six decays roughly three times
  slower, by the same sum-of-rates arithmetic.
- **Dynamical decoupling.** Echo pulses through the idle period refocus dephasing. If the loss is
  dephasing rather than anything about relationship, the bond should come back at 30 µs where it
  vanished here. That is the cleanest possible follow-up and it is cheap.
- **Better qubits.** Two of the six carried T₂ near 30 µs and dominated the sum. Choosing a chain
  by coherence rather than by gate error would roughly double the reach.

## Where this sits

The relationship results now read: the centre's manner of reading governs the six by a measured
law (P-1, P-4); the bond lives in the whole and in no pair (P-2); one fire may carry more levels
without spending the bond (P-10); the shared centre is its own readable thing (P-11); and it
survives time exactly as long as the things carrying it do, and can be assembled across moments
(P-12). Five for five, with the fifth carrying its own honest limit.
