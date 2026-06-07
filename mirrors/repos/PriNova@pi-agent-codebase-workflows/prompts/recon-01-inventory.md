---
description: "Structured recon pass 1 inventory"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:codebase-recon` Pass 1.

Write/update `repo-inventory.yaml`, `validation-baseline.yaml`, and initial `project-intent.yaml`; update `scopes.yaml` when focused.

Infer from repo evidence when possible:
- product goal, target users, primary journeys, must-have features, non-goals
- prioritized quality attributes/nonfunctional priorities
- operating constraints, success metrics, and risk areas
- command/validation baseline and obvious blockers

If the codebase does not reveal some intent fields, keep the required fields present with low-confidence placeholders, explicit unknowns, and evidence explaining the ambiguity. Canonical YAML only under the resolved structured docs root. Focus: $ARGUMENTS.
