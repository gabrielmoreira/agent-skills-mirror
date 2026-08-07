---
name: lateralus-brainstorm
description: >
  Structured brainstorming skill for features, architecture, and ideas. Activates automatically
  during plan mode. Generates ideas in three tiers: Grounded (practical, shippable),
  Balanced (assumption-questioning, loosely feasible), Wild (speculative, constraint-free).
  Use when user invokes /lateralus-brainstorm, says "let's plan", "brainstorm", "what are our options",
  "how should we approach this", or agent enters plan mode. Use for new work, not debugging.
---

Generate ideas, not fixes. Widen the solution space before narrowing. Always establish goal and horizon first.

## Activation

This skill activates in two ways:
- Explicitly: user invokes `/lateralus-brainstorm`
- Automatically: agent enters **plan mode** (user says "let's plan", "plan this out", "thinking through", "brainstorm", "what are our options", "how should we approach this")

In plan mode: run Phase 1 silently, then proceed to Phase 2 before producing any plan.

---

## Phase 1 — Read context silently (always first)

**Do this before presenting any options:**

1. Check for `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` at repo root — read fully if present.
2. If absent: detect stack from `go.mod`, `package.json`, `requirements.txt`, `Cargo.toml`, etc. Skim `README.md` (first 60 lines). Run `git log -10 --oneline`.
3. Identify: existing architecture patterns, tech constraints, recent directions, open issues or TODOs.

No codebase accessible → skip to Phase 2 immediately.

Surface relevant context briefly before the mode menu (e.g. "I can see this is a React app with a REST backend — that shapes the ideas.").

---

## Phase 2 — Establish goal and horizon

Ask before generating anything:

```
What are we brainstorming, and what's the horizon?

  [1] Grounded  — practical ideas you could ship soon, within current constraints
  [2] Balanced  — ideas that question some assumptions but stay loosely feasible
  [3] Wild      — constraint-free, blue-sky, no wrong answers

Pick a number, or describe what you're exploring and I'll route you.
```

If the user's message already makes the horizon obvious, infer it and confirm in one line before generating.

Follow-up questions to ask (adapt to the chosen mode):

**Grounded:**
- What exists already that this builds on?
- What are the hard constraints? (timeline, stack, team size, backwards compat)
- What does success look like — how will you know an idea is good?

**Balanced:**
- What assumptions are you treating as fixed that might not be?
- Is there a version of this that solves the same goal differently?
- How long does this need to last — prototype, product, or platform?

**Wild:**
- If resources and time were unlimited, what would you build?
- What would you do if the current stack didn't exist?
- What problem is underneath the problem?

Cold user → one question at a time. Engaged user → batch the mode's questions.

---

## Phase 3 — Generate ideas by mode

Always label the tier. Always output the context block before ideas.

### Context block (always first)

```
Mode: Grounded | Balanced | Wild
Goal: <one line>
Horizon: shipping soon | exploring | blue-sky | unknown
Constraints: <list or "none stated">
Existing context: <key facts from Phase 1, or "none">
Success signal: <what a good idea looks like>
```

---

### Grounded ideas

5-8 concrete, actionable ideas that fit within stated constraints.

Format:
```
Idea: <name>
What: <one line description>
Why it fits: <constraint alignment>
First step: <smallest thing to try or validate>
```

Optimise for: shippability, familiarity, low risk. No moonshots.

---

### Balanced ideas

5-7 ideas that challenge one assumption each while remaining loosely buildable.

Format:
```
Idea: <name>
What: <one line description>
Assumption challenged: <what this questions>
Loose feasibility: <why it's not crazy>
Open question: <what needs answering before committing>
```

Optimise for: assumption surfacing, creative-but-credible. Not pure speculation.

---

### Wild ideas

5-6 speculative, constraint-free ideas. State clearly these are not literal plans.

Format:
```
Idea: <name>
Reframe: <one or two sentences — make it vivid>
Seed: <what grain of this could be extracted into something real>
```

Optimise for: jolting new associations, not implementation readiness. Short. Punchy. No over-justification.

---

## After generating

Always end with:
1. Ask which idea or direction to develop further.
2. Offer to switch modes: "Want Grounded takes on any of the Wild ideas? Or go deeper on one?"
3. If the user picks something → hand off to planning / implementation, do not generate another batch unprompted.

---

## Rules

- **Never generate ideas before establishing goal and horizon.**
- Wild ideas are labeled "non-literal" — never present them as plans.
- Don't blend modes in one output. Each generation pass is one mode only.
- In plan mode: run this skill automatically, but keep the menu step — don't skip straight to ideas.
- If the user says "just give me ideas" without context → ask for goal and horizon first, one question.
- Repeat passes only when the user asks for more or switches mode.
