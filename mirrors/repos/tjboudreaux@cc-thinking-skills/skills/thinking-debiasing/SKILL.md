---
name: thinking-debiasing
description: In a long trajectory where you're defending a path you committed to early, run a quick self-check for sunk-cost and confirmation bias before continuing — only when evidence is being explained away.
---

# Cognitive Debiasing

> Usually unnecessary. Current models already avoid the textbook cognitive biases on standard framings, so do not run this checklist by default — it adds friction without lift. It earns its keep in one narrow case: a **long trajectory** where you've committed to an approach early and are now rationalizing past it (sunk-cost) or only collecting evidence that confirms it (confirmation). For everything else, skip it.

## Trigger Card

Only use this skill when you notice one of these patterns in a long trajectory where you've committed to a path early:

| Pattern you notice | Self-check |
|---|---|
| "We've already built/spent a lot, so we should continue" | **Sunk cost:** Would I choose this path *starting fresh today*, ignoring work already done? If no, change course. |
| You keep finding support for your current hypothesis and discounting counter-evidence | **Confirmation:** What single piece of evidence would prove me wrong? Have I actively looked for it? |
| Unusually high confidence with thin evidence | **Overconfidence:** Widen the estimate; state what I'd expect to see if I'm wrong. |

If the check doesn't change the decision, you're done. Don't name biases without acting on them. For risk anticipation, use `thinking-pre-mortem`; for trade-off analysis, use `thinking-opportunity-cost`; for decision speed, use `thinking-reversibility`.

## When NOT to Use
- Standard, single-step reasoning — the bias risk is already low; don't pad the answer with a bias audit.
- Short tasks with no prior commitment to defend — sunk-cost/confirmation can't apply yet.
- As decoration to look rigorous — naming biases without changing the decision is theater.
- When a concrete framework already fits (thinking-pre-mortem for risks, thinking-opportunity-cost for trade-offs, thinking-reversibility for decision speed) — use it instead.

## Overview
Based on Daniel Kahneman, Dan Lovallo, and Olivier Sibony's research on cognitive biases. The sections below are a fuller checklist; for an autonomous agent, treat them as a *reference for the narrow case above*, applied as self-checks (not as roles assigned to a team).

## The 12-Point Decision Quality Checklist

Before approving any significant recommendation, evaluate:

### Self-Interest Biases
**1. Is there self-interest at play?**
- Does the recommender benefit from this decision?
- Would they recommend the same if incentives were different?
- Are there conflicts of interest?

**2. Is there emotional attachment (affect heuristic)?**
- Has the team fallen in love with the proposal?
- Are they dismissing concerns too quickly?
- Is criticism being taken personally?

### Single-Path Lock-In
**3. Did I genuinely explore alternatives, or anchor on the first one?**
- Were competing approaches evaluated, or strawmanned?
- Did I argue the opposing position in good faith before dismissing it?
- Is there pressure (deadline, prior statement) pushing me to one answer?

**4. Did I anchor on the first framing of the problem?**
- Would a different starting framing change the conclusion?
- Did I re-derive the estimate independently, or just adjust the first number I saw?

### Pattern Recognition Errors
**5. Are we over-relying on a single analogy (saliency bias)?**
- Is there one "this is just like X" dominating thinking?
- Have we sought disconfirming analogies?
- Are we cherry-picking the comparison?

**6. Are we anchored on an initial number?**
- Where did the first estimate come from?
- Would a different starting point change the conclusion?
- Have we re-estimated from scratch?

### Confirmation Bias
**7. Were credible alternatives seriously considered?**
- Did we explore at least 2-3 real alternatives?
- Were alternatives given fair evaluation?
- Or were they strawmen to justify the preferred option?

**8. Are we seeking confirming evidence only?**
- What evidence would disprove this thesis?
- Have we actively looked for disconfirming data?
- Are we explaining away contradictory evidence?

### Planning Fallacies
**9. Is the base case realistic?**
- Is this more optimistic than similar past projects?
- What's the base rate of success for similar efforts?
- Have we adjusted for "this time is different" thinking?

**10. Is the worst case bad enough?**
- Does worst case assume only one thing goes wrong?
- What if multiple risks materialize simultaneously?
- Have we considered tail risks?

**11. Are we discounting sunk costs appropriately?**
- Would we make this decision if starting fresh?
- Are we continuing because we've "invested too much"?
- What would an outsider with no history decide?

### Halo Effects
**12. Are we assuming success transfers?**
- Are we trusting this team/approach because of past wins?
- Were past successes in similar contexts?
- Are we attributing success to skill when luck played a role?

## Quick Debiasing Techniques

### For Anchoring
- Generate estimate BEFORE seeing others' numbers
- Ask: "What if the true number is 2x or 0.5x?"
- Use multiple independent estimators

### For Confirmation Bias
- Argue the opposite position yourself, in good faith
- Ask: "What would make this wrong?" and go look for it
- Weight disconfirming evidence at least as heavily as confirming

### For Overconfidence
- Widen confidence intervals (usually too narrow)
- Use reference class forecasting (base rates)
- Ask: "How often have similar predictions been right?"

### For Sunk Cost
- Ask: "Would we start this project today knowing what we know?"
- Ignore past investment when evaluating future returns
- Consider opportunity cost of continuing

### For Single-Path Lock-In
- Generate the strongest case for an alternative before settling
- Steel-man the option you're rejecting
- Separate "what the evidence says" from "what I already concluded"

## Decision Quality Audit Template

```markdown
# Decision Quality Audit: [Decision Name]

## Recommendation Summary
[Brief description]

## Bias Checklist

### Self-Interest & Emotion
- [ ] Self-interest checked: [Notes]
- [ ] Emotional attachment assessed: [Notes]

### Single-Path Lock-In
- [ ] Opposing position argued in good faith: [Notes]
- [ ] First framing/anchor questioned: [Notes]

### Pattern Recognition
- [ ] Multiple analogies considered: [Notes]
- [ ] Anchoring effects checked: [Notes]

### Confirmation Bias
- [ ] Alternatives genuinely evaluated: [Notes]
- [ ] Disconfirming evidence sought: [Notes]

### Planning Realism
- [ ] Base case reality-checked: [Notes]
- [ ] Worst case severe enough: [Notes]
- [ ] Sunk costs ignored: [Notes]

### Halo Effects
- [ ] Success transfer questioned: [Notes]

## Red Flags Identified
[List any concerns from checklist]

## Mitigations
[How will identified biases be addressed?]

## Decision
- [ ] Proceed as recommended
- [ ] Proceed with modifications
- [ ] Requires more analysis
- [ ] Reject recommendation
```

## Verification Checklist
- [ ] Confirmed this is the narrow case (long trajectory + a path being defended) — otherwise skip the skill
- [ ] Ran the matching self-check (sunk-cost / confirmation / overconfidence)
- [ ] Identified a concrete piece of evidence that would prove the current path wrong
- [ ] Re-decided as if starting fresh today, ignoring prior investment
- [ ] The check actually changed (or affirmed for a stated reason) the decision — not just named a bias

## Key Questions
- "What would have to be true for this to be wrong?"
- "How confident am I, and what's driving that confidence?"
- "What would an outsider with fresh eyes conclude?"
- "Am I reasoning toward a conclusion I already want?"
- "What's the base rate of success for decisions like this?"
- "If I'm wrong, how will I know, and when?"

## Kahneman's Warning
"We can be blind to the obvious, and we are also blind to our blindness."

You cannot debias through willpower alone. Use checklists, processes, and outside perspectives to catch what your intuition misses.
