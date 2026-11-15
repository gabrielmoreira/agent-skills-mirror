---
type: regex
target: trace
pattern: 'READY: yes[\s\S]*MERGE CONFLICT with main'
weight: 1
---

After the PR was ready the run kept watching, and its watch reported the merge conflict with main.
