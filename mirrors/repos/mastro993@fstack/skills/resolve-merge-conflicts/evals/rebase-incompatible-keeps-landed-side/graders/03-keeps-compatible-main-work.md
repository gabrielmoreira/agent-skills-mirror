---
type: llm
focus: trace
weight: 1
---

main's refund work survives the rebase: src/refund.js and test/refund.test.js are unchanged, src/index.js exports roundMoney, lineTotal, refundTotal and invoiceTotal, and main's negative-rounding test still asserts roundMoney(-0.375) is -0.38 and roundMoney(-1.234) is -1.23.
