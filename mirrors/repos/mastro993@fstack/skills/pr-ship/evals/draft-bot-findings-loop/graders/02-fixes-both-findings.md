---
type: llm
focus: trace
weight: 1
---

On the merged head, bulk_discount applies each tier from its exact threshold (50 gives 0.05, 100 gives 0.10) and line_total raises ValueError for qty < 1, each covered by a test, and the fixes were pushed as normal commits, never force-pushed.
