---
name: codebase-recon
description: Structured reconstruction workflow for unfamiliar or undocumented codebases. Produces agent-first YAML artifacts only under a resolved structured docs root, with no prose Markdown fallback.
---

# Codebase Reconstruction — Structured API Only

Goal: reconstruct durable project understanding into canonical YAML artifacts for coding-agent ingestion.


## Structured Artifact API Contract

Legacy prose artifacts are deprecated. Do not create, update, or rely on `docs/agent/*.md`, scoped prose docs, or generated human-readable Markdown views. Use structured YAML for canonical artifacts. Root `AGENTS.md` remains a harness interoperability file and may be generated/updated only by workflows that explicitly say so.

Resolved structured docs root:

Treat `docs/agent/api` as a logical layout rooted at a resolved structured docs root, not a fixed repo path.

Resolution rules:
1. Resolve `workspace_root` with `git rev-parse --show-toplevel 2>/dev/null` or fallback to `pwd`.
2. Canonicalize `workspace_root` before fingerprinting when possible (`realpath`, `pwd -P`, `Path(...).resolve()`, or equivalent).
3. `safe-start` always creates and uses the initial repo-local root: `<workspace_root>/docs/agent/api`.
4. `codebase-recon` uses repo-local only when `<workspace_root>/docs/agent/api` already exists.
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
- `project-intent`: goals, users, journeys, non-goals, constraints, assumptions.
- `architecture`: components, architecture style, side-effect boundaries, high-level flow refs.
- `data-flow`: typed flow graph/steps, inputs, outputs, error states.
- `data-model`: entities, IDs, schemas, relationships, lifecycles, serialized formats.
- `invariants`: rules, forbidden states, enforcement locations, invariant-test refs.
- `dependency-rules`: layers, allowed/forbidden dependencies, violations, coupling hotspots.
- `design-issues`: structural drift, deferred decisions, ambiguity, ownership gaps.
- `risk-register`: failure modes, severity/confidence, affected refs, suggested tests/fixes.
- `contracts`: cross-scope APIs, schemas, events, generated clients, DB/file/deployment/env contracts.
- `testing-strategy`: test topology, coverage gaps, risk-to-test priorities.
- `change-guide`: workflow routing and checklists; references owner artifacts, duplicates no facts.
- `adr`: structured decision records with bounded prose fields.
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
2. New IDs use deterministic slugs from owner scope + semantic name: `risk:<slug>`, `entity:<slug>`, `component:<slug>`, etc.
3. If two objects slug-collide, append shortest stable discriminator from path/component/contract, not a random suffix.
4. Never renumber IDs because order changed.

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

- Do not edit production code.
- No Markdown artifacts except root `AGENTS.md` for harness interoperability in Pass 6.
- Each pass writes/updates only its owner artifacts.
- Later passes read prior YAML artifacts instead of re-reading whole repo.
- Evidence is mandatory for observed claims.
- Unknowns are explicit records, not vague prose.
- Use stable IDs and cross-references to mirror codebase ownership and relationships.

## Passes

Users may invoke this skill directly for any pass, or use the matching prompt template as a pass shortcut.

1. Inventory (`/recon-01-inventory`): write `repo-inventory.yaml` and `validation-baseline.yaml`; update `scopes.yaml` for focus.
2. Architecture (`/recon-02-architecture`): write `architecture.yaml` with components, style, boundaries, execution flow refs.
3. Data/invariants (`/recon-03-data-invariants`): write `data-model.yaml` and `invariants.yaml`.
4. Dependencies/drift (`/recon-04-dependency-rules`): write `dependency-rules.yaml` and `design-issues.yaml`.
5. Risks (`/recon-05-risk-register`): write `risk-register.yaml`.
6. Agent operating guide (`/recon-06-agents`): write `agent-operating-guide.yaml` and root `AGENTS.md`.
7. Change guide (`/recon-07-change-guide`): write `change-guide.yaml`.
8. Consolidation (`/recon-08-consolidate`): reconcile YAML artifacts, resolve contradictions with evidence, preserve owner-only facts.
9. ADR (`/recon-09-adr`): write `adr.yaml` with structured ADR records.
10. Risk-to-tests (`/recon-10-risk-tests`): write/update `testing-strategy.yaml`.

All-in-one shortcut: `/recon-all` runs the pass sequence until the requested focus is complete or the repo size requires stopping at a pass boundary.

## Artifact Shape Source

For each pass, use the shared runtime schemas as the only shape contract: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and the matching artifact schema(s). Do not rely on prose key lists.
