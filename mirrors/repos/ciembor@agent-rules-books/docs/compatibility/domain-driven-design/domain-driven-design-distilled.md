# Domain-Driven Design vs Domain-Driven Design Distilled

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 15%
Overlap: 88%
Complementarity: 34%

## Loading Decision

Choose one as the active DDD rule set for a task. `domain-driven-design-distilled` is the better default when the agent needs selective, low-ceremony DDD guidance; `domain-driven-design` is better when the task needs the fuller Evans vocabulary and strategic modeling pressure. Loading both mostly duplicates the same Bounded Context, Ubiquitous Language, Aggregate, domain-layer, and Core Domain decisions.

## Book A Pressure

- Domain-Driven Design drives model-first design when business complexity, model language, lifecycle rules, or cross-team/system boundaries dominate.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-9 and 13-27.

## Book B Pressure

- Domain-Driven Design Distilled drives the same DDD decisions with an explicit "smallest effective DDD" and anti-ceremony gate.
- Evidence: `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-9 and 13-30.

## Complementary Forces

- Claim: Distilled can act as a lighter gate around Evans' broader DDD vocabulary, especially by saying not to apply full tactical DDD to simple CRUD.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 21-27: defines Bounded Contexts, context relationships, Core Domain protection, model patterns, and domain-language tests.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-15: starts from business capability, subdomain class, Bounded Context, language, and only tactical patterns that earn their cost.

## Overlap

- Claim: The overlap is dominant: both rule sets steer the same agent decision layer around Ubiquitous Language, Bounded Contexts, tactical DDD patterns, Aggregates, infrastructure isolation, domain tests, and Core Domain focus.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-18: model, Ubiquitous Language, domain layer, Entities, Value Objects, Domain Services, Modules, Aggregates, Factories, Repositories, and model-first persistence.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 16-28: explicit Bounded Context, context translation, Ubiquitous Language, Entities, Value Objects, Aggregates, Domain Events, Application Services, infrastructure isolation, and richer concepts.

## Conflicts

- Claim: There is little direct contradiction, but equal loading can make the agent over-apply the fuller DDD set when Distilled is trying to keep DDD selective.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 16-18: gives tactical patterns as normal model-building blocks.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-15: tactical patterns must earn their cost, and full tactical DDD is rejected for simple CRUD, generic subsystems, or mainly technical problems.

## Use Together When

- Use together only as reference context when a human explicitly wants Evans' full vocabulary plus Vernon's selective gate.

## Prefer One When

- Prefer `domain-driven-design-distilled` for most agent tasks that need practical DDD without ceremony.
- Prefer `domain-driven-design` when the task is explicitly about Evans' original strategic modeling concepts, context maps, Core Domain distillation, or deeper model refactoring.

## Source Basis

- `domain-driven-design/domain-driven-design.mini.md` lines 3-9: DDD scope and corrective bias.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: DDD decision layer.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-9: selective DDD scope and anti-ceremony bias.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: same DDD strategic and tactical areas in condensed form.
- External context: Pearson describes `Domain-Driven Design Distilled` as a concise guide that helps readers understand and benefit from DDD: https://www.pearson.com/en-us/subject-catalog/p/domain-driven-design-distilled/P200000009615/9780134434995
- External context: Pearson's DDD table of contents shows Evans' original book covers Ubiquitous Language, Model-Driven Design, Entities, Value Objects, Services, Modules, Aggregates, Repositories, Factories, and Strategic Design: https://www.pearson.com/en-gb/subject-catalog/p/domain-driven-design-tackling-complexity-in-the-heart-of-software/P200000009375/9780321125217

## Review Notes

- This is a substitute decision, not a quality judgment. The books are compatible as reading material, but not worth loading together as equal active agent rules for most tasks.
