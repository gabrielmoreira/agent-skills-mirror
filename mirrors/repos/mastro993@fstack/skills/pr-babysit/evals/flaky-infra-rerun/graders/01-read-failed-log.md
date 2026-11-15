---
type: tool_order
before:
  tool: Bash
  input_match: 'gh run view|--log|/logs'
after:
  tool: Bash
  input_match: 'gh run rerun'
weight: 1
---

The run read the failed log before re-running.
