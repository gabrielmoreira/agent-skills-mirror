# Example output: claim-checker

_Input: a 42-line monthly claim against a 60-item rate schedule. All figures are fictional._

---

**Sheet: Claim check – 2026-11-18**

| | |
|---|---|
| Total claimed | $186,420.00 |
| Total at agreed rates | $181,035.50 |
| **Net variance** | **+$5,384.50 (+2.97%)** |
| Lines checked / flagged | 42 / 5 |

| Line | Item | Issue | Claimed | Agreed | Variance | Variance % |
|---|---|---|---|---|---|---|
| 7 | 3.04 Excavation, bulk | Rate | $48.00/m³ | $44.50/m³ | +$1,470.00 | +7.9% 🔶 |
| 12 | 5.11 Concrete, 32MPa | Quantity | 128 m³ | cap 110 m³ | +18 m³ | +16.4% 🔶 |
| 19 | — "Traffic control, weekend" | Unknown item | $2,400.00 | — | +$2,400.00 | — 🔶 |
| 23 | 6.02 Kerb, type B | Arithmetic | $3,960.00 | 85 × $45 = $3,825.00 | +$135.00 | +3.5% |
| 31 | "Topsoil supply" → 8.01 | Matched by description | $22/m³ | $22/m³ | $0 | 0% |

🔶 = over the 5% / $500 threshold

**Chat summary**
- 37 of 42 lines match the agreed rates exactly.
- The biggest issue is line 12, where concrete quantity is 18 m³ over the schedule cap. Check for an approved change.
- Line 19 isn't in the schedule. Ask for the instruction or approval reference.
- Line 23 is an arithmetic error ($135).
- [Open "Claim check – 2026-11-18"](#)
