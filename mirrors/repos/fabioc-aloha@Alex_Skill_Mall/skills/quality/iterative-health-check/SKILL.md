---
type: skill
lifecycle: stable
inheritance: inheritable
name: iterative-health-check
description: One-time audits don't track improvement:
tier: standard
applyTo: '**/*iterative*,**/*health*,**/*check*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Iterative Health-Check Loop

## The Problem

One-time audits don't track improvement:

- "We found 47 issues" — so what?
- No prioritization
- No follow-through
- Same issues reappear

## The Solution

Score → Fix Top Issues → Rescore loop.

```
┌──────────────────┐
│   Score          │ Assess current state quantitatively
└────────┬─────────┘
         ▼
┌──────────────────┐
│   Prioritize     │ Rank by ROI (impact / effort)
└────────┬─────────┘
         ▼
┌──────────────────┐
│   Fix Top N      │ Address highest-ROI issues
└────────┬─────────┘
         ▼
┌──────────────────┐
│   Rescore        │ Measure improvement
└────────┬─────────┘
         │
         └─────────► Repeat
```

## Scoring Framework

```javascript
const dimensions = {
  testCoverage: { weight: 0.25, score: 0 },
  docAccuracy: { weight: 0.20, score: 0 },
  securityGaps: { weight: 0.30, score: 0 },
  techDebt: { weight: 0.25, score: 0 }
};

function calculateHealth() {
  return Object.values(dimensions)
    .reduce((sum, d) => sum + d.weight * d.score, 0);
}

// Score each dimension 0-100
dimensions.testCoverage.score = 72;  // 72% coverage
dimensions.docAccuracy.score = 85;   // 85% of docs verified
dimensions.securityGaps.score = 60;  // 3 medium issues
dimensions.techDebt.score = 45;      // High debt

console.log(`Health: ${calculateHealth().toFixed(0)}%`); // 64%
```

## ROI Prioritization

```markdown
| Issue | Impact (1-5) | Effort (1-5) | ROI | Priority |
|-------|--------------|--------------|-----|----------|
| Fix auth bug | 5 | 2 | 2.5 | 1 |
| Add tests | 3 | 3 | 1.0 | 3 |
| Update deps | 4 | 2 | 2.0 | 2 |
| Refactor X | 2 | 4 | 0.5 | 4 |
```

ROI = Impact / Effort. Fix highest ROI first.

## Progress Tracking

```markdown
## Health Check History

| Date | Score | Top Fix | Impact |
|------|-------|---------|--------|
| 2026-04-01 | 45% | Security patch | +12% |
| 2026-04-15 | 57% | Test coverage | +8% |
| 2026-04-29 | 65% | Doc update | +5% |
```

## Verification

1. Score is reproducible (same method each time)
2. Fixes address highest-ROI issues
3. Rescore shows measurable improvement
4. Loop continues until target score reached

## When to Apply

- Codebase health monitoring
- Documentation audits
- Security reviews
- Any quality improvement initiative

## Tags

`quality` `audit` `metrics` `continuous-improvement`
