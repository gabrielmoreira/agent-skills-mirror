# Patterns of Enterprise Application Architecture vs The Pragmatic Programmer

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 16%
Overlap: 38%
Complementarity: 72%

## Loading Decision

Use together when enterprise boundaries such as persistence, transactions, presentation, workflow, session state, or remoting intersect with the other rule set's local concern.

## Book A Pressure

- Patterns of Enterprise Application Architecture should drive tasks where enterprise pattern forces across workflow, persistence, transactions, integration, session state, or remoting dominate.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.

## Book B Pressure

- The Pragmatic Programmer should drive tasks where ownership, DRY knowledge, orthogonality, reversibility, tracer feedback, automation, and contracts dominate.
- Evidence: `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-5: applies as a general engineering operating style for accountable delivery, adaptability, fast feedback, and easy-to-change code.

## Complementary Forces

- Claim: Patterns of Enterprise Application Architecture contributes enterprise-pattern pressure across presentation, workflow, domain logic, persistence, transactions, integration, state, and remoting; The Pragmatic Programmer contributes ownership, DRY-knowledge, orthogonality, reversibility, tracer-feedback, automation, and contract pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 56-65: checks authoritative knowledge, independent concerns and reversible choices, feedback, accepted prototype/tool behavior, contracts/failures/resources, visible state/coupling, automation, relevant tests, communicative artifacts, and touched-area improvement/containment.

## Conflicts

- Claim: The tension is pattern pressure: PoEAA pattern choices must be justified by enterprise forces rather than added where the other rule set only needs a small local design or construction change.
- Evidence:
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 7-9: corrects inventing architecture for every feature and letting frameworks, ORMs, schemas, or transports choose the design.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.

## Use Together When

- Use together when one change simultaneously involves enterprise patterns for workflow, persistence, transactions, integration, session state, and remoting and ownership, DRY knowledge, orthogonality, feedback, automation, contracts, and pragmatic stopping points; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer PoEAA when enterprise pattern forces are visible; prefer the other book when no presentation/workflow/persistence/transaction/session/remote boundary is involved.

## Source Basis

- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 7-9: corrects inventing architecture for every feature and letting frameworks, ORMs, schemas, or transports choose the design.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: requires explicit responsibility ownership, earned layering, force-based business logic patterns, Service Layer boundaries, Remote Facade/DTOs at remote boundaries, deliberate persistence patterns, visible identity/write/loading behavior, explicit ORM mapping forces, workflow-owned transactions/concurrency, focused presentation, translated external systems, deliberate session state, concrete-pressure base patterns, no default distribution, ordered code generation, and responsibility-level tests.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-5: applies as a general engineering operating style for accountable delivery, adaptability, fast feedback, and easy-to-change code.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 7-9: corrects local-edit and ritual optimization by owning outcomes, reducing duplicated knowledge, keeping concerns independent, proving assumptions early, automating repeated work, and making intent clear.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 56-65: checks authoritative knowledge, independent concerns and reversible choices, feedback, accepted prototype/tool behavior, contracts/failures/resources, visible state/coupling, automation, relevant tests, communicative artifacts, and touched-area improvement/containment.

## Review Notes

- External context was not used as decisive evidence for Patterns of Enterprise Application Architecture vs The Pragmatic Programmer; the verdict is based on the cited local `mini` line ranges.
