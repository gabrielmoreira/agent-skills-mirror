# Domain-Driven Design vs Refactoring

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- Domain-Driven Design should drive tasks where model language, lifecycle rules, invariants, or Bounded Contexts dominate.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.

## Book B Pressure

- Refactoring should drive tasks where behavior-preserving structural change and current-smell scope control dominate.
- Evidence: `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.

## Complementary Forces

- Claim: Domain-Driven Design contributes model-language, Bounded-Context, invariant, and domain-test pressure; Refactoring contributes behavior-preserving, small-step, test-backed refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.
  - `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.
  - `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 7-9: corrects persistence/UI/framework/format/vocabulary replacing an implementation-driving model.
  - `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.

## Use Together When

- Use together when existing code must be reshaped toward Domain-Driven Design goals without changing observable behavior or turning cleanup into redesign.

## Prefer One When

- Prefer the refactoring rule set when observable behavior must stay unchanged; prefer the other book when designing new behavior rather than reshaping existing structure.

## Source Basis

- `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.
- `domain-driven-design/domain-driven-design.mini.md` lines 7-9: corrects persistence/UI/framework/format/vocabulary replacing an implementation-driving model.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.
- `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.
- `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.
- `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.
- `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.
- `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Review Notes

- External context was not used as decisive evidence for Domain-Driven Design vs Refactoring; the verdict is based on the cited local `mini` line ranges.
