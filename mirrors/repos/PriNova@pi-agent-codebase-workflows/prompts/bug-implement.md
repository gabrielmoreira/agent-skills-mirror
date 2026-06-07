---
description: "Structured bug implementation"
argument-hint: "[approved plan/focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:safe-change` bug implementation. Follow approved plan. Use/update canonical YAML artifacts only under the resolved structured docs root when durable semantics changed. No legacy prose docs.

Keep the fix minimal, preserve documented quality/security/reliability expectations, add regression coverage, and fail fast if schema/doc blockers make the change unsafe to reason about. Plan/focus: $ARGUMENTS.
