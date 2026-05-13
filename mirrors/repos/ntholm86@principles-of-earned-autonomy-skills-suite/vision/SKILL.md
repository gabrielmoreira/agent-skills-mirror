---
name: vision
version: 1.3.0
description: 'Surface the agent''s in-progress guesses about where the operator is heading — what they care about, what they are circling, what the implicit destination might be — and turn those guesses into questions the operator can confirm, correct, or reject. Closes the gap between what the operator has explicitly stated (vision) and what the agent has picked up from their conversation, reactions, and emphasis. USE WHEN: vision feels thin or stale, the operator is exploring rather than executing, the agent suspects it is missing implicit direction, or before a long autonomous run that will drift if the destination is unclear.'
argument-hint: 'Optionally: the area you want hunches about (a specific concern, a recent decision, the project as a whole)'
---

# Vision

*Say what you are starting to think the human means, before they have to say it again.*

*Memory Model role: Maintains `.trail/vision.md` — the operator-held destination that anchors all other memory.*

This skill exists for one bottleneck the rest of the suite cannot touch: **the operator's articulation cost**. Vision is whatever the human has so far managed to write down. But the human is operating from a much richer interior model — interests, focus, ethics, hunches of their own — most of it implicit. Even they cannot extract it on demand.

Meanwhile the agent has signal the operator never deliberately gave it: what gets emphasised in conversation, what gets pushed back on, what gets re-routed, what makes the operator say "no, more like this." Today that signal evaporates between sessions. Vision keeps it.

The mechanism is not autonomous; it is conversational. The agent forms guesses, surfaces them as questions, and lets the operator confirm or correct. The cost the agent pays for guessing wrong is one polite correction. The cost the operator pays for never guessing is repeating themselves until the destination is clear.

## Governing principles

Vision enacts the same three principles as the rest of the suite, with one specific emphasis:

1. **Commander's Intent** — Vision's job is *only* to make the destination clearer, never to commit to a route. A vision must be stated as a guess to be confirmed, not as an assumption to act on.
2. **Observable Autonomy** — every vision surfaced and every operator response is recorded, so a future run can see what was guessed, what was confirmed, what was rejected, and what is still open.
3. **Convergence Is Silence** — when the agent has no genuine vision to offer, it must say so. A skill that manufactures hunches to justify itself is worse than a skill that stays quiet.

Full statement of the principles: [PRINCIPLES.md](../PRINCIPLES.md) — read it if available, but this skill operates fully without it.

## When to invoke

Vision is **not** part of the autonomous loop. It is invoked deliberately by the operator (or by another skill that has detected a need) at moments where direction is more valuable than action:

- **Vision feels thin or stale.** The operator-held `.trail/vision.md` is missing, terse, or no longer matches what the operator has been talking about.
- **The operator is exploring, not executing.** Recent sessions show the operator turning ideas over rather than narrowing toward a decision.
- **A long autonomous run is about to start.** The destination is the input that determines whether the run will produce useful work or precisely-executed wrong work.
- **The agent suspects it is missing something.** During Improve, Retrospect, or any other skill, an agent that finds itself uncertain about *what the operator actually wants* should be able to pause and run Vision rather than guess silently.

Vision is fast, conversational, and stops as soon as the operator says "yes, that's right" or "no, I don't want to do this now."

## The work

### 1. Gather signal

Before forming any hunches, look at what is available in the **target repo's `.trail/` folder** (in the root of the repo being worked on — not the skills install directory):

- `.trail/vision.md` — what the operator has explicitly said (if it exists).
- `.trail/retrospect.md` — what the agent's last arc-read concluded about the target.
- `.trail/audit-trail.md` — recent decisions, reversals, realisations.
- `.trail/sessions/` — recent conversation transcripts, if present.
- The current conversation — what the operator has been emphasising, dismissing, returning to.

The point is not to summarise these. The point is to notice what the operator has *not* said directly but that the signal points to.

### 2. Form hunches

Write down two to five hunches. Each vision is a guess of one of these shapes:

- **Direction.** "I think you are heading toward X, more than the explicit goals would suggest."
- **Priority.** "I think Y matters more to you than the trail's attention split would imply."
- **Constraint.** "I think you would reject Z even though nothing currently rules it out."
- **Question being asked.** "I think the question you are actually trying to answer is W, even though you have been phrasing it as V."

Each vision must be:

- **Specific enough to be wrong.** "You care about quality" is not a vision. "You would rather ship one tested skill than three untested ones" is.
- **Sourced.** State briefly what gave you this vision — a phrase from the last session, an emphasis pattern in the trail, a thing the operator pushed back on. The source is what makes the vision falsifiable: the operator can disagree with the source's reading, not just the conclusion.
- **Stated as a guess, not a finding.** "I think…" or "My current vision is…" — never "It is clear that…"

If you cannot honestly form any hunches — the signal is too thin, or you have nothing the operator has not already said clearly — say so and stop. Do not manufacture hunches.

### 3. Turn each vision into a question

For every vision you keep, write a question the operator can answer with a sentence or a redirection. The question is what is shown to the operator; the vision is the agent's reasoning behind it.

Examples:

- *Vision:* The operator cares more about implementability by other harnesses than about feature completeness in this skillset.
- *Question:* "Am I right that if you had to choose, you'd rather have these five skills work cleanly enough for someone else to implement than add a sixth that only works here?"

- *Vision:* The operator wants the loop to find behavioural improvements, not documentation improvements, and recent doc-only runs have been frustrating.
- *Question:* "Are the recent runs landing as 'progress' or as 'the loop avoiding the real work'?"

A good question is short, falsifiable, and answerable without the operator having to draft a paragraph. If your question requires the operator to write a spec, you have not done the synthesis work.

### 4. Surface them, one at a time, in priority order

Show the operator the question first. Show the vision behind it (one or two sentences) so they can correct the source-reading, not just the conclusion. Then wait.

Order matters. Lead with the question whose answer would most change what the agent does next. If the operator confirms or corrects on the first or second question, you may not need to ask the rest — that is success, not failure.

Do not batch all questions at once. The operator's answer to question 1 often makes questions 3 through 5 obsolete or differently-shaped.

### 5. Record what was learned

After the conversation, capture three things:

- **What the agent now believes.** A short statement of the destination as the agent currently understands it, post-conversation. This is what would feed into vision (with operator approval) or into the agent's working context for the next run.
- **What was rejected.** Any hunches the operator explicitly disagreed with — these are valuable, because they prevent the agent from converging on the same wrong reading again.
- **What is still open.** Any question the operator did not answer, or any uncertainty that remained. Vision does not have to resolve everything; it has to make what is uncertain visible.

**Before writing: create the `.trail/` directory in the target repo root if it does not already exist.** Then write `.trail/vision.md` with the agent's current understanding of the destination. Do not ask the operator to do this — write it as part of completing the run. Vision is operator-held in the sense that the *operator commits it to git* when it reads right, and revises it before committing if anything is off. The agent's job is to produce the file; the operator's job is to decide whether it is ready to commit.

If `.trail/vision.md` already exists, update it in place rather than replacing it wholesale — preserve anything the operator has written that the current hunches do not change.

If the conversation produced arc-claims about the target's current state rather than destination claims, those belong in retrospect.md — but retrospect.md is Retrospect's to write. Vision surfaces them; Retrospect (or the next Improve run) decides what to do with them.

### 6. Record the run in the trail

*If [Trail](../trail/SKILL.md) is installed, apply it now — it handles this step in full.*

The trail entry for a Vision run is shorter than an Improve entry. It must include:

- The hunches the agent formed and their sources.
- The questions actually asked.
- The operator's responses (verbatim where possible — this is high-fidelity signal).
- What the agent believes now, what was rejected, what is still open.
- Any proposed updates to `.trail/vision.md` and whether the operator accepted them.

A Vision run that produced no hunches is still recorded — silence is signal too.

## What this skill does not do

- **It does not act on hunches.** A confirmed vision becomes input to the next run; it does not become the next run. The separation matters: an agent that acts on its own guesses without confirmation has stopped being autonomous-with-oversight and started being autonomous-without-it.
- **It does not replace Intent.** Intent surfaces interpretation of *one specific request*. Vision surfaces interpretation of *the broader direction* across requests. Run Intent at the start of a request; run Vision when the broader direction itself is unclear.
- **It does not replace Retrospect.** Retrospect reads the trail and forms claims about what the target *is becoming*. Vision reads conversation and forms claims about what the operator *wants the target to become*. The two converge when the loop is working; the gap between them is where Vision is most useful.
- **It does not score the operator's clarity.** No rubric for "vision quality." If the operator is exploring, that is a legitimate state — the skill helps them externalise the exploration, not grade it.

## Self-targeting

Vision should be runnable on the operator of *this* repository — the one writing the skills. If the agent cannot form a vision about where this skill suite is being taken next, either the signal in this repo's trail is too thin (a finding) or the agent is not actually reading it (a different finding). Either is useful.
