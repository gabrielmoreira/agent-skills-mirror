# Concise Report Template

## When to Use
Use this template when the diagram is for presentation/report purposes and simplicity is the priority.
- Target audience: mentor, committee, cross-team review
- Goal: communicate the essential logic in one glance, not enumerate all implementation details

## Fixed Constraints
- **Max node count: 7** (hard ceiling, including all main boxes)
- **Orientation: left-to-right** (default; user may override to top-bottom)
- **No data store cylinders** (keep it clean, omit file artifact nodes)
- **Loop representation**: inner loop = one combined box with label "Inner Loop (Active)"; outer loop = one dashed box with label "Outer Loop (Planned)"
- **Phase 3 / external interface**: one exit box only, pointing to "Real World / Simulation" or equivalent

## Pending Confirmations Block
Always attach a note below the diagram listing items that are:
- Not yet implemented (shown as dashed in diagram)
- Known assumptions or limitations

Format:
> **Pending / Limitations:**
> 1. [item]
> 2. [item]

## Node Budget Guidance

| Slot | Suggested Role |
|------|---------------|
| 1 | Mission Input / Start |
| 2 | Phase 0 – Scene Binding |
| 3 | Phase 1 – Planning |
| 4 | Phase 2 Inner Loop (active, combined box) |
| 5 | Outer Loop (planned, dashed box) |
| 6 | Phase 3 Interface (exit box) |
| 7 | Real World / Simulation (terminal) |

Slots 5 and 7 are optional; total hard ceiling is 7.

## Style Rules for This Template
- Main flow boxes: blue fill, solid border, bold label
- Inner loop box: amber fill, solid border
- Outer loop box: light gray fill, dashed border, muted text
- Exit/external box: neutral gray fill
- Main arrows: solid, blue, block arrowhead
- Outer loop arrows: dashed, gray, open arrowhead
