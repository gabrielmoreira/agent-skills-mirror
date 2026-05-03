---
type: skill
lifecycle: stable
inheritance: inheritable
name: calibration-tracking
description: Record confidence claims and reconcile against outcomes — closing Tenet V (calibration over confidence)
tier: core
applyTo: '**/*calibration*,**/*tracking*'
currency: 2026-04-27
lastReviewed: 2026-04-30
---

# Calibration Tracking Skill


Record the AI's confidence claims and reconcile them against actual outcomes. This closes ACT Tenet V (calibration over confidence) by creating a feedback loop.

## Why This Matters

Without a feedback loop, confidence statements are performative — "I'm 80% confident" means nothing if we never check whether the AI assistant is actually right 80% of the time. Calibration tracking creates that loop.

**Evidence**: Tetlock's superforecasting research (2005, 2015) and Mellers et al. (2014) show that calibration improves dramatically with feedback. Without feedback, even experts drift toward overconfidence or underconfidence.

## Schema: Calibration Register

**File**: `.github/quality/calibration-register.jsonl`

Each line is a JSON object with these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique ID (ISO timestamp + 4-char random: `2026-04-27T10:30:00Z-a3f2`) |
| `timestamp` | string | ✅ | ISO 8601 when claim was recorded |
| `claim` | string | ✅ | The specific prediction or confidence statement |
| `confidence` | number | ✅ | Confidence level 0.0–1.0 (e.g., 0.80 = 80%) |
| `domain` | string | ✅ | Category: `code`, `architecture`, `debugging`, `security`, `documentation`, `other` |
| `revisitTrigger` | string | ✅ | When to check outcome: `next-session`, `7d`, `30d`, `on-event:{event}` |
| `outcome` | string | ❌ | `correct`, `incorrect`, `partially-correct`, `indeterminate` |
| `resolvedAt` | string | ❌ | ISO 8601 when outcome was recorded |
| `notes` | string | ❌ | Optional context about resolution |

### Example Entry (Unresolved)

```json
{"id":"2026-04-27T10:30:00Z-a3f2","timestamp":"2026-04-27T10:30:00Z","claim":"The race condition is in the async handler, not the state initialization","confidence":0.85,"domain":"debugging","revisitTrigger":"next-session"}
```

### Example Entry (Resolved)

```json
{"id":"2026-04-27T10:30:00Z-a3f2","timestamp":"2026-04-27T10:30:00Z","claim":"The race condition is in the async handler, not the state initialization","confidence":0.85,"domain":"debugging","revisitTrigger":"next-session","outcome":"correct","resolvedAt":"2026-04-28T09:00:00Z","notes":"User confirmed after adding mutex"}
```

## When to Record

Record a calibration entry when **all** conditions hold:

1. **Explicit confidence**: the AI assistant states a specific confidence level (80%, "very likely", "probably")
2. **Falsifiable claim**: The claim can be proven right or wrong
3. **Non-trivial stakes**: The claim affects a decision (debugging path, architecture choice, security assessment)

### Confidence Language Mapping

| Language | Confidence |
|----------|------------|
| "I'm certain", "definitely" | 0.95 |
| "I'm confident", "very likely" | 0.85 |
| "Probably", "likely" | 0.70 |
| "I think", "seems like" | 0.60 |
| "Possibly", "might be" | 0.50 |
| "Uncertain but leaning toward" | 0.55 |

### Revisit Trigger Patterns

| Trigger | Use When |
|---------|----------|
| `next-session` | Outcome will be known by next work session |
| `7d` | Short-term prediction (build will pass, fix will hold) |
| `30d` | Architecture or design prediction |
| `on-event:deploy` | Outcome tied to specific event |
| `on-event:user-feedback` | Requires user input to resolve |

## Recording Protocol

When making a confidence claim in conversation:

1. **State the claim clearly** with confidence level
2. **Check if it's falsifiable** — if not, don't record
3. **Append to register** with appropriate revisit trigger
4. **Mention recording** briefly: *"(Logging this at 80% confidence for calibration)"*

### Recording Format

```markdown
**Claim recorded**: "[claim]" at [X]% confidence. Revisit: [trigger].
```

## Resolution Protocol

During `/calibration-review` or when a trigger fires:

1. **Read open entries** with passed revisit triggers
2. **For each entry**:
   - Check actual outcome
   - Mark `correct`, `incorrect`, `partially-correct`, or `indeterminate`
   - Add notes if context is useful
3. **Update the entry** with outcome and resolvedAt

### Indeterminate Outcomes

Mark `indeterminate` when:

- The situation changed making the claim moot
- Insufficient evidence to determine outcome
- The claim was ambiguous in retrospect

Indeterminate entries are excluded from Brier score calculation.

## Brier Score Calculation

The calibration-review muscle computes Brier score on resolved entries:

```
Brier Score = (1/N) × Σ(confidence - outcome)²
```

Where `outcome` is 1.0 for correct, 0.0 for incorrect, 0.5 for partially-correct.

**Interpretation**:

- 0.00 = perfect calibration
- 0.25 = no better than random
- <0.15 = good calibration
- <0.10 = excellent calibration

**Target**: <0.25 (F3 falsifier threshold)

## Integration Points

| Artifact | Role |
|----------|------|
| `epistemic-calibration.instructions.md` | Defines confidence levels this skill references |
| `calibration-review.cjs` | Muscle that surfaces open entries and computes Brier |
| `/calibration-review` | User-invokable prompt to resolve entries |
| `act-falsifier-bench.cjs` | F3 sub-runner reads this register |

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Recording every statement | Noise drowns signal | Only falsifiable, non-trivial claims |
| Vague claims | Can't verify | Restate precisely before recording |
| Never resolving | No feedback loop | Review weekly via `/calibration-review` |
| Retroactive confidence | Gaming the score | Only record at claim time, never edit confidence |
| Binary-only outcomes | Misses nuance | Use `partially-correct` when appropriate |

## Falsifiability (F3)

This skill is decorative if after 30 days with ≥10 resolved entries:

- Brier score cannot be computed (no data)
- Brier score is >0.25 (no better than random)
- the AI assistant stops recording new entries (loop collapsed)

The `act-falsifier-bench.cjs` F3 sub-runner measures this.
