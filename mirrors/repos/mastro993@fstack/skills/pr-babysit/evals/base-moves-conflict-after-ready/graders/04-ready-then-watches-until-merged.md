---
type: regex
target: trace
pattern: 'MERGE CONFLICT with main[\s\S]*READY: yes[\s\S]*?"type":"text","text":"(?:[^"\\]|\\.)*?(?:Ready|\bready\b|[Mm]ergeable|[Cc]an (?:now )?(?:be merged|merge))[\s\S]*(?:PR MERGED|state MERGED)'
weight: 1
---

After the watch showed the PR ready, a message to the user said so, and the run was still watching when the PR was merged.
