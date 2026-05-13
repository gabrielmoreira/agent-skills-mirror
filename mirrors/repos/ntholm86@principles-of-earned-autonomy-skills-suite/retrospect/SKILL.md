---
name: retrospect
version: 1.8.0
description: 'Read the trail as a single document and form arc-level claims about the target. What is the target becoming? Where has the loop''s attention been, and is that where the target''s real weight lies? What does the arc reveal that no individual iteration would surface? Writes .trail/retrospect.md — the Retrospect-derived current orientation for the target. Vision (.trail/vision.md), if present, is the operator-held destination and is read but never written. USE WHEN: about to declare convergence, recurring finding-class suspected, operator asks "how are we doing?", or an independent arc-read is needed without running a full improve loop.'
argument-hint: 'The target and its trail, and optionally the specific arc-question to answer'
---

# Retrospect

*Read the whole arc. See what no single iteration can.*

*Memory Model role: Synthesizes the trail into `.trail/retrospect.md` — the arc-level orientation the next run starts from.*

The Improve loop is optimised for one iteration at a time. Retrospect is optimised for reading all of them at once. Where Improve asks "what should change next?", Retrospect asks "what has been changing, where is the weight of this target actually sitting, and is the loop looking at the right thing?"

Run this skill when an arc-level view is more useful than another low-altitude pass: before declaring convergence, when a pattern of similar findings has emerged, when the operator asks "how are we doing?", or any time you want arc-level understanding without committing to a change.

## Governing principles

This skill enacts two principles:

1. **Observable Autonomy** — the trail exists so that arc-claims can be made and checked. Retrospect is the mechanism that reads the trail as evidence rather than as a log.
2. **Convergence Is Silence** — convergence is only meaningful if the arc was read honestly before it was declared. Retrospect is that check.

Full statement of the principles: [PRINCIPLES.md](../PRINCIPLES.md) — read it if available, but this skill operates fully without it.

## The work

### 0. Read vision first

Before forming any scope statement, read `.trail/vision.md` **in the target repo root** if it exists. Vision is the operator-held destination — what the target is for and what constraints hold across all runs. Reading it first ensures the arc is read against what the operator actually cares about, not retrofitted afterward.

If no `vision.md` exists, proceed — but note the absence. A Retrospect run on a target without vision is reading the arc without a destination to orient against.

### 1. Identify the scope

State what you are about to read and what question you are trying to answer before reading anything. Examples:

- "Read the last 10 entries and determine whether the recent finding pattern is meaningful or coincidental."
- "Read the full trail before declaring silence — is the silence well-earned or is the loop stuck in a comfortable corner?"
- "Read the arc and assess whether the loop has been looking at the parts of the target that carry real weight."

A scope statement prevents the arc-read from being undirected. It also makes the result falsifiable: a future reader can check whether the question was answered.

### 1b. Freshness guard (derived artifacts)

Before forming arc-claims, refresh the derived trail artifacts from the current `.trail/audit-trail.md`.

- If the target repo has `tools/record.py`, run:
	- `python tools/record.py history --write`
	- `python tools/record.py learning --write`
- If `tools/record.py` is not available, run the target's equivalent derivation commands.
- Confirm `.trail/history.md` and `.trail/learning.md` are not older than `.trail/audit-trail.md` (via verify checks or file mtime).

If the refresh cannot be completed, stop and report the blocker. Do not write arc-claims from stale derived artifacts.

Use this execution checklist in the run notes:

- [ ] `python tools/record.py history --write`
- [ ] `python tools/record.py learning --write`
- [ ] `python verify.py` (or target-equivalent integrity check)
- [ ] Confirm there are no stale-artifact failures for `.trail/history.md` or `.trail/learning.md`
- [ ] If any freshness check fails, stop and report the blocker; no arc-claims are allowed

Minimal filled example:

```markdown
**Freshness check (run evidence):**
- commands: `python tools/record.py history --write`; `python tools/record.py learning --write`; `python verify.py`
- verify result: `OK — trail integrity checks pass`
- gate: PASS (arc-claims allowed)
```

### 2. Read the arc

Read `.trail/audit-trail.md` **in the target repo root** as a single document about the target — not as a list of past runs. Look for:

- **What has changed, and in what order?** The sequence often reveals a target's actual architecture more clearly than any single snapshot.
- **Outcome anchoring:** For every claim and prediction made in the trail across the arc, did it actually hold up over subsequent runs? If multiple entries confidently claim improvements (e.g., "reduced complexity") but reality contradicts it, the trail is confabulating per-iteration.
- **Reversal density:** Identify the ratio of smooth "successes" to reversals and failed predictions. A long unbroken sequence with no `[!REVERSAL]`, `[!REALIZATION]`, or mismatched predictions strongly suggests post-hoc rationalization rather than flawless execution.
- **Where has attention been concentrated?** Name the specific areas of the target that received the most runs, the most finding-types, the most reversals.
- **What has been consistently avoided?** Corners the loop never examined are as informative as corners it examined repeatedly.
- **Which `[!REALIZATION]` markers aged well, and which were later contradicted?** Realizations that got overturned without a matching `[!REVERSAL]` signal the loop was converging on a wrong model.
- **What is the target becoming?** Not what it was at run 1 — what trajectory does the arc suggest?
- **Candidate next moves:** What did prior runs suggest as the next most valuable work? Are those suggestions being followed, ignored, or superseded? This is a direct signal of how the operator-gate is steering the work.

### 2b. Adversarial Audit Mode

If invoked explicitly to audit the trail (Mitigation #4), use this lens:
- **Hunt for rationalizations:** Where does the stated outcome conveniently ignore part of the prediction?
- **Test the failures:** Is the trail completely green (no reversals)? A trail with no `[!REVERSAL]` or `[!REALIZATION]` markers is mathematically unlikely in complex work and strongly indicates post-hoc LLM confabulation.
- **Diff vs. Claim:** Do the actual file diffs support the grand claims made in the log entries? 

### 3. Form arc-claims

Write what the arc reveals as falsifiable claims. The shape is always a statement a future run could disagree with by finding contrary evidence.

Examples of the right shape:

- "This target has converged on documentation consistency but has not been examined for behavioural correctness — every finding to date has been a text fix."
- "The loop has examined the external interface exhaustively but has not touched the internal state model. The next finding, if one exists, lives there."
- "The trail shows three reversals in the same area. The loop has not yet found a stable model of that area."

Avoid: "The target seems to be in good shape." That is an observation without content, not a claim.

### 4. Evaluate loop effectiveness (when the arc warrants it)

When the arc-read surfaces questions about whether the loop is achieving what it is for, answer them. The loop's effectiveness is part of the target's story — examining it is a lens, not navel-gazing.

Ask:

- Has the loop been finding genuine findings, or finding excuses to act?
- Is the silence earned, or is the loop stuck looking at easy surfaces?
- What kind of finding would this loop structurally miss? Name it concretely.
- If the operator could see the arc as a whole, would they say "yes, that is the right focus"?

Run this step when: the loop is about to declare convergence, the finding pattern looks suspiciously tidy, or the operator explicitly asked how the loop is performing.

### 4b. Extract operational rules (Learning)

The arc is the mechanism by which the agent learns how to work within the specific target environment. Without explicitly harvesting structural lessons, the agent will repeat the same mistakes in fresh sessions.

- Look for `[!REALIZATION]` markers across the arc that describe operational failures, successful rules of engagement, or architectural landmines specific to this target (e.g., "Never trust the build script to clean up," "This repo forbids adding third-party dependencies").
- Synthesize these historical realizations into concrete, imperative rules for future agents. Do not just summarize what happened; state *what must be done differently next time*.

### 5. Write the retrospect.md

**Before writing: create the `.trail/` directory in the target repo root if it does not already exist.**

Write the arc-claims from step 3 (and any loop-effectiveness findings from step 4) to `.trail/retrospect.md` in the target repo root. This file is the **retrospect.md** — the current Retrospect-derived orientation: where the loop's attention has been, what the arc currently shows is true of the target, and what the next runs should test.

The retrospect.md should make sense in light of vision (read at step 0) — arc-claims may reference whether the loop has been pursuing what vision says matters — but must not duplicate vision content. Never write to `.trail/vision.md` from a Retrospect run.

`.trail/retrospect.md` is not append-only. Retrospect replaces it each time it runs. The full reasoning history lives in `audit-trail.md`; vision is the destination; the retrospect.md is the current distillation of where the target is along the way.

The file shape is simple:

```markdown
# retrospect.md — <target name>

_Last updated: YYYY-MM-DD (run: <slug>)_

## Current claims

<Arc-claims from step 3, each as a falsifiable statement.>

## What the next runs should test

<Specific arc-derived suggestions for what would most advance the target now. This section should synthesize the `Candidate Next Moves` from recent trail entries.>

## Active operational rules

<Imperative, target-specific rules of engagement extracted from step 4b (e.g., "Do not bypass the prediction block", "Always use replace encoding when reading audit-trail.md"). These carry the 'Learning' forward across sessions.>

## Loop-effectiveness notes

<From step 4, if triggered. Omit section if step 4 was not run.>
```

Commit `.trail/retrospect.md` alongside `audit-trail.md`, `history.md`, and `learning.md` after the run. Never commit changes to `.trail/vision.md` from a Retrospect run.

### 6. Record

*If [Trail](../trail/SKILL.md) is installed, apply it now — it handles this step in full.*

If Trail is not installed: append a single entry to `.trail/audit-trail.md` containing:

- Date, target, operator (if known), model identity (provider + tool-call ID prefix if observable).
- The scope statement from step 1.
- The arc-claims from step 3 — written as falsifiable statements, not summaries.
- Loop-effectiveness findings from step 4 (if triggered), marked with `[!REALIZATION]` where material.

There is no separate "decision" or "action" field unless a follow-up action was identified. Retrospect is observational; its output is claims, not changes.

## What this skill does not do

- **It does not make changes to the target.** Retrospect reads and claims; Improve changes. If the arc reveals a specific finding, hand off to Improve.
- **It does not replace Improve's step 6b.** Step 6b is a lightweight in-loop check that fires inside an improve iteration when a trigger condition is met. Retrospect is a standalone arc-read run instead of an improve iteration when a high-altitude view is what is needed. Use both.
- **It does not score the trail.** No number, no rubric, no grade. Claims are the output — claims a future run can test.
