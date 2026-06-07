---
name: safe-start
description: Structured greenfield project workflow. Creates agent-first YAML project truth under a resolved structured docs root plus root AGENTS.md for harness interoperability.
---

# Safe Start — Structured API Only

Goal: create new projects by defining canonical structured artifacts before feature depth, then scaffold and validate one thin slice.


## Structured Artifact API Contract

Legacy prose artifacts are deprecated. Do not create, update, or rely on `docs/agent/*.md`, scoped prose docs, or generated human-readable Markdown views. Use structured YAML for canonical artifacts. Root `AGENTS.md` remains a harness interoperability file and may be generated/updated only by workflows that explicitly say so.

Resolved structured docs root:

Treat `docs/agent/api` as a logical layout rooted at a resolved structured docs root, not a fixed repo path.

Resolution rules:
1. Resolve `workspace_root` with `git rev-parse --show-toplevel 2>/dev/null` or fallback to `pwd`.
2. Canonicalize `workspace_root` before fingerprinting when possible (`realpath`, `pwd -P`, `Path(...).resolve()`, or equivalent).
3. `safe-start` always creates and uses the initial repo-local root: `<workspace_root>/docs/agent/api`.
4. Other skills use repo-local only when `<workspace_root>/docs/agent/api` already exists.
5. Otherwise use the global overlay root: `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`.
6. Compute `<workspace-fingerprint>` exactly from canonical `workspace_root`: strip one leading slash/backslash, replace every slash, backslash, and colon with `-`, then wrap with `--`. This keeps the same workspace stable.
7. Example: `/data/data/com.termux/files/home/CodeProjects/pi-mono` -> `--data-data-com.termux-files-home-CodeProjects-pi-mono--`.
8. Do not create new repo-local structured docs in unadopted repos unless the user explicitly asks for repo-local adoption there.

Logical structured layout under the resolved docs root:

```text
repo/
  scopes.yaml
  repo-inventory.yaml
  project-intent.yaml
  architecture.yaml
  data-flow.yaml
  data-model.yaml
  invariants.yaml
  dependency-rules.yaml
  design-issues.yaml
  risk-register.yaml
  change-guide.yaml
  testing-strategy.yaml
  validation-baseline.yaml
  contracts.yaml
  adr.yaml
  agent-operating-guide.yaml
scopes/
  by-path/<repo-relative-path>/...
  by-domain/<slug>/...
```

Every structured artifact must conform to `../_shared/references/schemas/common.schema.json` plus its artifact-specific schema. Do not inline, invent, or vary envelope fields.

Stable IDs required: `scope:*`, `component:*`, `entity:*`, `invariant:*`, `risk:*`, `contract:*`, `flow:*`, `command:*`, `issue:*`, `adr:*`, `testplan:*`.

Ownership rules:
- `scopes`: scope routing, ownership, cross-scope discovery only.
- `repo-inventory`: file tree, commands index, entry points, external boundaries, configs.
- `validation-baseline`: command status, blockers, recommended validation order.
- `project-intent`: product goal, users, journeys, must-have features, non-goals, constraints, assumptions, open questions, success metrics, prioritized quality attributes, operating constraints, risk areas.
- `architecture`: components, architecture style, style rationale, alternatives/tradeoffs, side-effect boundaries, deployment/operating shape, reliability expectations, observability expectations, security assumptions, high-level flow refs.
- `data-flow`: typed flow graph/steps, trust boundaries, sensitive-data handling steps, inputs, outputs, error states, degradation/recovery notes.
- `data-model`: entities, IDs, schemas, relationships, lifecycles, serialized formats, retention/compliance notes.
- `invariants`: rules, forbidden states, enforcement locations, invariant-test refs.
- `dependency-rules`: layers, allowed/forbidden dependencies, violations, coupling hotspots.
- `design-issues`: structural drift, deferred decisions, ambiguity, ownership gaps.
- `risk-register`: failure modes, severity/confidence, affected refs, mitigations/recommended actions, suggested tests/fixes.
- `contracts`: cross-scope APIs, schemas, events, generated clients, DB/file/deployment/env/auth/telemetry contracts.
- `testing-strategy`: test topology, quality-attribute coverage, coverage gaps, risk-to-test priorities, operability checks.
- `change-guide`: workflow routing and checklists; references owner artifacts, duplicates no facts.
- `adr`: structured decision records with bounded prose fields, including alternatives and consequences for major design choices.
- `agent-operating-guide`: structured source for agent operating rules. Root `AGENTS.md` may mirror this in compact harness-readable Markdown when produced by safe-start or codebase-recon Pass 6.

Redundancy rule: define each fact in its owner artifact exactly once. Other artifacts reference IDs.
Current truth rule: canonical YAML artifacts represent current state, not audit history. Remove resolved or superseded records from canonical owner artifacts by default. Keep them only when another live record still references them or an active migration requires temporary continuity. Use Git history, PRs, issues, or ADRs for audit/history.
Prose rule: bounded prose allowed only in `summary`, `notes`, `rationale`, `context`, `decision`, `recommended_action`, and similar scalar fields.
Scope rule: if focus is path-like, write under `<docs-root>/scopes/by-path/<focus>/`; otherwise under `<docs-root>/scopes/by-domain/<slug>/`. Always update `<docs-root>/repo/scopes.yaml`.



## Runtime Schema Loading

When a workflow creates, updates, migrates, or validates structured artifacts, read `../_shared/references/artifact-api.md` first. Then read only the shared skill package schemas needed for the artifacts being written:
- `../_shared/references/schemas/common.schema.json`
- `../_shared/references/schemas/<artifact-file-base>.schema.json`

Do not read all schemas. Do not use templates. Schemas are runtime API contracts; project docs outside the shared runtime refs are maintainer aids unless the user asks about this package itself.

## Structured Artifact Write/Update Protocol

Use this protocol whenever creating or updating YAML artifacts.

### 1. Scope and owner resolution

1. Resolve scope first from task/focus and `<docs-root>/repo/scopes.yaml` when present.
2. Path focus uses longest prefix match; domain focus requires explicit domain/contract/task evidence.
3. Select the single owner artifact for each fact using the ownership rules above.
4. Never duplicate owner facts in router/checklist artifacts; reference stable IDs instead.

### 2. Read-before-write

1. Read the existing target YAML if it exists.
2. Read directly referenced owner artifacts needed to preserve refs and avoid duplication.
3. If target YAML is absent, create it with the common envelope and artifact-specific top-level keys.
4. Preserve unknown fields unless they conflict with this protocol; do not silently drop agent/user-added structured data.

### 3. Stable ID generation

1. Reuse existing IDs whenever the semantic object is the same, even if name/path changed.
2. New record IDs use deterministic slugs from owner scope + semantic name: `risk:<slug>`, `entity:<slug>`, `component:<slug>`, etc.
3. Envelope `artifact_id` values use `repo:<artifact-slug>` for repo-level artifacts and `<scope.id>/<artifact-slug>` for scoped artifacts, e.g. `repo:architecture` and `scope:packages/ai/architecture`.
4. Never append an artifact slug to a scope ID with a second colon; `scope:packages/ai:architecture` is invalid.
5. If two objects slug-collide, append shortest stable discriminator from path/component/contract, not a random suffix.
6. Never renumber IDs because order changed.

### 4. Upsert semantics

For each discovered fact/object:
1. Match existing record by ID first.
2. If no ID match, match by stable source-of-truth fields: path+symbol, contract source path, command string+cwd, entity name+owner scope, rule owner+kind.
3. If matched, update only changed fields, append/refresh evidence, and preserve unrelated fields.
4. If unmatched, insert new record in deterministic order by ID or explicit `order` field.
5. If an existing observed record is resolved, superseded, or no longer supported, delete it from the canonical owner artifact by default.
6. Keep a record with `status: stale` or `deprecated` only when a live reference still depends on it or an active migration needs temporary continuity. Add evidence/unknown explaining why, and link replacement ID when known.
7. Delete accidental duplicates, malformed records, and unreferenced resolved/superseded records, and mention deletion in final response.

### 5. Evidence and confidence

1. Every observed record needs at least one evidence ref with file/symbol/command/doc/diff observation.
2. Planned records may use `evidence_mode: planned` and confidence `low` or `medium`.
3. Mixed records must separate observed fields from planned/assumed fields via evidence refs or `unknowns`.
4. Do not upgrade `status: current` or confidence `high` without source or command evidence.

### 6. Reference integrity

Before writing final artifacts:
1. Check every `*_ref`, `*_refs`, and `depends_on` ID points to a record in the same artifact set or is explicitly listed as external/unknown.
2. Prefer adding missing owner records as compact stubs over leaving dangling refs.
3. For cross-scope refs, ensure `scopes.yaml` and `contracts.yaml` identify owner/consumer relationship.
4. If ownership is ambiguous, create/update `design-issues.yaml` with `kind: ownership_gap` and reference it.

### 7. Status transitions

Allowed transitions:
- `planned -> partial -> current`
- `current -> stale -> current`
- `current|stale|partial -> deprecated`

Rules:
- `current` requires sufficient observed evidence for the represented scope.
- `partial` means useful but incomplete evidence.
- `stale` means contradicted by newer source evidence or missing source path. Use it as a temporary migration/quarantine state, not a permanent archive state.
- `deprecated` means superseded; include `replacement_ref` when known. Use it only when a live reference still needs continuity during migration; otherwise remove the record from the canonical artifact.

### 8. Deterministic formatting

1. Use YAML with two-space indentation.
2. Use stable top-level key order: envelope keys first, artifact-specific keys next.
3. Sort unordered arrays by `id`; keep ordered flow/checklist arrays by `order`.
4. Use `null`, `[]`, or `{}` consistently rather than omitting required envelope fields.
5. Keep prose scalar fields concise; no long narrative blocks.

### 9. Validation before completion

Perform best-effort validation after writing:
1. Re-read changed YAML for parse/syntax sanity when practical.
2. Validate against the shared schemas by inspection/re-read: envelope keys, artifact-specific top-level keys, required arrays/items, stable ID prefixes, and obvious dangling refs.
3. Verify no legacy Markdown artifacts were created or updated by the workflow, except root `AGENTS.md` when explicitly produced for harness interoperability.
4. Report changed YAML files, validation performed, unresolved unknowns, and any records intentionally retained or pruned as part of compaction.


## Core Rules

- Produce canonical YAML artifacts under the resolved structured docs root. Safe-start creates the initial repo-local root at `<workspace_root>/docs/agent/api`; root `AGENTS.md` is the only Markdown workflow output.
- Do not write README or prose docs as workflow artifacts. Root `AGENTS.md` is allowed as compact harness interoperability output.
- Make decision-driving quality attributes explicit early. Capture proportional depth, but do not skip the fields; use concise notes or empty arrays only when clearly not applicable and justified by context.
- Design data flow first, then boundaries, then scaffold.
- Stop for approval after intent, data flow, architecture/scaffold plan, and vertical-slice plan unless user explicitly requested implementation.
- After baseline and first slice, future changes use `safe-change` with structured artifacts.

## Guidance Levels

Ask once if unknown: `freshman`, `standard`, or `expert`. Guidance level affects conversation only, not artifact schema.

## Passes

Users may invoke this skill directly for any pass, or use the matching prompt template as a pass shortcut.

1. Intent (`/safe-start-01-intent`): write `project-intent.yaml`, initial `repo-inventory.yaml`, optional `scopes.yaml`; explicitly capture prioritized quality attributes, operating constraints, success metrics, and risk areas.
2. Data flow (`/safe-start-02-data-flow`): write `data-flow.yaml`, `data-model.yaml`, `invariants.yaml`; surface trust boundaries, sensitive data, failure/degradation states, and retention/compliance implications.
3. Architecture (`/safe-start-03-architecture`): write `architecture.yaml`, `dependency-rules.yaml`, `design-issues.yaml`, `risk-register.yaml`, `adr.yaml`; require style rationale, alternatives/tradeoffs, reliability expectations, observability expectations, security assumptions, and ADR linkage for major decisions.
4. Contract docs (`/safe-start-04-contract-docs`): write `change-guide.yaml`, `testing-strategy.yaml`, `contracts.yaml` whenever the project has inter-process, persistence, deployment, env, auth, or external integration boundaries, `agent-operating-guide.yaml`, and root `AGENTS.md`; include quality-attribute verification and operability expectations.
5. Scaffold plan (`/safe-start-05-scaffold-plan`): output plan in chat only; after approval create files. Plan must preserve architecture constraints and first-slice validation path.
6. Validation baseline (`/safe-start-06-validation`): write `validation-baseline.yaml` from actual commands/status; include schema/docs validation expectations and blockers, especially legacy artifacts missing now-required fields.
7. Thin vertical slice (`/safe-start-07-vertical-slice`): implement one minimal slice that exercises a primary journey and at least one critical quality attribute or operating constraint; update structured artifacts only for durable semantic changes.
8. Handoff (`/safe-start-08-handoff`): update `change-guide.yaml`, `risk-register.yaml`, `repo-inventory.yaml`, `design-issues.yaml`, `scopes.yaml`; ensure unresolved quality/security/reliability/operability gaps are captured for `safe-change`.

All-in-one shortcut: `/safe-start-all` runs the pass sequence with approval gates unless implementation was explicitly requested.

## Required Artifact Content

- `project-intent.yaml`: `intent.product_goal`, `intent.target_users`, `intent.primary_journeys`, `intent.must_have_features`, `intent.non_goals`, `intent.constraints`, `intent.assumptions`, `intent.open_questions`, `intent.quality_attributes`, `intent.operating_constraints`, `intent.success_metrics`, `intent.risk_areas`.
- `data-flow.yaml`: `flows` with `trigger`, `inputs`, ordered `steps`, `outputs`, `error_states`, `trust_boundaries`, `sensitive_data`, and `risk_refs`.
- `data-model.yaml`: `entities`, `lifecycles`, `serialized_formats`; include retention/compliance notes when they influence architecture or operations.
- `invariants.yaml`: invariant records with enforcement status and locations.
- `architecture.yaml`: `architecture.style`, `architecture.style_rationale`, `architecture.alternatives_considered`, `architecture.boundaries`, `architecture.reliability_expectations`, `architecture.observability_expectations`, `architecture.security_assumptions`, plus `components`, `dependency_direction`, `execution_flows`, `side_effect_boundaries`.
- `risk-register.yaml`: risk records with `affected_refs`, evidence-backed severity/confidence, and `recommended_action`; include quality/security/reliability risks when relevant.
- `testing-strategy.yaml`: `test_structure`, `quality_attribute_coverage`, `coverage_gaps`, `risk_to_test_priorities`, `known_blockers`, optional `operability_checks`; connect important risks and quality attributes to verification.
- `contracts.yaml`: owner/consumer contract records for APIs, schemas, events, generated clients, persistence, deployment, env, auth, telemetry, or CLI boundaries.
- `adr.yaml`: ADR records for major architecture choices with context, decision, alternatives, and consequences.
- `validation-baseline.yaml`: command records with cwd, status, last_run, blockers, recommended order; include docs/schema validation when the workflow introduces or changes structured artifacts.
