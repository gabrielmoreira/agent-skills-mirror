---
type: llm
focus: last_message
weight: 1
---

PASS if the reply says PR #13 was merged and mentions the fix the run pushed (zero-padding the invoice sequence, or its commit).
FAIL if it does not report the merge, or leaves that out.
