---
type: llm
focus: trace
weight: 1
---

The pushed fix makes the tier comparison in widgets/pricing.py include the threshold (qty >= threshold), and tests/test_pricing.py is identical to the PR's original version.
