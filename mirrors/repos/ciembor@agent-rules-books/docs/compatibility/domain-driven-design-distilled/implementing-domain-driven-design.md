# Domain-Driven Design Distilled vs Implementing Domain-Driven Design

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 20%
Overlap: 78%
Complementarity: 52%

## Loading Decision

Choose `domain-driven-design-distilled` when the agent needs the smallest effective DDD practice. Choose `implementing-domain-driven-design` when the task is already committed to DDD implementation details. Loading both together usually duplicates strategic/tactical DDD guidance and lets the implementation-heavy version weaken Distilled's anti-ceremony gate.

## Book A Pressure

- DDD Distilled drives selective DDD: business capability, subdomain importance, Bounded Context, Ubiquitous Language, and tactical patterns only where they earn cost.
- Evidence: `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-9 and 13-30.

## Book B Pressure

- IDDD drives detailed DDD implementation across bounded contexts, aggregates, repositories, events, application services, package structure, and cross-context integration.
- Evidence: `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-9 and 13-31.

## Complementary Forces

- Claim: Distilled is a gate; IDDD is an implementation playbook. They complement only after DDD is selected and implementation detail matters.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-15: classify domain importance and avoid full tactical DDD unless complexity justifies it.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 18-31: supplies detailed aggregate, repository, event, application service, projection, CQRS, code-generation, and test guidance.

## Overlap

- Claim: Both cover the same DDD strategic and tactical areas: subdomains, contexts, language, integrations, Entities, Value Objects, Aggregates, Domain Events, Application Services, infrastructure boundaries, and tests.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 16-30: Bounded Contexts, translation, tactical patterns, events, application services, infrastructure isolation, modeling tools, and planning.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: context, local language, Core Domain, context interactions, Aggregates, tactical types, Repositories, Domain Events, Event Sourcing, Application Services, modules, DTOs, CQRS, and tests.

## Conflicts

- Claim: Distilled deliberately restricts DDD ceremony, while IDDD gives a broad tactical implementation stack. Equal loading can cause an agent to add repositories, events, CQRS, projections, or application-service ceremony before Distilled's trigger is satisfied.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-15 and 52-56: tactical patterns must earn cost and should not be used for simple CRUD, generic subsystems, or mainly technical problems.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 23-31 and 54-57: repository, event, event sourcing, application service, DTO/projection, and boundary checks are central once IDDD is active.

## Use Together When

- Use together only when the user explicitly wants Distilled's selectivity plus IDDD's implementation detail for a DDD codebase.

## Prefer One When

- Prefer `domain-driven-design-distilled` for default DDD guidance and early modeling.
- Prefer `implementing-domain-driven-design` for committed DDD implementation work.

## Source Basis

- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-9: selective DDD scope.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: strategic and tactical DDD gate.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-9: implementation-specific DDD scope.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: implementation-level DDD stack.
- External context: Pearson describes `Domain-Driven Design Distilled` as a concise introduction to DDD: https://www.pearson.com/en-us/subject-catalog/p/domain-driven-design-distilled/P200000009615/9780134434995
- External context: InformIT describes `Implementing Domain-Driven Design` as guidance for putting DDD into practice: https://www.informit.com/store/implementing-domain-driven-design-9780133039887

## Review Notes

- This is not a conflict when used sequentially. It becomes overlap when both are loaded as equal active rules for the same agent task.
