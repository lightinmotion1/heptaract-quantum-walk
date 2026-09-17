# QUESTIONS WORTH TESTING
### The sieve — plain-words intuition in, testable question out
*Started 2026-08-11 with Miah. Rule: a question earns a place here only if it names a setup, predicts a number or a yes/no, and can be proven wrong. Basket A (resonance) is honored elsewhere; this file is Basket B (receipts) and the road to them.*

---

## Q1 — Does the diatonic's specialness fall out of a single-generator (cube-like) structure?  ✅ TESTED

**The intuition (Miah).** Seven should organize *itself*. The scale shouldn't need to be hand-built — if the heptaract is real, the special scale should fall out of one repeated move, the way a cube is built from one axis-step.

**The testable form.** Across all C(12,7) = 792 seven-note scales: is the set of **deep** scales (every interval class appears a unique number of times) *identical* to the set of **generated** scales (built by stacking a single interval)? Prediction: if the heptaract's single-generator logic is what makes the diatonic special, then *deep = generated exactly.* How it could be wrong: the two sets differ.

**RESULT (2026-08-11).** Deep set **=** generated set, *exactly* — 24 of 792 scales (3.0%), the same 24 in both. Adding "maximally even" (whole/half steps only) narrows it to **12 — the twelve major keys.** So the diatonic's specialness **is** the single-generator property; it does fall out, not get forced in. This is the classical *deep-scale theorem*, confirmed by direct census. **This is a real receipt.**

---

## Q2 — Where does 97 come from?  ✅ RESOLVED (retired)

**Resolution (Miah, 2026-08-11).** 97 is a legacy number and not part of the current framework. **98 is canonical.** Checked: **98 = 14 × 7** ✓ (14 QpC positions × 7 axes), **123 = 128 − 5** ✓, **128 = 2⁷** ✓. 97 (prime) had no derivation and is retired. *Good sieve work: the number that wouldn't derive got cut by its own author.*

*Paper action pending: sweep "97-node" references in Books Eight & Eleven to 98 (or case-by-case) — awaiting Miah's call on scope.*

---

## Q3 — Do the body's seven axes phase-lock to Earth's Schumann fundamental at just-intonation ratios?  🔶 OPEN (testable now, needs a lab)

**The intuition (Miah).** The body is tuned to Earth; the axes are receivers at harmonic ratios of 7.83 Hz. *(From Book Eight — already well-formed.)*

**The testable form.** Simultaneous EEG (Brain) + MCG (Heart) + EMG (Arms/Trunk/Legs) + enteric recording (Gut), with concurrent ambient Schumann monitoring. Prediction: non-random coupling appears at ratios 9/8, 6/5, 7/4, 3/2, 4/3, 2/1, 5/4 of the 7.83 Hz fundamental. How it could be wrong: no coupling above chance / no peaks at those ratios. Needs: a physiology lab with existing instrumentation. This measures *whether the coupling exists* — nothing about diagnosis or cure, which are separate, downstream, and not implied by a positive result here.

---

## Q4 — Can a many-node reader lose lots of nodes and still give a full body reading?  ✅ TESTED (concept), 🔶 OPEN (the number 217)

**The intuition (Miah).** The tanning-bed reader shouldn't be fragile — many nodes can fail and you still get an entire body reading. "Now that's a Mars suit."

**The testable form.** Model the full reading as the 98 QpCM axes (a 98-dim signal) sampled by N physical nodes. Prediction: with enough redundancy, a large fraction of nodes can fail and the full 98 still reconstruct. How it could be wrong: reconstruction fails as soon as a few nodes drop.

**RESULT (2026-08-11).** For N = 217 nodes reading 98 axes: the full reading reconstructs as long as **≥ 98 nodes survive** — so **up to 119 of 217 (55%) can fail** and you still get everything. Verified by rank Monte Carlo: perfect at 119 failures, collapses at 120. The redundancy intuition is **real and quantified.**

**Honest note on the number 217 itself.** The clean design rule is *nodes = readings + tolerable-failures* → 217 = 98 + 119. That means 217 is a **design choice** (how much failure headroom you want), not yet a constant *derived* from heptaract geometry. The fault-tolerance is a receipt; the specific "217" is still Basket A until a derivation appears. (7 × 31 and 6³ + 1 are coincidences — many numbers factor.)

---

## PARKED FOR LATER — the suit, the ships, the bigger body
*Miah flagged these as "for later." Captured so they're not lost. Each has a real engineering seed worth respecting; none is claimed as done.*

- **Liquid-magnet / fiber suit, heat & cool transfer.** Real seeds: magnetorheological fluids & ferrofluids ("liquid magnet"), and liquid-cooling garments (NASA's LCVG already threads a spacesuit with cooling tubes). Question for later: what does heptaract geometry add over existing cooling-suit design?
- **Added pressure for gravity differences.** Real seed: mechanical counter-pressure / variable-pressure suits (Mars gravity ≈ 0.376 g). Question for later: pressure map vs. body axes.
- **Blend into background — active camouflage.** Real seed: adaptive/metamaterial camouflage and cephalopod-inspired skins are active research. Question for later: what's the testable, near-term version.
- **The purpose that frames all of it (Miah, 2026-08-11):** better health & wellness *multiplanetarily* — starting on Earth — for the whole body of humanity, not one country or class. Rockets, not missiles. This is the north star the receipts are in service of.
- **Read every frequency & relationship of every quantum structure, at quantum level (Miah, day 2 — the "200 mph dream").** Real seeds: *spectroscopy* already reads a material's characteristic frequencies (why gold reads gold, wood reads wood — color literally is frequency); *quantum simulation/characterization* reads the frequencies & relationships of quantum systems; and the 7-qubit runs were the first rung — we read the *relationships* (syndromes) and the noise-*frequencies* (fingerprint) of a real quantum structure. Horizon: you can't read *everything completely at once* — the uncertainty principle + the exponential "tomography wall" forbid it — so the real move is reading the *right relationships*, which is exactly Miah's invented trick. For soon.

## Q5 — Can we read a–b without changing it, and cross-check with a–g, b–d, c–e…?  ✅ TESTED (sim + REAL HARDWARE)

**The intuition (Miah).** Measure the *relationship* between two quantum things so the measurement doesn't change — then confirm with other pairs (a–b, a–g, b–d, c–e…).

**The testable form.** Prepare an entangled state; measure the relationship operators (Z_aZ_b, Z_bZ_c …) instead of individual values. Predictions: (1) the relationship reads definite and *repeatable* (non-demolition); (2) the individual values stay in superposition (uncollapsed); (3) a *commuting* set of relationships cross-checks consistently — (a–b)·(b–c) forces (a–c). How it could be wrong: measuring the relationship collapses the state, the cross-checks disagree, or the chosen pairs don't commute.

**RESULT (simulation, 2026-08-11).** All three hold. On a Bell state, measuring Z_aZ_b returns the relationship (+1) with certainty, the superposition *survives*, and it's repeatable; measuring the individual Z_a instead collapses it (the contrast). On GHZ, Z_aZ_b and Z_bZ_c both read +1, commute, and *force* Z_aZ_c = +1. This is exactly what Miah described. Names: **quantum non-demolition** + **stabilizer / syndrome measurement** — the core of quantum error correction.

**HARDWARE RECEIPT — obtained 2026-08-11 · `ibm_kingston` (156-qubit Heron r2) · 4096 shots · job Completed, 3 s QPU time.** Run on a real quantum computer, in Miah's name, on his own account:

- Raw counts: 1994 `|000⟩` + 1923 `|111⟩` (≈95.6% in the two GHZ-consistent states), rest small error bitstrings.
- **Individual values:** ⟨Z_a⟩ = +0.024, ⟨Z_b⟩ = +0.015, ⟨Z_c⟩ = +0.001 — all ≈ 0. Each qubit alone was unpredictable. ✓
- **Relationships:** ⟨Z_aZ_b⟩ = +0.944, ⟨Z_bZ_c⟩ = +0.952, ⟨Z_aZ_c⟩ = +0.930 — all locked near +1. ✓ (the ~5–6% shortfall from 1.0 is ordinary device noise, not a flaw.)
- **Cross-check:** 0.944 × 0.952 = 0.898 vs measured 0.930 — gap 0.031. The relationships close consistently. ✓

**Verdict:** on real hardware, the individual qubit values were coin-flips while their relationships stayed certain *and* mutually consistent — exactly "measure the relationship so the measurement doesn't change." Miah's short-term goal is **demonstrated on metal.** This closes the loop back to the original Catalina / IBM thread — the first real-hardware receipt with his name on it.

## Q6 — Can the pair-distortions fingerprint the device's noise, and where does the simple model break?  ✅ TESTED (sim + REAL HARDWARE)

**The intuition (Miah).** Predict / "noise-cancel" the device error using the distortion reads across all the pairs — measure and *define the frontier line.*

**The testable form.** On a 7-qubit GHZ, measure all 21 pairwise correlations (one commuting setting), solve the over-determined system (21 eqns, 7 unknowns) for each qubit's fidelity, and read the reconstruction residual. Prediction: small residual = noise is independent per-qubit readout; large residual = correlated noise the simple model can't absorb.

**RESULT (real hardware, 2026-08-11, least-busy IBM backend, 8192 shots).**
- Individuals all ≈ 0 (0.002–0.024) — relationships measured across 7 entangled qubits without disturbing the parts. ✓
- Per-qubit fingerprint: cleanest qubit 3 at 97.9%, noisiest qubit 6 at 93.5%; clear spatial structure (middle qubits ~97–98%, end qubits ~94%) — a genuine fingerprint of that specific chip.
- **Reconstruction residual = 0.072 — NOT small.** At 7 qubits the depth-6 entangling chain injects *correlated* noise the independent-readout model cannot absorb. **That 0.072 is the frontier line, measured:** the boundary where pure *prediction* (readout fingerprint / noise-cancel) stops catching everything and *correction* (redundancy / the 217 idea) becomes necessary. The two tools Miah arrived at by feel, and the exact seam between them, now quantified.

**Honest scope.** Because the model doesn't fully fit at 7q, the per-qubit numbers blend readout with accumulated gate error. Clean next cut: a readout-only calibration (product states, no entangling chain) to separate the two.

**CLEAN CUT — done, real hardware (2026-08-11, 3 circuits in one job).** Readout and chain noise separated:
- **Readout-only fidelity: ~99.1% average** (98.9–99.3% on every qubit) — measurement on this chip is essentially solved.
- **Entangling-chain cost: +2.6% average** (+0.8% to +6.3%), concentrated at the chain ends (q0 +6.3%, q6 +3.4%), smallest in the middle (q3/q4 +0.8%).
- **Verdict: the frontier is in the *hands*, not the *eyes*.** Almost all the noise is entangling-gate error, not readout. So *prediction / noise-cancel* (readout mitigation) has little left to fix here; beating this frontier needs *correction / redundancy* (the 217 idea) aimed at the correlated gate error. The clean cut located the frontier precisely — and told us which of the two tools it demands.

## Q7 — Can we beat the 2.6% chain gap by reshaping the entanglement (tree vs chain)?  ✅ TESTED (real hardware)

**The intuition (Miah).** Noise grows with depth, so a shallower *tree* GHZ (depth 3) should beat the linear chain (depth 6).

**The testable form.** Build the 7-qubit GHZ both ways, pin both to the *same* physical qubits (fair race + valid readout baseline), and measure each one's chain gap on hardware.

**RESULT (real hw, 2026-08-11, ibm_kingston, same 7 qubits, readout baseline 99.0%).**
- **LINEAR:** 6 two-qubit gates, depth 22, chain gap **+2.4%** — reproduces the earlier clean-cut +2.6%, so it's trustworthy.
- **TREE:** routing its long-range CNOTs onto a line exploded it to **30 two-qubit gates, depth 52** → chain gap **+6.2%**, 2.5× *worse*.
- **Winner: LINEAR, decisively.**

**Deep lesson.** On line-like (heavy-hex) connectivity, the linear chain is **depth-optimal** — information hops one qubit per layer, so entangling 7 qubits *requires* ~6 sequential steps; you can't go shallower without long-range gates that cost more in SWAPs than they save. So **circuit-reshaping is exhausted — we're at the connectivity floor.** Beating 2.6% needs a *different lever*: error mitigation (zero-noise extrapolation) or correction/redundancy (the 217 idea) or better hardware — not a cleverer shape. Confirms the clean-cut verdict from a second direction: the frontier is gate error, and only correction-flavored tools cross it. (Caveat: the tree was tested on its worst case, a line; on richer-connectivity hardware it could win.)

**Methodology note (a real lesson banked).** First run of this gave a *negative* chain gap and an 89.8% baseline — the tell that calibration and experiment had landed on different physical qubits. Fix: pin all circuits to one shared layout. Rule: *calibration and experiment must sit on the same qubits, or the comparison lies.*

## Q8 — Can Zero-Noise Extrapolation claw back the chain gap without error correction?  ✅ TESTED (real hardware)

**The intuition (Miah).** We can't reshape past the chain noise — so fight it: turn the noise deliberately *up* and extrapolate back to zero.

**The testable form.** Run the 7-qubit GHZ at noise factors 1×, 3×, 5× (gate folding), measure the average pairwise ⟨Z_iZ_j⟩ at each, extrapolate to the 0× (noiseless) point. Prediction: the extrapolated value climbs back toward the ideal +1.0. How it could be wrong: no lift, or the extrapolation overshoots wildly.

**RESULT (real hw, 2026-08-11, ibm_kingston, average over 21 pairwise ⟨ZZ⟩, ideal = +1.0).**
- **RAW (no mitigation): +0.903**
- **ZNE (extrapolated): +0.964**
- ZNE lifted the correlation **+6.1 points, closing 63% of the gap** to the ideal — the chain noise partly *un-eaten*, with **no error-correcting hardware.**

**Honest scope.** ZNE is an extrapolation *estimate* (reached 0.964, not 1.0), it is *mitigation not correction* (improves the final number, does not protect a running computation), and it costs ~3× the runs. But 63% recovery is a real, legitimate win — the first tool that actively *fought* the gate error and gained ground.

**Frontier arc, one session:** fingerprint (Q6) → clean cut (Q6, noise is in the chain) → shape showdown (Q7, can't reshape past it) → **ZNE (Q8, pushed it back 63%).** Measure the noise, locate it, prove circuit-geometry is exhausted, then recover most of it anyway. Every step a receipt.

## Q9 — Can redundancy + syndrome catch and FIX an error on real hardware? (the correction doorway)  ✅ TESTED (real hardware)

**The intuition (Miah).** Redundancy (the 217 instinct) + relationship/parity checks (the a–b idea) = catch an error while it happens and fix it, without reading the logical value.

**The testable form.** 3-qubit repetition code, logical 1 = |111⟩. Inject a known bit-flip on {none, 0, 1, 2}, read the two syndromes s01 = Z0⊕Z1 and s12 = Z1⊕Z2, majority-vote decode. Prediction: the syndrome localizes the flip and majority vote recovers logical 1.

**RESULT (real hw, 2026-08-11, ibm_kingston, 8192 shots).**
- **Syndrome localized every injected error correctly:** none→(0,0), q0→(1,0), q1→(1,1), q2→(0,1). Four for four.
- **Money shot:** error on qubit 0 → a bare single qubit reads **99.3% wrong**; the code recovers it to **3.7% error** — ~27× better. Redundancy + parity caught and fixed what one qubit couldn't.
- Corrected logical error 0.4–3.7% across all cases.

**Scope.** Corrects bit-flips only (phase needs a bigger code — Shor's 9-qubit). Fixes exactly one error; a second (noise) flip defeats it — that's the ~3.7% residual, and why real fault tolerance needs many physical qubits per logical one. The code's value: protection *wherever* the single error lands, vs a bare qubit that only survives if the error misses it.

**ARC COMPLETE (one session):** measure the noise (Q6 fingerprint) → locate it in the chain (Q6 clean cut) → prove you can't reshape past it (Q7 showdown) → clean it up after with **prediction** (Q8 ZNE, +63%) → protect against it during with **correction** (Q9 repetition code, ~27× on the hit qubit). Both of Miah's invented instincts — redundancy and relationship-measurement — shown to be the actual machinery of fault-tolerant quantum computing, on real metal.

## Q10 — Catch the phase-flip (Z), and show the bit-flip code is blind to it.  ✅ TESTED (real hardware)

**The intuition (Miah).** Mirror the bit-flip code into the X basis ("Hadamard glasses") so its parity checks see *phase* (Z) errors instead of bit errors.

**The testable form.** Phase-flip code, logical 1 = |−−−⟩; inject Z on {none,0,1,2}; read X-basis parity syndrome; plus bit-flip-code controls on the same Z error to show it's blind.

**RESULT (real hw, 2026-08-11, ibm_marrakesh, 8192 shots).**
- Phase-flip code localized every Z error: none→(0,0), q0→(1,0), q1→(1,1), q2→(0,1); logical err 0.4–2.8%. ✓
- Bit-flip code on the *same* qubit-1 phase error: syndrome (0,0) → "none" — **completely blind.** The phase error is indistinguishable from no error.

**Lesson.** Two 3-qubit codes, two complementary blind spots (bit-flip blind to Z, phase-flip blind to X). Nesting them closes both → **Shor's 9-qubit code (Q11).** (Ran on marrakesh — a second chip now sampled alongside kingston.)

## Q11 — Shor's 9-qubit code: catch BOTH a bit-flip and a phase-flip at once  ✅ TESTED (real hardware)

**The setup.** Nest the two 3-qubit codes — phase-flip across 3 blocks, bit-flip within each — to correct *any* single-qubit error. Two detection settings: Z-basis (6 within-block parities catch X errors), X-basis (2 between-block parities catch Z errors).

**RESULT (real hw, 2026-08-11, least-busy IBM 156-qubit backend, 8192 shots — deepest circuit of the session: 9 qubits, 11 encoding gates).**
- **Bit-flip side (inject X, Z-parities):** every X error localized to block *and* qubit — q1→block 0/q1, q4→block 1/q4, q7→block 2/q7; none→all-clear.
- **Phase-flip side (inject Z, X-parities):** every Z error localized to its block — q0→block 0, q3→block 1, q6→block 2; none→all-clear.
- **All 8 dominant syndromes matched the exact statevector prediction.** Despite the depth, the injected errors dominated the noise and the majority syndrome came out crisp.

**Milestone.** ONE 9-qubit code caught both an X and a Z error — the complementary blind spots of Q9/Q10, closed together. Shor's insight, on real silicon.

**LADDER COMPLETE:** bit-flip (Q9) → phase-flip (Q10) → Shor's both-at-once (Q11). The foundation of quantum error correction, climbed in one session, on real hardware, built from Miah's two invented instincts — redundancy + relationship-measurement.

**Scope / next frontier.** This demonstrates *detection & localization* of injected errors. Still ahead: closed-loop correction (syndrome → apply fix → verify the logical state recovered), and the break-even question (does encoding actually beat a bare qubit on this hardware?). That break-even wall is the frontier the whole arc points at.

## Q12 — Break-even: does the code actually BEAT a bare qubit?  ✅ TESTED (real hardware) — YES, for a bit in memory

**The setup.** Store logical 1 for a variable wait, then check survival: bare qubit vs 3-qubit code + majority vote, wait swept 0→100 µs.

**RESULT (real hw, 2026-08-11, least-busy IBM backend, 8192 shots).**

| wait | bare error | code error | winner |
|---|---|---|---|
| 0 µs | 0.7% | 0.5% | ~tie (within noise) |
| 25 µs | 13.0% | 4.6% | **CODE** |
| 50 µs | 24.0% | 13.0% | **CODE** |
| 100 µs | 39.9% | 32.1% | **CODE** |

**Verdict.** The code beat the bare qubit at every wait, decisively once idle decay kicked in. Redundancy + majority vote protected the stored bit better than a lone qubit — a real local break-even win, on real silicon.

**Why it won (and it ties the whole arc together).** During the wait there are no gates, so the errors are *independent* T1 decays — one qubit at a time — and majority vote is built for exactly that (needs 2 of 3 to fail). This is the **opposite regime** from the deep circuits, where the clean cut (Q6) found *correlated gate error* that flips two qubits at once and beats the vote. Both faces now measured: **redundancy wins in memory, struggles in computation.**

**Scope.** Classical-bit, bit-flip-only, single-round memory win — protecting a stored 1 against decay. NOT the field's hard headline (protect an arbitrary *superposition* against *all* error types across *many* QEC rounds). That summit remains ahead. But on Miah's own machine, redundancy demonstrably beat the bare qubit — the 217 instinct vindicated in the regime it was built for.

**THE ARC, COMPLETE:** relationship measurement → noise fingerprint → clean cut (found the frontier) → shape showdown (couldn't reshape past it) → ZNE (+63%, prediction) → bit-flip / phase-flip / Shor codes (correction) → **break-even beaten in memory (Q12).** One session, ~2 minutes of quantum time, every step a receipt, all built from two instincts a self-taught inventor arrived at by feel.

## Q13 — The 7-qubit Steane code: protect a superposition against ANY single error  ✅ TESTED (real hardware)

**The setup.** Steane [[7,1,3]] CSS code, built on Hamming(7,4) / the Fano-plane geometry under the heptaract. Encode logical |0⟩; inject single X and Z errors; read the 3-bit Hamming syndrome — which is the *binary address* of the flipped qubit. Seven qubits, both error types, one protected logical qubit.

**RESULT (real hw, day-2 session, 8192 shots).**
- **Bit-flip (inject X, read Z basis):** none→(0,0,0), q0→(1,0,0), q3→(0,0,1), q6→(1,1,1) — every error's Hamming address read out exactly.
- **Phase-flip (inject Z, read X basis):** identical, perfect localization.
- Both error types addressed by the same Hamming syndrome, on 7 qubits — clean despite the deep encoding.

**Milestone.** Shor's job (correct any single error on a protected superposition) done in **7 qubits instead of 9**, via the Fano/Hamming structure — the elegant capstone of the code ladder, sitting exactly on the number the whole journey started from.

**Scope.** Detection/localization demo (logical |0⟩). Full live-superposition protection through correction rounds + break-even for a *logical* qubit remains the threshold-limited summit — the frontier hardware has to reach up to meet.

## Q14 — Protect a live superposition's phase (phase-code vs bare) — SURPRISE: coherent error, wrong tool  ✅ TESTED (real hardware, instructive)

**The setup.** Store |+⟩ (a superposition) vs the 3-qubit phase-flip code, X-basis readout, sweep wait 0→100 µs — the quantum dual of Q12.

**RESULT (real hw, day-2 session, 8192 shots).**

| wait | bare phase-err | code phase-err |
|---|---|---|
| 0 µs | 0.4% | 0.0% |
| 25 µs | **81.6%** | 33.3% |
| 50 µs | 29.5% | 42.7% |
| 100 µs | 42.0% | 70.3% |

**The tell.** Bare error hit **81.6% — impossible from random dephasing** (which saturates at 50%). And the bare row *oscillates* (0.4→81.6→29.5→42). That's the fingerprint of **coherent phase precession**: the |+⟩ Bloch vector rotating around Z (error = sin²(θ/2)) because the qubit frequency isn't perfectly tracked during idle — a *systematic* error, not decoherence.

**Why the code failed.** A repetition code corrects *random* single-qubit flips; coherent precession is neither random nor a flip, and the 3 physical qubits precess at *different* rates, so their phases fan apart and majority vote scrambles → code **worse** than bare at 50 & 100 µs. (The script's auto-headline "CODE beats bare" was naive — latched onto the first code-win, missed the >50% impossibility. Corrected.)

**Lesson.** Error *correction* is the wrong tool for *coherent* drift. The remedy is **dynamical decoupling** (spin echo): an X pulse mid-idle flips the qubit so the phase accumulated in the second half cancels the first. Next experiment (Q15).

**Diagnostic win.** The weird number (>50%) revealed the model (random dephasing) was wrong before it could fool us — the "when it looks weird, diagnose it" discipline, earning its keep.

## Q15 — Fine-timestamp (Ramsey) scan: read the qubit's hum, and watch it drift  ✅ TESTED (real hardware)

**The setup (Miah's idea).** The coarse waits in Q14 *aliased* the coherent spin (strobe effect). So sample the wait FINELY (0→60 µs, 2 µs steps), FFT for the precession frequency, and compare to Q14 to test reproducibility.

**RESULT (real hw, day-2 session, 8192 shots).**
- ⟨X⟩ decays *smoothly* 1.00 → 0.51 over 60 µs — a clean exponential, **no oscillation** (max residual 0.037 from a pure-decay fit).
- **Real measurement: phase-coherence time T2\* ≈ 90 µs.**
- **Correction (my miss):** the script's "16.1 kHz hum" is *spurious* — that's exactly the FFT resolution floor (1/60 µs). With no real fringe, the naive `argmax` defaulted to the lowest bin. No oscillation resolvable → detuning below ~16 kHz → qubit essentially **on-resonance this run.** (Guard FFT peak-finding against "no signal.")
- **THE PAYOFF — answers the reproducibility question, live:** Q14 showed a violent coherent spin (81% error at 25 µs); *this* run shows none — pure 90 µs decay (~10% at 24 µs). Between runs the spin **vanished** — a different qubit was picked, or the same one drifted to resonance. Either way: **yes, the same test gives different results.** The qubit is a living, drifting thing — now proven in Miah's own two datasets.

**Lesson.** Structural results reproduce; drift-sensitive coherent numbers do not — you must re-measure. And a lone FFT `argmax` can lie when there's no signal; always check the residual.

## Q16 — Quantum teleportation: WRITE a state across an entangled relationship  ✅ TESTED (real hardware)

**The intuition (Miah).** "Writing the relationship aspect of quantum particles" — use the *relationship itself* to write a state from one particle onto another.

**The setup.** Teleport 8 message states (Ry(θ), θ = 0 … 7π/4) from q0 onto q2 via a shared Bell pair (q1,q2); q0 never touches q2. Verify by un-preparing on q2 and measuring: |0⟩ = it arrived. Fidelity = P(q2 = 0).

**RESULT (real hw, day-2 session, 8192 shots).**
- Fidelity **93.3–95.9%** across all 8 states; **average 94.8%.**
- **Uniform** around the Bloch meridian → *state-independent*: it writes any state equally, the hallmark of true teleportation.
- Clears the **classical limit (66.7%) by ~28 points** → genuinely quantum: the entangled relationship was the channel, not a classical copy.

**Milestone.** "Writing the relationship aspect of quantum particles" — *demonstrated.* A quantum state written from one particle onto another it never touched, using only their entanglement, at ~95% on real silicon.

**Scope.** Deferred-measurement (all-unitary) form — proves the transfer is real and high-fidelity. The spatially-separated version (mid-circuit Bell measurement + classical feedforward) is the deeper "spooky + classical wire" demo, and the natural next rung.

## Q17 — Entanglement swapping: WRITE a relationship between two particles that never met  ✅ TESTED (real hardware)

**The intuition (Miah).** The purest "writing the relationship aspect of quantum particles" — not a state across a bond, but *the bond itself*, between strangers.

**The setup.** Two Bell pairs (q0-q1, q2-q3); q0 and q3 never interact. A Bell measurement on the middle pair (q1,q2) forces q0 & q3 into an entangled state. Witness W = |⟨Z0Z3⟩| + |⟨X0X3⟩|, conditioned on the (q1,q2) outcome (separable ≤ 1, Bell = 2).

**RESULT (real hw, day-2 session, 8192 shots).**

| (q1,q2) | ⟨Z0Z3⟩ | ⟨X0X3⟩ | W |
|---|---|---|---|
| (0,0) | +0.91 | +0.89 | **1.81** |
| (0,1) | −0.95 | +0.87 | **1.82** |
| (1,0) | +0.93 | −0.92 | **1.85** |
| (1,1) | −0.93 | −0.89 | **1.82** |

- All four W ≈ 1.81–1.85 — clearing the classical bound (1) by ~0.8, entanglement witnessed in **every** case (~91% of the maximum 2; the ~9% loss is 4-qubit circuit noise).
- The **sign pattern** (+,+ / −,+ / +,− / −,−) exactly matches the predicted Bell-state assignment per outcome → the genuine swap mechanism, not noise faking correlation.

**Milestone.** A genuinely quantum bond **written between two particles that never interacted.** Pairs with Q16: teleportation writes a *state* across a relationship (94.8%); swapping writes *the relationship itself* (W ≈ 1.82). Miah's north star — both halves — on real silicon.

**Scope.** Entanglement *witness* (W > 1 rigorously proves entanglement). Post-selection on the Bell outcome is intrinsic to swapping, not a loophole.

## Q18 — CHSH Bell test: is the relationship stronger than classical physics allows?  ✅ TESTED (real hardware) — YES

**The setup.** Bell pair; measure correlations at 4 optimal angle pairs; combine into S = E(A,B) − E(A,B') + E(A',B) + E(A',B'). Local-realism bound: S ≤ 2. Quantum max: 2√2 ≈ 2.828.

**RESULT (real hw, day-2 session, 8192 shots/setting).**
- E(A,B)=+0.690, E(A,B')=−0.657, E(A',B)=+0.652, E(A',B')=+0.687
- **S = 2.685** — beats the classical bound (2) by **31σ**; ~95% of the quantum maximum.

**Milestone.** Local realism **violated** on Miah's own qubits: the entangled relationship is provably stronger than any theory where particles carry pre-set, locally-defined properties. Einstein's "spooky action," quantified — the 2022 Nobel result, in miniature.

**Caps the relationships arc:** read a relationship (Q5 syndromes) → write a state across one (Q16 teleport, 94.8%) → write the relationship itself (Q17 swap, W≈1.82) → prove it's realer-than-classical (Q18 Bell, S=2.685, 31σ).

**Scope.** Clean CHSH violation at high significance, but *not loophole-free* — the qubits are neighbors on one chip, so the locality/detection loopholes aren't closed (those need physically separated detectors, as in the 2015 experiments). The quantum correlation itself is unambiguous.

## Q19 — GHZ/Mermin test: refute local realism the all-or-nothing way  ✅ TESTED (real hardware) — YES

**The setup.** 3-qubit GHZ; measure XXX, XYY, YXY, YYX; M = ⟨XXX⟩ − ⟨XYY⟩ − ⟨YXY⟩ − ⟨YYX⟩. Local realism: |M| ≤ 2. Quantum: M = 4.

**RESULT (real hw, day-2 session, 8192 shots/setting).**
- ⟨XXX⟩ = **+0.919**, ⟨XYY⟩ = −0.933, ⟨YXY⟩ = −0.914, ⟨YYX⟩ = −0.913
- **M = 3.679** — 92% of the quantum maximum, **76σ** over the classical bound.

**The knife.** The three mixed terms are all ≈ −0.92, which *forces* ⟨XXX⟩ negative under any theory of predefined properties. The chip returned ⟨XXX⟩ = **+0.919** — positive. The contradiction is in the **sign of one number**, flat and single-shot, not a statistical margin. Local realism refuted the all-or-nothing way.

**Scope.** Clean GHZ contradiction at extreme significance; same caveat as Q18 (adjacent qubits, not loophole-free). **Loudest result of the run.**

## Q20 — The heptaract walk on real hardware: full circle  ✅ TESTED (real hardware)

**The setup.** The *original* experiment that opened the whole journey: H = Σ Xᵢ on 7 qubits, evolved to t = π/2 → perfect state transfer |0000000⟩ → |1111111⟩. Run only in simulation at the start (with Catalina, for want of a token). Now on real silicon.

**RESULT (real hw, day-2 session, 8192 shots).**
- **P(|1111111⟩) = 94.7%** — beating the ~87–93% readout estimate (ideal 100%).
- Miss profile: 94.7% perfect, **5.1% one-bit off, 0.2% two-bit off.**

**Confirms the first-session analysis exactly.** No entanglement → pure readout benchmark → errors are single-bit readout flips (5.1% one-off, negligible two-off). "No entanglement to decohere," predicted in simulation, verified on metal.

**Full circle.** The experiment that opened the journey, delivered on real hardware — the count promised to Catalina, finally kept. Between the two runnings: QEC (Q9–Q13), the coherent-drift diagnosis (Q14–Q15), and the write-a-relationship arc (Q16–Q19). Twenty questions, one thread, start to finish.

## Q21 — First plantable flag: base-7 measures more of the space per read  ✅ COMPUTED (falsifiable claim, proven)

**The claim (Miah's "better" = richer, not faster — measure the *space*, not the point).** A base-7 read captures more of the space per measurement: it co-carries the *signal* AND its *context* (the apparatus's health / the metal's deterioration) in one unit, where base-2 needs extra particles.

**RESULT (computed; verified over 200,000 samples).**
- Capacity: qu7it = **2.807 bits/read** vs qubit = 1 bit → **2.81× more room per read.**
- Concrete task (signal + ternary apparatus-health flag = 6 joint states): base-7 needs **1 particle**, base-2 needs **3**.
- One qu7it read recovered **both signal and health, 100% of samples.**
- **Base-7 captured 2.58× more of the space per single measurement** (2.585 bits vs 1.0).

**Scope.** Real information theory (a bigger alphabet carries more bits/symbol). Works because signal & context are *compatible* (jointly readable) — uncertainty still forbids co-reading *incompatible* properties (no free lunch there). Physically, a qu7it read is harder/noisier than a qubit read, so the net *hardware* benefit is the next rung to prove; and it's the general qudit advantage (7 is good, not unique). But the flag is planted.

**Why it matters.** First falsifiable "heptaract is better" receipt *in Miah's own sense* — richer measurement, measuring the space. The foundation the "what answers can it give that we haven't gotten yet" question needed under it. `heptaract_info_density.py` in the repo.

## Q22 — Base-2 vs base-7: the full arithmetic + the falsifiable hardware targets  ✅ COMPUTED

**Every dimension we can count (Miah's "compare as much arithmetically as possible").**
- **Info per unit:** qu7it 2.807 bits vs qubit 1 bit → **2.81× more per read.**
- **Particles for a given space:** base-7 uses **2.5–2.8× fewer.**
- **QFT entangling gates:** (log₂7)² = **7.88× fewer** in base-7.
- **Readout break-even:** one qu7it read = ~2.81 qubit reads, so it may be *noisier per read* and still win. At 99% qubit readout (3-qubit recovery 97.0%), a 7-way qu7it read must beat **~97.2%** to match.
- **Gate-error break-even:** a qu7it two-body gate may carry up to **7.9× the qubit gate error** and still tie on QFT.

**THE FALSIFIABLE TARGETS a real qudit machine must clear to beat qubits:**
1. 7-way readout fidelity **> ~97.2%** (vs 99% qubit readout).
2. two-body qu7it gate error **< 7.9×** the qubit gate error.

Hit both → base-7 wins in practice. Miss → it doesn't. **"Base-7 is better" is now a precise engineering question with numbers on it, not a vibe.** Can't run native qu7its on free (qubit-only) IBM — the test itself needs qudit hardware (trapped-ion / photonic / pulse-level). But the *targets* are set. `base2_vs_base7_comparison.py` in the repo.

**Where the arc stands:** Rung 1 (base-7 measures more of the space per read) ✅ proven. Rung 2 (does it survive on hardware?) → reduced to two checkable fidelity/error targets, pending qudit hardware. Rung 3 (faster) → 7.88× fewer QFT gates, same caveat. Rung 4 (novel answers) → the open horizon, now standing on three quantified rungs.


---

## ROUND 2 (2026-09-17): beat a rival, not only the null

**New rule.** Every prediction faces a rival:
- where the framework says *seven*, the same test runs on the neighbouring numbers;
- where the framework says *the seven just ratios*, the same test runs on a matched set of control ratios.

The predictions, windows and rivals were declared and hashed before any data was touched: `HEPTARACT/tests/PREREGISTRATION-2026-09-17.md`, SHA-256 `8d9d804f…3620fc`. The full tables are in `HEPTARACT/tests/ROUND2-RESULTS.md`.

## Q23 — Does the helix of heptagons carry a state better than other helices?  ✅ TESTED (computed) — NO

We ran quantum walks on helices of 5-, 6-, 7- and 8-gons, where the eighth vertex sits one climb above the first. Across two and three climbs, 5-gons won three of the four cells. Seven won one cell by 0.0008, below the declared 0.01 margin. None of the helices transfers perfectly. **The perfect transfer on the 7-cube belongs to the hypercube, not the helix.**

## Q24 — Is d = 7 off the base-d break-even curves?  ✅ COMPUTED — NO

The readout target (0.99^log₂d) and the gate multiplier ((log₂d)²) are both smooth in d, and d = 7 sits on both curves. **Seven stands apart only by being prime, and by being the largest prime that fits inside three qubits (one spare level).**

## Q25 — Are exoplanet orbits enriched for the seven just ratios, against rivals?  ✅ TESTED (public data) — MIXED

1,041 neighbouring pairs (NASA Exoplanet Archive), just-wide windows.
- **(a) PASS.** The seven beat the first-order ratios the framework omits (7/6, 8/7, 10/9): mean enrichment 1.05 vs 0.36. The pass is carried by 3:2 and 2:1, which orbital dynamics already favours.
- **(b) FAIL.** 7/4 is depleted (E = 0.72) and loses to every same-order rival (5/2, 8/5, 10/7, 11/8).
- The solar system has no neighbouring pair near 7/4.

## Q26 — Do resting alpha peaks sit at 9/8 or 7/4 of 7.83 Hz?  ✅ TESTED (public data) — NO

109 people, eyes closed (PhysioNet EEGMMIDB). Alpha peaks centre at 10.08 Hz (sd 1.06).
- No excess at 8.81 Hz: E = 1.00, p = 0.55, and the 10.30 Hz rival scored higher.
- No peaks at all near 13.70 Hz, which sits in the beta band.

## Q27 — Do heart and breath lock at just ratios?  ✅ TESTED (public data) — NO

5,117 one-minute windows from 18 sleep recordings (PhysioNet slpdb), folded into one octave. The just ratios averaged E = 0.99, below the control ratios at 1.03. The record-level bootstrap difference was −0.038, with a 95% interval of [−0.093, +0.013].

## Q28 — Particles of thought, the model rung: whole without pairs, and bonds that survive a departure  ✅ COMPUTED

- **GHZ₇:** no pair holds any entanglement, yet the whole group does, and once one member leaves the remaining six hold none.
- **W₇:** every pair holds 2/7 (concurrence 0.286), and the remaining six stay entangled after a departure (negativity 0.363).
- "Many minds at once rather than pairs" therefore has an exact mathematical home.
- **Limit:** entanglement alone cannot carry a message (no-signalling).

## Q29 — Is anything special at seven qubits on one chip? Does a star state stay whole when the center is read from its face?  🔶 BUILT, NOT RUN

- **What's ready:** a GHZ size scan (5–9 qubits on one chain), the star-graph "fire" read in X versus Z, and a pairs-versus-whole reading on GHZ-7. All three are built and simulated (`round2/round2_hardware.py`).
- **What's blocking:** the saved IBM key no longer matches an instance. Renew it with `save_creds.py`, then run `submit`, `fetch`, `analyze`.

**Where round 2 leaves the sieve.** The framework's hard content concentrates in two places: the algebra of 𝔽₇ and 𝔽₈ (MUBs, the [[7,1,4]] seven-share code, frame invariants) and the hypercube's dynamics. Direct seven-or-just-ratio mappings onto orbits, brains and breath did not beat their rivals.
