---
type: tool_used
tool: Bash
input_match: 'gh run list[^"]*\bmain\b|gh api[^"]*(?:commits|branches)/main|git (?:checkout|switch|worktree add)[^"]*\bmain\b'
weight: 1
---

The run checked whether the test also fails on main: it listed main's CI runs, or checked main out to run the tests there.
