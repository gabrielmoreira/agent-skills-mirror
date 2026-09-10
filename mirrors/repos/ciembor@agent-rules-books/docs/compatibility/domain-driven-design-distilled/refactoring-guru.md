# Domain-Driven Design Distilled vs Refactoring.Guru

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- Domain-Driven Design Distilled should drive tasks where selective DDD, subdomain importance, Bounded Contexts, local language, and justified tactical patterns dominate.
- Evidence: `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-5: applies when business software has domain complexity, language ambiguity, strategic differentiation, or integration risk but needs smallest effective DDD rather than ceremony.

## Book B Pressure

- Refactoring.Guru should drive tasks where smell diagnosis, smallest treatment choice, behavior verification, and stop conditions dominate.
- Evidence: `refactoring-guru/refactoring-guru.mini.md` lines 3-5: applies when code smells, technique choice, behavior preservation, and cleanup scope control matter.

## Complementary Forces

- Claim: Domain-Driven Design Distilled contributes selective-DDD, subdomain, Bounded-Context, local-language, and justified-pattern pressure; Refactoring.Guru contributes smell-diagnosis, smallest-treatment, behavior-verification, and stop-condition pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.
  - `refactoring-guru/refactoring-guru.mini.md` lines 13-37: requires separating behavior changes, diagnosing smell/cost/scope/end state/verification/stop condition, smallest treatment first, runnable small transformations, checks after risky moves, Rule of Three, debt paid by current cost, smell categories, bloaters/switch/change/coupler/dispensable treatments, comments vs code fixes, behavior with data, no getter/setter-only encapsulation, no speculative abstractions, public compatibility, extraction/movement/condition/data/generalization prechecks, and deliberate exceptions.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.
  - `refactoring-guru/refactoring-guru.mini.md` lines 57-64: checks work type, diagnosed smell/cost, smallest treatment, behavior preservation, smell reduction, no speculative pattern use, public/state/ownership checks, and documented untreated smells.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 7-9: corrects starting from tactical patterns, frameworks, persistence, APIs, or class shapes before business capability, subdomain, context, and language.
  - `refactoring-guru/refactoring-guru.mini.md` lines 7-9: corrects treating refactoring as general cleanup or pattern application instead of smell-driven treatment with verification and stop condition.

## Use Together When

- Use together when existing code must be reshaped toward Domain-Driven Design Distilled goals without changing observable behavior or turning cleanup into redesign.

## Prefer One When

- Prefer the refactoring rule set when observable behavior must stay unchanged; prefer the other book when designing new behavior rather than reshaping existing structure.

## Source Basis

- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-5: applies when business software has domain complexity, language ambiguity, strategic differentiation, or integration risk but needs smallest effective DDD rather than ceremony.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 7-9: corrects starting from tactical patterns, frameworks, persistence, APIs, or class shapes before business capability, subdomain, context, and language.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.
- `refactoring-guru/refactoring-guru.mini.md` lines 3-5: applies when code smells, technique choice, behavior preservation, and cleanup scope control matter.
- `refactoring-guru/refactoring-guru.mini.md` lines 7-9: corrects treating refactoring as general cleanup or pattern application instead of smell-driven treatment with verification and stop condition.
- `refactoring-guru/refactoring-guru.mini.md` lines 13-37: requires separating behavior changes, diagnosing smell/cost/scope/end state/verification/stop condition, smallest treatment first, runnable small transformations, checks after risky moves, Rule of Three, debt paid by current cost, smell categories, bloaters/switch/change/coupler/dispensable treatments, comments vs code fixes, behavior with data, no getter/setter-only encapsulation, no speculative abstractions, public compatibility, extraction/movement/condition/data/generalization prechecks, and deliberate exceptions.
- `refactoring-guru/refactoring-guru.mini.md` lines 57-64: checks work type, diagnosed smell/cost, smallest treatment, behavior preservation, smell reduction, no speculative pattern use, public/state/ownership checks, and documented untreated smells.

## Review Notes

- External context was not used as decisive evidence for Domain-Driven Design Distilled vs Refactoring.Guru; the verdict is based on the cited local `mini` line ranges.
