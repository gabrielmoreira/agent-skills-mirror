# Clean Code vs Domain-Driven Design

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

- Domain-Driven Design should drive tasks where model language, lifecycle rules, invariants, or Bounded Contexts dominate.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.

## Complementary Forces

- Claim: Clean Code contributes local-readability, naming, function-shape, side-effect, test, and scoped-cleanup pressure; Domain-Driven Design contributes model-language, Bounded-Context, invariant, and domain-test pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
  - `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.

## Conflicts

- Claim: The tension is DDD ceremony: tactical patterns must protect model meaning and should not displace the other rule set's simpler construction, refactoring, data, or operational constraints.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.

## Use Together When

- Use together when one change simultaneously involves local readability, names, function shape, side effects, and scoped cleanup and model language, invariants, lifecycle rules, and Bounded Contexts; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer the DDD rule set when language, lifecycle, invariants, or context boundaries drive design; prefer the other book for tasks without visible domain-model pressure.

## Source Basis

- `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.
- `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
- `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.
- `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
- `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.
- `domain-driven-design/domain-driven-design.mini.md` lines 7-9: corrects persistence/UI/framework/format/vocabulary replacing an implementation-driving model.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.
- `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.

## Review Notes

- External context was not used as decisive evidence for Clean Code vs Domain-Driven Design; the verdict is based on the cited local `mini` line ranges.
