# Spec: [name] — [date] · author: [name] · status: draft/in-review/approved

**This spec decides:** 1) … 2) … 3) *(reviewers: argue with THESE)*
**Reversibility:** [which decisions are one-way doors — they get the scrutiny]
**Comment deadline:** [date] · Named reviewers & their angle: [who: what to check]

## Problem & constraints
[What we must achieve; the constraints that will pick winners below: scale, deadline, team, compliance]

## Decision 1: [name]
| Option | Genuine strengths | Why it loses/wins (→ constraint) |
|---|---|---|
**Chosen:** … 

*(repeat per decision)*

## Design overview
[The shape, once decisions are made — diagram > prose]

## Blast radius (fishing for "wait, this breaks…")
- Data/migrations (order matters?): …
- API consumers / other teams: …
- On-call & cost at 10×: …

## Failure modes & detection
| When [X fails] | Behaviour | How we detect |
|---|---|---|

## Rollout & rollback
[stages, flags, the half-deployed state handled]

## Open questions → resolutions (updated through review)
| # | Question | Resolution | Date |
|---|---|---|---|
