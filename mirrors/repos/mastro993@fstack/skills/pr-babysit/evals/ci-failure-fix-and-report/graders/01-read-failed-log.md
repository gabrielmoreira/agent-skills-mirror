---
type: tool_order
before:
  tool: Bash
  input_match: 'gh run view|--log|/logs'
after:
  tool: Bash
  input_match: '\bgit\b.*\b(?:commit|push)\b'
weight: 1
---

The run read the failing check's log before committing or pushing a change.
