# Domain-Driven Design Distilled vs Working Effectively with Legacy Code

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

- Working Effectively with Legacy Code should drive tasks where unclear or weakly tested code requires characterization, seams, dependency breaking, and small safe changes.
- Evidence: `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.

## Complementary Forces

- Claim: Domain-Driven Design Distilled contributes selective-DDD, subdomain, Bounded-Context, local-language, and justified-pattern pressure; Working Effectively with Legacy Code contributes characterization, seam, dependency-breaking, small-change, and local-refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 13-27: requires treating untested areas as legacy, stating behavior delta and preserved behavior, following the legacy loop, focused tests, effect tracing, smallest useful seam, deliberate dependency breaking, separated behavior/refactor/cleanup, sprout/wrap/extract moves for risky edits, side-effect/policy separation, barrier-specific dependency breaking, responsibility sketching, legacy-risk review, rejecting hidden-dependency expansion or premature architecture, and leaving touched area more testable/changeable.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 7-9: corrects starting from tactical patterns, frameworks, persistence, APIs, or class shapes before business capability, subdomain, context, and language.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.

## Use Together When

- Use together when changing weakly tested code toward Domain-Driven Design Distilled goals: first characterize behavior and create the smallest seam, then apply the other rule set inside the controlled change area.

## Prefer One When

- Prefer Working Effectively with Legacy Code when tests are weak or behavior is unclear; prefer the other book only after control, characterization, or seams make the change safe.

## Source Basis

- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-5: applies when business software has domain complexity, language ambiguity, strategic differentiation, or integration risk but needs smallest effective DDD rather than ceremony.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 7-9: corrects starting from tactical patterns, frameworks, persistence, APIs, or class shapes before business capability, subdomain, context, and language.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 13-27: requires treating untested areas as legacy, stating behavior delta and preserved behavior, following the legacy loop, focused tests, effect tracing, smallest useful seam, deliberate dependency breaking, separated behavior/refactor/cleanup, sprout/wrap/extract moves for risky edits, side-effect/policy separation, barrier-specific dependency breaking, responsibility sketching, legacy-risk review, rejecting hidden-dependency expansion or premature architecture, and leaving touched area more testable/changeable.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Review Notes

- External context was not used as decisive evidence for Domain-Driven Design Distilled vs Working Effectively with Legacy Code; the verdict is based on the cited local `mini` line ranges.
