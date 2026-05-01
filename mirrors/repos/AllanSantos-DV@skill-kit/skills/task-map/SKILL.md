---
name: task-map
description: "**WORKFLOW SKILL** — Persist analysis so it survives context compression and chains between tasks. USE FOR: any task whose decisions affect future work — features, refactors, architecture changes, integrations. Produces a lightweight Task Analysis Map that externalizes intent, decisions, and chain context. Use to document decisions, create continuity, prevent context loss, bridge tasks, externalize reasoning. DO NOT USE FOR: quick intent validation (use task-intent), deep structured analysis (use contextação)."
argument-hint: Describe the task to map and where to store the map file
license: MIT
---

# Task Map — Externalize and Chain

## The Problem You Solve

Everything an agent analyzes lives in the context window. When the window compresses (long conversations, session boundaries, model switching), relevant information is silently lost. Each task starts from zero. Previous decisions, assumptions, and reasoning evaporate.

You exist to make analysis survive.

## When to Produce a Map

Not every task needs a map. Produce one when:
- The task involves **decisions that constrain future work** (technology choice, architecture, data model)
- The task is **part of a series** where the next task builds on this one
- The task required **significant reasoning** that would be expensive to reconstruct
- The outcome **changes how the codebase works** in ways a new contributor wouldn't guess

Do NOT produce a map for: renames, typo fixes, simple dependency updates, formatting changes.

## The Task Analysis Map

Produce this as a markdown file in the project (location agreed with user, default: `docs/maps/`):

> If **task-intent** was already applied, reuse its Success Condition output in the Intent section — do not re-derive it.

```markdown
## Task: [brief description]
Related: [link to previous map if this continues earlier work]

### Intent
- WHY: [what caused this request — the root problem]
- WHAT FOR: [broader purpose it serves]
- FOR WHOM: [who receives the solution]

### Key Decisions
| Decision | Why this over alternatives | Verified? |
|----------|--------------------------|:---------:|
| ...      | ...                      | ✅/⚠️    |

> Mark each decision: ✅ = based on verified facts (docs read, code checked, spec confirmed). ⚠️ = based on assumption or memory — flag for future verification.

### Done When
- [ ] [concrete, verifiable criterion derived from intent]
- [ ] [...]

### For Next
[What the NEXT task in this area needs to know.
 Constraints introduced. Assumptions made.
 What should be re-validated if context changes.]
```

### Scaling

| Task impact | What to write |
|-------------|--------------|
| Moderate (feature, refactor) | Intent + Key Decisions + Done When |
| High (architecture, migration, integration) | Full map including For Next |
| Series of related tasks | Full map — For Next is critical |

## The Chain Effect

Each map's **For Next** section becomes the starting context for the next related task. This creates a living thread:

```
Map #1 (auth module) → For Next: "Uses JWT with refresh. No rate limiting yet."
    ↓
Map #2 (rate limiting) → reads #1's chain → starts informed
    → For Next: "Sliding window. Shares Redis with sessions."
    ↓
Map #3 (session optimization) → reads #2's chain → knows Redis constraint
```

Without the chain, Map #3 might propose a Redis-heavy solution that conflicts with the constraint discovered in Map #2. With the chain, the agent starts informed.

## Rules

- **ALWAYS** link to previous maps when they exist (Related field)
- **ALWAYS** write the For Next section for high-impact tasks — this is the chain
- **ALWAYS** mark Key Decisions as ✅ or ⚠️ — the next agent needs to know which decisions rest on verified ground and which on assumptions
- **NEVER** produce a map that takes longer to write than the task itself
- **NEVER** leave Key Decisions without reasoning — "decided X" without "because Y" is useless
- **NEVER** record a decision as ✅ verified unless you actually checked the source — claiming verification without doing it poisons the chain for every future task
- The map is for the NEXT agent/session, not the current one — write for someone with zero context

### Common Pitfalls

| | Pitfall | Consequence |
|---|---------|-------------|
| ❌ | Writing a map for a typo fix or rename | Overhead exceeds value. Maps are for decisions that constrain future work. |
| ❌ | "Decided to use PostgreSQL" (no reasoning) | Next agent doesn't know WHY → might reverse the decision or conflict with it. |
| ❌ | Marking a decision ✅ without actually checking the source | Poisons the chain. Every future task trusts a lie. |
| ❌ | Skipping "For Next" on a multi-task series | Chain breaks. Next task starts from zero, re-discovers constraints the hard way. |
| ❌ | Writing a 500-line map for a 10-line change | Map should be proportional to the task's impact, not a documentation exercise. |
| ✅ | "Chose JWT because: stateless, works with our API gateway, team familiar" | Next agent inherits the reasoning and can validate or extend. |
| ✅ | "For Next: Redis is shared with rate limiter. Don't add heavy caching without checking memory limits." | Prevents the next task from accidentally breaking the constraint. |
| ✅ | Linking to Map #1 when Map #2 continues the same work area | Creates a traceable decision chain across sessions. |

## When the User Asks for Help

- **"Where do I put the map file?"** → Default: `docs/maps/`. Ask if they prefer a different location. Use kebab-case filenames: `docs/maps/auth-module.md`.
- **"Do I need a map for this?"** → Apply the criteria: does the task involve decisions that constrain future work, is it part of a series, or did it require significant reasoning? If none apply, skip the map.
- **"What happened in the previous task?"** → Search `docs/maps/` for the most recent map related to the current area. Read its **For Next** section and summarize what the current task inherits.
- **"This map is too heavy for what I did"** → Scale down: for moderate tasks, Intent + Key Decisions + Done When is enough. Drop For Next if there's no follow-up task expected.
- **"Link this to the previous work"** → Find the related map, add it to the Related field, and incorporate its For Next into the current map's context.

## Companion Skills

- For **understanding intent before implementing**: use **task-intent**
- For **deep structured analysis** when complexity is high: use **contextação**
