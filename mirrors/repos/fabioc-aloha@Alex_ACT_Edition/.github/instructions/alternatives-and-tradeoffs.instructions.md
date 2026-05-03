---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Generate alternatives and compare them — methods for option generation and trade-off analysis"
application: "When choosing between options, recommending an approach, or explaining 'it depends'"
applyTo: "**/*option*,**/*alternative*,**/*trade*,**/*compare*,**/*decision*,**/*choose*,**/*versus*,**/*pros*,**/*cons*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Alternatives and Trade-offs

> **ACT Tenet III**: Never test a hypothesis against the null. Always against at least one rival.
> **ACT Tenet VI**: Materiality gating requires understanding what matters.

Two halves of the same discipline: **generate** options, then **compare** them. Replaces `option-generation` and `trade-off-analysis`.

## When to Use

| Trigger | Section |
|---------|---------|
| About to commit to a single solution | §1 — generate alternatives first |
| User says "how should I..." | §1 — present options, not a single answer |
| Stuck on a problem | §1 — divergent techniques to unstick |
| Multiple options exist | §2 — compare explicitly |
| "It depends" temptation | §2 — specify *what* it depends on |
| High-stakes choice | §1 + §2 — generate then compare with documented reasoning |

## §1 — Generate Options

### SCAMPER (Improving Existing Solutions)

Apply each lens to the current approach:

| Lens | Question |
|------|----------|
| **S**ubstitute | What can be replaced? |
| **C**ombine | What can be merged? |
| **A**dapt | What can be borrowed from elsewhere? |
| **M**odify | What can change in scale, frequency, intensity? |
| **P**ut to other uses | What else could this do? |
| **E**liminate | What can be removed? |
| **R**everse | What if we flip the order, role, or assumption? |

### MECE (Structuring Option Space)

Mutually Exclusive, Collectively Exhaustive — cover the space without overlap:

| Dimension | Splits |
|-----------|--------|
| Build vs. Buy | Create OR purchase/license |
| Fast vs. Thorough | Quick-and-dirty OR comprehensive |
| Centralized vs. Distributed | One place OR many places |
| Push vs. Pull | We initiate OR they request |
| Automated vs. Manual | System OR human |

**Test**: Can every possible option fit into exactly one category?

### How Might We (HMW)

Reframe constraints as opportunities:

| Constraint | HMW Reframe |
|------------|-------------|
| "No budget" | HMW achieve the goal with zero budget? |
| "Takes too long" | HMW deliver value in 1/10th the time? |
| "Won't adopt" | HMW make adoption effortless? |
| "Impossible" | HMW work around the technical limit? |

### Inversion

Instead of "How do we succeed?" → "How would we guarantee failure?" Then avoid those things.

### Lateral Triggers (When Stuck)

| Technique | Use |
|-----------|-----|
| **Analogy** | "How would [doctor / architect / chef] solve this?" |
| **Constraint removal** | "What if we had unlimited [time / money / people]?" |
| **Extreme parameters** | "What if the deadline was tomorrow? Next year?" |

### Generation Anti-Patterns

| Pattern | Fix |
|---------|-----|
| Single option presented | Generate ≥2 always — even if one is "do nothing" |
| Strawman alternatives | Each option must be genuinely viable |
| Anchoring on first idea | Generate before evaluating any |
| Analysis paralysis | Cap at 3-5 meaningfully different options |

## §2 — Compare Options

### Decision Matrix (Weighted Scoring)

For 3+ options on multiple criteria:

```markdown
| Criteria | Weight | A | B | C |
|----------|--------|---|---|---|
| Criterion 1 | 30% | 8 | 6 | 9 |
| Criterion 2 | 25% | 7 | 9 | 5 |
| Criterion 3 | 25% | 6 | 7 | 8 |
| Criterion 4 | 20% | 9 | 5 | 6 |
| **Weighted Total** | 100% | **7.4** | **6.8** | **7.1** |
```

**Rules**:

- Weights sum to 100%
- Scores 1–10 (or 1–5 for simpler decisions)
- Independent criteria (no double-counting)
- **Set weights *before* scoring options** — otherwise post-hoc rationalization

### Pros / Cons with Severity

When quantitative scoring feels forced:

| Option | Pro (severity) | Con (severity) |
|--------|----------------|----------------|
| A | Fast (high) | Inflexible (med) |
| A | Cheap (med) | Tech debt (high) |
| B | Flexible (high) | Complex (high) |

Severity: High = deal-maker/breaker, Medium = significant, Low = nice-to-have.

### 2×2 Matrix (Two Dominant Dimensions)

Common framings: Impact vs. Effort, Urgency vs. Importance, Risk vs. Reward, Certainty vs. Impact.

### Reversibility Test

| Decision Type | Approach |
|---------------|----------|
| **Reversible** (Type 2) | Decide fast, correct later — feature flag, A/B, pilot |
| **Irreversible** (Type 1) | Decide carefully — architecture, contracts, public commitments |

> "Most decisions should be made with around 70% of the information you wish you had." — Bezos

### Output Format (Recommended)

When presenting alternatives + trade-offs:

```markdown
## Options for [decision]

| Option | Description | Pros | Cons | Effort |
|--------|-------------|------|------|--------|
| A | ... | ... | ... | ... |
| B | ... | ... | ... | ... |

**Recommendation**: A — because [specific reason].
**Trade-off**: Accepting [downside] in exchange for [upside].
**Would revise if**: [specific evidence that would change the call].
```

### Comparison Anti-Patterns

| Pattern | Fix |
|---------|-----|
| Hidden trade-offs | Make all explicit upfront |
| Unweighted criteria | Weight before scoring |
| Post-hoc rationalization | Document criteria *before* evaluating |
| False precision (7.42 vs. 7.38) | Round scores; acknowledge uncertainty |
| Over-analyzing reversible decisions | Type 2: faster is better |

## What This Replaces

- `option-generation` → §1
- `trade-off-analysis` → §2

Combined because the two halves are inseparable: generating without comparing produces noise; comparing without generating produces premature anchoring.
