---
type: llm
focus: trace
weight: 1
---

The reply recognizes the sprint-capacity rule in commitToSprint (committed estimates must not exceed capacity) as an invariant spanning items and a sprint, and either keeps it inside one aggregate boundary (for example a Sprint aggregate recording its commitments and their estimates) or asks the user whether a sprint can be briefly over capacity; it does not silently drop the rule.
