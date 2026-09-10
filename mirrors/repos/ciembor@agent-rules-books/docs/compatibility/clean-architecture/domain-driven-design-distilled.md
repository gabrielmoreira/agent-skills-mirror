# Clean Architecture vs Domain-Driven Design Distilled

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 22%
Overlap: 55%
Complementarity: 68%

## Loading Decision

Use together for business application design where one book defines policy/model boundaries and the other chooses implementation or pattern boundaries.

## Book A Pressure

- Clean Architecture should drive tasks where business policy must stay independent from frameworks, databases, delivery, vendors, and volatile mechanisms.
- Evidence: `clean-architecture/clean-architecture.mini.md` lines 3-5: applies when business rules should survive changes in frameworks, databases, delivery mechanisms, services, vendors, or schedule pressure.

## Book B Pressure

- Domain-Driven Design Distilled should drive tasks where selective DDD, subdomain importance, Bounded Contexts, local language, and justified tactical patterns dominate.
- Evidence: `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-5: applies when business software has domain complexity, language ambiguity, strategic differentiation, or integration risk but needs smallest effective DDD rather than ceremony.

## Complementary Forces

- Claim: Clean Architecture contributes policy-independence and replaceable-detail pressure; Domain-Driven Design Distilled contributes selective-DDD, subdomain, Bounded-Context, local-language, and justified-pattern pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 13-24: requires inward dependencies, domain/use-case policy placement, plain request/response boundaries, outer-layer details, policy-owned ports, humble adapters, use-case structure, boundary cost checks, and enforceable boundaries.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.

## Overlap

- Claim: They overlap where both affect business policy placement, domain behavior, boundaries, tests, and framework/persistence isolation; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 42-49: checks policy independence, inward dependencies, invariant-guarding entities/use cases, enforced boundaries, humble adapters, business-revealing structure, fast core tests, and replaceable details.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.

## Conflicts

- Claim: The tension is ceremony: layering, contexts, repositories, services, adapters, and patterns must be triggered by real policy, language, lifecycle, persistence, or integration pressure.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 7-9: corrects detail-driven architecture by keeping business policy independent and dependencies pointing inward.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.

## Use Together When

- Use together when business policy must be independent from frameworks and the model language, invariants, aggregates, or Bounded Contexts also shape the code.

## Prefer One When

- Prefer Clean Architecture when policy independence and replaceable details are the risk; prefer the other book when the task is narrower than architecture boundaries.

## Source Basis

- `clean-architecture/clean-architecture.mini.md` lines 3-5: applies when business rules should survive changes in frameworks, databases, delivery mechanisms, services, vendors, or schedule pressure.
- `clean-architecture/clean-architecture.mini.md` lines 7-9: corrects detail-driven architecture by keeping business policy independent and dependencies pointing inward.
- `clean-architecture/clean-architecture.mini.md` lines 13-24: requires inward dependencies, domain/use-case policy placement, plain request/response boundaries, outer-layer details, policy-owned ports, humble adapters, use-case structure, boundary cost checks, and enforceable boundaries.
- `clean-architecture/clean-architecture.mini.md` lines 42-49: checks policy independence, inward dependencies, invariant-guarding entities/use cases, enforced boundaries, humble adapters, business-revealing structure, fast core tests, and replaceable details.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-5: applies when business software has domain complexity, language ambiguity, strategic differentiation, or integration risk but needs smallest effective DDD rather than ceremony.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 7-9: corrects starting from tactical patterns, frameworks, persistence, APIs, or class shapes before business capability, subdomain, context, and language.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.

## Review Notes

- External context was not used as decisive evidence for Clean Architecture vs Domain-Driven Design Distilled; the verdict is based on the cited local `mini` line ranges.
