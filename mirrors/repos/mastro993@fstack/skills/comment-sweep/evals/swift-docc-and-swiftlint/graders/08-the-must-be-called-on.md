---
type: llm
focus: trace
weight: 1
---

The "Must be called on the main actor" comment on SyncStatus.apply is still present, and the final reply proposes annotating apply or SyncStatus with @MainActor (or an equivalent compiler-enforced main-actor isolation) as the way to retire it.
