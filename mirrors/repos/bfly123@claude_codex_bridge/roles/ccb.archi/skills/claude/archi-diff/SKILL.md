---
name: archi-diff
description: Run diff-based architecture analysis with Architec. Use when the user asks whether current changes are architecturally safe, what the current git diff impacts, or which changed components carry structural risk.
---

# Archi Diff

Inspect `ccb-archi --help || archi --help`, then run the supported incremental
review command. Newer Architec uses `ccb-archi || archi`; older installs may
need `ccb-archi --diff . || archi --diff .`.

Read `.architec/architec-summary.md` first and use
`.architec/architec-analysis.json` for exact scores and concern details. Lead
with blocking architecture findings and do not paste raw JSON.

