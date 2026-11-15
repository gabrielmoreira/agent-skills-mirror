---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: '^history: kept\s*$'
weight: 1
---

Nothing was pushed: the PR head is unchanged.
