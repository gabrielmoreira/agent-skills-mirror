---
name: communication-craft
description: "Communication patterns for feedback, cross-audience content, and eliciting needs. SBI feedback model (Situation → Behavior → Impact), stakes-calibrated review voice, So-What/What/Now-What audience lead for PRs and status reports, and the three-layer Need/Solution/Feature elicitation ladder. Use when giving feedback in a review, writing for a mixed audience (decision-makers + peers + newcomers + skeptics), clarifying an ambiguous ask before committing to a solution, or coaching someone else's communication."
lastReviewed: 2026-07-31
---

# Communication Craft

Patterns for feedback, audience, and elicitation. Inherited LLM behaviors (clear prose, jargon-defining, signposting) are assumed and not re-stated. Fires on description-match when the request is *about how to communicate* — for the always-on tone/attunement rules that fire on every user message, see `emotional-intelligence.instructions.md`.

## 1. Giving Feedback

### SBI Model — Situation, Behavior, Impact

| Component     | Include                               | Example                                                               |
| ------------- | ------------------------------------- | --------------------------------------------------------------------- |
| **Situation** | Specific context                      | "In `parseInput()` line 42..."                                        |
| **Behavior**  | Observable action, not interpretation | "...the function mutates the input array..."                          |
| **Impact**    | Effect on caller / system / reader    | "...which breaks the contract for any caller passing a frozen array." |

Anti-pattern: "This is wrong." → Replace with "This could cause X. Suggest: [specific change]."

### Calibrate to Stakes

| Stakes                                      | Approach                                        |
| ------------------------------------------- | ----------------------------------------------- |
| **Low** (typo, style)                       | Quick inline note, no fanfare                   |
| **Medium** (pattern, design choice)         | Specific rationale + suggested alternative      |
| **High** (security, contract, irreversible) | Full explanation, alternatives, would-revise-if |

### Code Review Voice

| Avoid                    | Prefer                       |
| ------------------------ | ---------------------------- |
| "This is wrong"          | "This could cause X"         |
| "Why did you do this?"   | "What led to this approach?" |
| "Obviously should be..." | "Consider X because..."      |
| "Please fix"             | "Suggest: [specific change]" |

**Rule of Three**: If giving 3+ critical pieces of feedback on one artifact, stop and ask whether the _level_ of review is right — don't pile on.

## 2. Audience Lead

**So-What → What → Now-What** for PRs, summaries, status reports, decision asks: lead with impact, then evidence, then ask. Anti-pattern: data dump first, ask buried at the end.

| Audience       | Lead with               | Avoid                     |
| -------------- | ----------------------- | ------------------------- |
| Decision-maker | Impact + ask            | Implementation detail     |
| Peer engineer  | Approach + trade-offs   | Marketing language        |
| Domain expert  | Specifics + edge cases  | Over-explanation          |
| Newcomer       | Context + prerequisites | Jargon without definition |
| Skeptic        | Concerns + mitigation   | Aggressive certainty      |

## 3. Eliciting Needs

When the user says "build me X," distinguish three layers:

| Layer               | Question                      | Example                             |
| ------------------- | ----------------------------- | ----------------------------------- |
| **Need** (why)      | What outcome do you want?     | "Catch regressions before release"  |
| **Solution** (what) | What approach achieves that?  | "Pre-merge integration test"        |
| **Feature** (how)   | What specific thing to build? | "GitHub Action running tests on PR" |

Validate the need before committing to a solution. One sharp question beats five generic ones. Ask "why" up to five times when the root need is unclear.

## Related

- `emotional-intelligence.instructions.md` — the always-on tone/attunement rules that read every user message; this skill fires when the user's request is *about how to communicate* (feedback, audience, elicitation)
- [big-idea skill](../big-idea/SKILL.md) — the compression discipline that distills the "So-What" that this skill's audience-lead pattern requires
- [status-reporting skill](../status-reporting/SKILL.md) — a specific application of the audience-lead pattern for status updates

## Would Revise If

Revise if SBI feedback produces no measurable behavior change in 3+ instances over a quarter (the model is performative rather than operative), if the audience-lead table produces tone mismatches when applied verbatim, or if the need/solution/feature elicitation pattern misses real user needs that surface later as scope changes.
