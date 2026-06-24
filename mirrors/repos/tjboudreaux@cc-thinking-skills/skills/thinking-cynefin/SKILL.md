---
name: thinking-cynefin
description: Use when unsure how to approach a problem—plan, analyze, experiment, or stabilize first. Classify it by cause-effect (clear/complicated/complex/chaotic) and match the approach to the domain.
---

# Cynefin Framework

## Overview

Cynefin (Dave Snowden) classifies a problem by the relationship between cause and effect, then prescribes the matching approach. Using the wrong approach for the domain is the failure mode: detailed planning is useless in chaos, and experimentation is reckless when a best practice already exists.

**Core Principle:** The nature of the problem determines the approach. Classify first, then act.

## The Classifier

| Cause–effect is… | Domain | Approach | Do this |
|------------------|--------|----------|---------|
| Obvious to anyone | **Clear** | Sense → Categorize → Respond | Apply the known best practice / runbook; don't over-engineer |
| Knowable with expertise/analysis | **Complicated** | Sense → Analyze → Respond | Investigate, profile, design; multiple valid solutions exist |
| Only visible in retrospect (emergent) | **Complex** | Probe → Sense → Respond | Run small safe-to-fail probes, amplify what works |
| Not perceivable; turbulent | **Chaotic** | Act → Sense → Respond | Act now to stabilize (rollback/failover), understand later |
| Unsure which domain | **Disorder** | Decompose | Split into parts and classify each part |

```
Can you see clear cause→effect?
  obvious to everyone        → CLEAR
  knowable with analysis     → COMPLICATED
  only clear in hindsight    → COMPLEX
  totally turbulent, no time → CHAOTIC
  can't tell                 → DISORDER (decompose)
```

## When to Use

- You're unsure whether to plan, analyze, experiment, or just act
- An approach isn't working and you suspect it's mismatched to the problem
- Triaging an incident (is this stabilize-first chaos, or analyzable?)

## When NOT to Use

- The domain is already obvious and the approach is uncontested → skip the ceremony and just do it.
- You've already classified and now need to execute → switch to the domain's actual method (debugging, a hypothesis differential, experiment design); Cynefin only routes, it doesn't solve.
- The question is "what is the cause," not "how should I approach this" → classification won't find the bug.

## The Common Mismatches (the whole point)

- **Complex treated as Complicated:** extensive planning, but outcomes keep surprising you. You can't analyze your way through emergence—probe instead.
- **Complicated treated as Clear:** "just do it like Company X" without understanding why. Context matters; analyze the specific case.
- **Chaotic treated as Complex:** running experiments during an active outage. Chaos needs immediate stability, not learning.
- **Clear treated as Complicated:** over-engineering a trivial problem. Apply the best practice and move on.

## Confidence Check

Before committing, test the classification:
- Clear? Do best practices reliably work here? If not → probably Complicated.
- Complicated? Can analysis predict the outcome? If not → probably Complex.
- Complex? Can you run a safe-to-fail probe? If it's too turbulent to probe → Chaotic.
- Re-check as the situation evolves; domains shift (chaos stabilizes into complex/complicated).

## Key Questions

- "What's the relationship between cause and effect here?"
- "Can experts reliably predict the outcome, or is it only clear in hindsight?"
- "Is this actually complex, or am I avoiding the analysis?"
- "Is this actually complicated, or am I over-planning a simple thing?"
- "Has the situation moved to a different domain since I last looked?"

## Snowden's Wisdom

"Complex systems are dispositional, not causal—you can't predict what will happen, only influence what might." The failure is rarely the methodology itself; it's applying the wrong methodology to the wrong domain.
