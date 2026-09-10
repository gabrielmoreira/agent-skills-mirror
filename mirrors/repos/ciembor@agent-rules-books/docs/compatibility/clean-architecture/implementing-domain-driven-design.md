# Clean Architecture vs Implementing Domain-Driven Design

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 46%
Overlap: 66%
Complementarity: 58%

## Loading Decision

Choose one primary architecture implementation rule set. Clean Architecture is the better primary guide when dependency direction and replaceable details are the risk. IDDD is the better primary guide when the system is intentionally DDD and implementation choices around contexts, aggregates, repositories, events, application services, DTOs, projections, and integration dominate. Loading both as equal active rules can over-layer the same code.

## Book A Pressure

- Clean Architecture drives inward dependencies, policy-owned ports, humble adapters, use-case boundaries, enforceable boundaries, and tests without real details.
- Evidence: `clean-architecture/clean-architecture.mini.md` lines 13-26.

## Book B Pressure

- IDDD drives explicit Bounded Contexts, local language, Core Domain protection, Aggregate rules, Repositories, Domain Events, Event Sourcing, Application Services, modules, DTOs, CQRS, and boundary tests.
- Evidence: `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31.

## Complementary Forces

- Claim: They can complement in a deliberately DDD application where Clean Architecture keeps infrastructure out and IDDD defines the domain implementation stack.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 14-19: core policy must not import details; outer adapters translate and wire dependencies.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 17, 23, 26, and 31: foreign/infrastructure models stay outside the domain, repositories are aggregate-root access points, application services coordinate use cases, and boundaries are tested.

## Overlap

- Claim: The overlap is high because both govern application architecture, domain boundaries, persistence isolation, application services/use cases, DTOs/adapters, and tests.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 15-25 and 42-49: entities/use cases, request/response models, ports/adapters, business-revealing structure, enforced boundaries, and core tests.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 26-31 and 48-57: application services, modules, DTO/projection/query separation, CQRS gates, code-generation order, domain/boundary tests, repositories, and external representations outside the domain.

## Conflicts

- Claim: Equal loading can cause ceremony stacking: ports, use cases, adapters, repositories, events, DTOs, projections, CQRS, and application services may all appear even when only one boundary style is justified.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 21-24: boundaries must be chosen by cost and enforced with code/tests/build rules.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 23-31 and 44: the DDD implementation stack is appropriate when the subdomain is not simple CRUD and invariant/lifecycle complexity is real.

## Use Together When

- Use together only when the project is intentionally DDD and also has a concrete need for Clean Architecture dependency direction or replaceable infrastructure.

## Prefer One When

- Prefer Clean Architecture for policy independence, framework leakage, ports/adapters, and use-case boundaries.
- Prefer IDDD for DDD implementation decisions: contexts, aggregates, repositories, events, application services, projections, CQRS, and translation.

## Source Basis

- `clean-architecture/clean-architecture.mini.md` lines 13-26: Clean Architecture implementation pressure.
- `clean-architecture/clean-architecture.mini.md` lines 42-49: final architecture checks.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: IDDD implementation pressure.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: final DDD implementation checks.
- External context: Clean Architecture vs DDD comparisons commonly distinguish architecture boundaries from domain modeling: https://khalilstemmler.com/articles/software-design-architecture/domain-driven-design-vs-clean-architecture/
- External context: InformIT positions IDDD as practical DDD implementation guidance: https://www.informit.com/store/implementing-domain-driven-design-9780133039887

## Review Notes

- This changed from complementary to overlap because the two rule sets compete for the same implementation architecture layer unless a human explicitly assigns roles.
