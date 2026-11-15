---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: 'pricing'
match: not_contains
weight: 1
---

Nothing touching widgets/pricing.py or tests/test_pricing.py was pushed to the PR branch.
