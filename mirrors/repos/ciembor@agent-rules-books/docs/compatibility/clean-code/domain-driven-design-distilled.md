# Clean Code vs Domain-Driven Design Distilled

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 14%
Overlap: 38%
Complementarity: 74%

## Loading Decision

Use together when domain language, invariants, lifecycle, or Bounded Contexts affect the task and the other rule set governs implementation quality, reliability, data, or safe change.

## Book A Pressure

- Clean Code should drive tasks where local readability, naming, function shape, side effects, tests, and scoped cleanup dominate.
- Evidence: `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.

## Book B Pressure

- Domain-Driven Design Distilled should drive tasks where selective DDD, subdomain importance, Bounded Contexts, local language, and justified tactical patterns dominate.
- Evidence: `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-5: applies when business software has domain complexity, language ambiguity, strategic differentiation, or integration risk but needs smallest effective DDD rather than ceremony.

## Complementary Forces

- Claim: Clean Code contributes local-readability, naming, function-shape, side-effect, test, and scoped-cleanup pressure; Domain-Driven Design Distilled contributes selective-DDD, subdomain, Bounded-Context, local-language, and justified-pattern pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.

## Conflicts

- Claim: The tension is DDD ceremony: tactical patterns must protect model meaning and should not displace the other rule set's simpler construction, refactoring, data, or operational constraints.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.

## Use Together When

- Use together when one change simultaneously involves local readability, names, function shape, side effects, and scoped cleanup and selective DDD, subdomain importance, local language, and justified tactical patterns; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer the DDD rule set when language, lifecycle, invariants, or context boundaries drive design; prefer the other book for tasks without visible domain-model pressure.

## Source Basis

- `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.
- `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
- `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.
- `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-5: applies when business software has domain complexity, language ambiguity, strategic differentiation, or integration risk but needs smallest effective DDD rather than ceremony.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 7-9: corrects starting from tactical patterns, frameworks, persistence, APIs, or class shapes before business capability, subdomain, context, and language.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.

## Review Notes

- External context was not used as decisive evidence for Clean Code vs Domain-Driven Design Distilled; the verdict is based on the cited local `mini` line ranges.
