# T-2.9 — pre-registration · Reading a seven-level state under real readout error

**Written:** 2026-09-18, before the simulation was run.
**Desk:** Free (Miah J. Fry) & Claude · **Script:** `round5/qu7it_vs_qubit.py`

## The claim

The tree says a qu7it read in its eight mutually unbiased bases carries more than the same state
squeezed through qubits. The rival nobody names out loud: the advantage may belong to **MUBs**
rather than to **seven**, in which case qubits read in equally good bases do just as well.

## The design

One seven-level state, read four ways, at **matched total shots** and **matched total readout
error** (a wrong outcome with the same total probability, whatever the alphabet):

- **A** qu7it · the 8 MUBs of dimension seven — the framework's claim
- **B** qu7it · 8 random bases — isolates the MUB structure from the dimension
- **C** three qubits · all 27 Pauli products — what hardware actually does today
- **D** three qubits · 8 random bases — the matched-effort rival

States: 60 random states per cell, purity 0.85. Shots: 2,000 / 8,000 / 32,000 total. Readout
error: 0%, 2%, 5%, 10%. Estimator: linear inversion, then the nearest physical state. Metric:
mean infidelity, lower is better.

## Predictions

- **H1.** A beats C at every shot budget and every readout level, by at least two standard errors.
- **H2.** A beats B by at least two standard errors once readout error is 2% or more.
- **H3 (the discriminating one).** A beats D by at least two standard errors.

**If H3 fails, the claim narrows**: the advantage belongs to good bases rather than to seven
levels, and the tree's wording must change to say so. That outcome is published exactly like a
pass.

## What this test is not

A simulation of measurement statistics, not a hardware result. No machine reads a native qu7it
for us. What is being compared is how much a given number of reads, through a given detector,
tells you about the state — an information claim, not an engineering one.
