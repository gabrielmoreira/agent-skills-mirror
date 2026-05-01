---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Debugging — hypothesis-driven investigation and root-cause analysis for bugs, errors, incidents"
application: "When investigating build failures, test errors, runtime crashes, recurring bugs, or incidents"
applyTo: "**/*debug*,**/*bug*,**/*error*,**/*fix*,**/*issue*,**/*incident*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Debugging

Apply the scientific method, then drive to root cause. Replaces `hypothesis-driven-debugging` and `root-cause-analysis`.

## When to Use

| Trigger | Section |
|---------|---------|
| New bug, build failure, test red, unexpected behavior | §1 — Hypothesis-driven |
| Recurring bug, post-incident analysis, "we already fixed this" | §2 — Root-cause analysis |
| Both apply for non-trivial bugs — start with §1, deepen to §2 |

## §1 — Hypothesis-Driven Investigation

### Core Protocol

1. **Observe** — Reproduce the failure. Capture exact error, stack trace, and conditions
2. **Hypothesize** — Form **at least 2** competing hypotheses. Rank by likelihood
3. **Experiment** — Design a minimal test that distinguishes between them
4. **Conclude** — Accept or reject each hypothesis based on evidence
5. **Verify** — Re-run full builds and tests after every change

### Key Rules

- Never change more than one variable at a time
- Always re-run the full test suite after a fix, not just the failing test
- Document what you ruled out, not just what you found
- If a hypothesis survives 3 experiments, it's likely correct
- If all hypotheses fail, step back and re-observe with fresh eyes

### Anti-Patterns

| Pattern | Fix |
|---------|-----|
| Single hypothesis → confirmation bias | Always ≥2 hypotheses (ACT Tenet III) |
| "It works now" with no understanding why | Don't ship until you can explain why |
| Trying random fixes | Each change must be a *test* of a hypothesis |

## §2 — Root-Cause Analysis

Activate when: a bug recurs after a fix, a production incident occurs, or a failure has no obvious cause.

### Step 1: Reproduce

- Confirm the issue is reproducible (failing test, repro steps, log evidence)
- If not reproducible: collect environment details, timestamps, traffic patterns

### Step 2: Isolate

- Find the smallest case that demonstrates the failure
- Binary search: `git bisect` between last-known-good and current-bad
- Strip away unrelated code/config until the minimal trigger remains

### Step 3: 5 Whys (with Evidence)

Ask "Why?" until you reach an actionable system change:

1. Each answer must have **evidence** (logs, code, metrics) — not speculation
2. Branch when multiple causes exist — don't follow a single chain
3. If the chain ends at human error → ask "Why was it possible to make this mistake?"
4. Stop when you reach a **preventable system change**

### Step 4: Categorize the Cause

| Category | Fix Pattern |
|----------|-------------|
| Code | Unit test + code fix |
| Data | Validation + migration |
| Infrastructure | Monitoring + capacity |
| Dependencies | Pin version + lockfile |
| Configuration | Config validation + safe defaults |
| Process | Checklist + automation |

### Step 5: Fix and Verify

1. Write a failing test that captures the root cause
2. Apply the minimal fix
3. Verify the test passes
4. Check for similar patterns elsewhere (`grep` for related code)
5. Document what was found and why in the commit message

### Step 6: Prevent Recurrence

- Add automated detection (lint rule, test, CI check)
- Update relevant runbooks or checklists
- If process gap: update PR template or review guidelines

## Skill Reference

Full procedural depth in:

- `.github/skills/critical-thinking/hypothesis-driven-debugging/SKILL.md`
- `.github/skills/critical-thinking/root-cause-analysis/SKILL.md`

## What This Replaces

- `hypothesis-driven-debugging` → §1
- `root-cause-analysis` → §2

Combined because every non-trivial bug uses both: hypotheses to find the cause, then RCA to prevent recurrence.
