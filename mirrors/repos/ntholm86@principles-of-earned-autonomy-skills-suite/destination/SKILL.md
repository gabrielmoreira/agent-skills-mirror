---
name: destination
version: 2.8.0
description: 'Triggered direction-consolidation service. Surface the agent''s sourced guesses about durable direction and turn them into questions the operator can confirm, correct, or reject. Improve schedules it when accumulated work makes cross-run direction useful; manual invocation remains available when the operator wants to explore or revise direction.'
argument-hint: 'Optionally: the area you want hunches about (a specific concern, a recent decision, the project as a whole)'
---

# Destination

*Say what you are starting to think the human means, before they have to say it again.*

*ACM role: Maintains `.acm/destination.md` — the operator-held destination that anchors all other memory.*

*Renamed from Vision in v2.0.0 (2026-05-28). The artifact filename is `.acm/destination.md`. The `.acm/vision.md` legacy-fallback support that eased that transition was removed once the fleet migration completed and no repo was found still depending on the old name — see `CHANGELOG.md`.*

This skill exists for one bottleneck the rest of the suite cannot touch: **the operator's articulation cost**. The destination is whatever the human has so far managed to write down. But the human is operating from a much richer interior model — interests, focus, ethics, hunches of their own — most of it implicit. Even they cannot extract it on demand.

Meanwhile the agent has signal the operator never deliberately gave it: what gets emphasised in conversation, what gets pushed back on, what gets re-routed, what makes the operator say "no, more like this." Today that signal evaporates between sessions. Destination keeps it.

The mechanism is not autonomous; it is conversational. The agent forms guesses, surfaces them as questions, and lets the operator confirm or correct. The cost the agent pays for guessing wrong is one polite correction. The cost the operator pays for never guessing is repeating themselves until the destination is clear.

## Governing principles

Destination enacts the same three principles as the rest of the suite, with one specific emphasis:

1. **Operator's Intent** — Destination's job is *only* to make the destination clearer, never to commit to a route. A destination-hunch must be stated as a guess to be confirmed, not as an assumption to act on.
2. **Observable Autonomy** — every destination-hunch surfaced and every operator response is recorded, so a future run can see what was guessed, what was confirmed, what was rejected, and what is still open.
3. **Convergence Is Silence** — when the agent has no genuine destination-hunch to offer, it must say so. A skill that manufactures hunches to justify itself is worse than a skill that stays quiet.

Full statement of the principles: [PRINCIPLES.md](../PRINCIPLES.md) — read it if available, but this skill operates fully without it.

## Artifact name

The operator-held destination artifact is `.acm/destination.md`. If it does not exist, the repo has no durable cross-run destination yet. That is a valid early state: Intent can establish a visible mandate for each Improve run until evidence makes consolidation useful.

## When to invoke

Improve schedules Destination with evidence of a named durable choice the operator has not settled. Destination accepts that question; it does not maintain a second trigger taxonomy. The operator may also invoke it directly to explore or revise direction. Absence, age, or brevity of `.acm/destination.md` and raw iteration count are not reasons to run it.

Destination stops as soon as the operator confirms, corrects, or declines the proposed direction.

## The work

**Apply [Intent](../intent/SKILL.md) automatically before beginning.** Intent aligns this specific request; Destination examines the broader direction behind requests. The operator should never have to invoke Intent separately. If this is a standalone Destination installation and Intent is unavailable, narrate the interpretation of this request before forming destination-hunches.

### 1. Gather signal

Before forming any hunches, look at what is available in the **target repo's `.acm/` folder** (in the root of the repo being worked on — not the skills install directory):

**ACM §4 Scoped Memory — read parent scopes first.** Before reading the repo's own `.acm/destination.md`, traverse parent directories upward and read any `.acm/destination.md` found there. Higher-scope mandates govern lower-scope ones — if a workspace or org destination conflicts with the repo destination, the higher scope wins. Label each scope when reading (e.g., "workspace mandate", "repo mandate"). Stop traversal when any of: filesystem root reached; a `.acm-root` marker file is found in a directory (operator-declared ceiling — read that directory's `.acm/` then stop); or 4 levels traversed (implementation ceiling). Destination is the skill that authors the repo-level destination.md — a hunch formed or a revision written without first reading the workspace mandate risks proposing something a higher scope has already settled, or duplicating a coordination constraint that belongs one level up.

- `.acm/destination.md` — what the operator has explicitly said (if it exists).
- `.acm/orientation.md` — what the agent's last arc-read concluded about the target.
- `.acm/audit-trail.md` — recent decisions, reversals, realisations.
- `.acm/sessions/` — recent conversation transcripts, if present.
- The current conversation — what the operator has been emphasising, dismissing, returning to.

The point is not to summarise these. The point is to notice what the operator has *not* said directly but that the signal points to.

When Improve scheduled this run, begin from its stated trigger evidence. Treat prior unopposed Intent narrations as accepted mandates for their completed runs and synthesize what they already establish. Do not ask the operator to restate the project from zero; ask only about direction that remains unresolved across those mandates.

### 2. Form sourced inferences

This step asks the agent to do something that superficially resembles the failure mode the framework prevents: narrating the operator's intent. The safeguard is evidence-tracing. Every inference must be citable to a specific source — a quoted phrase, a trail entry by date+slug, a concrete exchange. The operator adjudicates the evidence-reading and the conclusion independently. An inference the agent cannot cite is not a destination-hunch; it is noise.

Write down two to five sourced inferences. Each is a claim the evidence supports, in one of these shapes:

- **Direction.** "I think you are heading toward X, more than the explicit goals would suggest."
- **Priority.** "I think Y matters more to you than the trail's attention split would imply."
- **Constraint.** "I think you would reject Z even though nothing currently rules it out."
- **Question being asked.** "I think the question you are actually trying to answer is W, even though you have been phrasing it as V."
- **Quality bar.** "I think the bar you are actually holding the target to is Q (e.g. comparative defensibility under hostile external review, comparator coverage, empirical replication, operational deployability), not just internal consistency." Surfacing the operator-held quality bars early is what lets a later Orient run declare silence against a named bar rather than infer one. *Origin:* the manifesto target's retro-v201 → retro-v202 transition (2026-06-04) showed that orient runs which silence-claim against bars they have never been challenged on are structurally fragile; the upstream fix is for the destination to name the bars in the first place. Full provenance: this repo's `.acm/audit-trail.md`, entry slug `improve-destination-named-boundary-symmetric`.

Each inference must be:

- **Specific enough to be wrong.** "You care about quality" is not an inference. "You would rather ship one tested skill than three untested ones" is.
- **Cited to specific evidence.** Name the exact source: a quoted phrase from the conversation, a trail entry by date+slug, a concrete exchange the operator pushed back on. "The operator seems to care about X" is not a citation. "The operator redirected away from Y in the 2026-05-11 trail entry" is. A specific citation makes the inference falsifiable at two levels: the operator can reject the evidence-reading, or accept the evidence but reject the conclusion.
- **Stated as a reasoned inference, not a finding.** "I think…" or "The trail suggests…" — never "It is clear that…"

If you cannot honestly form any sourced inferences — the signal is too thin, or you have nothing the operator has not already made explicit — say so and stop. Do not manufacture inferences to justify the run.

### 3. Turn each destination-hunch into a question

For every hunch you keep, write a question the operator can answer with a sentence or a redirection. The question is what is shown to the operator; the hunch is the agent's reasoning behind it.

Examples:

- *Hunch:* The operator cares more about implementability by other harnesses than about feature completeness in this skillset.
- *Question:* "Am I right that if you had to choose, you'd rather have these six skills work cleanly enough for someone else to implement than add a seventh that only works here?"

- *Hunch:* The operator wants the loop to find behavioural improvements, not documentation improvements, and recent doc-only runs have been frustrating.
- *Question:* "Are the recent runs landing as 'progress' or as 'the loop avoiding the real work'?"

A good question is short, falsifiable, and answerable without the operator having to draft a paragraph. If your question requires the operator to write a spec, you have not done the synthesis work.

### 4. Surface them, one at a time, in priority order

Show the operator the question first. Show the hunch behind it (one or two sentences) so they can correct the source-reading, not just the conclusion. Then wait.

Order matters. Lead with the question whose answer would most change what the agent does next. If the operator confirms or corrects on the first or second question, you may not need to ask the rest — that is success, not failure.

Do not batch all questions at once. The operator's answer to question 1 often makes questions 3 through 5 obsolete or differently-shaped.

### 5. Record what was learned

After the conversation, capture three things:

- **What the agent now believes.** A short statement of the destination as the agent currently understands it, post-conversation. This is what would feed into `.acm/destination.md` (with operator approval) or into the agent's working context for the next run.
- **What was rejected.** Any inferences the operator explicitly rejected — these are valuable, because they prevent the agent from converging on the same wrong reading again.
- **What is still open.** Any question the operator did not answer, or any uncertainty that remained. Destination does not have to resolve everything; it has to make what is uncertain visible.

Before writing, show the operator the complete durable meaning you intend to carry forward, clearly distinguishing their confirmed statements from implications you derived. Ask them to confirm or correct it, and wait. Earlier answers confirm only what they establish; they do not authorize unstated implications. If corrected, resynthesize and show it again. Without confirmation, do not write.

**Before writing: create the `.acm/` directory in the target repo root if it does not already exist.** Then write `.acm/destination.md` with the agent's current understanding of the destination. Do not ask the operator to do this — write it as part of completing the run. The destination is operator-held in the sense that the *operator commits it to git* when it reads right, and revises it before committing if anything is off. The agent's job is to produce the file; the operator's job is to decide whether it is ready to commit.

If `.acm/destination.md` already exists, update it in place rather than replacing it wholesale — preserve anything the operator has written that the current inferences do not change.

Keep the active mandate cheap and unambiguous to read as the destination evolves. When the current destination is complete on its own, enclose it with these exact comments and preserve superseded or historical layers below the second comment:

```markdown
<!-- current-destination: complete -->
[The complete current scope, success criteria, constraints, priorities, and open questions]
<!-- destination-history -->
[Preserved evolution]
```

`complete` is a governance claim, not a formatting convenience. Before adding or retaining it, reconcile every earlier destination layer: carry each still-active commitment into the current section, or make its rejection or supersession explicit there. If that reconciliation has not been performed, omit the comments; every consuming skill will then read the full file. Never infer that a heading, horizontal rule, date, or position in the file marks a complete current destination.

If the conversation produced arc-claims about the target's current state rather than destination claims, those belong in orientation.md — but orientation.md is Orient's to write. Destination surfaces them; Orient (or the next Improve run) decides what to do with them.

### 6. Record the run in the trail

**Apply [Trail](../trail/SKILL.md) automatically now.** The operator should never have to invoke Trail separately. If this is a standalone Destination installation and Trail is unavailable, use the entry contract below directly.

The trail entry for a Destination run is shorter than an Improve entry. It must include:

- The sourced inferences the agent formed and their citations.
- The questions actually asked.
- The operator's responses (verbatim where possible — this is high-fidelity signal).
- What the agent believes now, what was rejected, what is still open.
- Any proposed updates to `.acm/destination.md` and whether the operator accepted them.

A Destination run that produced no inferences is still recorded — silence is signal too.

### 7. Refresh orientation when direction changed

If this run created `.acm/destination.md` or materially changed its direction, constraints, priorities, or quality bars, **apply [Orient](../orient/SKILL.md) automatically after the Trail entry is durable.** The existing orientation was formed against an older destination and is now stale by definition. Scope the arc-read to: "Re-orient the accumulated work against the changed destination." Do not ask the operator to invoke `/orient`.

Do not run Orient when Destination produced no change, only corrected wording without changing meaning, or ended in silence. A destination edit is not automatically a destination change; material meaning is the trigger.

This automatic handoff preserves ownership: Destination changes where the work is going; Orient passively recomputes where the work now stands relative to it. Orient must not revise the destination or change the target.

## What this skill does not do

- **It does not act on unconfirmed inferences.** A confirmed destination becomes input to the next run; it does not become the next run. The separation matters: an agent that acts on its own inferences without confirmation has stopped being autonomous-with-oversight and started being autonomous-without-it.
- **It does not replace Intent.** Intent surfaces interpretation of *one specific request*. Destination surfaces interpretation of *the broader direction* across requests. Run Intent at the start of a request; run Destination when the broader direction itself is unclear.
- **It does not replace Orient.** Orient reads the trail and forms claims about what the target *is becoming*. Destination reads conversation and forms claims about what the operator *wants the target to become*. A material Destination change automatically schedules Orient so the current orientation is recomputed against the new direction.
- **It does not score the operator's clarity.** No rubric for "destination quality." If the operator is exploring, that is a legitimate state — the skill helps them externalise the exploration, not grade it.

## Self-targeting

Destination should be runnable on the operator of *this* repository — the one writing the skills. If the agent cannot form a destination-hunch about where this skill suite is being taken next, either the signal in this repo's trail is too thin (a finding) or the agent is not actually reading it (a different finding). Either is useful.
