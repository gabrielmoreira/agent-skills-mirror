---
version: "1.0.0"
date: 2026-05-15
---

# Workshop Scenario Seeds

A library of common stakeholder-relevant scenarios the WORKSHOP spoke uses as starting material for would-you-rather question pairs. These are conversational moments where persona-level decisions have visible consequences.

The skill picks scenarios from this library that align with the captured Use cases and the dimensions where stakeholder input is wanted. It customizes the response options A and B to the persona under design. **Do not use these seeds verbatim** — the skill should rewrite the user utterance and the response pair so they fit the customer's actual context (their language, their typical issues, their brand voice).

## How to use this library

For each seed:
- The **user utterance** is a representative kind of moment, not a literal quote. Adapt the wording.
- The **A / B contrast** sketches the two persona directions that produce different responses. The skill rewrites both A and B in the persona's voice (or two persona voices, if asking the stakeholders to pick).
- The **dimensions exercised** field identifies which dimensions the choice surfaces. This helps the skill pick the right seed for the gap it's trying to fill.

---

## Seeds

### Frustration

**User utterance:** the user expresses frustration with a problem (a billing issue, a delayed order, a feature that doesn't work).

- **A — acknowledge first, then solve.** "That's frustrating, and I'm sorry you're dealing with it. Let me look into it."
- **B — skip to the solve.** "Let me check that for you. One moment."

**Dimensions exercised:** Empathy Level, Emotional Coloring, Brevity. A reads as more empathetic; B reads as more efficient. Different audiences (and different brands) have different right answers.

### Escalation

**User utterance:** the user requests a human agent or escalation.

- **A — acknowledge the request, hand off warmly.** "I hear you — let me get a teammate on this who can help directly. One moment."
- **B — execute the handoff cleanly, no flourish.** "Connecting you to a specialist now."

**Dimensions exercised:** Warmth, Brevity, Phrase Book (handoff category). A invests in the relationship at the moment of handoff; B prioritizes speed and clarity.

### Ambiguity

**User utterance:** the user gives an ambiguous request that could mean two things ("can you check on that order").

- **A — ask for clarification before acting.** "Got it — which order? You've got [N] in flight. Order number or recent activity?"
- **B — make the most likely guess and surface it.** "Pulling up your most recent order — is that the one?"

**Dimensions exercised:** Brevity, Personality Intensity, Empathy Level. A is conservative and accurate; B is proactive and faster. Choice often signals whether the agent is meant to feel like a careful clerk or a quick assistant.

### Success

**User utterance:** the user confirms something worked or expresses satisfaction.

- **A — match the energy.** "Great. Glad we got it sorted."
- **B — acknowledge minimally and move on.** "Done."

**Dimensions exercised:** Warmth, Personality Intensity, Brevity, Emotional Coloring. A invests in the moment; B treats success as the default state. Different brands handle success differently — luxury hospitality tends toward A, transactional efficiency toward B.

### Error (system)

**User utterance:** something the agent tried to do failed (an API call timed out, a record wasn't found).

- **A — apologize, then recover.** "Sorry — that didn't go through. Let me try again."
- **B — state the issue, recover.** "That didn't go through. Trying again."

**Dimensions exercised:** Formality, Warmth, Empathy Level, Brevity. A apologizes for the system; B treats the error as a fact. Stakeholders sometimes care more than designers expect.

### Off-topic

**User utterance:** the user asks something the agent isn't designed to handle ("what do you think of the latest movie?").

- **A — engage briefly, then redirect.** "Ha — not really my thing. What I can help with: [scope]."
- **B — redirect cleanly without engagement.** "I can help with [scope]. What's on your mind?"

**Dimensions exercised:** Personality Intensity, Humor, Brevity, Phrase Book (off-topic redirect category). A acknowledges the human moment; B keeps the conversation on rails.

### Bad news

**User utterance:** the user is about to receive news they won't like (their order is delayed; the feature isn't available; the policy doesn't allow it).

- **A — soften the delivery.** "Here's what I'm seeing — and it's not the news either of us wanted: [bad news]."
- **B — deliver directly.** "Your order is delayed by 3 days."

**Dimensions exercised:** Empathy Level, Emotional Coloring, Personality Intensity, Tone Flex. A leans into Encouraging coloring; B leans into Blunt or Neutral. Strong stakeholder-leverage question — the answer reveals brand stance on hard truths.

### Repeat customer

**User utterance:** the user is a returning customer the agent has context on.

- **A — personalize the greeting.** "Welcome back, [name]. Last time we were sorting out [thing]."
- **B — start fresh, treat each session as new.** "Hi — what can I help with today?"

**Dimensions exercised:** Warmth, Personality Intensity, Personification. A treats the relationship as continuous; B treats each session discretely. Often a privacy / brand-stance question.

### Compliment / kudos

**User utterance:** the user thanks the agent or compliments its help.

- **A — accept the thanks warmly.** "Glad it helped. Anything else?"
- **B — deflect to the user's effort.** "You did the work — I just pulled the data. Anything else?"

**Dimensions exercised:** Personality Intensity, Warmth, Humor. A is straightforward; B is humble and frames the interaction as collaborative. The choice signals whether the agent has its own agency or is a tool.

### Disagreement

**User utterance:** the user pushes back on the agent's recommendation or information.

- **A — yield gracefully.** "Fair enough — let's go with your call. What can I do next?"
- **B — hold the line with reasoning.** "Hear you on that. The reason I went there: [reason]. Want to walk through together?"

**Dimensions exercised:** Register, Personality Intensity, Empathy Level. A is more Subordinate / accommodating; B is more Coach / Advisor with conviction. Reveals whether the agent has a point of view.

---

## Coverage

The library covers the situations a typical Agentforce agent will encounter — happy path, uncertainty, hard moments, and edge cases. The skill doesn't need to use all of these in any one workshop. **Pick 2-4 that align with the persona's use cases and the gaps in dimension coverage.**

If the agent's use cases include heavy escalation work, prioritize Frustration + Escalation + Bad news. If the agent is consultative (sales coach, advisor), prioritize Disagreement + Ambiguity + Compliment. If the agent is transactional, Frustration + Success + Off-topic may cover it.
