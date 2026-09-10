# Code Complete vs Domain-Driven Design

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 14%
Overlap: 38%
Complementarity: 74%

## Loading Decision

Use together when domain language, invariants, lifecycle, or Bounded Contexts affect the task and the other rule set governs implementation quality, reliability, data, or safe change.

## Book A Pressure

- Code Complete should drive tasks where defect reduction, data clarity, defensive checks, evidence-based debugging, and reviewability dominate.
- Evidence: `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.

## Book B Pressure

- Domain-Driven Design should drive tasks where model language, lifecycle rules, invariants, or Bounded Contexts dominate.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.

## Complementary Forces

- Claim: Code Complete contributes defect-reduction, data-clarity, defensive-check, evidence-based-debugging, and reviewability pressure; Domain-Driven Design contributes model-language, Bounded-Context, invariant, and domain-test pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.
  - `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.

## Conflicts

- Claim: The tension is DDD ceremony: tactical patterns must protect model meaning and should not displace the other rule set's simpler construction, refactoring, data, or operational constraints.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.

## Use Together When

- Use together when one change simultaneously involves defect-risk construction, data clarity, defensive checks, reviewability, and model language, invariants, lifecycle rules, and Bounded Contexts; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer the DDD rule set when language, lifecycle, invariants, or context boundaries drive design; prefer the other book for tasks without visible domain-model pressure.

## Source Basis

- `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.
- `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.
- `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.
- `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.
- `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.
- `domain-driven-design/domain-driven-design.mini.md` lines 7-9: corrects persistence/UI/framework/format/vocabulary replacing an implementation-driving model.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.
- `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.

## Review Notes

- External context was not used as decisive evidence for Code Complete vs Domain-Driven Design; the verdict is based on the cited local `mini` line ranges.
