---
description: "Structured safe-start all passes"
argument-hint: "[project intent/focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:safe-start` all-in-one mode.

Create canonical YAML artifacts under the resolved structured docs root and root `AGENTS.md` for harness interoperability. Do not create README or other prose docs as workflow artifacts.

Run the pass sequence with these requirements:
- capture prioritized quality attributes, operating constraints, success metrics, and risk areas early
- surface trust boundaries, sensitive data, and failure/degradation behavior before architecture
- record architecture style rationale, alternatives, reliability expectations, observability expectations, and security assumptions
- write contracts when the project has API, persistence, deployment, env, auth, telemetry, or external-system boundaries
- build validation baseline that catches missing schema fields in legacy artifacts when structured docs already exist
- end with one thin vertical slice plus explicit handoff blockers/gaps

Stop for approval gates unless implementation was explicitly requested. Input: $ARGUMENTS.
