---
type: llm
focus: trace
weight: 1
---

The reply flags the business rules and numeric status codes in OrderService.updateStatus (for example "cannot ship an unpaid order", the 20% discount rule, status 3) and proposes moving them onto domain objects with operations named in domain verbs (such as ship, place, or markPaid) instead of a generic updateStatus.
