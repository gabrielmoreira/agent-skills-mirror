---
type: llm
focus: trace
weight: 1
---

Only comments changed: with comments set aside every file has exactly the same code tokens as before the run, and the strings """https://api.example.com // v2""", "/* no sku */", and "${item.quantity} × ${item.name} // ${item.sku.ifBlank { NO_SKU }}" are byte-identical.
