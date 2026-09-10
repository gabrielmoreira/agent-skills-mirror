# Clean Architecture vs Patterns of Enterprise Application Architecture

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 44%
Overlap: 64%
Complementarity: 52%

## Loading Decision

Choose one primary enterprise architecture guide. Clean Architecture should be primary when policy independence and dependency direction are the main risk. PoEAA should be primary when the task is choosing enterprise application patterns across presentation, workflow, domain logic, persistence, transactions, concurrency, integration, session state, or remoting. Loading both equally can make the agent add too many layers and pattern mechanisms.

## Book A Pressure

- Clean Architecture protects independent business rules through inward dependencies, policy-owned ports, use cases, adapters, enforceable boundaries, and core tests.
- Evidence: `clean-architecture/clean-architecture.mini.md` lines 3-9 and 13-26.

## Book B Pressure

- PoEAA chooses enterprise application patterns by force across layers, business logic pattern, service layer, persistence, transactions, concurrency, integration, state, and remoting.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-9 and 13-30.

## Complementary Forces

- Claim: PoEAA can fill in concrete persistence, transaction, remoting, and session-state pattern choices after Clean Architecture has established policy boundaries.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 17-19: details are outer-layer adapters and do not own business decisions.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 19-23 and 26-28: persistence, identity, Unit of Work, lazy loading, transactions, locks, session state, and remote distribution are force-based choices.

## Overlap

- Claim: Both govern enterprise responsibility separation, layering, business logic placement, service/application boundaries, persistence isolation, integration boundaries, and tests.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 15-25 and 42-49: entities/use cases, request/response boundaries, details behind adapters, enforceable boundaries, and tests.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-18, 24-30, and 47-54: layering, business logic patterns, Service Layer, presentation focus, integration boundaries, no default distribution, generation order, and responsibility tests.

## Conflicts

- Claim: PoEAA explicitly allows Transaction Script, Table Module, Active Record, and other pattern choices when their forces fit; Clean Architecture pushes stronger policy independence and inward dependencies. Equal loading can produce contradictory defaults for simple enterprise flows.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 13-18 and 21-24: preserve independent business rules, inward dependencies, policy-owned ports, and enforced boundaries.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 15-20: Transaction Script, Table Module, Domain Model, Service Layer, Repository/Data Mapper/Gateway/Active Record, Identity Map, Unit of Work, and Lazy Load are chosen by force.

## Use Together When

- Use together only when Clean Architecture is primary for dependency direction and PoEAA is used narrowly for a concrete persistence, transaction, remoting, or session-state decision.

## Prefer One When

- Prefer Clean Architecture when business policy must survive framework, database, delivery, vendor, or deployment changes.
- Prefer PoEAA when selecting an enterprise pattern family or reviewing responsibilities across application workflow, persistence, transactions, concurrency, remoting, and session state.

## Source Basis

- `clean-architecture/clean-architecture.mini.md` lines 3-9: Clean Architecture scope and bias.
- `clean-architecture/clean-architecture.mini.md` lines 13-26: Clean Architecture boundary rules.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-9: PoEAA enterprise pattern scope.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 13-30: PoEAA pattern selection rules.
- External context: Fowler's PoEAA catalog is organized around enterprise application patterns such as Domain Model, Transaction Script, Service Layer, Data Mapper, and Unit of Work: https://martinfowler.com/eaaCatalog/
- External context: Clean Architecture and DDD/architecture comparisons highlight the separate concern of dependency-direction boundaries: https://khalilstemmler.com/articles/software-design-architecture/domain-driven-design-vs-clean-architecture/

## Review Notes

- Marked overlap because both are enterprise architecture guides; use one as primary and the other only for a constrained subproblem.
