# CONTEXT.md — Project Glossary Format

`CONTEXT.md` is a glossary and nothing else: the project's chosen words, one definition each. No implementation details, no specs, no scratch notes.

## Shape

```md
# {Project or Context Name}

{One sentence: what this context covers.}

## Terms

**Deal**
One negotiated agreement with one sponsor, containing its deliverables.
Not: "campaign", "contract", "engagement"

**Milestone**
A payment checkpoint on a deal with an amount and a due date.
Not: "invoice", "installment"
```

## Rules

- One canonical term per concept; competing synonyms go on the `Not:` line so the ban is explicit.
- A definition is one or two sentences stating what the thing *is*. If you're describing behavior, it belongs in code or the plan, not here.
- Admit only domain terms. Anything a programmer would recognize from any other project (retry, handler, cache) stays out no matter how often it appears in this one.
- Flat list until clusters genuinely emerge; then subheadings.
- Create the file only when the first term is actually settled — never speculatively.

## Repos with more than one domain

Large repos sometimes hold several bounded vocabularies (e.g. `ordering` vs `billing`). Signal this with a root `CONTEXT-MAP.md` that lists each context, its folder, and how they talk to each other (events consumed, shared identifiers). Each context then keeps its own `CONTEXT.md` in its folder.

Resolution order when the skill runs: `CONTEXT-MAP.md` present → find the context matching the current work (ask if ambiguous); root `CONTEXT.md` only → single context; neither → create a root `CONTEXT.md` lazily.
