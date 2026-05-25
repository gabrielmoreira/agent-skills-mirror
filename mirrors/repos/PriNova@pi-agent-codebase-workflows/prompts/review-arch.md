---
description: "Structured architecture review"
argument-hint: "[scope]"
---
Load `/skill:arch-code-review`, resolve `<docs-root>` exactly per that skill (canonicalize `workspace_root`; if repo-local `<workspace_root>/docs/agent/api` does not apply/exist, strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`), then read only task-relevant canonical YAML artifacts there and resolve scope via `<docs-root>/repo/scopes.yaml` when present. Review current diff for architecture/data/invariant/dependency/contract/risk/test alignment. Scope: $ARGUMENTS. Read-only: do not edit code or artifacts.
