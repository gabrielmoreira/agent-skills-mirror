---
description: "Validate structured YAML docs"
argument-hint: "[scope|docs-root|diff]"
---
Load `/skill:structured-doc-validate`, resolve `<docs-root>` exactly per that skill (canonicalize `workspace_root`; if repo-local `<workspace_root>/docs/agent/api` does not exist, strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`), then read `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only schemas for artifacts being validated. Validate schema shape, shared schema coverage for canonical artifact files, reference integrity, evidence validity, coverage, and granularity. Treat missing now-required fields in legacy artifacts as schema failures, not compatibility notes. Read-only: do not edit code or artifacts unless explicitly asked to repair. Focus: $ARGUMENTS.
