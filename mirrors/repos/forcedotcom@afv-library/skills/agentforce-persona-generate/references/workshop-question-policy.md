---
version: "1.0.0"
date: 2026-05-15
---

# Workshop Question Policy

Rules for generating stakeholder-facing questions in the WORKSHOP spoke. The skill produces these questions for a customer's internal stakeholders to answer **asynchronously** — not in a live workshop with the skill running. So the questions need to be open-ended, thought-provoking, scoped to what's actually unresolved, and respectful of stakeholder time.

## Guiding principle

**Quality over coverage. Better to ask 4 great questions than 12 generic ones.**

There is an infinite possible question set the framework could generate. Most of those questions are noise for any specific persona. The job here is identifying *what's actually unresolved or high-leverage* for *this* persona, given everything the skill already knows.

## Skip what you already know

The skill must NOT generate questions for things it already knows from the brand input, persona draft, or context. Stakeholder attention is the scarce resource.

**Examples of what to skip:**

- The brand input clearly says "always formal" → don't ask about Formality.
- The customer is a serious law firm → don't ask "How much humor?" (the answer is probably None and asking burns attention on a non-question).
- Channel is locked to telephony → don't ask "Should the agent use emoji?" (no formatting in audio).
- Personification is locked to Talking System → don't ask about character names.
- Identity is filled with strong-signal traits → don't ask the stakeholders to re-validate every adjective; pick one or two with productive tension.

This is harder than it sounds. The framework has 14 dimensions × 5+ persona artifacts × business context. Most could generate plausible questions. The skill must actively prune.

## What to ask about

In priority order:

1. **High up the dimensions ladder** — Identity, Personification, Register. These have the most leverage; getting them wrong cascades.
2. **Where confidence is low** — when a draft dimension was filled with a default rather than a strong signal, that's a candidate question.
3. **Where productive tension exists** — Tension Pairs in the framework (Cool Warmth + Bold Personality, Blunt Coloring + Playful Humor, etc.) are inherently questions stakeholders should weigh in on.
4. **Where the brand input is silent or contradictory** — e.g., the brand guide says "approachable" but doesn't say how much humor; that's worth asking.
5. **Where channel forces a tradeoff** — voice agents handling frustrated callers; humor in escalation flows.
6. **Where the use case raises a tone-flex question** — the framework's tone-flex triggers (system errors, content sensitivity, escalation) are stakeholder-relevant moments.

## What never to ask about

- Things the input or context already answers definitively.
- Things downstream of a higher decision already made (don't ask about emoji if Formal Register is locked — Formal pulls Emoji to None).
- Internal mechanics the stakeholders shouldn't be making decisions about (e.g., dimension constraint notes, tension-pair resolution rules).
- Anything that produces a "neutral default" answer — those questions waste stakeholder attention without changing the persona.

## Question styles

Three styles, picked per question based on what's needed:

### 1. Validate

Use when the skill has a strong-signal draft and wants stakeholder confirmation.

> "We assumed [X] from your brand guide. Confirm or push back."
> "The agent will speak in Coach register — instructive, takes a position. That fits the 'sales coach' framing in the brief. Right call?"

### 2. Choose between

Use when there are two genuinely different positions on a spectrum, with consequences spelled out.

> "When a customer expresses frustration, would you rather the agent (A) acknowledge the frustration before solving, or (B) skip to the solve? A reads as more empathetic; B reads as more efficient. Pick one."

The two options must be **meaningfully different**. Don't write false binaries where both options are the same with cosmetic differences. If you can't articulate the consequence of each choice, drop the question.

### 3. Open spectrum

Use when it's a blank slate — no signal in the input, and the stakeholders genuinely need to make the call.

> "Place the agent on this line: [Brisk] ⟷ [Languid]"
> "How much character should come through? [Talking System] ⟷ [Familiar Thing] ⟷ [Personal Assistant]"

These are dimension-card-shaped — print on a page, dot-vote, or place stickies on a FigJam board. Especially good for high-leverage dimensions (Identity, Personification, Register, Warmth) where the stakeholder team needs to converge.

## Output format constraints

The workshop outline is meant to be **lightweight and printable** — a FigJam board, a whiteboard, a Google Doc with sticky notes. Not a slide deck. Not a long-form persona document. The skill's job is to produce the outline; the customer's job is to run the workshop with it.

- Aim for 4-8 total questions per workshop outline. Fewer if the persona is well-grounded.
- Group questions by Activity (Identity calibration, Tone in difficult moments, Spectrum check) so the workshop has a clear arc.
- Pre-read materials section: link to or attach the brand-grounded persona draft and sample dialog so stakeholders walk in informed.
- Include a brief "Background" paragraph for the facilitator (≤1 paragraph) summarizing where the persona stands and what input is needed.

## Anti-patterns to refuse

- A 20-question workshop outline. If you're hitting 20, you haven't pruned.
- A workshop outline for a Talking System that asks "What kind of humor?" Skip. You know the answer.
- A workshop outline that asks every dimension "where on the spectrum?" — that's a coverage approach, not a leverage approach.
- A workshop outline where every option in a "choose between" pair reads as neutral or compromised. The job is to surface real tradeoffs, not to write safe choices.
