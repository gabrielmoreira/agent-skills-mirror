---
name: thinking-triz
description: Use when stuck between two architecture or API requirements that seem mutually exclusive — name the contradiction precisely, then separate the conflicting states in time, space, or condition.
---

# TRIZ Thinking

## Overview

TRIZ is a systematic method for resolving **architecture and API design contradictions** — situations where two requirements seem mutually exclusive. When you're about to accept a trade-off because "you can't have both," TRIZ says: name the contradiction precisely, then try to **separate** the conflicting states in time, space, or condition so you get both — no compromise.

The separation moves are the primary procedure. The 40 Inventive Principles are a reference library, not a required checklist. The skill is scoped to technical design contradictions (architecture, API, system parameters); it is NOT for non-technical problems, ordinary prioritization, or contradictions that dissolve under measurement.

**Core Principle:** Great design doesn't compromise — it separates. Find the dimension where the conflicting states can coexist.

## When to Use

- An architecture or API design decision is stuck between two requirements that seem mutually exclusive (fast vs accurate, stable vs evolving, large cache vs fast invalidation)
- You're about to accept a trade-off because "you can't have both"
- The same weakness shows up in every solution you've considered — the contradiction is structural

Decision flow:

```
Two requirements seem mutually exclusive?
  → Yes → NAME THE CONTRADICTION, TRY SEPARATION
  → No → About to accept a trade-off curve compromise?
      → Yes → APPLY TRIZ FIRST
      → No → This is a routine decision — just pick based on constraints
```

## When NOT to Use

- **Ordinary trade-offs with a correct answer.** If one option is simply better given your constraints (cheaper, simpler, well-understood), just pick it — don't manufacture a contradiction.
- **The "contradiction" dissolves under measurement.** If you can cheaply test which side actually matters, do that instead of inventing a separation.
- **Non-technical or people problems.** Separation principles target system parameters, not organizational dynamics or interpersonal conflicts.
- **The contradiction is already well-solved by standard patterns.** If there's an established pattern (cache-aside, CQRS, feature flags), apply the pattern directly.

## Trigger Card

When stuck between two architecture or API requirements that seem mutually exclusive:

1. **Name the contradiction precisely** — "We need [PARAMETER A] to be [STATE 1] for [BENEFIT 1] BUT also [STATE 2] for [BENEFIT 2]." If you can't write it in this form, it's not a TRIZ problem.
2. **Try separation** — can you satisfy state 1 at one TIME and state 2 at another? In different SPACES (components, layers)? Under different CONDITIONS (context, load, user)?
3. **Test the simplest separation first** — separate in time (feature flags, scheduled behavior) before space (separate services) before condition.

If one option is simply better given your constraints, just pick it. If you can cheaply test which side actually matters, test instead of designing a separation. For standard patterns (cache-aside, CQRS, feature flags), apply the pattern directly.

## Procedure

### Step 1: Name the Contradiction Precisely

Use this template:

```
"We need [PARAMETER A] to be [STATE 1] for [BENEFIT 1]
 BUT also [STATE 2] for [BENEFIT 2]"

Example:
"We need the API to be STABLE for client compatibility
 BUT also EVOLVING to support new features"
```

If you can't write the contradiction in this form, it's not a TRIZ problem — use another skill.

### Step 2: Envision the Ideal Final Result (IFR)

Before solving, describe the outcome where the problem solves itself:

```
"The API supports both old and new clients simultaneously,
without version negotiation overhead,
while maintaining a single codebase."
```

IFR questions: What if the problem solved itself? What if the harmful element became useful? What's the result with zero cost?

### Step 3: Try Separation Moves (Primary Procedure)

For each separation dimension, ask: "Can the conflicting states exist at different [times/places/conditions/scales]?"

#### Separation in Time

"Can we be in state 1 at one time and state 2 at another?"

```
Contradiction: "Cache must be FRESH AND cached"
Separation in Time: TTL-based invalidation — cached now, refreshed later
```

#### Separation in Space

"Can we be in state 1 in one place and state 2 in another?"

```
Contradiction: "Data must be LOCAL (fast) AND DISTRIBUTED (resilient)"
Separation in Space: Multi-region with local reads, distributed writes
```

#### Separation by Condition

"Can we be in state 1 under some conditions and state 2 under others?"

```
Contradiction: "Auth must be STRICT AND frictionless"
Separation by Condition: Strict for sensitive operations, frictionless for low-risk — risk-based authentication
```

#### Separation in Scale/Level

"Can state 1 and state 2 exist at different levels of the system?"

```
Contradiction: "API must be STABLE AND evolving"
Separation in Scale: Stable interface (API contract), evolving implementation — versioned APIs
```

### Step 4: If Separation Fails, Scan the Principles (Reference)

When no separation dimension resolves the contradiction, scan the software-adapted inventive principles for inspiration:

| Principle | Software Pattern |
|-----------|-----------------|
| Segmentation (#1) | Microservices, sharding, chunked processing |
| Preliminary Action (#10) | Pre-computation, caching, warm-up, materialized views |
| The Other Way Round (#13) | Push vs pull, invert control, event-driven instead of polling |
| Intermediary (#24) | Proxy, message queue, API gateway, adapter |
| Copying (#26) | Caching, replication, CDN, read replicas |
| Dynamization (#15) | Feature flags, runtime configuration, adaptive thresholds |
| Another Dimension (#17) | Add metadata layer, versioning, event sourcing |

The full 40 principles are reference material; scan only the most applicable ones.

### Step 5: Resource Analysis

Before adding new components, ask: what already exists that can be used?

```
Before: "We need a new service to track user sessions"
Resource check:
- What data already exists? → Auth tokens carry user identity
- What's already running? → Load balancer sees all requests
- What's unused? → Request headers have room for session ID
Solution: Encode session in existing auth flow — no new service
```

### Step 6: Synthesize and Decide

Combine the separation move with resource reuse into a concrete design decision. Document the contradiction, the separation dimension used, and the resolution.

## Output Contract

A completed TRIZ analysis produces:

1. **Contradiction Statement** — in the precise template form (Parameter A must be State 1 for Benefit 1 BUT State 2 for Benefit 2)
2. **Ideal Final Result** — what the self-solving outcome looks like
3. **Separation Attempts** — which dimensions were tried (time, space, condition, scale) and the result
4. **Principles Scanned** (if separation failed) — which inventive principles were considered
5. **Resources Used** — what existing capabilities were leveraged before adding new ones
6. **Resolution** — the concrete design decision that resolves the contradiction without compromise

## Anti-Patterns

| Anti-Pattern | Symptom | Correction |
|---|---|---|
| **Manufacturing contradictions** | Applying TRIZ to "which database should we use" when one is clearly better | Use it only for genuine "I need both opposite states" tension |
| **Compromising instead of separating** | Accepting a midpoint on the trade-off curve without trying separation | Try all four separation dimensions before compromising |
| **Skipping separation, jumping to principles** | Immediately scanning the 40 principles without trying time/space/condition/scale | Separation is the primary procedure; principles are the fallback |
| **Applying to non-technical problems** | Using TRIZ for org dynamics or interpersonal conflicts | Separation targets system parameters, not people |
| **Over-applying to testable contradictions** | Running full TRIZ when a quick measurement resolves which side matters | If you can test it cheaply, test it |
| **Ignoring existing resources** | Adding new components when existing ones could be reused | Resource analysis before new component proposals |
