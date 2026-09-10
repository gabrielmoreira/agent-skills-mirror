# A Philosophy of Software Design vs Patterns of Enterprise Application Architecture

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 16%
Overlap: 38%
Complementarity: 72%

## Loading Decision

Use together when enterprise boundaries such as persistence, transactions, presentation, workflow, session state, or remoting intersect with the other rule set's local concern.

## Book A Pressure

- A Philosophy of Software Design should drive tasks that need module-depth, API-shape, information-hiding, and complexity-reduction judgment.
- Evidence: `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.

## Book B Pressure

- Patterns of Enterprise Application Architecture should drive tasks where enterprise pattern forces across workflow, persistence, transactions, integration, session state, or remoting dominate.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.

## Complementary Forces

- Claim: A Philosophy of Software Design contributes module-depth, API-shape, information-hiding, and complexity-reduction pressure; Patterns of Enterprise Application Architecture contributes enterprise-pattern pressure across presentation, workflow, domain logic, persistence, transactions, integration, state, and remoting. Together they are useful only where both scopes are active.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.

## Conflicts

- Claim: The tension is pattern pressure: PoEAA pattern choices must be justified by enterprise forces rather than added where the other rule set only needs a small local design or construction change.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.

## Use Together When

- Use together when one change simultaneously involves module/API depth, information hiding, and complexity reduction and enterprise patterns for workflow, persistence, transactions, integration, session state, and remoting; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer PoEAA when enterprise pattern forces are visible; prefer the other book when no presentation/workflow/persistence/transaction/session/remote boundary is involved.

## Source Basis

- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 7-9: corrects inventing architecture for every feature and letting frameworks, ORMs, schemas, or transports choose the design.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.

## Review Notes

- External context was not used as decisive evidence for A Philosophy of Software Design vs Patterns of Enterprise Application Architecture; the verdict is based on the cited local `mini` line ranges.
