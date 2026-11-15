---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: '^history: kept\s*$'
weight: 1
---

Nothing was pushed: the remote head is unchanged.
