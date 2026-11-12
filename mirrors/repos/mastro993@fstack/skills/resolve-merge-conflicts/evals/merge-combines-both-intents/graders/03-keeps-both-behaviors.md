---
type: llm
focus: trace
weight: 1
---

In the resolved src/cart.js, lineTotal both throws a RangeError for quantities that aren't whole numbers of at least 1 and applies and rounds the discount per line, and orderTotal passes the discount to each line instead of discounting the subtotal.
