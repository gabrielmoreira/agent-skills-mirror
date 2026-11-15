---
type: regex
target: { source: file, path: repo/widgets/pricing.py }
pattern: 'raise ValueError[\s\S]*1 - bulk_discount\(qty\)'
weight: 1
---

line_total keeps both sides of the conflict: main's ValueError for qty < 1 and the PR's bulk discount.
