---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: 'toml|config'
flags: i
match: not_contains
weight: 1
---

No config loading was pushed: nothing mentions config or TOML.
