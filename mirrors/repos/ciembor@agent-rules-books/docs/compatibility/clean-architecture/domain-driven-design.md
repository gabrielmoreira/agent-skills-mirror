# Clean Architecture vs Domain-Driven Design

Status: reviewed
Research basis: mini-plus-external

Verdict: ✅ Complementary

Conflict: 36%
Overlap: 62%
Complementarity: 70%

## Loading Decision

Load together only for business software where both forces are visible: Clean Architecture governs dependency direction, policy independence, and replaceable details; DDD governs model language, Bounded Contexts, invariants, Aggregates, and Core Domain decisions. They are not substitutes, but they must be scoped carefully because both can introduce architecture vocabulary and boundaries.

## Book A Pressure

- Clean Architecture protects business policy from frameworks, databases, delivery mechanisms, services, vendors, and volatile details through inward dependencies and use-case boundaries.
- Evidence: `clean-architecture/clean-architecture.mini.md` lines 3-9 and 13-26.

## Book B Pressure

- DDD protects implementation-driving domain models, Ubiquitous Language, Bounded Contexts, tactical patterns, Core Domain focus, and domain-language tests.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-9 and 13-27.

## Complementary Forces

- Claim: Clean Architecture gives technical dependency direction; DDD gives domain model boundaries and language. Together they can keep policy independent while preserving model meaning.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 14-19: domain/use cases must not import details; outer-layer adapters translate external formats and do not own business decisions.
  - `domain-driven-design/domain-driven-design.mini.md` lines 14-18 and 21-23: one Ubiquitous Language per context, domain-layer logic, model-first persistence, explicit Bounded Contexts, context relationships, and Core Domain protection.

## Overlap

- Claim: They overlap substantially around business behavior placement, boundary design, isolation from infrastructure, tests, and business-revealing structure.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 15-25 and 42-49: entities/use cases, ports/adapters, boundary enforcement, tests without real details, and business-revealing structure.
  - `domain-driven-design/domain-driven-design.mini.md` lines 15, 18, 26, and 43-48: domain-layer logic, model-first persistence, domain tests, explicit domain behavior, language, tactical patterns, translation, and Core Domain protection.

## Conflicts

- Claim: The tension is boundary priority. Clean Architecture may push use-case/application boundaries and ports; DDD may push model/context/aggregate boundaries. Equal loading is risky when a task lacks real policy independence or domain-model pressure.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 16-24: use-case request/response boundaries, policy-owned ports, adapters, feature/use-case organization, and enforced boundaries.
  - `domain-driven-design/domain-driven-design.mini.md` lines 16-18 and 21-24: tactical DDD patterns, Aggregates, Repositories, Bounded Contexts, context relationships, Core Domain, and large-scale structure.

## Use Together When

- Use together when a domain-rich application also needs business rules insulated from framework, persistence, delivery, vendor, or deployment churn.

## Prefer One When

- Prefer Clean Architecture when the risk is dependency direction, framework leakage, replaceable details, or use-case boundary enforcement.
- Prefer DDD when the risk is domain language, invariants, lifecycle, context boundaries, or Core Domain modeling.

## Source Basis

- `clean-architecture/clean-architecture.mini.md` lines 3-9: Clean Architecture scope and bias.
- `clean-architecture/clean-architecture.mini.md` lines 13-26: dependency, policy, adapter, boundary, testing, and incremental extraction rules.
- `domain-driven-design/domain-driven-design.mini.md` lines 3-9: DDD scope and bias.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: model, language, tactical patterns, contexts, Core Domain, and tests.
- External context: Khalil Stemmler compares Clean Architecture and DDD as related but different concerns around architecture boundaries and domain modeling: https://khalilstemmler.com/articles/software-design-architecture/domain-driven-design-vs-clean-architecture/
- External context: Community discussions commonly distinguish DDD's domain model focus from Clean Architecture's dependency-direction and boundary focus: https://softwareengineering.stackexchange.com/questions/405973/difference-between-domain-driven-design-and-clean-architecture

## Review Notes

- This remains complementary, but the comparison should be read as "combine only when both triggers are real," not as permission to add both CA and DDD ceremony to every business feature.
