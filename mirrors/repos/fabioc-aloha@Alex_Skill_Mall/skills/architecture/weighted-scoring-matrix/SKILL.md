---
type: skill
lifecycle: stable
inheritance: inheritable
name: weighted-scoring-matrix
description: Multi-factor decisions become arbitrary without explicit weights:
tier: standard
applyTo: '**/*weighted*,**/*scoring*,**/*matrix*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Weighted Scoring Matrix

## The Problem

Multi-factor decisions become arbitrary without explicit weights:

- "We chose Option A because it felt better"
- No audit trail for why factors mattered
- Inconsistent decision-making across time

## The Solution

Explicit scoring matrix with normalized weights.

```javascript
// Define factors and weights (must sum to 1.0)
const factors = {
  performance: { weight: 0.30, description: 'Response time, throughput' },
  maintainability: { weight: 0.25, description: 'Code clarity, test coverage' },
  cost: { weight: 0.20, description: 'Infrastructure, licensing' },
  security: { weight: 0.15, description: 'Vulnerability surface' },
  userExperience: { weight: 0.10, description: 'Ease of use, learning curve' }
};

// Score each option (1-5 scale)
const options = {
  optionA: { performance: 4, maintainability: 5, cost: 3, security: 4, userExperience: 4 },
  optionB: { performance: 5, maintainability: 3, cost: 2, security: 5, userExperience: 3 },
  optionC: { performance: 3, maintainability: 4, cost: 5, security: 3, userExperience: 5 }
};

// Calculate weighted scores
function calculateScore(scores) {
  return Object.entries(factors).reduce((total, [factor, { weight }]) => {
    return total + (scores[factor] * weight);
  }, 0);
}

Object.entries(options).forEach(([name, scores]) => {
  console.log(`${name}: ${calculateScore(scores).toFixed(2)}`);
});
// optionA: 4.05, optionB: 3.70, optionC: 4.00
```

## Optional Boosts

For factors that can disqualify or strongly prefer:

```javascript
const boosts = {
  mustHave: (score) => score < 3 ? 0 : score,  // Zero if below threshold
  preferred: (score) => score >= 4 ? score * 1.1 : score  // 10% boost if high
};
```

## Output Format

| Option | Perf (0.30) | Maint (0.25) | Cost (0.20) | Sec (0.15) | UX (0.10) | **Total** |
|--------|-------------|--------------|-------------|------------|-----------|-----------|
| A | 4 (1.20) | 5 (1.25) | 3 (0.60) | 4 (0.60) | 4 (0.40) | **4.05** |
| B | 5 (1.50) | 3 (0.75) | 2 (0.40) | 5 (0.75) | 3 (0.30) | **3.70** |
| C | 3 (0.90) | 4 (1.00) | 5 (1.00) | 3 (0.45) | 5 (0.50) | **3.85** |

## Verification

1. Weights sum to 1.0
2. Scores are consistently applied (same rubric)
3. Winner matches intuition (if not, weights are wrong)

## When to Apply

- Technology selection
- Vendor evaluation
- Architecture decisions
- Hiring decisions
- Any multi-factor choice

## Tags

`architecture` `decision-making` `scoring` `evaluation`
