---
type: regex
target: trace
pattern: 'NO LONGER A DRAFT(?:(?!CHANGES_REQUESTED by alice)[\s\S])*?"type":"text","text":"(?:[^"\\]|\\.)*?(?:[Dd]raft|ready for review)'
weight: 1
---

The watch woke on the PR leaving draft, and the run told the user before alice's review arrived a minute later.
