# T-3.1 · Why E?  — and the answer the model actually gives

**Run:** 2026-09-18, by exhaustive scan on a laptop.
**Script:** `round5/t3_1_why_e.py` · **Results:** `results/t3_1_why_e.json`
**Desk:** Free (Miah J. Fry) & Claude

## What was declared before the scan

**Criterion:** the largest axis magnitude among symmetric spreads. Secondary: an axis landing
exactly on a pitch class. Tertiary: symmetry at all.
**Prediction (the tree's):** E is the unique maximiser.
**Falsifier:** several roots tie, or E loses.

## What the port reproduces first

The Lab v0.2 radial module was ported line for line and its locked values recovered exactly:
C major reads **D** at 0.00 ¢ · Pythagorean +3.93 ¢ · just +38.49 ¢ · the climb on E stands at
**F♯**, symmetric · seven even rays read magnitude **0**. The instrument is faithful.

## The scan

Every centre root (12) × every root-step set (steps 1–6) × three tunings × both orientations —
432 configurations.

| Step between roots | Axis magnitude | Spread symmetric |
|---|---|---|
| **1 semitone** | **0.74641** | yes |
| 2 (the whole-tone climb) | 0.20000 | yes |
| 3 | 0.20000 | no |
| 4 | 0.20000 | no |
| 5 | 0.05359 | yes |
| 6 | 0.20000 | no |

**Verdict: the prediction fails, and instructively.**

- **The magnitude is identical across all twelve centre roots**, in every tuning and both
  orientations. The axis offset from the centre is fixed per configuration. The reading is
  transposition-covariant: rotate the whole picture and nothing changes but the names.
- Under the declared criterion, **72 configurations tie for best**, at every one of the twelve
  centres. E is not the unique maximiser. E is not a maximiser of anything here.
- What the criterion *does* single out is **the step, not the centre**: a semitone-spaced climb
  carries the largest symmetric magnitude, 0.746 against the whole-tone climb's 0.200.

## Why E looked central

The five roots of the climb are C · D · E · F♯ · G♯. E is the midpoint of that span — but the span
begins at C, and C is where the naming of notes begins, not where the mathematics does. **E centres
the climb because the climb was anchored at C.** Start the same climb at F and its centre is A;
the magnitude, the symmetry and the F♯-style standing result all follow along unchanged.

## What this costs, and what it opens

The Lab's standing result survives intact — every climb stands at centre + 2, symmetric, in every
key. What does not survive is the claim that **E** is derivable. A pitch class cannot be forced by
a model that has no absolute reference in it.

For E to mean more than convention, the framework needs an **anchor in frequency, not in naming** —
a physical rate the circle is pinned to, from which one pitch class follows. That is now a sharp,
separate question, and the honest place the tree should carry E until then is as a chosen origin,
not a derived one.
