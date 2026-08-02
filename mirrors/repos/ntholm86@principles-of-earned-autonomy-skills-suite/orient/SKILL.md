---
name: orient
version: 2.4.0
description: 'Read the trail as a single document and form arc-level claims about the target. What is the target becoming? Where has the loop''s attention been, and is that where the target''s real weight lies? What does the arc reveal that no individual iteration would surface? Writes .acm/orientation.md — the Orient-derived current orientation for the target. Destination (.acm/destination.md), if present, is the operator-held destination and is read but never written. USE WHEN: about to declare convergence, recurring finding-class suspected, operator asks "how are we doing?", or an independent arc-read is needed without running a full improve loop.'
argument-hint: 'The target and its trail, and optionally the specific arc-question to answer'
---

# Orient

*Read the whole arc. See what no single iteration can.*

*Memory Model role: Synthesizes the trail into `.acm/orientation.md` — the arc-level orientation the next run starts from.*

The Improve loop is optimised for one iteration at a time. Orient is optimised for reading all of them at once. Where Improve asks "what should change next?", Orient asks "what has been changing, where is the weight of this target actually sitting, and is the loop looking at the right thing?"

*Lineage:* this split mirrors Boyd's OODA loop (Observe-Orient-Decide-Act) — Boyd's own insight was that Orientation, not Decision, is the phase that shapes everything downstream and the one most commonly neglected. Cited explicitly in this suite's v1 ancestor but dropped when v2's skills merged into v3; restored here since it is this skill's own namesake.

Run this skill when an arc-level view is more useful than another low-altitude pass: before declaring convergence, when a pattern of similar findings has emerged, when the operator asks "how are we doing?", or any time you want arc-level understanding without committing to a change.

## Governing principles

This skill enacts two principles:

1. **Observable Autonomy** — the trail exists so that arc-claims can be made and checked. Orient is the mechanism that reads the trail as evidence rather than as a log.
2. **Convergence Is Silence** — convergence is only meaningful if the arc was read honestly before it was declared. Orient is that check.

Full statement of the principles: [PRINCIPLES.md](../PRINCIPLES.md) — read it if available, but this skill operates fully without it.

## The work

### 0. Read the destination first (all scopes)

Before forming any scope statement, read `.acm/destination.md` **in the target repo root** if it exists. This is the operator-held destination — what the target is for and what constraints hold across all runs. Reading it first ensures the arc is read against what the operator actually cares about, not retrofitted afterward.

**ACM §4 Scoped Memory — read parent scopes first.** Before reading the repo's `.acm/destination.md`, traverse parent directories upward and read any `.acm/destination.md` found there. Higher-scope mandates govern lower-scope ones — if a workspace or org destination conflicts with the repo destination, the higher scope wins. Label each scope when reading (e.g., "workspace mandate", "repo mandate"). Stop traversal when any of: filesystem root reached; a `.acm-root` marker file is found in a directory (operator-declared ceiling — read that directory's `.acm/` then stop); or 4 levels traversed (implementation ceiling). The workspace destination gives the arc its organizational context; arc-claims made without it may miss cross-repo coordination constraints.

If no `destination.md` exists at any scope, proceed — but note the absence. An Orient run on a target without a destination is reading the arc without somewhere to orient against.

### 1. Identify the scope

State what you are about to read and what question you are trying to answer before reading anything. Examples:

- "Read the last 10 entries and determine whether the recent finding pattern is meaningful or coincidental."
- "Read the full trail before declaring silence — is the silence well-earned or is the loop stuck in a comfortable corner?"
- "Read the arc and assess whether the loop has been looking at the parts of the target that carry real weight."

A scope statement prevents the arc-read from being undirected. It also makes the result falsifiable: a future reader can check whether the question was answered.

### 1b. Freshness guard (derived artifacts)

Before forming arc-claims, refresh the derived trail artifacts from the current `.acm/audit-trail.md`.

- If the target repo has `tools/record.py`, run:
	- `python tools/record.py history --write`
	- `python tools/record.py learning --write`
- If `tools/record.py` is not available, run the target's equivalent derivation commands.
- Confirm `.acm/history.md` and `.acm/learning.md` are not older than `.acm/audit-trail.md` (via verify checks or file mtime).

If the refresh cannot be completed, stop and report the blocker. Do not write arc-claims from stale derived artifacts.

Use this execution checklist in the run notes:

- [ ] `python tools/record.py history --write`
- [ ] `python tools/record.py learning --write`
- [ ] `python verify.py` (or target-equivalent integrity check)
- [ ] Confirm there are no stale-artifact failures for `.acm/history.md` or `.acm/learning.md`
- [ ] If any freshness check fails, stop and report the blocker; no arc-claims are allowed

Minimal filled example:

```markdown
**Freshness check (run evidence):**
- commands: `python tools/record.py history --write`; `python tools/record.py learning --write`; `python verify.py`
- verify result: `OK — trail integrity checks pass`
- gate: PASS (arc-claims allowed)
```

### 2. Read the arc

Read `.acm/audit-trail.md` **in the target repo root** as a single document about the target — not as a list of past runs. Look for:

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

### 3b. Ask whether a recurring arc-claim is a single-loop symptom or a double-loop signal

When step 3 produces a claim describing a *recurring* pattern — the same finding-class across multiple entries, the same kind of correction applied repeatedly, the same corner returned to again and again — ask explicitly whether the recurrence is a single-loop symptom or a double-loop signal. Single-loop correction fixes the action within existing governing variables (a goal, constraint, or quality-bar choice in `.acm/destination.md`, or an unstated assumption the arc has been carrying) while leaving those variables themselves unexamined. If the same finding-class keeps recurring despite repeated correction, the recurrence itself is evidence that the governing variable — not the action — is the actual defect.

This question can resolve to "no." A recurring pattern is not automatically a governing-variable defect — some recurrences are the arc correctly behaving as designed (candidates sitting unpicked across entries while the operator directs attention elsewhere is an explicitly valid pattern, not a defect). Answer honestly in both directions; the question exists to be asked, not to manufacture an escalation.

When it resolves to "yes": name the specific governing variable implicated, write it as a candidate destination-revision — not another arc-claim about the target's surface — and record it as such. Whether to act on it is the operator's decision via [Destination](../destination/SKILL.md); Orient's job is to make the governing-variable question visible, not to resolve it unilaterally.

*Why this belongs in Orient, and not only in Improve's step 6b:* step 6b fires from inside a single iteration, when that iteration happens to notice a recurring pattern. Orient reads the whole arc at once and is positioned to catch governing-variable-level recurrences that no individual iteration had enough surface area to see — exactly the kind of finding an arc-level read exists for. (Argyris, *Organizational Learning*, 1977 — single-loop learning corrects action within existing governing variables; double-loop learning questions and revises the governing variables themselves.)

### 4. Evaluate loop effectiveness (Argyris & Schon's deutero-learning: is the way this loop learns itself sound?)

When the arc-read surfaces questions about whether the loop is achieving what it is for, answer them. The loop's effectiveness is part of the target's story — examining it is a lens, not navel-gazing. Where step 3b asks whether the target's governing variables are wrong (double-loop), this step asks the next-order question: is the mechanism by which this loop itself learns, reflects, and detects errors well designed — or is the reflection process itself what needs revision? (Argyris & Schon, *Organizational Learning II*, 1978 — deutero-learning: learning about the learning system itself, distinct from correcting either the action or the governing variable.)

Ask:

- Has the loop been finding genuine findings, or finding excuses to act?
- Is the silence earned, or is the loop stuck looking at easy surfaces?
- **Which quality bars has the loop actually tested, and which has it never been challenged on?** An orient run can only test the bars it knows about. Internal text-layer consistency, comparative defensibility under hostile external review, comparator coverage, empirical replication, and operational deployability are distinct bars; passing one says nothing about the others. Name the bar this orient run's silence claim applies to.
- What kind of finding would this loop structurally miss? Name it concretely.
- If the operator could see the arc as a whole, would they say "yes, that is the right focus"?

Run this step when: the loop is about to declare convergence, the finding pattern looks suspiciously tidy, or the operator explicitly asked how the loop is performing.

**If this step surfaces a structural blind spot in how the loop itself learns** — a lens it never applies, a trigger that never fires, a trail format that hides the evidence it should show — that is not a target-level finding to file away among this run's arc-claims. Name the specific mechanism implicated (a lens, a trigger, a check, the trail format itself), state it as a candidate revision to the loop's own design, and route it to the operator via [Destination](../destination/SKILL.md) — the same way step 3b routes governing-variable findings. A blind spot in how the loop learns is at least as load-bearing as a blind spot in the target itself: it silently caps every future run's ability to find anything the current mechanism cannot see.

Acting on the candidate is itself a subsequent [Improve](../improve/SKILL.md) iteration targeting the implicated mechanism — no separate incremental-vs-radical logic is needed here, because that iteration's own Purpose lens and Kaikaku question (step 3) already make that decision generically, for any target. If the outcome is a redesign of how the loop reasons, its validation is Convergence Is Silence, not the agent's own judgment that it improved.

### 4b. Extract operational rules (Learning)

The arc is the mechanism by which the agent learns how to work within the specific target environment. Without explicitly harvesting structural lessons, the agent will repeat the same mistakes in fresh sessions.

- Look for `[!REALIZATION]` markers across the arc that describe operational failures, successful rules of engagement, or architectural landmines specific to this target (e.g., "Never trust the build script to clean up," "This repo forbids adding third-party dependencies").
- Synthesize these historical realizations into concrete, imperative rules for future agents. Do not just summarize what happened; state *what must be done differently next time*.

### 5. Write the orientation.md

**Before writing: create the `.acm/` directory in the target repo root if it does not already exist.**

Write the arc-claims from step 3 (and any loop-effectiveness findings from step 4) to `.acm/orientation.md` in the target repo root. This file is the **orientation.md** — the current Orient-derived orientation: where the loop's attention has been, what the arc currently shows is true of the target, and what the next runs should test.

The orientation.md should make sense in light of the destination (read at step 0) — arc-claims may reference whether the loop has been pursuing what the destination says matters — but must not duplicate destination content. Never write to `.acm/destination.md` from an Orient run.

`.acm/orientation.md` is not append-only. Orient replaces it each time it runs. The full reasoning history lives in `audit-trail.md`; the destination is where the target is going; the orientation.md is the current distillation of where the target is along the way.

The file shape is simple:

```markdown
# orientation.md — <target name>

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

Commit `.acm/orientation.md` alongside `audit-trail.md`, `history.md`, and `learning.md` after the run. Never commit changes to `.acm/destination.md` from an Orient run.

### 5a. Bound every silence claim

Any claim in `orientation.md` that the target has reached silence, convergence, or readiness must name **which quality bar** the silence applies to and **which surfaces** are in scope. Unbounded silence claims ("the target is in good shape", "text-layer silence is now earned") are the form most likely to be overturned by the next operator-initiated probe, because a bar the orient has never tested cannot be inside the silence claim.

The pattern: *"Silence on `<named bar>` for `<named surfaces>`. Bars not tested by this orient run: `<list>`."

Examples:
- *"Silence on internal text-layer consistency for all non-operator-locked surfaces. Bars not tested: comparative defensibility under hostile external review, comparator coverage."*
- *"Silence on comparative defensibility for the prior-work bullets currently in scope. Bars not tested: comparator coverage (whether the right set of prior works has been engaged at all), empirical replication."*

If the orient run cannot name the bar, the silence claim is not yet ready to be made. Either name the bar or write the claim as a bar-scoped observation rather than as silence.

*Origin:* This rule was promoted from the manifesto target's `retro-v201` -> `retro-v202` transition (entry slug `retrospect-v202-comparative-defensibility`, 2026-06-04), where a retrospect-declared text-layer silence was overturned within the same day by an operator-initiated publication-rigour-review run that tested a quality bar the prior retrospect had never been challenged on. Full provenance in this repo's `.acm/audit-trail.md` under entry slug `retro-named-boundary-rule-from-manifesto-arc`.

### 6. Record

*If [Trail](../trail/SKILL.md) is installed, apply it now — it handles this step in full.*

If Trail is not installed: append a single entry to `.acm/audit-trail.md` containing:

- Date, target, operator (if known), model identity (provider + tool-call ID prefix if observable).
- The scope statement from step 1.
- The arc-claims from step 3 — written as falsifiable statements, not summaries.
- Loop-effectiveness findings from step 4 (if triggered), marked with `[!REALIZATION]` where material.

There is no separate "decision" or "action" field unless a follow-up action was identified. Orient is observational; its output is claims, not changes.

## What this skill does not do

- **It does not make changes to the target.** Orient reads and claims; Improve changes. If the arc reveals a specific finding, hand off to Improve.
- **It does not replace Improve's step 6b.** Step 6b is a lightweight in-loop check that fires inside an improve iteration when a trigger condition is met. Orient is a standalone arc-read run instead of an improve iteration when a high-altitude view is what is needed. Use both.
- **It does not score the trail.** No number, no rubric, no grade. Claims are the output — claims a future run can test.
