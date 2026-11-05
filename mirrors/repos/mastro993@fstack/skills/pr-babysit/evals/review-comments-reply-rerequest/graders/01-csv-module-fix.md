---
type: llm
focus: trace
weight: 1
---

widgets/export.py on the pushed head writes rows with the csv module (csv.writer or csv.DictWriter) and the test check passes on that head.
