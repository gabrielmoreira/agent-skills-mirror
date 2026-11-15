---
type: regex
target: { source: file, path: .gh-stub/pushed.diff }
pattern: '^(?![\s\S]*tests/test_pricing\.py)[\s\S]*\n\+\s*if qty >= threshold'
weight: 1
---

The pushed fix makes the tier comparison include the threshold (qty >= threshold) and leaves tests/test_pricing.py alone.
