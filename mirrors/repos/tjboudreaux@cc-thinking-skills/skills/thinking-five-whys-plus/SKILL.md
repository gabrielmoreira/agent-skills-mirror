---
name: thinking-five-whys-plus
description: Use when a fault is localized to a component and the proximate cause is known but the systemic root is not — chain 'why' with evidence, a counterfactual cause test, and an explicit stop condition.
---

# Five Whys Plus

## Overview

Five Whys Plus is a **post-localization root-cause analysis** skill. It assumes a fault has already been localized to a specific component or subsystem (by `thinking-scientific-method` or equivalent hypothesis-differential debugging). From that starting point — the proximate cause is known — it chains "why" questions backward to reach the systemic root cause, with explicit guards against the technique's known failure modes.

**Core Principle:** Never ask "why" without evidence for the answer. Chain backward from localized fault to actionable root cause, and stop only when the cause passes a counterfactual test: "Would the problem NOT have occurred if this cause were absent?"

## When to Use

- A fault has been localized to a specific component (use `thinking-scientific-method` first if you don't know which component is at fault)
- The proximate cause is known but the systemic cause isn't
- A problem keeps recurring despite previous fixes
- You need the root cause, not just the proximate one

Decision flow:

```
Fault localized to a specific component?
  → No → Run thinking-scientific-method first to localize
  → Yes → Proximate cause known?
      → No → Gather evidence on proximate cause
      → Yes → Is the root cause already obvious and verified?
          → Yes → Fix directly; don't chain
          → No → APPLY FIVE WHYS PLUS
```

## When NOT to Use

- **The fault is not yet localized.** If you don't know which component is at fault (multiple candidate causes), this is a localization problem. Use `thinking-scientific-method` (hypothesis-differential debugging) first, then run Five Whys on the cause it confirms.
- **The root cause is already obvious and verified.** Don't ritualistically chain "why" — just fix it.
- **The chain would be pure speculation with no evidence for the next "why".** Stop and gather evidence; don't speculate deeper (see Anti-Patterns: Speculation Dive).
- **The problem is a one-off with no systemic dimension.** If a single fat-finger error caused an outage and there's no process gap, don't force a chain.

## Procedure

### Step 1: State the Problem Precisely

Document the localized fault with specific, measurable details:

```markdown
Problem Statement:
- What happened: [Specific observable symptom]
- Localized to: [Component/subsystem confirmed by scientific-method or equivalent]
- When: [Time range]
- Where: [Affected systems/users]
- Extent: [Scope and severity]
- Impact: [Business/user impact]
```

### Step 2: Build the Evidence Chain

For each "why," require evidence, confidence, and alternatives considered:

```markdown
Why #N: Why did [answer N-1] occur?
Answer: [Hypothesis]
Evidence: [Data, logs, metrics that support this — NOT speculation]
Confidence: High / Medium / Low
What else considered: [Alternative causes checked]
Ruled out because: [Evidence against alternatives]
```

**Evidence types:** Logs showing the event, metrics correlating with timeline, code showing the behavior, configuration proving the state, testimony from multiple independent sources.

**Branch on "what else?"** at each step — explicitly list and rule out alternative explanations before proceeding.

### Step 3: Apply the Counterfactual Cause Test

Before stopping, test the proposed root cause:

> **Counterfactual:** "Would the problem NOT have occurred if this cause were absent?"

If the answer is "no" or "maybe not" — you haven't reached the root cause. Keep going.

If the answer is "yes, the problem would not have occurred" — AND the cause passes the stop condition (Step 4) — you've found the root cause.

### Step 4: Check the Stop Condition

Only stop when ALL criteria are met:

| Criterion | Question |
|-----------|----------|
| Actionable | Can we take concrete action on this cause? |
| Controllable | Is this within our control to fix? |
| Fundamental | Would fixing this prevent recurrence? |
| Evidenced | Do we have evidence, not just speculation? |
| Counterfactual | Would the problem NOT have occurred if this cause were absent? |
| Not-blame | Is this a system/process issue, not just "someone messed up"? |

**Never stop at human error.** When you reach "someone made a mistake," ask "Why was the mistake possible?" — that's the systemic cause.

### Step 5: Apply Devil's Advocate Review

Before finalizing, challenge the conclusion:

```markdown
Counter-analysis:
1. What evidence contradicts this conclusion?
2. What other explanation fits the evidence equally well?
3. Would someone outside our team reach the same conclusion?
4. If we fix X, are we confident the problem won't recur?
5. Are we finding what we expected to find? (confirmation bias check)
```

### Step 6: Document and Recommend

Record the full chain and prescribe actions that address the root cause (not just the symptom).

## Output Contract

A completed Five Whys Plus analysis produces:

1. **Problem Statement** — specific, measurable, with localized component
2. **Evidence Chain** — each "why" step with answer, evidence, confidence, and alternatives ruled out
3. **Counterfactual Test Result** — explicit answer to "would the problem NOT have occurred?"
4. **Stop Condition Check** — all six criteria satisfied
5. **Devil's Advocate Review** — contradicting evidence, alternative explanations, bias check
6. **Root Cause(s)** — primary and any contributing factors
7. **Recommended Actions** — addressing root cause, with owner and timeline
8. **Verification Plan** — how to confirm the fix worked

## Anti-Patterns

| Anti-Pattern | Symptom | Correction |
|---|---|---|
| **Pre-localization application** | Running Five Whys when you don't know which component failed | Use `thinking-scientific-method` first to localize |
| **Premature stop** | Accepting the first plausible cause without the counterfactual test | Apply the counterfactual: "Would the problem NOT have occurred?" |
| **Blame stop** | Ending at "someone made a mistake" | Ask "Why was the mistake possible?" — find the systemic gap |
| **Speculation dive** | Answers become increasingly speculative without evidence | Stop and gather evidence; mark un-evidenced steps as hypotheses |
| **Circular why** | "Why A?" → "Because B" → "Why B?" → "Because A" | Introduce external evidence or a third factor to break the cycle |
| **Single-cause bias** | Assuming one root cause without branching | At each step, ask "what else could cause this?" and rule out alternatives |
| **Confirmation bias** | Finding the cause you expected to find | Devil's advocate review; ask "what evidence contradicts this?" |
| **Ritualistic chaining** | Asking five whys when one would do | Stop when the counterfactual test passes and the stop condition is met |
