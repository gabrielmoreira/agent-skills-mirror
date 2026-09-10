# Domain-Driven Design vs Patterns of Enterprise Application Architecture

Status: reviewed
Research basis: mini-plus-external

Verdict: ❌ Conflicting

Conflict: 62%
Overlap: 68%
Complementarity: 44%

## Loading Decision

Do not load these as equal active guidance for one task. DDD should be primary when model language, invariants, lifecycle, Core Domain, or Bounded Contexts drive the design. PoEAA should be primary when the task is choosing enterprise application patterns by force, including simpler Transaction Script, Table Module, Active Record, Service Layer, Data Mapper, Unit of Work, DTO, and remoting choices. They can inform each other, but equal loading can make the agent oscillate between rich domain modeling and simpler enterprise pattern alternatives.

## Book A Pressure

- DDD drives an implementation-driving model, Ubiquitous Language, domain-layer behavior, tactical patterns, Aggregates, Repositories, Bounded Contexts, Core Domain, and domain-language tests.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-9 and 13-27.

## Book B Pressure

- PoEAA drives force-based enterprise patterns across presentation, workflow, domain logic, persistence, transactions, concurrency, integration, session state, and remoting.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-9 and 13-30.

## Complementary Forces

- Claim: PoEAA can supply concrete persistence, transaction, service-layer, DTO, and remoting decisions after DDD has already established that a rich domain model is justified.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 17-18 and 26: Aggregates, Factories, Repositories, model-first persistence, and domain-language tests.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 17-22 and 29-30: Service Layer, DTOs, persistence patterns, Unit of Work, Identity Map, Lazy Load, transaction ownership, generation order, and responsibility-level tests.

## Overlap

- Claim: The overlap is high because both decide business logic organization, domain model richness, service/application layer responsibilities, repositories, transactions, persistence mapping, integration boundaries, and tests.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 15-18, 21-23, and 43-48: domain layer, tactical patterns, Aggregates/Repositories, Bounded Contexts, Core Domain, explicit domain behavior, translation, and tests.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-20 and 47-54: responsibility ownership, layering, Transaction Script/Table Module/Domain Model, Service Layer, persistence patterns, identity/write/loading behavior, and final responsibility checks.

## Conflicts

- Claim: The conflict is active and practical. DDD pushes deeper domain modeling when language, invariants, lifecycle, and context boundaries matter; PoEAA explicitly permits simpler Transaction Script/Table Module/Active Record designs when those forces fit. Equal loading can cause an agent to both add DDD tactical patterns and preserve a simpler enterprise pattern.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-18 and 31-39: refine language, move business decisions into domain objects/services/specifications, isolate framework/persistence shaping, review Aggregate ownership, and distill Core Domain.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 15-20 and 36-39: choose Transaction Script, Table Module, or Domain Model by force; Active Record is acceptable for simple domains; revisit Domain Model only when duplication/lifecycle/invariant complexity grows.

## Use Together When

- Use together only with DDD as primary and PoEAA constrained to a specific infrastructure or enterprise pattern decision.

## Prefer One When

- Prefer DDD when business language, invariants, lifecycle, Bounded Contexts, Core Domain, or deeper model insight are the design force.
- Prefer PoEAA when selecting enterprise application patterns for workflow, persistence, transactions, concurrency, integration, remoting, or simple business logic flows without strong domain-model pressure.

## Source Basis

- `domain-driven-design/domain-driven-design.mini.md` lines 3-9: DDD scope and bias.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: DDD model and strategic rules.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-9: PoEAA scope and bias.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: PoEAA pattern-selection rules.
- External context: Fowler's PoEAA catalog includes alternative business logic and data source patterns such as Transaction Script, Domain Model, Table Module, Active Record, Data Mapper, Repository, Unit of Work, and Service Layer: https://martinfowler.com/eaaCatalog/
- External context: Pearson's Evans DDD contents show DDD's focus on Ubiquitous Language, Model-Driven Design, Entities, Value Objects, Services, Modules, Aggregates, Repositories, Factories, and Strategic Design: https://www.pearson.com/en-gb/subject-catalog/p/domain-driven-design-tackling-complexity-in-the-heart-of-software/P200000009375/9780321125217

## Review Notes

- This is marked conflicting because the loading decision is about equal active guidance. PoEAA can still be useful as background under DDD, but DDD must arbitrate domain-model decisions.
