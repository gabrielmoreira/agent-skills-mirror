---
type: regex
target: { source: file, path: .gh-stub/state.json }
pattern: '"PRRT_typo": \[(?:(?!\n  \])[\s\S])*?"body": "(?:[^"\\]|\\.)*?\b[0-9a-f]{7,40}\b'
weight: 1
---

Thread PRRT_typo has a reply naming a commit SHA.
