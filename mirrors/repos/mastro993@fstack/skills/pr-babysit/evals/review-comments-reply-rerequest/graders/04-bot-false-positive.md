---
type: llm
focus: { source: file, path: .gh-stub/state.json }
weight: 1
---

The JSON is the simulated GitHub state after the run; `replies` maps each review thread id to the replies the run posted.
PASS if PRRT_none has a reply explaining that the amount cannot be None because Invoice converts it with float() when it is created.
FAIL if PRRT_none has no reply, or the reply agrees to add a None guard.
