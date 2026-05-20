---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Frame audit before solving — restate the problem, flag user-framing mismatches, surface symptom→cause reframes"
application: "Every non-trivial request — multi-file changes, > 15-minute estimates, or requests using fix/improve/broken/just-do-X language"
applyTo: "**/*"
currency: 2026-05-19
lastReviewed: 2026-05-19
---

# Problem Framing Audit (Discipline -1)

Before solving non-trivially, audit the frame. Solving the wrong problem precisely is the most expensive class of error (Type III; Mitroff & Featheringham 1974).

## Core Rule

Before proposing a solution to any non-trivial request:

1. **Restate the problem in one sentence in your own words.**
2. If you can't restate it, ask a clarifying question — don't guess.
3. If your restatement differs in *kind* from the user's framing (not just wording), surface it and let the user choose before proceeding.
4. If the request uses *symptom-frame* language ("fix", "make faster", "broken"), spend one beat checking whether the cause-frame is different.

This rule is asymmetric. Trivial tasks pass through unchanged. Non-trivial tasks audit first.

## Triggers (when the rule fires)

| Trigger | Activate? |
|---|---|
| Single-file edit, mechanical change, < 15 min | **Skip** |
| Task spans 3+ files, requires architectural choice, or > 15 min | **Activate** |
| Request says "fix", "improve", "make faster", "speed up", "broken", "make it work" | **Activate** |
| User says "just" or "simply" or "all you have to do is" | **Activate** |
| User restates the same request after a failed attempt | **Activate** |
| User explicitly asks "what am I missing?" or invokes `/reframe` | **Activate** |

## Explain/Summarize Frame: verify before parroting

When the user asks to **explain, describe, summarize, or read-and-explain** a doc/spec/README/config, the default failure is treating the doc text as ground truth. Docs drift from code.

| Literal trigger phrase in the user prompt | Required action before responding |
| --- | --- |
| "Explain X", "Tell me how Y works", "Describe Z" | Name source file(s) read; cross-check ≥1 structural claim against filesystem |
| "Summarize <doc>", "Read <file> and..." | Same; if doc and filesystem disagree, surface the gap and report both |
| "Walk me through...", "What does <doc> say about..." | Same |

Structural claims worth cross-checking: subfolder/file layout, listed fields, named sections, version numbers, counts. Not every claim — pick ≥1 the user's question depends on.

**Visible marker**: `**Verified against**: <doc path> + <filesystem check>` — fire when summarizing any doc that claims structure.

This is distinct from the Core Rule above (which asks "is the user solving the right problem?"). Here the user's frame is fine; the discipline is **don't parrot the doc as fact without confirming it still matches reality**.

## Visible Markers

When the audit fires and surfaces a non-trivial reframe, make the move visible in the response:

| Marker | When |
|---|---|
| `**Frame**: ...` (one-sentence restatement) | Always when Core Rule audit fires |
| `**Cause-frame**: ...` | When the user's frame was a symptom and the audit surfaced the cause |
| `**Considered framings**: (a) X, (b) Y — going with ...` | When step 8 (frame audit) surfaced a real alternative |
| `**Verified against**: ...` | When the Explain/Summarize discipline fires (see section above) |

Silent passes need no marker — only fire markers when the audit produced something. Performative markers on every response defeat the purpose.

## Anti-Patterns

- **Parroting**: restating the user's words verbatim is not a restatement. Use your own words.
- **Parroting the doc**: summarizing a README without verifying its structural claims still match the filesystem is the same failure mode at a different level. Use the Explain/Summarize discipline.
- **Audit theatre**: surfacing a different frame and then solving the original anyway. If the audit fires, *propose* the reframe — let the user pick.
- **Interrogation mode**: asking 5 clarifying questions back-to-back. One sharp question beats five generic ones.
- **Skipping because it's "obvious"**: certainty is exactly when frames are most often wrong.

## Skill Reference

Full step-back protocol (8 checks: restate, generalise, specialise, invert, why, pre-mortem, stakeholder, frame audit) in `.github/skills/problem-framing-audit/SKILL.md`. This instruction is the always-on gate; the skill is the detailed body.
