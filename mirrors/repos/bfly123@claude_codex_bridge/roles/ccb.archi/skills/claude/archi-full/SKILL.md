---
name: archi-full
description: Run full-project architecture analysis with Architec. Use when the user asks for an overall architecture score, full hotspot review, topology diagnosis, or main structural weaknesses.
---

# Archi Full

Inspect `ccb-archi --help || archi --help`, then run the supported full review.
Newer Architec uses `ccb-archi --full || archi --full`; older installs may use
`ccb-archi . || archi .`.

Use `--refresh-from-hippo --full` only when the user asks for fresh structural
inputs. Read `.architec/architec-summary.md` before JSON. Summarize score,
top structural problems, improvements, and validation gates.

