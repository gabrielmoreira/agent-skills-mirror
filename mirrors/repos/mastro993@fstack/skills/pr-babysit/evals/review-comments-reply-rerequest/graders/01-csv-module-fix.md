---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: '^(?![\s\S]*\n\+[^\n]*\bNone\b)[\s\S]*\n\+[^\n]*csv\.(?:writer|DictWriter)'
weight: 1
---

The pushed change writes rows with the csv module and adds no None guard.
