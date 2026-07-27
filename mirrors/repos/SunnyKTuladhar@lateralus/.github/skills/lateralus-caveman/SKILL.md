---
name: lateralus-caveman
description: "Caveman-compressed lateral-thinking escape hatch for stalled debugging. Surfaces end goal and horizon (long-term, MVP, POC, workaround) then generates goal-appropriate alternatives in two tiers. 60% fewer tokens. Use only after normal debugging genuinely stalled."
argument-hint: "What tried, what failed, current error, end goal"
user-invocable: true
license: MIT
---

Goal first. Break tunnel vision. Generate outside failed approach.

## Step 0 — Interrogate before ideating (always first)

### P1 — Read codebase silently first

1. Check for `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` at repo root — read fully if present.
2. If absent: detect stack from `go.mod` / `package.json` / etc., skim `README.md` (60 lines), run `git log -10 --oneline`, glob for config files.
3. Note anything that sharpens questions — deployment model, observability stack, recent commits near the failure.

No codebase accessible (pasted scenario) → skip to P2.

### P2 — Present options, ask user to pick

If P1 found context → surface it briefly before the menu.

```
Four paths — which fits?

  [1] Tier 1 · Ground    — testable hypotheses outside the obvious
  [2] Tier 2 · Balanced  — question assumptions, loosely verifiable
  [3] Tier 3 · Wild      — speculative reframes, break tunnel vision
  [4] Workaround         — bypass now, fix later

Pick a number or describe your situation.
```

Situation described → infer best fit, confirm before proceeding.
Distressed / deadline → suggest [4] first.

### P3 — Tailored questions by choice

**[1] Ground:**
```
1. What tried, why failed?
2. Which component/layer fails?
3. What observability do you have? (profiler, APM, logs, metrics)
4. What does monitoring show beyond the headline symptom?
5. When did it start — correlates with a specific change?
6. Any profiling data collected yet? (heap dump, flame graph, etc.)
7. What can't change?
8. How will you verify a fix?
```

**[2] Balanced:**
```
1. What tried?
2. What assumed fine but never checked?
3. Horizon? (long-term / MVP / POC / test)
4. How will you know it's fixed?
```

**[3] Wild:**
```
1. What's assumed definitely NOT the problem?
2. Error location vs actual origin?
3. If the failing component is off-limits, what then?
4. Solve with data not code — what does that look like?
```

**[4] Workaround:**
```
1. What's blocking you right now?
2. How long does bypass need to last?
3. What breaks if it stays in?
```

Cold → one question at a time. Engaged → batch the path's questions.

### P4 — Dead-ends audit (Ground / Balanced / Wild only)

`git log -10 --oneline`, `git diff HEAD~3`, `git grep`. Grep/Glob for changes. Read ranges only.

No prior attempt → `No stall yet. Normal debugging first.`
Data-loss risk → state plainly before dead-ends table.

### Context block (before ideation)

```
Choice: Ground | Balanced | Wild | Workaround
Goal / Horizon / Constraints / Unverified assumptions / Success signal
Ruled out: <area> — <fix tried> — <why failed>
Still unknown: <open question>
```

Route to chosen agent after block is complete.

## When

Fire only after debugging stalled:
- 2+ fixes on same bug failed
- "still broken" / "already tried" / "same error" / "going in circles"
- About to repeat variant of ruled-out fix

NOT first attempt.

## Rules

Confidence calibration — three layers, always before tiers:

| Layer | What | Label |
| --- | --- | --- |
| **Facts** | What logs/metrics literally show | No hedge needed |
| **Inferences** | Conclusions supported by facts | `high-confidence` / `medium-confidence` |
| **Speculation** | Possible but unverified | `unverified hypothesis` |

Never present inference or speculation as fact. No traceability to a signal → must be labeled.

Dead ends first. One line: ruled out + why. Never repeat.

Two tiers. Both. Always labeled. Never blend.

Pattern: `Goal: [horizon]. Facts: [observed]. Inferences: [confidence-labeled]. Ruled out: [x]. T1: [grounded]. T2: [balanced]. T3: [wild].`

## Tiers

| Tier | Agent | What | Length |
| --- | --- | --- | --- |
| **T1 — Ground** | `lateralus-ideator-ground` | 3-5 testable causes outside obvious. Cache, encoding, timezone, race, stale build, dep drift, inverted baseline, adjacent component. Depth = horizon. | Name it. How to test it. |
| **T2 — Balanced** | `lateralus-ideator-balanced` | 3-5 assumption-questioning, loosely testable hypotheses. Bridge T1 and T3. | Hypothesis + assumption + loose signal. |
| **T3 — Wild** | `lateralus-ideator-wild` | 3-5 reframes. Not literal. Jolt associations: ignored premise, data not code, distrust error location, unify bugs, question if problem needs solving. State non-literal up front. | 1-2 sentences. No over-justification. |

## Boundaries

No prior attempt → skip.
Don't fire twice same stall without new info.
User picks direction → investigate before new batch.
End: ask which direction next.
