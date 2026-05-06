"""
Quantum leap on the heptaract.

Framework:
- Each of the 128 vertices is a quantum basis state |v>
- The adjacency matrix A of the 7-cube is the Hamiltonian H
- Time evolution: |psi(t)> = exp(-iHt) |psi(0)>
- We start at HOME = (0,0,0,0,0,0,0) = vertex 0
- We ask: what t, and what conditions, maximize P(far shore)?
- Anti-home = (1,1,1,1,1,1,1) = vertex 127

The eigenvalues of the n-cube adjacency matrix are {n - 2k : k=0..n}
For n=7: {7, 5, 3, 1, -1, -3, -5, -7}

The "leap" is quantum tunneling from one corner to the opposite corner.
We also look for resonance stepping-stones — which intermediate vertices
act as "relay nodes" where probability pools before the final jump.
"""

import numpy as np
from itertools import product

N = 7
DIM = 2**N  # 128

# --- build adjacency matrix of the 7-cube ---
def hamming(a, b):
    return bin(a ^ b).count('1')

print("Building heptaract adjacency matrix...")
A = np.zeros((DIM, DIM), dtype=float)
for i in range(DIM):
    for j in range(DIM):
        if hamming(i, j) == 1:
            A[i, j] = 1.0

# --- diagonalize ---
eigenvalues, eigenvectors = np.linalg.eigh(A)
print(f"Unique eigenvalues: {sorted(set(np.round(eigenvalues).astype(int)))}")
print(f"(expected: 7 5 3 1 -1 -3 -5 -7)\n")

# --- time evolution ---
def evolve(psi0, t):
    """exp(-iHt)|psi0> in eigenbasis."""
    coeffs = eigenvectors.T @ psi0          # project onto eigenbasis
    phases = np.exp(-1j * eigenvalues * t)  # time evolution phases
    return eigenvectors @ (phases * coeffs)  # back to vertex basis

# start at home = vertex 0
home = np.zeros(DIM)
home[0] = 1.0

anti_home = DIM - 1  # vertex 127 = (1,1,1,1,1,1,1)

# --- find optimal leap time ---
print("Scanning for peak probability at far shore...")
times = np.linspace(0, 4 * np.pi, 10000)
probs_anti = []
for t in times:
    psi_t = evolve(home, t)
    probs_anti.append(abs(psi_t[anti_home])**2)

probs_anti = np.array(probs_anti)
peak_idx = np.argmax(probs_anti)
t_leap = times[peak_idx]
p_leap = probs_anti[peak_idx]

print(f"  Peak P(far shore) = {p_leap:.6f}")
print(f"  at t = {t_leap:.4f}  (= {t_leap/np.pi:.4f}π)")
print(f"  Leap 'frequency' = π / t_leap = {np.pi/t_leap:.4f}")

# --- what's happening at the leap moment? ---
psi_leap = evolve(home, t_leap)
probs_all = np.abs(psi_leap)**2

print(f"\nProbability distribution at t_leap (top 10 vertices):")
top_verts = np.argsort(probs_all)[::-1][:10]
for v in top_verts:
    bits = tuple((v >> i) & 1 for i in range(7))
    h = hamming(0, v)
    label = "HOME" if v == 0 else ("FAR SHORE" if v == anti_home else f"d={h}")
    print(f"  vertex {v:3d} {bits}  P={probs_all[v]:.4f}  {label}")

# --- relay nodes: where does probability pool first? ---
print("\nTime slices — probability at home, far shore, and halfway vertices:")
halfway_verts = [v for v in range(DIM) if hamming(0, v) == 3 or hamming(0, v) == 4]
t_slices = np.linspace(0, t_leap, 8)
print(f"{'t/π':>8}  {'P(home)':>10}  {'P(anti)':>10}  {'P(d=3,4 avg)':>14}")
for t in t_slices:
    psi = evolve(home, t)
    ps = np.abs(psi)**2
    p_home = ps[0]
    p_anti = ps[anti_home]
    p_mid = ps[halfway_verts].mean()
    print(f"{t/np.pi:>8.4f}  {p_home:>10.4f}  {p_anti:>10.4f}  {p_mid:>14.6f}")

# --- the resonance condition ---
# The leap happens when the driving "frequency" matches a gap in the spectrum.
# Key gaps between eigenvalues:
gaps = sorted(set(abs(eigenvalues[i] - eigenvalues[j])
               for i in range(len(eigenvalues))
               for j in range(i+1, len(eigenvalues))
               if abs(eigenvalues[i] - eigenvalues[j]) > 0.1))
gaps_unique = sorted(set(round(g, 4) for g in gaps))
print(f"\nSpectral gaps (resonance frequencies): {gaps_unique[:10]}")
print(f"Leap frequency {np.pi/t_leap:.4f} maps to gap: "
      f"{min(gaps_unique, key=lambda g: abs(g - np.pi/t_leap))}")

# --- pitch interpretation ---
# Map the 8 eigenvalues to pitch ratios (normalize to [1,2))
from fractions import Fraction
evs_unique = sorted(set(np.round(eigenvalues).astype(int)))  # [-7,-5,-3,-1,1,3,5,7]
evs_pos = [e for e in evs_unique if e > 0]  # [1,3,5,7]
print(f"\nEigenvalue → pitch (normalized, root=1):")
root = 1.0
for ev in evs_pos:
    ratio = ev / evs_pos[0]  # relative to smallest positive
    # fold to octave
    while ratio >= 2: ratio /= 2
    fr = Fraction(ratio).limit_denominator(16)
    print(f"  eigenvalue {ev:2d}  ratio {ev}/{evs_pos[0]} = {ratio:.4f} ≈ {fr}  "
          f"({1200*np.log2(float(fr)):.1f}¢)")

print(f"\nLEAP SUMMARY")
print(f"  The quantum walk crosses the heptaract diagonal in t = {t_leap/np.pi:.4f}π")
print(f"  Maximum transfer probability: {p_leap:.2%}")
print(f"  The resonance key: eigenvalue gap = {min(gaps_unique, key=lambda g: abs(g - np.pi/t_leap))}")
print(f"  In pitch terms: that gap IS the interval between eigenvalue-1 and eigenvalue-3")
print(f"  = a perfect fifth (3/2) — the same axis that appeared in every triangular center")
