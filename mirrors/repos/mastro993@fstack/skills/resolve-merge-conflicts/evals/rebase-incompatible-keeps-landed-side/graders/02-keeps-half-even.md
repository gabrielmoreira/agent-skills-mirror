---
type: llm
focus: trace
weight: 1
---

The resolved roundMoney is PR #21's round-half-to-even: roundMoney(0.125) is 0.12 and roundMoney(-0.125) is -0.12; it is not main's half-away-from-zero, and not a new hybrid that rounds positive and negative ties by different rules.
