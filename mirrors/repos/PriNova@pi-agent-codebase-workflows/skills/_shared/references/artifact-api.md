# Structured Artifact API Runtime Reference

Read this file only when creating/updating structured artifacts or validating artifact shape.

## Schema loading

Before writing any artifact, read this shared schema set only for outputs being written:

- common envelope: `schemas/common.schema.json`
- artifact schema: `schemas/<artifact-file-base>.schema.json`

Examples:
- `risk-register.yaml` -> `schemas/risk-register.schema.json`
- `repo-inventory.yaml` -> `schemas/repo-inventory.schema.json`
- `agent-operating-guide.yaml` -> `schemas/agent-operating-guide.schema.json`

Do not read all schemas. Do not use templates.

## Resolved structured docs root

When a skill or prompt says "resolved structured docs root", resolve it exactly:

1. Resolve `workspace_root` with `git rev-parse --show-toplevel 2>/dev/null` or fallback to `pwd`.
2. Canonicalize `workspace_root` before fingerprinting when possible (`realpath`, `pwd -P`, `Path(...).resolve()`, or equivalent).
3. Use repo-local `<workspace_root>/docs/agent/api` only when the selected skill says repo-local applies and that directory exists.
4. Otherwise compute `<workspace-fingerprint>` from canonical `workspace_root` by stripping one leading slash/backslash, replacing every slash, backslash, and colon with `-`, then wrapping with `--`.
5. Use overlay root `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`.
6. Example: `/data/data/com.termux/files/home/CodeProjects/pi-mono` -> `--data-data-com.termux-files-home-CodeProjects-pi-mono--` -> `~/.pi/agent/workspaces/--data-data-com.termux-files-home-CodeProjects-pi-mono--/docs/agent/api`.

## Artifact to schema mapping

- `scopes.yaml` -> `scopes.schema.json`
- `repo-inventory.yaml` -> `repo-inventory.schema.json`
- `project-intent.yaml` -> `project-intent.schema.json`
- `architecture.yaml` -> `architecture.schema.json`
- `data-flow.yaml` -> `data-flow.schema.json`
- `data-model.yaml` -> `data-model.schema.json`
- `invariants.yaml` -> `invariants.schema.json`
- `dependency-rules.yaml` -> `dependency-rules.schema.json`
- `design-issues.yaml` -> `design-issues.schema.json`
- `risk-register.yaml` -> `risk-register.schema.json`
- `change-guide.yaml` -> `change-guide.schema.json`
- `testing-strategy.yaml` -> `testing-strategy.schema.json`
- `validation-baseline.yaml` -> `validation-baseline.schema.json`
- `contracts.yaml` -> `contracts.schema.json`
- `adr.yaml` -> `adr.schema.json`
- `agent-operating-guide.yaml` -> `agent-operating-guide.schema.json`

## Envelope artifact IDs

- Repo-level artifact IDs use `repo:<artifact-slug>`, e.g. `repo:architecture`.
- Scoped artifact IDs append the artifact slug to the scope ID with `/`, e.g. `scope:packages/ai/architecture`.
- Never append an artifact slug to a scope ID with a second colon. `scope:packages/ai:architecture` is invalid because stable IDs allow only the prefix colon.

## Runtime rule

Schemas are contracts. Skills/prompts describe behavior. Project docs outside these shared runtime refs are maintainer aids and are not runtime instructions unless user explicitly asks about this package itself.

## Schema evolution note

Shared schemas are user-facing contracts too. When new required fields are introduced, older artifacts that omit them are invalid until repaired or migrated. Validation should report missing schema coverage or missing now-required fields as schema failures, not as compatibility footnotes.
