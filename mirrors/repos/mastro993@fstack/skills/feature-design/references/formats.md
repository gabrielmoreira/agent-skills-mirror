# File formats

Use these when the project has no format of its own. When it does (an existing glossary, ADR folder, or spec folder), follow its location, numbering, and template instead. Create files and folders only when there is something to write.

## Glossary: `GLOSSARY.md`

```md
# Glossary

**Swap**:
A request by one staff member to hand a shift to a named colleague.
_Avoid_: trade, exchange

**Cover request**:
A shift offered to anyone qualified, with no named colleague.
_Avoid_: open swap
```

- One or two sentences per term, saying what it is, not how it is implemented.
- Be opinionated: one word per concept, and the words not to use under `_Avoid_`.
- Only the project's own concepts. General programming terms stay out.
- Group terms under subheadings once clusters appear.

## ADR: `docs/adr/NNNN-slug.md`

Number after the highest existing one (`0001`, `0002`, …).

```md
# Swaps inside the weekly-hours limit approve themselves

Status: accepted (supersedes [0002](0002-swaps-need-manager-approval.md))

Managers approved every swap, and staff arranged them over text because approval took days. Swaps
that keep both people inside their weekly hours and role now approve at once, and the manager is
told afterwards; anything else still waits for the manager.

Considered: keeping approval for every swap with a 4-hour reminder (still too slow for same-day
swaps); no approval at all (breaks the weekly-hours rule that 0002 protects).
```

- A title that states the decision, then one to three sentences: the context, the decision, and why.
- **Status** only when it isn't simply accepted: `superseded by [NNNN](…)` on the old record, `supersedes [NNNN](…)` on the new one.
- **Considered** when the rejected options are worth remembering, above all the ones the user turned down.
- **Consequences** only when the effects aren't obvious.
- A decision qualifies when a real alternative existed and a future reader would wonder why. Easy-to-reverse details and the only sensible option stay in the spec.

## Spec: `docs/specs/<slug>.md`

```md
# {Feature name}

## Problem
Who has it, what happens today, and the evidence.

## Outcome
What success looks like for the user, and how we will know.

## Scope
In, and explicitly out.

## Behavior
The numbered decisions as rules, then each flow step by step: what the user does, what they see,
and every state (first use, empty, loading, error, limits). Edge cases with the agreed result.

## UX
Screens or surfaces touched, with the mockup, diagram, or prototype path that settled each choice.

## Design
How it is built, in plain words, with a diagram of the parts. Data that is added or changed,
interfaces, and how it rolls out. Each technical decision in one line, linked to its ADR.

## Assumptions
What was decided without asking, and what would change if it is wrong.

## Acceptance
Checks that prove the feature works, written so a test or a person can run them.

## Slices
In implementation order. Each: what it delivers end to end, its acceptance checks, and what it
depends on.

## Open questions
Ideally none. Anything here blocks the slice that needs it.
```

Use the glossary's terms throughout, and link ADRs instead of repeating their reasoning.

## Issue

```md
## What
The slice, in two or three sentences, in the glossary's terms.

## Acceptance
- [ ] …

## Context
Spec: docs/specs/<slug>.md#slices · ADRs: 0003, 0004
Blocked by: #12
```

Title each issue with the outcome ("Staff can propose a swap to a colleague"), not the layer.
