---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: '^history: kept\ndiff --git'
weight: 1
---

The fix sits on top of the PR's original head: nothing was force-pushed.
