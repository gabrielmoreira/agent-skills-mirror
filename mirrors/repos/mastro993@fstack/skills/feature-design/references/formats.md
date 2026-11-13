# File formats

Use these when the project has no format of its own. When it does (an existing glossary, ADR folder, or spec folder), follow its location, numbering, and template instead. Create files and folders only when there is something to write.

The glossary and ADRs use [domain-driven-design's formats](../../domain-driven-design/references/formats.md).

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
