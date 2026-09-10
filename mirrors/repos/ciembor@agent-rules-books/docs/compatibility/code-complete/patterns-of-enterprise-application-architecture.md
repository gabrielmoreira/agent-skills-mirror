# Code Complete vs Patterns of Enterprise Application Architecture

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 16%
Overlap: 38%
Complementarity: 72%

## Loading Decision

Use together when enterprise boundaries such as persistence, transactions, presentation, workflow, session state, or remoting intersect with the other rule set's local concern.

## Book A Pressure

- Code Complete should drive tasks where defect reduction, data clarity, defensive checks, evidence-based debugging, and reviewability dominate.
- Evidence: `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.

## Book B Pressure

- Patterns of Enterprise Application Architecture should drive tasks where enterprise pattern forces across workflow, persistence, transactions, integration, session state, or remoting dominate.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.

## Complementary Forces

- Claim: Code Complete contributes defect-reduction, data-clarity, defensive-check, evidence-based-debugging, and reviewability pressure; Patterns of Enterprise Application Architecture contributes enterprise-pattern pressure across presentation, workflow, domain logic, persistence, transactions, integration, state, and remoting. Together they are useful only where both scopes are active.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.

## Conflicts

- Claim: The tension is pattern pressure: PoEAA pattern choices must be justified by enterprise forces rather than added where the other rule set only needs a small local design or construction change.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.

## Use Together When

- Use together when one change simultaneously involves defect-risk construction, data clarity, defensive checks, and reviewability and enterprise patterns for workflow, persistence, transactions, integration, session state, and remoting; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer PoEAA when enterprise pattern forces are visible; prefer the other book when no presentation/workflow/persistence/transaction/session/remote boundary is involved.

## Source Basis

- `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.
- `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.
- `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.
- `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 7-9: corrects inventing architecture for every feature and letting frameworks, ORMs, schemas, or transports choose the design.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.

## Review Notes

- External context was not used as decisive evidence for Code Complete vs Patterns of Enterprise Application Architecture; the verdict is based on the cited local `mini` line ranges.
