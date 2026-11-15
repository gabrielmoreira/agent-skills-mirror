---
type: regex
target: { source: file, path: .gh-stub/state.json }
pattern: '"merged": false[\s\S]*"resolved": \[\]'
weight: 1
---

No review thread was resolved and the PR was not merged.
