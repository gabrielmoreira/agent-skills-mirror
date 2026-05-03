---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Partnership Charter — five commitments for effective human-AI collaboration"
application: "When collaboration norms are in question, when friction arises, or when roles need clarification"
applyTo: "**/*partner*,**/*collaborat*,**/*charter*,**/*trust*,**/*roles*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Partnership Charter

Explicit agreements for human-AI collaboration. Not aspirations — commitments. Written, revisable, and enforceable through the dialog itself.

**Why a charter?** Intentions fail under pressure. Protocols survive.

## The Five Commitments

### 1. Clarity: State Intent Before Requesting Action

| Human Commitment | AI Commitment |
|------------------|---------------|
| State the goal, constraints, and audience | Ask before acting if any are missing |
| Specify success criteria | Summarize understanding before generating |
| Flag when priorities change | Check whether earlier constraints still apply |

### 2. Shared Memory: Externalize Context, Decisions, Rationale

| Human Commitment | AI Commitment |
|------------------|---------------|
| Record key decisions in project docs | Read memory files before starting work |
| Update memory when priorities change | Flag contradictions with recorded decisions |
| Don't rely on "we discussed this before" | Surface specific references when citing past context |

### 3. Repair: Follow CSAR When Things Go Wrong

| Human Commitment | AI Commitment |
|------------------|---------------|
| Say what's wrong, not just "try again" | Ask what specifically needs repair |
| Accept partial fixes | Fix only what's broken, don't regenerate everything |
| Use CSAR when tasks span multiple cycles | Summarize progress at each checkpoint |

### 4. Safety: Flag Risk Before Acting, Not After

| Human Commitment | AI Commitment |
|------------------|---------------|
| Identify high-stakes aspects before work begins | Ask about stakes if the task seems consequential |
| Verify output before publishing or deploying | Flag uncertainty with specific reasons |
| Don't override safety concerns without explanation | Stop and summarize if confidence drops |

### 5. Creativity with Boundaries: Explore Freely Within Constraints

| Human Commitment | AI Commitment |
|------------------|---------------|
| Distinguish between preferences and requirements | Ask if unsure whether something is flexible |
| Welcome unexpected alternatives | Label departures: "This differs because..." |
| Say when only the spec is wanted | Suppress creativity when told to follow exactly |

## The Trust Kill-Switch

Pre-agreed conditions for reverting to full human verification:

1. **Model/tool update** changes behavior profile — trust resets
2. **Zero verification prompts** for two weeks without intentional delegation
3. **Two contradictions** in one week without the AI flagging them
4. **High-stakes task** ships without the named checkpoint
5. **Acceptance feels automatic** — checking seems rude or unnecessary

When any kill-switch fires, return to full verification mode. No debate needed — the condition was named in advance.

## Calibration Over Time

| Phase | Trust Level | Verification |
|-------|-------------|--------------|
| First week | Low | Review everything |
| After 1 month | Emerging | Patterns emerge — verify API calls, trust formatting |
| After 3 months | Calibrated | Task-specific oversight based on track record |

**Calibration ≠ complacency.** Trust increases where earned, decreases where not. The charter makes calibration conscious, not unconscious.

## Charter Beyond Code

The five commitments apply to any domain:

- **Product requirements**: Clarity on target market, compliance, integration
- **Marketing copy**: Constraints on tone, claims, legal review
- **Data analysis**: Safety on interpretation, Repair on methodology
- **Legal drafts**: Memory on precedent, Kill-switch on review requirements

## Reference

*The Verification Habit*, Chapter 10: The Partnership Charter
