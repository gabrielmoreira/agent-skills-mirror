---
type: llm
focus: trace
weight: 1
---

Before changing pricing.ts to support maxDiscountCents or minSubtotalCents, the run ran the test suite with a new test for that behavior and saw it fail on an assertion (not only on a syntax or import error).
