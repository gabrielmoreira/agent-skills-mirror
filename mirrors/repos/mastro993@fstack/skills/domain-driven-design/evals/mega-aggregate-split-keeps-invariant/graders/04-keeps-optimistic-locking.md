---
type: llm
focus: trace
weight: 1
---

The reply keeps optimistic concurrency on each aggregate, consistent with docs/adr/0001-optimistic-locking.md, and does not recommend last-write-wins or removing the version check as the fix.
