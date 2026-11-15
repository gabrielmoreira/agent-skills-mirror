---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: '^history: kept\n[\s\S]*\n\+\s*raise ValueError'
weight: 1
---

The pushed head still contains the PR's original commit (no rebase or force-push) and brings in main's qty < 1 check.
