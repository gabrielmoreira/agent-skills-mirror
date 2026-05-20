---
name: arch-code-review
description: Architecture-aware code review for current diffs in documented codebases. Use to review changes against architecture, data model, invariants, dependency rules, risk register, side-effect boundaries, and tests. Read-only workflow.
---

# Architecture Code Review

Goal: review proposed changes for correctness, drift, data consistency, side-effect boundary violations, and missing tests.

## Scope Argument

Review prompts accept an optional `[scope]` argument. Use it to focus review on a module, package, app, service, directory, or bounded domain area when a diff spans multiple areas. Still inspect immediate dependencies and contracts needed to judge correctness.

## Artifact Compatibility Contract

Architecture review accepts artifacts produced by both `safe-start` and `codebase-recon`.

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

Treat `planned` docs as design intent, not source evidence. Use source diff and observed docs as implementation truth. Report divergence from intent only when it is unacknowledged, risky, or violates current docs/contracts.

## Context Budget and Non-Duplication

Review should not load every artifact by default. Read router docs needed to locate scope, then owner artifacts relevant to changed semantics.

Artifact ownership rules:
- `CHANGE_GUIDE.md` routes workflow; semantic truth lives in specific docs.
- `REPO_INVENTORY.md` maps files/entry points/command names; `VALIDATION_BASELINE.md` owns command status/blockers.
- `ARCHITECTURE.md` owns structure and side-effect boundaries; `DEPENDENCY_RULES.md` owns import/dependency direction.
- `DATA_FLOW.md` owns lifecycles and transformations; `DATA_MODEL.md` owns schemas/entities; `INVARIANTS.md` owns rules/forbidden states.
- `DESIGN_ISSUES.md` owns drift/deferred design problems; `RISK_REGISTER.md` owns failure modes and risk-tested fixes.
- `TESTING_STRATEGY.md` owns test approach/gaps; `VALIDATION_BASELINE.md` owns exact validation status.
- `SCOPES.md` routes to scoped docs; scoped docs own local detail, top-level docs hold repo-wide summary.

Flag review findings when a change duplicates detailed semantic truth across artifacts instead of updating the owner artifact and linking from router docs.

## Scoped Docs Discovery

Architecture review works with both legacy unscoped docs and hierarchical scoped docs.

If `docs/agent/SCOPES.md` is absent:
- review against top-level `docs/agent/*.md` only

If `docs/agent/SCOPES.md` is present:
- read it before selecting deeper docs
- match diff paths and explicit scope arguments to `path` scopes by longest repo-relative path prefix
- use domain scopes only when review target, scope tags, or contract links make them relevant
- read matching scoped `README.md` only if present, then task-relevant scoped docs
- read top-level docs as fallback for missing categories and repo-wide rules
- safe-start scoped docs may include `PROJECT_INTENT.md`, `DATA_FLOW.md`, `TESTING_STRATEGY.md`, and `VALIDATION_BASELINE.md`; read them only when relevant to changed files/behavior
- for cross-scope diffs, read relevant scoped `CONTRACTS.md` and `DEPENDENCY_RULES.md` from each touched owner/consumer scope
- verify matched source paths still exist before treating scoped docs as current
- when scoped docs are marked `planned`, use them as intent and verify implementation-sensitive claims against source evidence

## Rules

- Do not edit code.
- Review current diff unless user specifies another target.
- Do not explicitly read `AGENTS.md`; pi injects root `AGENTS.md` automatically.
- Read only relevant deeper docs:
  - `docs/agent/CHANGE_GUIDE.md` when present
  - `docs/agent/SCOPES.md` when present
  - matched scoped `README.md` if present, and relevant scoped docs when present
  - matching scoped `REPO_INVENTORY.md` or top-level `docs/agent/REPO_INVENTORY.md` when entry points, commands, or external boundaries matter
  - matching scoped `VALIDATION_BASELINE.md` or top-level `docs/agent/VALIDATION_BASELINE.md` when build/test/tooling/validation behavior changes; if absent, infer validation expectations from package/build files and note missing baseline only when relevant
  - `docs/agent/PROJECT_INTENT.md` for scope, non-goals, users, journeys, or product-sensitive changes
  - `docs/agent/ARCHITECTURE.md`
  - `docs/agent/DATA_FLOW.md` for user journeys, pipelines, transformations, side effects, and error states
  - `docs/agent/DATA_MODEL.md`
  - `docs/agent/INVARIANTS.md`
  - `docs/agent/DEPENDENCY_RULES.md`
  - `docs/agent/RISK_REGISTER.md`
  - `docs/agent/DESIGN_ISSUES.md` for known drift, deferred decisions, or refactor risks
  - `docs/agent/TESTING_STRATEGY.md` for test coverage expectations and validation shape; if absent, infer from existing tests and mention missing strategy only when it materially affects review confidence
  - scoped `CONTRACTS.md` files for touched cross-scope APIs, shared types, schemas, events, generated clients, or persistence boundaries
- Prioritize correctness, architecture drift, data consistency, side-effect boundaries, public contracts, and tests.
- Ignore style unless it affects maintainability or correctness.
- No generic comments.
- Every finding needs evidence and fix direction.
- Classify severity: critical / high / medium / low.

## Review Checklist

- Does diff match documented architecture and dependency directions?
- Does diff preserve project intent/non-goals, or intentionally update them?
- Are invariants preserved or intentionally updated?
- Are data model/schema changes documented and tested?
- Are data-flow, transformation, side-effect, or error-state changes documented and tested?
- Are side effects kept at existing boundaries?
- Are public contracts/backward compatibility respected?
- Are known risk areas or `DESIGN_ISSUES.md` items touched or worsened?
- Are tests sufficient for changed behavior and aligned with `TESTING_STRATEGY.md` when present?
- Are validation baseline commands still correct after build/test/tooling changes?
- If scoped docs exist, did diff update owner/consumer docs and `SCOPES.md` where ownership/contracts changed?
- Did implementation combine feature, bug fix, and refactoring accidentally?
- Are docs updated only for durable semantic changes?
- Are detailed facts placed in the owner artifact instead of duplicated across router/index docs?
- Are docs marked `planned` now backed by observed implementation, still valid as intent, or stale?

## Output

1. Summary verdict:
   - approve
   - approve with comments
   - request changes
2. Findings, each with:
   - Severity
   - Location
   - Problem
   - Evidence
   - Why it matters
   - Suggested fix
3. Missing tests
4. Documentation updates needed
5. Architecture drift risk
6. Final recommendation
