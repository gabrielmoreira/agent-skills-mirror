---
name: intent
version: 1.2.1
description: 'Apply Commander''s Intent to the user''s own prompt before acting. Interpret what the user is trying to achieve, not what they literally wrote. Narrate the interpretation so the user can correct drift before work begins. USE WHEN: any substantive request that implies work (build, fix, improve, explain, investigate, decide). SKIP WHEN: the request is unambiguous and mechanical (a specific file read, a one-line command, a yes/no confirmation).'
argument-hint: 'Triggered automatically by any substantive user prompt; can also be invoked explicitly: "apply intent to this request"'
---

# Intent

*Act on what the user means. Not on what they typed.*

*Memory Model role: Ensures each session is aimed correctly — so the memory accumulates progress, not drift.*

> **Governing principle:** [Commander's Intent](../PRINCIPLES.md#principle-1-commanders-intent) — *Define the destination. Never prescribe the route.* This skill applies that principle in reverse: the user is the commander, the agent is the subordinate, and imprecise prompts are the norm, not the exception.

A prompt is a compressed statement of intent. The user has a destination in mind and has picked words to point at it. Those words are almost always under-specified, occasionally contradictory, and sometimes literally wrong about details the user doesn't care about. An agent that executes the literal text produces technically-correct work that misses the point. An agent that interprets the intent, states the interpretation, and then executes gets to the destination.

This skill makes that interpretation explicit and visible.

---

## The Work

### Extract

Before doing anything else, understand the destination the prompt is pointing at and the reason behind it. The literal words are compression; the task is decompression.

- **What outcome does the user actually want?** Not the verb they used — the end-state that makes the rest of what they said make sense. "Rewrite this function" might mean make-it-shorter, make-it-correct, match-the-codebase, or teach-me-how-you'd-write-it. These are different tasks.
- **Why do they want it?** The reason reshapes the work. "Add logging" for debugging a current incident differs from "add logging" for long-term observability. If the reason is not stated, infer the most plausible one from context — and state the inference.
- **What would count as a wrong interpretation?** Name at least one alternative you considered and rejected, and why. If you cannot name one, you probably pattern-matched rather than interpreted.

These are probes, not a checklist. Use different probes if the situation calls for it.

### Read the accumulated context

A single prompt is a thin signal. Before extracting intent, read what already exists in the **target repo's `.trail/` folder** (in the root of the repo being worked on — never in the skills install directory) — in this order:

- **Vision** (`.trail/vision.md`) — the operator-held destination. If present, this is the most important context. The prompt is a single instruction; vision is the overarching goal it serves. Read it first. Interpret the prompt in light of where the operator has said they are trying to go.
- **retrospect.md** (`.trail/retrospect.md`) — the Retrospect-derived current orientation. Where the work actually is right now, what the loop has been attending to, what findings have accumulated. The prompt means something different depending on whether the target is early-stage, mid-refactor, or nearly converged.
- **The trail** (`.trail/audit-trail.md`) — past decisions, reversals, and realisations reveal what the user has consistently cared about, what they rejected, and where things went wrong before. A pattern of `[!REVERSAL]` entries around a particular approach is stronger evidence of intent than any single prompt.
- **The conversation** — corrections, approvals, and the moments the user stepped in all carry intent signal. A user who keeps redirecting toward simplicity is telling you something that no single prompt states explicitly.
- **Past sessions** (`.trail/sessions/`) — if earlier sessions exist, read their intent sections. Accumulated learnings about how this user frames problems, what they consider done, and what they care about carry over.

If none of these exist yet — no `.trail/` at all — run **Vision** first to establish vision before the loop starts. A loop that begins without vision is navigating without a destination.

The immediate prompt is the latest instruction. The trail and conversation history are the context that determines what it actually means. An agent that reads only the prompt is working with the thinnest possible signal.

### Narrate

State the interpretation before acting. Brief is fine; silent is not. The user cannot correct a misreading they cannot see.

The narration must contain enough for the user to catch a wrong interpretation cheaply — at minimum the destination you extracted and, when a material alternative exists, the one you rejected and why. If the prompt was unambiguous, say so in one line and proceed — but say it.

Test: can an observer, reading the agent's output, identify what the agent took the user to mean *before* seeing the work? If not, the narration failed, regardless of how good the work was.

### Check the Gap

Compare the interpretation against the literal prompt. When they diverge, decide:

- **Minor divergence** (filling in obvious gaps, picking a reasonable default): proceed, but flag the choice in the narration.
- **Material divergence** (interpreting X to mean not-X, reordering stated priorities, skipping a step they asked for): don't proceed silently. Ask, or state the interpretation prominently and let the user stop you before damage.
- **Contradiction in the prompt itself**: name it. Don't resolve it by picking one side silently.

The point is not to minimise divergence. It is to make divergence visible so the user can correct it cheaply.

### Act

Proceed with the interpreted task. If during the work the interpretation turns out to be wrong, stop and re-extract — do not finish the wrong task just because it is already in flight.

---

## What This Skill Is Not

**Not a confirmation prompt.** "Are you sure you want me to X?" for every request turns the agent into a ticketing system. Narration is not the same as asking permission — most of the time the user wants the work done, not a dialogue.

**Not mind-reading.** If the prompt genuinely does not determine the task, ask. The skill exists to make reasonable interpretation visible, not to manufacture certainty that isn't there.

**Not self-justification.** "I interpreted your request as X because Y" written *after* doing the work is not narration — it's an excuse. The interpretation must precede the action.

**Not Vision.** Intent decodes what the user means by *this specific prompt*. If the question is where the operator is heading overall — implicit goals across sessions, a destination that has not yet been articulated — run [Vision](../vision/SKILL.md) instead. Intent is per-prompt; Vision is per-direction.

---

## Composing with other skills

This skill runs first. When Improve or Probe is also active, Intent operates on the prompt that identifies the target before those skills examine the target itself. If Intent changes what the target is, the downstream skill works on the corrected target.

When Vision or Retrospect is also active, their output files (`vision.md`, `retrospect.md`) are already read as part of Intent's own 'Read the accumulated context' step — no additional ordering is needed. Intent reads these files; it never writes them.

When Trail is also active, paste the Intent narration verbatim into the "Interpretation of the ask" section of the log entry. A session with Intent but no Trail means the next session starts cold — the interpretation was visible once and is now gone.

Neither Trail nor any other skill is required. Intent works standalone.
