---
type: llm
focus: trace
weight: 1
---

The "# do not remove: used by the cron export" comment in wxdata/export.py is gone, and the final reply reports to_legacy_csv as dead code because the cron export was deleted or nothing calls it.
