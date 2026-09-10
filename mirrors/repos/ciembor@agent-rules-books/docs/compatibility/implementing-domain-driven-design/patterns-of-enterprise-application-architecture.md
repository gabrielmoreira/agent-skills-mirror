# Implementing Domain-Driven Design vs Patterns of Enterprise Application Architecture

Status: reviewed
Research basis: mini-plus-external

Verdict: ❌ Conflicting

Conflict: 66%
Overlap: 72%
Complementarity: 40%

## Loading Decision

Do not load these as equal active implementation guidance. IDDD is a committed DDD implementation stack; PoEAA is a broader enterprise pattern decision aid that can deliberately choose non-DDD approaches such as Transaction Script, Table Module, Active Record, gateways, or simpler service layers. Equal loading can make an agent introduce DDD tactical mechanisms while PoEAA says the simpler enterprise pattern is the better force fit.

## Book A Pressure

- IDDD drives explicit contexts, local language, Core Domain protection, aggregate consistency, identity references, repositories, domain events, event sourcing, application services, DTOs/projections, CQRS gates, and boundary tests.
- Evidence: `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-9 and 13-31.

## Book B Pressure

- PoEAA drives enterprise responsibility and pattern choices across business logic, Service Layer, persistence, transactions, concurrency, remoting, session state, and tests.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-9 and 13-30.

## Complementary Forces

- Claim: PoEAA can help with specific enterprise infrastructure concerns under an IDDD design, especially Unit of Work, Identity Map, Data Mapper, DTOs, Remote Facade, locks, and session state.
- Evidence:
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 23, 26, 28-31: repositories, application services, DTOs/projections, CQRS, model-walk code generation, and tests.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 18-23 and 26-28: DTOs, persistence patterns, Identity Map, Unit of Work, Lazy Load, transactions, locks, session state, and distribution gates.

## Overlap

- Claim: The overlap is very high in implementation choices: repositories, services, DTOs, transactions, persistence boundaries, domain models, events/integration, tests, and package/layer responsibility.
- Evidence:
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 18-31 and 48-57: aggregates, repositories, events, application services, modules, DTOs, CQRS, tests, and external representations outside the domain.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30 and 47-54: responsibilities, layering, business logic pattern, service layer, DTOs, persistence, transactions, remoting, generation order, and tests.

## Conflicts

- Claim: IDDD starts from DDD implementation choices, while PoEAA starts from force-based enterprise alternatives. Equal guidance can lead to generic repositories, active records, transaction scripts, or service layers fighting aggregate-root repositories, domain events, local language, and one-aggregate transaction defaults.
- Evidence:
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 18-24, 38-44, and 54-57: small invariant-driven Aggregates, repositories for Aggregate Roots, meaningful Domain Events, one Aggregate per transaction by default, generic CRUD repository blockers, simple CRUD stays simple, and external representations stay outside the domain.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 15-20 and 36-39: Transaction Script, Table Module, Domain Model, Service Layer, Repository, Data Mapper, Gateway, Active Record, Identity Map, Unit of Work, and Lazy Load are force-based alternatives.

## Use Together When

- Use together only with IDDD as primary and PoEAA limited to one infrastructure pattern decision whose force fits the DDD boundaries.

## Prefer One When

- Prefer IDDD for committed DDD implementation work.
- Prefer PoEAA when the system has enterprise application pattern forces but no committed DDD model/invariant/context pressure.

## Source Basis

- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-9: IDDD scope and bias.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: IDDD implementation rules.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-9: PoEAA scope and bias.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: PoEAA pattern choices.
- External context: InformIT positions IDDD as practical DDD implementation guidance: https://www.informit.com/store/implementing-domain-driven-design-9780133039887
- External context: Fowler's PoEAA catalog lists broader enterprise application pattern alternatives: https://martinfowler.com/eaaCatalog/

## Review Notes

- This is the strongest implementation conflict: IDDD is not merely "PoEAA plus DDD names"; it commits the agent to a DDD implementation model that PoEAA may deliberately avoid.
