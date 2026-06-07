---
description: "Structured safe-start pass 5 scaffold plan"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:safe-start` Pass 5.

Produce scaffold plan in chat only before file creation approval: tree, tooling, commands, generated files, first thin slice, validation path, and major risks. Do not create docs except canonical YAML updates already approved.

The scaffold plan must:
- preserve the architecture boundaries and dependency rules already recorded
- identify how the first slice exercises a primary journey and at least one critical quality attribute or operating constraint
- include observability/security/reliability hooks needed for that first slice
- identify what to validate immediately after scaffolding

Ask one short clarification if the proposed scaffold cannot clearly satisfy the architecture constraints or first-slice validation path. Focus: $ARGUMENTS.
