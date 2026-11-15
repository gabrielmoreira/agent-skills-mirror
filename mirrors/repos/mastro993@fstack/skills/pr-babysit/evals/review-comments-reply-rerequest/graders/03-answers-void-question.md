---
type: llm
focus: { source: file, path: .gh-stub/state.json }
weight: 1
---

The JSON is the simulated GitHub state after the run; `replies` maps each review thread id to the replies the run posted.
PASS if PRRT_void has a reply saying voided invoices are already left out of the export.
FAIL if PRRT_void has no reply, or the reply says otherwise.
