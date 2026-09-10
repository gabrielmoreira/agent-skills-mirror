# Domain-Driven Design Distilled vs Patterns of Enterprise Application Architecture

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 50%
Overlap: 66%
Complementarity: 48%

## Loading Decision

Choose one primary decision layer. DDD Distilled is the better active guide when the agent must decide whether DDD is justified at all and how little ceremony to use. PoEAA is the better guide when the task is choosing enterprise patterns across workflow, domain logic, persistence, transactions, integration, state, or remoting. They can be used sequentially, but equal loading makes the agent arbitrate between DDD modeling and broader enterprise pattern alternatives.

## Book A Pressure

- DDD Distilled drives selective DDD: subdomain importance, Bounded Context, local language, integration contracts, tactical patterns only where they earn their cost, and no full DDD for simple CRUD.
- Evidence: `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-9 and 13-30.

## Book B Pressure

- PoEAA drives enterprise pattern selection by force, including Transaction Script, Table Module, Domain Model, Service Layer, DTOs, persistence patterns, transactions, locks, session state, remoting, and tests.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-9 and 13-30.

## Complementary Forces

- Claim: Distilled can decide whether DDD is warranted; PoEAA can then supply lower-level enterprise persistence, transaction, remoting, or session-state patterns if needed.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-15: classify the subdomain and apply tactical DDD only where justified.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 19-23 and 26-28: persistence patterns, Unit of Work, Identity Map, Lazy Load, transaction/lock decisions, session state, and distribution gates.

## Overlap

- Claim: They overlap on domain model richness, service/application layer roles, persistence boundaries, integration contracts, translation, tactical patterns, tests, and anti-ceremony gates.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 21-28 and 48-56: local language, Entities, Value Objects, Aggregates, Domain Events, Application Services, infrastructure isolation, richer concepts, and final tactical checks.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 15-20 and 47-54: business logic pattern choice, Service Layer, DTOs, persistence patterns, identity/write/loading behavior, and final responsibility checks.

## Conflicts

- Claim: The tension is less severe than full DDD vs PoEAA because Distilled has a strong anti-ceremony gate, but equal loading still competes around whether to choose a DDD tactical model or an enterprise pattern alternative.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 15 and 24-27: do not apply full tactical DDD to simple CRUD; use Aggregates, Domain Events, Application Services, and infrastructure isolation when justified.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 15-20 and 36-39: simple flows can remain Transaction Script or Active Record, and Domain Model is revisited when complexity grows.

## Use Together When

- Use together only if DDD Distilled first gates whether DDD is justified, and PoEAA is then used for a specific enterprise pattern subdecision.

## Prefer One When

- Prefer DDD Distilled for selective DDD decisions and domain modeling.
- Prefer PoEAA for enterprise application pattern choice outside clear DDD pressure.

## Source Basis

- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-9: selective DDD scope.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: DDD gate and tactical rules.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-9: enterprise pattern scope.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: enterprise pattern decisions.
- External context: Pearson positions `Domain-Driven Design Distilled` as a concise guide to DDD: https://www.pearson.com/en-us/subject-catalog/p/domain-driven-design-distilled/P200000009615/9780134434995
- External context: Fowler's PoEAA catalog lists the enterprise pattern alternatives this mini uses: https://martinfowler.com/eaaCatalog/

## Review Notes

- Marked overlap rather than conflict because Distilled's anti-ceremony gate makes it easier to sequence with PoEAA. Still, equal active loading is not recommended.
