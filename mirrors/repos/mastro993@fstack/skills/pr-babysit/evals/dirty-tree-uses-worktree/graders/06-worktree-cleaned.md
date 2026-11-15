---
type: tool_order
before:
  tool: Bash
  input_match: 'worktree add'
after:
  tool: Bash
  input_match: 'worktree (?:remove|prune)'
weight: 1
---

The run worked in its own worktree and removed it afterwards.
