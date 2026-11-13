---
type: llm
focus: trace
weight: 1
---

The fix in duration.py accumulates the parts (for example total += ...) without unrelated behavior changes to parse_duration.
