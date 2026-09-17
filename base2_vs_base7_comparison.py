#!/usr/bin/env python3
"""
base2_vs_base7_comparison.py  --  the full arithmetic: qubits (base-2) vs qu7its (base-7).

Turns "heptaract/base-7 is better" into COUNTED quantities and FALSIFIABLE hardware targets.
No qudit hardware needed to compute these; they are the numbers a real qudit machine must
clear to beat qubits in practice.
"""
import numpy as np
from math import log2, log, ceil
L = log2(7)  # ~2.807 : a qu7it carries this many qubits' worth of information

def report():
    print("========== BASE-2  vs  BASE-7 : the full arithmetic ==========\n")

    print("1) INFORMATION PER UNIT (per single read)")
    print(f"   qubit = 1.000 bit ;  qu7it = {log2(7):.3f} bits  ->  base-7 carries {log2(7):.2f}x more per unit\n")

    print("2) PARTICLES TO SPAN A GIVEN SPACE (Hilbert dimension D)")
    print(f"   {'D':>20} | {'qubits':>7} | {'qu7its':>7} | fewer by")
    for D in [2**10, 2**20, 2**40, 2**80]:
        n = ceil(log2(D)); m = ceil(log(D)/log(7))
        print(f"   {D:>20} | {n:>7} | {m:>7} | {n/m:.2f}x")
    print(f"   asymptotic: base-7 uses {L:.2f}x FEWER particles for the same space\n")

    print("3) ENTANGLING-GATE COUNT for QFT-class algorithms (~particles^2)")
    print(f"   ratio = (log2 7)^2 = {L**2:.2f}x FEWER two-body gates in base-7\n")

    print("4) READOUT BREAK-EVEN (from a measured ~99% qubit readout)")
    print("   One qu7it read does the work of ~2.81 qubit reads -> it may be NOISIER per read and still win.")
    print(f"   {'qubit readout':>13} | {'base-2 (3-qubit) recovery':>26} | {'qu7it 7-way must beat':>22}")
    for f2 in [0.98, 0.99, 0.995, 0.999]:
        print(f"   {f2*100:>12.1f}% | {f2**3*100:>25.2f}% | {f2**L*100:>21.2f}%")
    print()

    print("5) GATE-ERROR BREAK-EVEN (for QFT-class algorithms)")
    print(f"   base-7 uses {L**2:.1f}x fewer two-body gates, so one qu7it two-body gate may carry up to")
    print(f"   {L**2:.1f}x the error of a qubit gate and STILL tie on total algorithm error.\n")

    print("========== THE FALSIFIABLE TARGETS a real qudit machine must clear ==========")
    print(f"   * 7-way readout fidelity   >  ~{0.99**L*100:.1f}%     (vs 99% qubit readout)")
    print(f"   * two-body qu7it gate error  <  {L**2:.1f}x  the qubit gate error")
    print("   Hit both -> base-7 wins in practice. Miss -> it doesn't. The claim, made checkable.")

if __name__ == "__main__":
    report()
