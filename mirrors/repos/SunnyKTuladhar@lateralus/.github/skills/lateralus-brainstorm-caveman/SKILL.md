---
name: lateralus-brainstorm-caveman
description: "Caveman-compressed brainstorming skill. Same as lateralus-brainstorm — goal and horizon first, three modes (Grounded, Balanced, Wild) — but ~60% fewer tokens. Use when context window is nearly full or you want faster responses."
argument-hint: "What brainstorming, constraints, horizon (ship soon / exploring / blue-sky)"
user-invocable: true
license: MIT
---

Ideas not fixes. Widen before narrowing. Goal + horizon first, always.

## Activation

Explicit: `/lateralus-brainstorm-caveman`
Auto: plan mode ("let's plan", "brainstorm", "what are our options", "thinking through")

In plan mode: read context silently, then present menu.

## P1 — Read context silently

1. Check `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` at repo root — read fully if present.
2. If absent: detect stack from `go.mod` / `package.json` / etc., skim `README.md` (60 lines), run `git log -10 --oneline`.
3. Note: architecture patterns, tech constraints, recent directions.

No codebase → skip to P2.

## P2 — Goal + horizon

Surface context briefly if found. Then:

```
Brainstorming — pick a mode:

  [1] Grounded  — practical, shippable soon, within constraints
  [2] Balanced  — question one assumption, stay loosely feasible
  [3] Wild      — constraint-free, blue-sky

Pick a number or describe what you're exploring.
```

Horizon obvious from message → infer + confirm in one line, proceed.
Distressed / deadline → suggest [1] first.

Follow-up (batch if user is engaged, one at a time if cold):

**[1] Grounded:** What exists already? Hard constraints? What does a good idea look like?
**[2] Balanced:** What assumption is treated as fixed but maybe isn't? Prototype or platform?
**[3] Wild:** Unlimited resources — what would you build? Problem beneath the problem?

## P3 — Generate

Context block first, always:
```
Mode: Grounded | Balanced | Wild
Goal / Horizon / Constraints / Existing context / Success signal
```

**Grounded** — 5-8 ideas:
`Idea: <name> | What: <one line> | Why it fits: <constraint> | First step: <smallest test>`

**Balanced** — 5-7 ideas:
`Idea: <name> | What: <one line> | Assumption challenged: <what> | Open question: <what to answer>`

**Wild** — 5-6 ideas (non-literal — state this upfront):
`Idea: <name> | Reframe: <1-2 sentences> | Seed: <extractable real grain>`

## Rules

Never generate before goal + horizon established.
Wild = non-literal. Never present as plan.
One mode per pass. No blending.
End: ask which direction to develop, offer to switch modes.
