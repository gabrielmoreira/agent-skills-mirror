---
description: "Structured safe-start pass 8 handoff"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:safe-start` Pass 8.

Verify structured artifacts are ready for `safe-change`; update `change-guide.yaml`, `risk-register.yaml`, `repo-inventory.yaml`, `design-issues.yaml`, and `scopes.yaml` as needed.

Handoff must make unresolved work explicit:
- remaining quality-attribute gaps
- unresolved security/reliability/observability concerns
- missing contracts, tests, or validation commands
- recommended next workflow entrypoint for follow-up work

If the docs are not yet safe for `safe-change`, say so explicitly and record the blockers in owner artifacts rather than silently handing off. YAML only. Focus: $ARGUMENTS.
