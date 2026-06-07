---
description: "Structured safe-start pass 7 vertical slice"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:safe-start` Pass 7.

Implement one thin vertical slice after approval/request. The slice should exercise a primary user journey and at least one critical quality attribute or operating constraint when practical. Update owner YAML artifacts only for durable semantic changes.

Before implementation, confirm:
- which journey is being proven
- which quality attribute/constraint is being exercised
- which validation commands prove the slice is trustworthy

Ask one short clarification if the requested slice is too broad to validate cleanly or no meaningful validation path exists. Focus: $ARGUMENTS.
