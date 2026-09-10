# Clean Code vs Patterns of Enterprise Application Architecture

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 16%
Overlap: 38%
Complementarity: 72%

## Loading Decision

Use together when enterprise boundaries such as persistence, transactions, presentation, workflow, session state, or remoting intersect with the other rule set's local concern.

## Book A Pressure

- Clean Code should drive tasks where local readability, naming, function shape, side effects, tests, and scoped cleanup dominate.
- Evidence: `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.

## Book B Pressure

- Patterns of Enterprise Application Architecture should drive tasks where enterprise pattern forces across workflow, persistence, transactions, integration, session state, or remoting dominate.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.

## Complementary Forces

- Claim: Clean Code contributes local-readability, naming, function-shape, side-effect, test, and scoped-cleanup pressure; Patterns of Enterprise Application Architecture contributes enterprise-pattern pressure across presentation, workflow, domain logic, persistence, transactions, integration, state, and remoting. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.

## Conflicts

- Claim: The tension is pattern pressure: PoEAA pattern choices must be justified by enterprise forces rather than added where the other rule set only needs a small local design or construction change.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.

## Use Together When

- Use together when one change simultaneously involves local readability, names, function shape, side effects, and scoped cleanup and enterprise patterns for workflow, persistence, transactions, integration, session state, and remoting; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer PoEAA when enterprise pattern forces are visible; prefer the other book when no presentation/workflow/persistence/transaction/session/remote boundary is involved.

## Source Basis

- `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.
- `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
- `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.
- `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 7-9: corrects inventing architecture for every feature and letting frameworks, ORMs, schemas, or transports choose the design.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.

## Review Notes

- External context was not used as decisive evidence for Clean Code vs Patterns of Enterprise Application Architecture; the verdict is based on the cited local `mini` line ranges.
