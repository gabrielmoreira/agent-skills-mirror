---
name: thinking-probabilistic
description: Use when stating a forecast, estimate, or risk. Anchor on the base rate, give a confidence range instead of a point, and update the number when new evidence arrives.
---

# Probabilistic Thinking

## Overview

Probabilistic thinking, informed by Philip Tetlock's "Superforecasting," treats a forecast as a probability and a range rather than a single confident number. Three moves do almost all the work: **anchor on the base rate**, **express the estimate as a range** (not a point), and **update the number** when new evidence arrives.

**Core Principle:** Start from how often similar things happen, state your estimate as a range with a confidence level, and move the number — explicitly — when the evidence moves.

> **Stateless-agent note.** Across a single task you have no persistent prediction log, so there is no "track my calibration over months" step here. The leverage is in the *act* of estimating: base rate, range, update. Apply the calibration *attitude* (assume you're overconfident; widen the range) without pretending to keep a cross-session scorecard you don't have.

## When to Use

- Stating a timeline or effort estimate
- Assessing the risk of an action (migration, deploy, change)
- Predicting an outcome (will this fix work? will this launch hit the target?)
- Evaluating an uncertain technical choice
- Any time you're about to give a confident single number you can't actually be sure of

Decision flow:

```
About to state a forecast/estimate/risk?
  → Outcome genuinely uncertain? → yes → BASE RATE, then a RANGE (not a point)
  → New evidence since last estimate? → yes → UPDATE THE NUMBER
  → Can you just look it up / measure it? → yes → DO THAT INSTEAD
```

## When NOT to Use

- **The quantity is knowable.** If you can measure it, query it, or look it up, do that — don't dress a checkable fact as a probability.
- **A single piece of evidence updates a single prior.** That's the narrower mechanics of `thinking-bayesian`; use it for the explicit prior × likelihood-ratio update.
- **The decision doesn't depend on the number.** If you'd act the same across the plausible range, skip the estimate and act.
- **You'd be inventing the base rate.** If there's no real reference class, say the estimate is a guess rather than manufacturing false precision.

## Core Concepts

### Probability as Confidence

Convert vague language to numbers:

| Vague Statement | Probability Range |
|-----------------|-------------------|
| "Certain" | 99%+ |
| "Almost certain" | 90-99% |
| "Very likely" | 80-90% |
| "Likely" / "Probable" | 65-80% |
| "Better than even" | 55-65% |
| "Toss-up" | 45-55% |
| "Unlikely" | 20-35% |
| "Very unlikely" | 10-20% |
| "Almost impossible" | 1-10% |
| "Impossible" | <1% |

### Confidence Intervals

Express estimates as ranges, not points:

```
BAD: "The project will take 6 weeks"
GOOD: "I'm 80% confident the project will take 4-8 weeks"
BETTER: "50% confidence: 5-7 weeks; 90% confidence: 3-10 weeks"
```

### Base Rates

Start with how often similar things happen:

```
Question: Will this feature launch on time?
Base rate: What % of similar features launched on time? ~40%
Adjustment: This team is experienced (+10%), scope is clear (+10%)
Estimate: ~60% probability of on-time launch
```

## The Probabilistic Process

### Step 1: Express Initial Probability

State your belief as a number:

```markdown
## Prediction: Will we hit Q2 revenue target?

Initial estimate: 65%
Reasoning:
- Last 4 quarters: Hit 3/4 targets (75% base rate)
- Current pipeline: Slightly below historical (-10%)
- New product launching: Uncertain impact
```

### Step 2: Identify Key Uncertainties

What could change the probability?

```markdown
Key uncertainties:
1. Will Enterprise deal close? (+15% if yes)
2. Will new product cannibalize existing? (-10% if significant)
3. Will competitor launch disrupt? (-20% if aggressive)
```

### Step 3: Create Probability Tree

For complex predictions, branch scenarios:

```
Project success: ?
├── Technical risk resolves well (60%)
│   ├── Team stays intact (80%) → 0.60 × 0.80 = 48% → SUCCESS
│   └── Key person leaves (20%) → 0.60 × 0.20 × 0.50 = 6% → PARTIAL
├── Technical risk causes delays (30%)
│   ├── Scope reduced (60%) → 0.30 × 0.60 × 0.70 = 12.6% → SUCCESS
│   └── Scope maintained (40%) → 0.30 × 0.40 = 12% → FAILURE
└── Technical risk blocks project (10%) → 10% → FAILURE

P(Success) = 48% + 12.6% = 60.6% ≈ 60%
```

### Step 4: Update with New Information

When new evidence arrives, update:

```markdown
Original estimate: 65% hit revenue target

New information: Enterprise deal delayed to Q3
Impact: -15% (was +15% if closed, now neutral)
Updated estimate: 50%

New information: Competitor launch was weak
Impact: +10% (was -20% if aggressive)
Updated estimate: 60%
```

### Step 5: State the Estimate So It Can Be Checked

Make the forecast falsifiable within the task itself: a clear claim, a timeframe, and the range. This lets the *user or a later observation* verify it — you don't carry a personal scorecard across sessions, but a sharply-stated prediction can still be proven right or wrong.

```markdown
Prediction: "80% confident the migration completes with <5 min downtime,
            range 1-15 min downtime." (Checkable against the actual run.)
```

## Calibration Techniques

> These are sanity checks you apply *now*, within the task — not a longitudinal tracking exercise.

### The Equivalent Bet Test

"Would I bet at these odds?"

```
Prediction: 80% confident project finishes on time
Equivalent: Would I bet $4 to win $1?
If that feels wrong, adjust the probability.
```

### The Outside View

Always check base rates:

```
Inside view: "Our team is great, we'll definitely finish on time"
Outside view: "What % of similar projects finished on time?"

Inside tends toward overconfidence
Outside provides calibration anchor
```

### The Pre-Mortem Adjustment

Imagine failure, then adjust:

```
Initial estimate: 85% success
After pre-mortem: Identified 5 failure modes I hadn't considered
Adjusted estimate: 70%
```

### The Confidence Interval Check

Are your intervals too narrow?

```
Test: Of your 90% confidence intervals, do 90% contain the actual?
Common finding: Only 60-70% do
Fix: Widen intervals by 50%
```

## Application Examples

### Project Estimation

```markdown
## Project: Payment System Rewrite

Timeline estimate:
- 50% confidence: 8-12 weeks
- 80% confidence: 6-16 weeks
- 95% confidence: 4-24 weeks

Key variables:
- API complexity: High uncertainty (+/- 3 weeks)
- Team availability: Medium uncertainty (+/- 2 weeks)
- Integration testing: High uncertainty (+/- 4 weeks)

Commitment: "We're 80% confident we'll deliver in Q2"
```

### Risk Assessment

```markdown
## Risk: Database migration causes extended downtime

Probability assessment:
- Base rate for similar migrations: 20% have issues
- Our preparation level: Above average (-5%)
- Complexity of our schema: Above average (+5%)
- Rollback plan quality: Strong (-5%)

Estimate: 15% probability of extended downtime

Mitigation value:
- If issue occurs: 4 hours downtime × $10K/hour = $40K
- Expected loss: 15% × $40K = $6K
- Mitigation cost: $3K for additional testing
- Decision: Mitigation worth it (ROI positive)
```

### Technical Decision

```markdown
## Decision: Adopt new framework

Success probability factors:
| Factor | Probability | Weight |
|--------|-------------|--------|
| Team learns quickly | 70% | 0.3 |
| Framework matures | 80% | 0.2 |
| Performance meets needs | 60% | 0.3 |
| Integration works | 75% | 0.2 |

Combined probability (simplified):
0.70 × 0.80 × 0.60 × 0.75 = 25% (if all must succeed)
OR weighted average: 70% (if partial success acceptable)

Decision: High uncertainty suggests pilot first
```

## Probabilistic Thinking Template

```markdown
# Probabilistic Assessment: [Prediction]

## Prediction
[Clear, falsifiable statement with timeframe]

## Initial Probability
Estimate: [X]%
Base rate: [Similar events: Y%]
Adjustment rationale: [Why different from base rate]

## Confidence Interval
- 50% CI: [Range]
- 80% CI: [Range]
- 95% CI: [Range]

## Key Uncertainties
| Uncertainty | If positive | If negative |
|-------------|-------------|-------------|
| [Factor 1] | +X% | -Y% |
| [Factor 2] | +X% | -Y% |

## Updates (within this task)
| New information | Old P | New P |
|-----------------|-------|-------|
| | | |

## Checkable Outcome
[The specific observation that will prove this forecast right or wrong]
```

## Verification Checklist

- [ ] Expressed prediction as specific probability
- [ ] Checked base rate for similar events
- [ ] Created appropriate confidence intervals
- [ ] Identified key uncertainties and their impacts
- [ ] Stated the prediction so it's checkable (claim + timeframe + range)
- [ ] Applied equivalent bet test for sanity check
- [ ] Willing to update the number when new information arrives

## Key Questions

- "What probability would I assign to this?"
- "What's the base rate for similar things?"
- "What would change my estimate up or down?"
- "Am I being overconfident? (Usually yes — widen the range)"
- "Have I given a range, or am I hiding uncertainty behind a single number?"
- "Would I bet at these odds?"

## Tetlock's Superforecaster Traits

1. **Update often:** Change the number when evidence changes
2. **Granular probabilities:** Use 65% not "likely"
3. **Outside view:** Start with base rates
4. **Seek disconfirming evidence:** Look for reasons you're wrong
5. **Ranges, not points:** Express confidence as an interval, and widen it
6. **Intellectual humility:** Assume you're often wrong

## Tetlock's Wisdom

"The fox knows many things, but the hedgehog knows one big thing."

Superforecasters are foxes—they integrate many perspectives, update frequently, and avoid ideological certainty. They're not smarter; they're more calibrated.

"Beliefs are hypotheses to be tested, not treasures to be protected."

Your predictions should change as evidence changes. Holding steady when you should update is a calibration failure.
