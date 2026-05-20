---
name: safe-change
description: Safe-change workflow for documented codebases. Use for bug fixes, feature work, refactoring, risk-fix passes, test-only work, and docs-only work. Every workflow starts with preflight, then design/diagnosis, approval gate, implementation, validation, and semantic docs update only when needed.
---

# Safe Change

Goal: make changes in an existing documented codebase without architecture drift.

## Task/Focus Arguments

Prompt arguments may include a target, focus, or scope. Use these to limit investigation and implementation to a module, package, app, service, directory, user flow, risk cluster, or bounded domain area. In monorepos, prefer scoped preflight/design first, then broader consolidation only when durable docs need repo-level reconciliation.

## Core Rules

- Preflight comes first for every non-trivial task. Read `references/preflight.md`.
- Do not edit code during preflight/design/diagnosis unless explicitly asked.
- Separate bug fixing, feature work, and refactoring. Never combine in one pass.
- Prefer smallest safe change inside affected slice/module.
- Preserve public behavior unless task requires changing it.
- Add regression/characterization tests when behavior is risky or uncovered.
- Run focused validation first, then relevant broader validation.
- Update docs only when durable semantics changed. Read `references/docs-update.md` when docs may need updates.
- Do not explicitly read `AGENTS.md`; The harness injects root `AGENTS.md` automatically.

## Artifact Compatibility Contract

Safe-change accepts artifacts produced by both `safe-start` and `codebase-recon`.

Canonical repo-level docs may include:

```text
docs/agent/
  REPO_INVENTORY.md
  PROJECT_INTENT.md
  ARCHITECTURE.md
  DATA_FLOW.md
  DATA_MODEL.md
  INVARIANTS.md
  DEPENDENCY_RULES.md
  DESIGN_ISSUES.md
  RISK_REGISTER.md
  CHANGE_GUIDE.md
  TESTING_STRATEGY.md
  VALIDATION_BASELINE.md
  SCOPES.md
```

Respect artifact headers when present:

```text
Status: current | partial | stale
Evidence: planned | observed | mixed
Last validated: unknown | <date>
```

Treat `planned` docs as design intent, not source evidence. Verify against code before relying on them for implementation-sensitive claims.

## Context Budget and Non-Duplication

Do not read or update every artifact by default. Read only docs relevant to task category, scope, and risk. During preflight, apply `references/preflight.md`; during semantic docs updates, apply `references/docs-update.md`.

## Scoped Docs

If `docs/agent/SCOPES.md` exists or task uses a module/package/app/service/path focus, read `references/scoped-docs.md` during preflight. Scoped docs are optional and backward-compatible; if absent, use top-level `docs/agent/*.md` only.

## Workflow Selection

Classify task during preflight, then read the matching reference before design, diagnosis, or implementation:

- bug/error/regression/failing behavior -> `references/bug-fix.md`
- new behavior/API/UI capability/integration -> `references/feature.md`
- behavior-preserving structure change/design cleanup -> `references/refactoring.md`
- known risk, failing risk-derived test, or actionable `RISK_REGISTER.md` item -> `references/risk-fix.md`
- test-only task -> use `references/preflight.md`, preserve behavior, validate focused tests, update docs only if durable risk/invariant guidance changes
- docs-only task -> use `references/docs-update.md`, do not edit production code

## Universal Preflight Summary

Read first:
- `docs/agent/CHANGE_GUIDE.md` if present
- `docs/agent/SCOPES.md` if present; then apply `references/scoped-docs.md`
- matching scoped `REPO_INVENTORY.md` or top-level `docs/agent/REPO_INVENTORY.md` if present, for entry points, commands, and boundaries
- matching scoped `VALIDATION_BASELINE.md` or top-level `docs/agent/VALIDATION_BASELINE.md` if present, for known-good validation commands and blockers; if absent, derive validation commands from `REPO_INVENTORY.md`, package/build files, and test config, and note missing baseline in preflight

Read only docs relevant to task:
- project intent for scope, user-goal, non-goal, or product-sensitive changes
- architecture docs for module/flow changes
- data-flow docs for changes to user journeys, pipelines, transformations, or side effects
- data model docs for data/schema/API/type changes
- invariant docs for rule-sensitive changes
- dependency rules for imports/module boundaries
- risk register for risky areas
- design issues for refactoring/design work
- testing strategy for new/changed tests or validation approach; if `TESTING_STRATEGY.md` is absent, infer from existing tests and note missing strategy in preflight
- scoped `CONTRACTS.md` files for touched cross-scope APIs, shared types, schemas, events, generated clients, or persistence boundaries

Before editing code, produce:
1. Task classification
2. Relevant docs read
3. Affected slice/module/user flow
4. Expected files to inspect
5. Invariants/contracts at risk
6. Existing tests/validation commands
7. Whether implementation should proceed now or wait for approval

## Approval Gates

- Bug fixes: diagnose and propose minimal fix before implementation.
- Features: design and propose test plan before implementation.
- Refactors: design staged behavior-preserving plan before implementation.
- Risk fixes: select one failing test/risk cluster and propose minimal fix before implementation.

Stop for approval unless user explicitly asked to implement immediately.
