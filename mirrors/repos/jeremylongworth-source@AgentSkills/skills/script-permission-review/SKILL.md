---
name: script-permission-review
description: Review scripts bundled with agent skills for permission and execution risk. Use when Codex is asked to inspect skill scripts, shell commands, file writes, destructive operations, dependency installation, or elevated permission requirements.
license: MIT
---

# Script Permission Review

## Core Workflow

1. Inventory scripts, command examples, install hooks, generated files, and
   runtime assumptions.
2. Inspect file reads/writes, deletion/move behavior, shell invocation, process
   spawning, network calls, dependency installs, and environment access.
3. Check parameter handling, path safety, quoting, dry-run support, and whether
   writes stay within the intended workspace.
4. Flag destructive, recursive, elevated, obfuscated, or auto-executed behavior.
5. Recommend sandboxing, dry-run modes, allowlists, explicit approvals, or
   converting scripts to instructions.
6. Report whether scripts are safe to keep, require changes, or should be
   blocked.

## Safety Rules

- Do not run unreviewed scripts to determine whether they are safe.
- Do not approve destructive file operations without path validation and user
  approval.
- Do not approve dependency installs or network calls without a clear purpose.

## Deliverable Shape

For script reviews, provide:

- Script inventory
- Permission and side-effect summary
- File/network/environment access
- Parameter and path safety notes
- Findings by severity
- Required changes
- Safe execution conditions

## References

- Read `references/script-permission-review-checklist.md` when reviewing
  bundled scripts or command examples.
