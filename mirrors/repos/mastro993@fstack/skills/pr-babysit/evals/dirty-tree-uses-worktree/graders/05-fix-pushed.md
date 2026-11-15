---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: '^history: kept\n[\s\S]*\n\+[^\n]*\{seq:04d?\}'
weight: 1
---

The zero-padding fix ({seq:04}) was pushed on top of the original head, without force.
