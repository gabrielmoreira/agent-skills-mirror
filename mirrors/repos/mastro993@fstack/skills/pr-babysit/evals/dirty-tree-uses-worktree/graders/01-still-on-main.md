---
type: regex
target: { source: file, path: repo/.git/HEAD }
pattern: 'ref: refs/heads/main'
weight: 1
---

The user's checkout is still on main.
