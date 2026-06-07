---
description: "Structured safe-start pass 2 data flow"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:safe-start` Pass 2.

Write/update `data-flow.yaml`, `data-model.yaml`, and `invariants.yaml`.

Capture at minimum:
- flows with `trigger`, `inputs`, ordered `steps`, `outputs`, `error_states`, `trust_boundaries`, `sensitive_data`, and `risk_refs`
- data entities/lifecycles/serialized formats plus retention/compliance notes when architecture-relevant
- invariants that protect correctness, security, or recovery behavior

Pass-2 questions to force when unclear:
- Where are trust boundaries, external actors, or privilege changes?
- What data is sensitive, regulated, durable, or recoverable?
- What can fail, what should degrade gracefully, and what must never silently fail?

Ask one short clarification if trust boundaries, sensitive data, or primary error states are still unclear. Stop for approval after presenting the data-flow summary unless implementation was explicitly requested. YAML only. Focus: $ARGUMENTS.
