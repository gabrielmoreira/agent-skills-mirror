---
kind: concept
title: Evidence bounds
---

Evidence is bounded by what it read, the question its method could answer, and the configuration under which it ran. A claim may exceed none of them.

- **State:** a result describes the bytes it read. After an edit, closing claims require evidence from the final state.
- **Question:** a result answers only the question its method could ask, and one successful run establishes only that run.
- **Configuration:** compiler version, host, capability, fixture, and protocol travel with the result. A comparison credits a change only when the rest stays fixed.

A result received from an earlier task on the route is bounded the same way: a finding, a behavior claim, or a built artifact establishes what that task observed and clears nothing else.

Truncated or elided output leaves the unseen portion open; narrow the report and ask again.

Where evidence cannot carry the desired claim, narrow the claim and name what remains unsettled.
