---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: 'diff --git a/tests/test_pricing\.py[\s\S]*\n\+[^\n]*ValueError[\s\S]*diff --git a/widgets/pricing\.py[\s\S]*\n\+\s*raise ValueError'
weight: 1
---

The pushed change makes line_total raise ValueError and adds a test for it.
