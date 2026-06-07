---
description: "Structured safe-start pass 1 intent"
argument-hint: "[intent/focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:safe-start` Pass 1.

Write/update `project-intent.yaml`, initial `repo-inventory.yaml`, optional `scopes.yaml`.

Capture at minimum in `project-intent.yaml`:
- `intent.product_goal`
- `intent.target_users`
- `intent.primary_journeys`
- `intent.must_have_features`
- `intent.non_goals`
- `intent.constraints`
- `intent.assumptions`
- `intent.open_questions`
- `intent.quality_attributes` with priority and concrete scenario/target
- `intent.operating_constraints`
- `intent.success_metrics`
- `intent.risk_areas`

Pass-1 questions to force when unclear:
- What are the top 3 quality attributes or nonfunctional priorities?
- What deployment, privacy, compliance, latency, cost, or platform constraints shape architecture?
- What assumptions could invalidate later architecture work if wrong?

Ask one short clarification if product goal, target users, or top quality attributes are still unclear. Stop for approval after presenting the intent summary unless implementation was explicitly requested. YAML only. Input: $ARGUMENTS.
