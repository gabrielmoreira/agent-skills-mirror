---
type: llm
focus: trace
weight: 1
---

The final reply flags "# timeout in seconds" in wxdata/config.py as a mismatch, because HTTP_TIMEOUT is 30_000 and the client divides it by 1000, so the value is in milliseconds.
