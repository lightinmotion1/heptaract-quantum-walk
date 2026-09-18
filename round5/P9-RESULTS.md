# P-9 · The MUB reading on hardware that was never built for it

**Run:** 2026-09-18, ibm_kingston, qubits [88, 89, 90] · 22 seconds of QPU time (11 per job)
**Pre-registration:** `PREREGISTRATION-2026-09-18-P9.md`
**SHA-256:** `b88836016302a47fa4bc6bc3c7e1a4867315ff23ccdcf2ea7aba82cf24c69a50`
**Script:** `round5/mub_hardware.py` · **Results:** `results/mub_hardware.json`

T-2.9 showed in simulation that a seven-level state read in its eight mutually unbiased bases
beats twenty-seven Pauli settings at matched shots. That comparison assumed the readings cost
nothing to perform. On a qubit machine they do.

| Test | Prediction | Verdict |
|---|---|---|
| H1 | The MUB reading survives its compilation cost on hardware | **Fails** |
| H2 | The two-qubit gate cost of the MUB readings eats the advantage | **Holds** — as declared in advance |

| State | MUB infidelity | Pauli infidelity | z (positive favours MUB) |
|---|---|---|---|
| level 0 | 0.1765 ± 0.0088 | 0.1035 ± 0.0122 | -4.86 |
| uniform | 0.3384 ± 0.0140 | 0.2223 ± 0.0168 | -5.31 |
| ends | 0.2899 ± 0.0096 | 0.2112 ± 0.0131 | -4.85 |
| random | 0.3453 ± 0.0125 | 0.2349 ± 0.0160 | -5.45 |

**Mean infidelity: MUB 0.28753, Pauli 0.19299.**
Two-qubit gates per circuit, state preparation included: MUB [0, 1, 5, 29, 30, 32], Pauli [0, 1, 5, 19, 20, 23, 24, 26].

## Reading

The information advantage is real and it is not enough. Each MUB of dimension seven, embedded in
three qubits, is a generic three-qubit unitary; compiled, the readings carry up to a third more
two-qubit gates than the Pauli settings, and every one of those gates spends fidelity. The
mathematics of T-2.9 is untouched — what fails is the attempt to perform seven-level structure on
machines whose native piece is two-level.

**This is the clearest statement the framework has of what it needs.** Not a better argument: a
different processor. The bar is now numeric — on this chip the MUB route must save more than the
~0.09 infidelity its compilation costs, and a native qu7it would pay none of that.

It also sharpens the tree's Base-7 branch. Every claim there survives; each one now carries the
same footnote, which is that its advantage is only collectable on hardware with a seven-level
piece. Anyone proposing to build one can point at this number.
