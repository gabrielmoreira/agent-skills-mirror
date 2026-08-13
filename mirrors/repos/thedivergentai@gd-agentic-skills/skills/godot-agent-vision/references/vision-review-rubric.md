# Vision review rubric (rollup + gates)

> **Primary scoring instrument:** [taste-receptors.md](taste-receptors.md) — **Taste Receptor Atlas v2** (**237** micro-receptors × 0–2 across 13 families).
>
> This file is the **rollup, hard gates, and routing sheet**. Do **not** score only the coarse V1–V8 bands and call it done — that is a FAIL of the skill itself.

Score **visible pixels** only. Default capture short-edge **512**; `--detail` when TYPE/micro receptors fail for illegibility; 2–8 frame sequence when MOT/hit-peak ambiguous.

---

## Core formula

> **Good visual review = Σ taste receptors − AI pretty centroid**

| Grade | % of applicable receptor max |
|-------|------------------------------|
| **A** | **≥ 90%** |
| **B** | **75–89%** |
| **C** | **58–74%** |
| **F** | **&lt; 58%** |

Hard gates: see [taste-receptors.md](taste-receptors.md).

---

## MANDATORY load order

1. Capture WebP(s) → Read.
2. Open **[taste-receptors.md](taste-receptors.md)** — score every applicable row.
3. Deepen as needed:
   - TYPE-* → [typography-sight.md](typography-sight.md)
   - HIER-*/CTRST-* → [hier-contrast-receptors.md](hier-contrast-receptors.md)
   - SPACE-*/AFF-* → [space-affordance-receptors.md](space-affordance-receptors.md)
   - COLOR-*/ICON-* → [color-icon-receptors.md](color-icon-receptors.md)
   - COMP-*/LIGHT-*/MOT-* → [composition-fx-receptors.md](composition-fx-receptors.md)
   - SLOP-* → [anti-slop-sight.md](anti-slop-sight.md)
   - ORIG-* → [originality-sight.md](originality-sight.md)
   - ID-* → [identity-sight.md](identity-sight.md)
   - Cross-check → [ui-taste-sight.md](ui-taste-sight.md)
4. Emit family subtotals + **zero list** + ordered fixes keyed to receptor IDs.
5. Optional: roll up to V1–V8 /120 using the map in taste-receptors.md.

---

## Coarse V bands (secondary only)

| V | Theme | Max | Source families |
|---|-------|----:|-----------------|
| V1 | Hierarchy | 15 | HIER + COMP |
| V2 | Pressure contrast | 15 | CTRST + LIGHT (pressure) |
| V3 | Typography | 20 | TYPE |
| V4 | Affordances | 10 | AFF |
| V5 | Spacing | 10 | SPACE |
| V6 | Anti-slop | 15 | SLOP |
| V7 | Originality | 15 | ORIG + MOT craft |
| V8 | Identity | 20 | ID + COLOR + ICON |

Legacy A-bar **108/120** ≈ receptor grade **A** (≥90%) when all families applicable.

---

## Mode routing

| Content | Score families |
|---------|----------------|
| HUD / menu / pause | HIER CTRST TYPE AFF SPACE COLOR ICON COMP SLOP ID (+ LIGHT if FX) |
| Asset / icon sheet | TYPE (labels) COLOR ICON ORIG ID SLOP |
| Gameplay viewport | HIER CTRST SPACE COLOR COMP LIGHT MOT SLOP ID (+ TYPE/AFF if UI) |
| Marketing + game pair | ID mandatory + SLOP + ORIG + TYPE |

---

## Incomplete review = invalid

A review is **invalid** if it:

- Reports only PASS/FAIL or only V1–V8 without receptor zeroes
- Skips Family TYPE when text is visible
- Skips Family SLOP on any UI/marketing frame
- Praises “looks good” without % + zero list
