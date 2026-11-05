---
type: llm
focus: trace
weight: 1
---

The thread PRRT_none (Copilot, amount may be None) has a reply explaining the amount is always a float because Invoice.__post_init__ converts it with float(), and no None guard was added to widgets/export.py.
