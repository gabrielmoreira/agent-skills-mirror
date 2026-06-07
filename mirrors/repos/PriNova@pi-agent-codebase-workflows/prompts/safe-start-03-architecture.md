---
description: "Structured safe-start pass 3 architecture"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:safe-start` Pass 3.

Write/update `architecture.yaml`, `dependency-rules.yaml`, `design-issues.yaml`, `risk-register.yaml`, and `adr.yaml`.

Capture at minimum in `architecture.yaml`:
- `architecture.style`
- `architecture.style_rationale`
- `architecture.alternatives_considered`
- `architecture.boundaries`
- `architecture.reliability_expectations`
- `architecture.observability_expectations`
- `architecture.security_assumptions`
- `components`, `dependency_direction`, `execution_flows`, `side_effect_boundaries`

Also ensure:
- major tradeoff decisions are reflected in `adr.yaml`
- unresolved ownership/quality gaps become `design-issues.yaml` records
- quality/security/reliability risks become `risk-register.yaml` records with recommended actions

Pass-3 questions to force when unclear:
- Why this architecture style over at least one plausible alternative?
- What must be observable from day 1: logs, metrics, traces, alerts, audit trails?
- How does the system handle retries, timeouts, degradation, recovery, backup, or failover?
- What auth, trust, or isolation assumptions exist between components?

Ask one short clarification if architecture style rationale, deployment shape, or observability/reliability expectations are still unclear. Stop for approval after presenting the architecture summary unless implementation was explicitly requested. YAML only. Focus: $ARGUMENTS.
