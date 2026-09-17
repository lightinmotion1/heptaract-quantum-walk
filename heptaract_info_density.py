#!/usr/bin/env python3
"""
heptaract_info_density.py  --  FIRST PLANTABLE FLAG: base-7 measures more of the space per read.

Miah's "better" = richer, not faster. Each read should capture the SIGNAL *and* its CONTEXT
(the space around it -- the apparatus's health, the metal's deterioration) in one measurement.

Concrete, countable claim:
  * carry a SIGNAL (1 data bit) AND a CONTEXT flag (ternary apparatus-health: 0 clean / 1 drifting
    / 2 degraded) together.
  * joint information = 2 x 3 = 6 states.
  * base-7: ONE qu7it holds all 6 (6 <= 7) -> one read returns signal AND context.
  * base-2: needs ceil(log2 6) = 3 qubits -> three particles/reads for the same sample.

We simulate a stream, encode signal+context into a single qu7it, decode, and confirm BOTH come
back from ONE read -- then put the number on "how much more of the space per measurement."
"""
import numpy as np
from math import log2, ceil

def encode(data, flag):   # data in {0,1}, flag in {0,1,2}  -> qu7it level 0..5 (6 reserved)
    return flag * 2 + data
def decode(level):
    return level % 2, level // 2

def main():
    # --- capacity per single read ---
    cap_qubit = log2(2)     # 1.000 bit
    cap_qu7it = log2(7)     # 2.807 bits
    print("=== capacity of ONE read ===")
    print(f"  qubit  (base-2): {cap_qubit:.3f} bit")
    print(f"  qu7it  (base-7): {cap_qu7it:.3f} bits   -> {cap_qu7it/cap_qubit:.2f}x more room per read")

    # --- the concrete co-encoding task ---
    joint = 6                       # signal(2) x apparatus-health(3)
    q7 = 1
    q2 = ceil(log2(joint))          # = 3
    print("\n=== task: carry SIGNAL + apparatus-health CONTEXT in one read ===")
    print(f"  joint states needed: {joint}")
    print(f"  base-7 particles: {q7}   base-2 particles: {q2}")

    # --- verify one qu7it read returns BOTH, over a stream ---
    rng = np.random.default_rng(0); N = 200000
    signal = rng.integers(0, 2, N)
    health = rng.integers(0, 3, N)          # the 'space' around the signal (the metal's state)
    level  = encode(signal, health)         # one qu7it per sample
    ds, dh = decode(level)
    both_ok = np.mean((ds == signal) & (dh == health))
    print(f"  one qu7it read recovers (signal AND health) correctly: {both_ok*100:.1f}% of samples")

    # --- put the number on it ---
    bits_per_read_7 = log2(joint) / q7      # ~2.585 bits in ONE read
    bits_per_read_2 = 1.0                    # a qubit read = 1 bit; you'd need 3 reads for the sample
    print("\n=== HOW MUCH MORE OF THE SPACE PER MEASUREMENT ===")
    print(f"  base-7: {bits_per_read_7:.3f} bits per read  (signal + full context, one shot)")
    print(f"  base-2: {bits_per_read_2:.3f} bit  per read  (a fragment; needs {q2} reads for the whole sample)")
    print(f"  --> base-7 captures {bits_per_read_7/bits_per_read_2:.2f}x more of the space in a single measurement.")

    print("\n--- honest scope (so it survives a skeptic) ---")
    print("  * Real information-theory: a bigger alphabet carries more bits/symbol. Not a trick.")
    print("  * Works because signal & context are COMPATIBLE (jointly readable); uncertainty still")
    print("    forbids co-reading INCOMPATIBLE properties -- no free lunch there.")
    print("  * Physically, a qu7it read is harder/noisier than a qubit read -> net HARDWARE benefit")
    print("    is the next thing to prove. And the gain is the general qudit advantage (7 is good,")
    print("    not magic). But the FLAG is planted: base-7 measures more of the space per read.")

if __name__ == "__main__":
    main()
