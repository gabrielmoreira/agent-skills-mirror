---
type: skill
lifecycle: stable
inheritance: inheritable
name: act-pass
description: Run the 7-step Artificial Critical Thinking pass — Materiality → Hypothesise → Alternatives → Disconfirmers → Audit priors → Severity → Commit-with-marker
tier: core
applyTo: '**/*act*,**/*pass*'
currency: 2026-04-26
lastReviewed: 2026-04-30
---

# ACT Pass (7-Step Operational Pass)


> ACT is not a posture; it is a 7-step pass for non-trivial requests. Short enough to run in seconds, concrete enough to leave evidence in the output.

## Purpose

The ACT manifesto names 10 tenets. This skill operationalises tenets I (Hypothesis primacy), II (Disconfirmation), III (Multiple working hypotheses), VI (Materiality), VII (Frame before solve), and VIII (Adversarial self-probe) as a single callable pass. Before this skill, the steps were distributed across `critical-thinking`, `awareness`, `anti-hallucination`, and `problem-framing-audit` — with no single entry point. The trifecta (this skill + `act-pass.instructions.md` + `/act-pass.prompt.md`) closes that gap.

## When to Run a Pass

| Stakes | Pass type | Trigger |
|---|---|---|
| **Low** — formatting, naming, internal refactor, mechanical edits | **Skip** — Materiality Gate exits at step 1 | Default for trivial work |
| **Medium** — architectural decision, plan change, manifesto/doc drafting, multi-file change | **Trimmed pass** — steps 1, 3, 5, 6 | Most common |
| **High** — release, deployment, irreversible op, security-critical change | **Full pass** — all 7 steps | Rare |

Trigger phrases that should fire a pass: "fix this", "make it faster", "release", "deploy", "merge", "is this safe", "should we", "what's the risk". The instruction (`act-pass.instructions.md`) carries the always-on detection rule.

## The 7 Steps

### Step 1 — Materiality (Tenet VI)

**Question**: If I get this wrong, would it change a decision?

If no → exit. Note the triage decision (e.g., *"low-stakes; ACT skipped"*) and proceed without the pass.

If yes → proceed and tag intensity (medium / high). Intensity sets which steps fire below.

**Visible artifact**: triage decision. On a trimmed pass, this can be implicit; on a full pass, state it.

### Step 2 — Hypothesise the ask (Tenet I, Tenet VII)

**Question**: What is the user's request, restated as a testable claim?

This is where Discipline -1 (frame audit) lives — the ask becomes a hypothesis with truth conditions, not a literal command. If the user said "make it faster", the hypothesis is "the bottleneck is in X, and reducing X will satisfy the user's underlying intent." That's a falsifiable claim. The literal request is not.

**Visible artifact**: `H1 — <restated claim>`.

### Step 3 — Surface alternatives (Tenet III)

**Question**: What is at least one rival hypothesis?

The Two-Hypothesis Floor (per `critical-thinking.instructions.md`) requires this even on trimmed passes. The alternative must cite a specific reason — performative alternatives without grounding fail the rule.

**Visible artifact**: `H2 — <alternative claim>` (with grounding: *because* / *given*).

### Step 4 — Identify disconfirmers (Tenet II)

**Question**: What evidence would falsify each hypothesis?

This is the load-bearing step. The point is not to confirm H1 — it's to specify what would *break* it. If nothing could, H1 is unfalsifiable and should be either retired or restated.

**Visible artifact**: `Disconfirmer for H1: <observation that would force revision>` and same for H2.

### Step 5 — Audit priors (Tenet IV)

**Question**: Which beliefs came from the request itself vs from independent evidence?

The user's framing is evidence, but it is *one* source. If 100% of my support for H1 comes from "the user said so", system-prompt skepticism (Tenet IV; `system-prompt-skepticism.instructions.md`) should fire. Surface the split.

**Visible artifact**: `Evidence split: <X> from request, <Y> from elsewhere (logs, code, prior session, domain knowledge)`.

### Step 6 — Severity check (Tenet VIII)

**Question**: If H1 is false, would my plan reveal it?

This is the adversarial self-probe. If my plan would silently succeed under H2 (the wrong hypothesis) without surfacing the error, the plan is decorative — it tests nothing. Redesign so the plan would *fail visibly* if H1 is wrong.

**Visible artifact**: `If H1 is false, the plan would reveal it because <X>` — or `the plan does not test H1; this is a known weakness`.

### Step 7 — Commit with marker (Tenet IX)

**Question**: Final answer + the conditions under which I'd revise.

Don't hedge. Commit. But pair the commit with falsifiability — "Going with H1; revisit if disconfirmer X appears." The visible marker is what makes the commitment auditable later.

**Visible artifact**: `Going with H1: <action>. Would revise if: <specific evidence>.`

## Worked Example

**User request**: *"The build is slow, speed it up."*

**Without ACT**: I propose generic build optimizations — parallel test runners, build cache tuning, dependency pruning. They may help. They may not. The user gets a list of patches and no diagnostic.

**With ACT**:

| Step | Output |
|---|---|
| 1. Materiality | Medium — wrong fix wastes 2–4 hours of engineering time. Run a trimmed pass. |
| 2. Hypothesise | H1 — Compile graph is over-large; build is compile-bound. |
| 3. Alternatives | H2 — Test suite dominates wall-clock (test-bound). H3 — Disk/network is the limit (I/O-bound). H4 — Wall-clock is fine but feedback is delayed (perception-bound). |
| 5. Audit priors | All four hypotheses are from "build is slow"; no independent evidence yet. Confidence is low. |
| 6. Severity check | A 90-second profiler run distinguishes all four before any fix is committed. The plan tests H1 by trying to refute it. |
| 7. Commit | Going with: profile first, fix second. Would revise the diagnosis if profiler shows a fifth pattern (e.g., GC pressure, lock contention). |

The difference: **answering** vs **testing**. ACT is the second.

## Visible Markers Cheat Sheet

When the pass fires, the response should carry these markers (omit unused ones — only fire what the pass produced):

- `**H1**: ...` — restated ask as hypothesis
- `**H2**: ... (because / given ...)` — at least one alternative with grounding
- `**Disconfirmer for H1**: ...` — what would force revision
- `**Evidence split**: X from request, Y from elsewhere` — prior audit
- `**Severity**: If H1 is false, the plan would reveal it because ...`
- `**Going with H1**: <action>. Would revise if ...` — the commit

These markers are not boilerplate. Every marker the pass emits should carry real content — performative markers without grounding violate Tenet IX (visible markers) by satisfying the surface form without the substance.

## Anti-Patterns

| Anti-pattern | Why it fails | Correction |
|---|---|---|
| Run a full pass on every request | Friction kills the discipline; trivial tasks die under it | Materiality first; exit cheap when stakes don't earn the pass |
| Performative alternatives ("could also be A or B") | Tenet IX Goodhart failure — surface form without content | Each alternative must cite specific grounding (Two-Hypothesis Floor rule) |
| Skip step 4 (disconfirmers) on trimmed pass | Pass becomes confirmation, not test | Step 4 is load-bearing; trimmed passes still need *one* disconfirmer |
| State "would revise if new evidence emerges" | Boilerplate falsifiability | Name *specific* evidence — "if profiler shows GC pressure" not "if new data" |
| Use ACT to delay action | Pyrrhonian regress — doubt becomes a stance, not a tool | Doubt is methodological; commit at step 7 even under uncertainty |
| Run pass silently (no visible markers) | Tenet IX violation — discipline that leaves no trace cannot be audited | Visible markers in the output, not just in internal reasoning |

## Falsifiability Test (per PLAN-act-brain-integration.md Lane 1)

After 30 days from v9.0.0 tag, count `/act-pass` invocations + canary-phrase hits in transcripts:

- **Target**: ≥ 5 invocations on real medium-stakes decisions, ≥ 1 on a high-stakes decision
- **If 0 invocations**: the trifecta is decorative. Retire per ACT moratorium §6.
- **If invocations exist but produce no visible markers**: Tenet IX is failing — the pass is silent. Fix the prompt to enforce markers.

## Integration

| Surface | How `act-pass` attaches |
|---|---|
| `critical-thinking/SKILL.md` | The 7 disciplines are the *parts*; this skill is the *composite pass* that uses them in order |
| `problem-framing-audit/SKILL.md` (Discipline -1) | Step 2 of the pass *is* the frame audit |
| `system-prompt-skepticism.instructions.md` (Tenet IV) | Step 5 of the pass enforces Tenet IV by auditing priors |
| `critical-thinking.instructions.md` (Two-Hypothesis Floor) | Step 3 of the pass enforces the floor — alternatives with grounding |
| `act-pass.instructions.md` | Always-on trigger calibration: when to fire a full vs trimmed pass |
| `/act-pass.prompt.md` | User-invokable guided workflow |
| `audit-critical-thinking.cjs` | Detects this skill's existence as the Lane 1 falsifier |

## Background Reading

- ACT/ACT-MANIFESTO.md §4 — the operational pass and the worked example
- ACT/INCREDULITY-AS-METHOD.md §4 — the build-is-slow worked example in full
- ACT/PLAN-act-brain-integration.md Lane 1 — design rationale and falsifiability
- ACT/IMPLEMENTING-ACT-IN-ALEX.md — tenet → artifact map
