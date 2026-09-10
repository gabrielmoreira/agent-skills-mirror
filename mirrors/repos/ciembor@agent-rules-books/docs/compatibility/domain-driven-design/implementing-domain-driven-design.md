# Domain-Driven Design vs Implementing Domain-Driven Design

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 22%
Overlap: 80%
Complementarity: 48%

## Loading Decision

Choose one DDD rule set as primary. `domain-driven-design` is the conceptual and strategic model source; `implementing-domain-driven-design` is the implementation-heavy version for bounded contexts, aggregates, repositories, events, application services, package structure, and integration. Loading both as equal rules spends context on the same DDD decisions and can double the pressure to introduce tactical DDD mechanisms.

## Book A Pressure

- Domain-Driven Design protects model meaning, Ubiquitous Language, Bounded Contexts, tactical patterns, aggregates, and Core Domain focus.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-9 and 13-27.

## Book B Pressure

- Implementing Domain-Driven Design operationalizes the same DDD concepts into implementation choices around contexts, repositories, events, services, DTOs, projections, CQRS, and tests.
- Evidence: `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-9 and 13-31.

## Complementary Forces

- Claim: IDDD is useful when the DDD decision has already been made and the agent needs implementation-level guardrails for Aggregates, Repositories, Domain Events, Application Services, and boundary translations.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 21-27: defines strategic context relationships, Core Domain, larger structures, prior art, and domain-language tests.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 18-31: gives implementation-level aggregate, repository, event, event sourcing, application service, module, DTO, projection, CQRS, code-generation, and test rules.

## Overlap

- Claim: The two rule sets mostly trigger on the same DDD situations and share the same vocabulary: Bounded Context, Ubiquitous Language, Core Domain, Aggregates, Entities, Value Objects, Repositories, Domain Services, Domain Events, translation, and tests.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-18: core DDD model and tactical pattern pressure.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-24: context-first interpretation, local language, Core Domain, translation, Aggregates, Entities, Value Objects, Domain Services, Repositories, and Domain Events.

## Conflicts

- Claim: The practical conflict is over-implementation. IDDD's more detailed tactical stack can turn Evans' modeling intent into ceremony when the original DDD pressure would have stopped at model discovery or context clarification.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-14: model use is justified by domain knowledge, communication, and implementation expression.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 23-31: detailed implementation mechanisms are appropriate only when the DDD implementation choice is actually active.

## Use Together When

- Use together only when a human explicitly wants Evans as the strategic source and IDDD as the implementation playbook for an intentionally DDD system.

## Prefer One When

- Prefer `domain-driven-design` when model discovery, Ubiquitous Language, context mapping, and deeper insight are the work.
- Prefer `implementing-domain-driven-design` when the design is already DDD and the task is implementing aggregates, repositories, events, application services, package boundaries, projections, or context translations.

## Source Basis

- `domain-driven-design/domain-driven-design.mini.md` lines 3-9: model-language and Bounded Context bias.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: strategic and tactical DDD guidance.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-9: implementation-specific DDD scope.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: implementation mechanisms for the same DDD concepts.
- External context: InformIT positions `Implementing Domain-Driven Design` as putting DDD into practice and implementing domain-driven enterprise applications: https://www.informit.com/store/implementing-domain-driven-design-9780133039887
- External context: Pearson's Evans DDD contents show the original conceptual and strategic source scope: https://www.pearson.com/en-gb/subject-catalog/p/domain-driven-design-tackling-complexity-in-the-heart-of-software/P200000009375/9780321125217

## Review Notes

- This pair is marked overlap because IDDD is best treated as the implementation-focused substitute or extension once DDD is chosen, not as a second equal rule set for every DDD task.
