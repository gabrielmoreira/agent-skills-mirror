---
description: "Structured safe-start pass 4 contract artifacts"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:safe-start` Pass 4.

Write/update structured YAML artifacts: `change-guide.yaml`, `testing-strategy.yaml`, `contracts.yaml` when the project has inter-process, persistence, deployment, env, auth, telemetry, or external integration boundaries, `agent-operating-guide.yaml`, and root `AGENTS.md` for harness interoperability. Do not write README or other prose docs.

Capture at minimum:
- `testing-strategy.yaml` with `test_structure`, `quality_attribute_coverage`, `coverage_gaps`, `risk_to_test_priorities`, `known_blockers`, and `operability_checks` when relevant
- `contracts.yaml` owner/consumer records for APIs, schemas, events, persistence, deployment, env, auth, telemetry, or CLI boundaries when they exist
- `agent-operating-guide.yaml` validation expectations and workflow guardrails for future agents

Pass-4 questions to force when unclear:
- What contracts exist across processes, scopes, environments, persistence boundaries, or external systems?
- What must be testable and operable from day 1 to trust the thin slice?
- Which quality attributes need explicit verification or operational checks?

If omitting `contracts.yaml` for a non-trivial project, record why in evidence/unknowns. Ask one short clarification if contract boundaries or quality-attribute verification strategy are still unclear. Continue without an extra approval gate unless unresolved contract or operability questions would materially change later passes. Focus: $ARGUMENTS.
