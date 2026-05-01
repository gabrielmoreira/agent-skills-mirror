---
type: skill
lifecycle: stable
inheritance: inheritable
name: falsifiability-test-pattern
description: Plans without measurable success criteria drift into wishful thinking:
tier: standard
applyTo: '**/*falsifiability*,**/*test*,**/*pattern*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Falsifiability Test Pattern

## The Problem

Plans without measurable success criteria drift into wishful thinking:

- "Improve performance" — how much? by when?
- "Better user experience" — measured how?
- "Reduce tech debt" — which debt? how will we know?

## The Solution

Every deferred or speculative work item declares a measurable rule for success/failure.

```markdown
## Feature: Caching Layer

**Hypothesis**: Adding Redis caching will reduce API latency by 50%.

**Falsifiability Test**: 
- Measure: p95 latency for /api/users endpoint
- Baseline: 450ms (measured 2026-04-20)
- Target: <225ms
- Window: 30 days post-deployment
- Decision rule: If p95 > 300ms after 30 days, revert and investigate

**Evidence collection**: Datadog dashboard, weekly snapshots
```

## Template

```markdown
## [Feature/Change Name]

**Hypothesis**: [What you believe will happen]

**Falsifiability Test**:
- Measure: [Specific metric]
- Baseline: [Current value with date]
- Target: [Success threshold]
- Window: [Time to evaluate]
- Decision rule: [What to do if fails]

**Evidence collection**: [How you'll gather data]
```

## Good vs Bad Tests

| Bad | Good |
|-----|------|
| "Will be faster" | "p95 latency < 200ms within 14 days" |
| "Users will like it" | "NPS > 40 after 500 responses" |
| "Reduces bugs" | "Bug reports for module X < 2/month" |
| "More maintainable" | "Time to implement similar feature < 2 days" |

## Decision Rules

```markdown
| Outcome | Action |
|---------|--------|
| Target met | Keep, document win |
| Partial (80%+) | Keep, note limitation |
| Missed | Revert or iterate |
| Can't measure | Fix instrumentation first |
```

## Verification

1. Every plan item has a falsifiability test
2. Tests have specific numbers and dates
3. Decision rules exist before implementation
4. Results are recorded

## When to Apply

- Feature planning
- Architecture decisions
- Process changes
- Any speculative investment

## Tags

`quality` `planning` `metrics` `decision-making`
