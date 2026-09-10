# Patterns of Enterprise Application Architecture vs Refactoring

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- Patterns of Enterprise Application Architecture should drive tasks where enterprise pattern forces across workflow, persistence, transactions, integration, session state, or remoting dominate.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.

## Book B Pressure

- Refactoring should drive tasks where behavior-preserving structural change and current-smell scope control dominate.
- Evidence: `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.

## Complementary Forces

- Claim: Patterns of Enterprise Application Architecture contributes enterprise-pattern pressure across presentation, workflow, domain logic, persistence, transactions, integration, state, and remoting; Refactoring contributes behavior-preserving, small-step, test-backed refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 34-43: fires on domain behavior in presentation/SQL/glue, collapsed responsibilities, Transaction Script complexity, table-shaped rich domains, scattered persistence/transactions/external access, lazy-load/N+1/identity issues, concurrency/stale locks, chatty remote APIs, unclear session state, and pass-through/generic repository/ORM/controller workflow blockers.
  - `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.
  - `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 7-9: corrects inventing architecture for every feature and letting frameworks, ORMs, schemas, or transports choose the design.
  - `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.

## Use Together When

- Use together when existing code must be reshaped toward Patterns of Enterprise Application Architecture goals without changing observable behavior or turning cleanup into redesign.

## Prefer One When

- Prefer the refactoring rule set when observable behavior must stay unchanged; prefer the other book when designing new behavior rather than reshaping existing structure.

## Source Basis

- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 7-9: corrects inventing architecture for every feature and letting frameworks, ORMs, schemas, or transports choose the design.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 34-43: fires on domain behavior in presentation/SQL/glue, collapsed responsibilities, Transaction Script complexity, table-shaped rich domains, scattered persistence/transactions/external access, lazy-load/N+1/identity issues, concurrency/stale locks, chatty remote APIs, unclear session state, and pass-through/generic repository/ORM/controller workflow blockers.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.
- `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.
- `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.
- `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.
- `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Review Notes

- External context was not used as decisive evidence for Patterns of Enterprise Application Architecture vs Refactoring; the verdict is based on the cited local `mini` line ranges.
