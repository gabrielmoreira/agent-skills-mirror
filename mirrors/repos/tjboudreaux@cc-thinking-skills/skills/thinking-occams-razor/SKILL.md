---
name: thinking-occams-razor
description: Use when multiple causes could explain a bug — test the fewest-assumption hypothesis first; escalate to complex only when evidence forces it. Skip the full procedure when one step resolves it.
---

# Occam's Razor

## Overview

Occam's Razor states: among competing hypotheses that fit the evidence equally well, prefer the one with the fewest assumptions. This skill operationalizes that principle for debugging: **test the simplest hypothesis first, and escalate to complex explanations only when evidence forces it.**

The skill has a **trigger-shrink gate**: if the simplest hypothesis can be tested in one step, just test it — don't run the full enumeration-and-scoring procedure. Reserve the full procedure for situations where multiple hypotheses genuinely compete and the simplest is not obviously testable.

**Core Principle:** "Everything should be made as simple as possible, but no simpler." — Einstein

## When to Use

- Multiple hypotheses could explain a bug and the simplest is NOT obviously testable in one step
- You're about to investigate a complex hypothesis without first testing a simpler one
- Architecture or design decisions where several approaches are viable and differ in complexity
- Root cause analysis where several causes seem plausible

Decision flow:

```
Multiple explanations exist?
  → No → Use the available explanation
  → Yes → Can the simplest be tested in one step?
      → Yes → JUST TEST IT (trigger-shrink — skip full procedure)
      → No → Do they explain the evidence equally well?
          → No → Prefer the better explanation
          → Yes → RUN FULL OCCAM'S RAZOR PROCEDURE
```

## When NOT to Use

- **Evidence already points to a specific cause.** Follow the evidence; don't downgrade to a "simpler" hypothesis it contradicts.
- **The domain is irreducibly complex** (distributed consensus, concurrency, security threat models). The simplest model is wrong; don't oversimplify ("but no simpler").
- **Only one plausible explanation exists.** There's nothing to compare — just test it.
- **"Simple" would mean ignoring a known interaction or skipping a load-bearing safeguard.** Local simplicity that creates systemic risk isn't parsimony.
- **The trigger check resolves it.** If you can test the simplest hypothesis in one step and it's confirmed, you're done — don't enumerate for completeness.

## Trigger Card

Before running the full enumeration-and-scoring procedure, ask one question: **"Can I test the simplest hypothesis in one step?"**

1. **Identify the simplest hypothesis** — the one with the fewest assumptions that still explains the evidence.
2. **Can you test it in one step?** → Yes → **Just test it.** If confirmed, report and stop. If refuted, move to the next simplest.
3. **If it can't be tested in one step** → run the full Occam's Razor procedure (enumerate, count assumptions, verify explanatory power, test in order).

If evidence already points to a specific cause, follow the evidence — don't downgrade to a "simpler" hypothesis it contradicts. For irreducibly complex domains (distributed consensus, concurrency), the simplest model is wrong.

## Procedure

### Trigger Check (Fast Path)

Before running the full procedure, ask: **"Can I test the simplest hypothesis in one step?"**

- Yes → Test it. If confirmed, report and stop. If falsified, move to the next simplest.
- No → The simplest hypothesis requires non-trivial investigation → run the full procedure below.

### Full Procedure: When the Trigger Check Doesn't Resolve

#### Step 1: Enumerate Competing Hypotheses

List all plausible explanations for the observed behavior:

```
Bug: Users intermittently can't log in

Hypotheses:
A. Session token expiration edge case
B. Race condition in auth service
C. Database connection pool exhaustion
D. Complex interaction between CDN cache, load balancer, and session service
```

#### Step 2: Count Assumptions per Hypothesis

| Hypothesis | Assumptions |
|------------|-------------|
| A. Token expiration | 1. Token validation has an edge case |
| B. Race condition | 1. Concurrent requests possible, 2. Shared mutable state exists |
| C. DB pool exhaustion | 1. Pool is undersized, 2. Connections are leaking |
| D. Complex interaction | 1. CDN caches auth, 2. LB sticky sessions fail, 3. Session sync delayed |

Count each independent assumption: +1 per assumption, +1 per component involved, +2 per external dependency, +2 for timing-dependent behavior, +3 for rare conditions, +5 for "perfect storm" scenarios.

#### Step 3: Verify Explanatory Power

Ensure simpler hypotheses actually explain the evidence:

```
Evidence: Failures correlate with high traffic periods
Hypothesis A (token edge case): Doesn't explain traffic correlation ✗
Hypothesis C (DB pool exhaustion): Explains traffic correlation ✓ — fewer assumptions than D
→ PREFERRED by Occam's Razor
```

#### Step 4: Test in Order of Fewest Assumptions

Investigate hypotheses from fewest to most assumptions. Do not skip to complex hypotheses until simple ones are ruled out.

#### Step 5: Escalate Complexity Only When Evidence Forces It

When simple explanations are ruled out with evidence, move to more complex ones. Never escalate on intuition alone.

## Output Contract

A completed Occam's Razor analysis produces:

1. **Trigger Check Result** — whether the simplest hypothesis was testable in one step
2. **Hypothesis Ranking** — ordered by assumption count, with each hypothesis' assumptions listed
3. **Explanatory Power Check** — which hypotheses fit the evidence
4. **Test Order and Results** — which hypotheses were tested, in what order, and the outcome
5. **Conclusion** — the confirmed hypothesis (or the next to test if unresolved)

For trigger-shrink cases, the output may be a single line: "Tested simplest hypothesis X — confirmed/refuted."

## Anti-Patterns

| Anti-Pattern | Symptom | Correction |
|---|---|---|
| **Oversimplifying irreducible domains** | Applying "simplest" to distributed consensus or security models | "But no simpler" — respect domain complexity |
| **Complexity bias** | Assuming complex = sophisticated, testing complex hypotheses first | Test fewest-assumption hypotheses first, always |
| **Trigger inflation** | Running the full enumeration for a one-step test | If the simplest is one-step testable, just test it |
| **Ignoring explanatory power** | Choosing the simplest hypothesis that doesn't fit the evidence | Fewer assumptions doesn't beat not fitting the data |
| **Local simplicity, systemic risk** | Choosing a simple local fix that creates fragility elsewhere | Prefer systemic simplicity over local simplicity |
| **Ritualistic assumption counting** | Spending more time counting assumptions than testing | The point is prioritization, not precision; rough count is enough |
