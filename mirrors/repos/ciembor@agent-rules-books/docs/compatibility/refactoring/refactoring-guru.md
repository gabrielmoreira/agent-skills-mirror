# Refactoring vs Refactoring.Guru

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 8%
Overlap: 90%
Complementarity: 30%

## Loading Decision

Choose one refactoring rule set. `refactoring` is the stronger process rule set for behavior-preserving, small-step changes; `refactoring-guru` is a smell-and-technique checklist. Loading both mostly repeats behavior preservation, smell diagnosis, smallest treatment, verification, and stop-condition guidance.

## Book A Pressure

- Refactoring controls safe structural change: preserve behavior, separate behavior change from structure, work in small testable steps, and stop before speculative cleanup.
- Evidence: `refactoring/refactoring.mini.md` lines 3-9 and 13-26.

## Book B Pressure

- Refactoring.Guru controls smell diagnosis and treatment choice with the same behavior-preserving and stop-condition discipline.
- Evidence: `refactoring-guru/refactoring-guru.mini.md` lines 3-9 and 13-37.

## Complementary Forces

- Claim: Refactoring.Guru can provide a broader smell taxonomy when the Fowler refactoring process has already identified that a specific smell needs treatment.
- Evidence:
  - `refactoring/refactoring.mini.md` lines 17-18: names common smells and prefers the simplest named move.
  - `refactoring-guru/refactoring-guru.mini.md` lines 21-37: expands smell categories and treatment cautions.

## Overlap

- Claim: The overlap is dominant because both rule sets solve the same agent problem: how to change existing code structurally without changing behavior.
- Evidence:
  - `refactoring/refactoring.mini.md` lines 13-26: behavior preservation, small steps, safety nets, smell scope, named moves, ownership, explicit contracts, evidence-based abstraction, and stop conditions.
  - `refactoring-guru/refactoring-guru.mini.md` lines 13-18: separate refactoring from feature work, diagnose smell, use smallest treatment, keep code runnable, run checks, and stop when the smell is reduced.

## Conflicts

- Claim: There is little contradiction. The risk is duplicate context and technique-catalog pressure, not opposing advice.
- Evidence:
  - `refactoring/refactoring.mini.md` lines 23-26: abstraction and cleanup stop when evidence and current smell justify it.
  - `refactoring-guru/refactoring-guru.mini.md` lines 30-36 and 53-64: avoid speculative abstractions and stop at the diagnosed smell.

## Use Together When

- Use together only if the agent needs the Fowler process plus an explicit smell catalog for a review-heavy cleanup task.

## Prefer One When

- Prefer `refactoring` for most code-change tasks because it is more procedural and safety-focused.
- Prefer `refactoring-guru` when the task is specifically smell identification or technique selection.

## Source Basis

- `refactoring/refactoring.mini.md` lines 3-9: refactoring scope and behavior-preserving bias.
- `refactoring/refactoring.mini.md` lines 13-26: process rules and stop condition.
- `refactoring-guru/refactoring-guru.mini.md` lines 3-9: same refactoring scope and smell-driven bias.
- `refactoring-guru/refactoring-guru.mini.md` lines 13-37: smell diagnosis and treatment selection.
- External context: Martin Fowler describes refactoring as a disciplined technique for restructuring existing code: https://martinfowler.com/books/refactoring.html
- External context: Refactoring.Guru presents a refactoring/smell catalog rather than a separate process philosophy: https://refactoring.guru/refactoring

## Review Notes

- Keep this as overlap. These are compatible ideas, but not efficient to load together unless the task explicitly needs catalog support.
