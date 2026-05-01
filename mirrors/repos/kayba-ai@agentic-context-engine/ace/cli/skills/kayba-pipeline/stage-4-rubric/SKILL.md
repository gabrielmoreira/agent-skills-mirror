---
name: kayba-stage-4-rubric
description: Organize computed metrics into a tiered evaluation rubric with leading, lagging, and quality indicators. Trigger when the user says "run stage 4", "build rubric", "tier metrics", or when invoked by the kayba-pipeline orchestrator. Requires eval/baseline_metrics.json and eval/compute_baselines.py to exist.
---

# Stage 4: Rubric Definition

Organize metrics into a tiered evaluation rubric. Detect and resolve redundancy quantitatively. Ensure every insight is accounted for.

## Inputs

- `eval/baseline_metrics.json` — computed baseline values from Stage 3
- `eval/compute_baselines.py` — to understand what each metric measures
- `eval/stage1_insights_summary.md` — the original insights
- `eval/stage2_domain_context.md` — domain context

Read all four files before starting.

## Process

### 1. Quantitative redundancy check

Before tiering, check every pair of metrics for overlap. Two metrics are redundancy candidates if ANY of the following hold:

- **Denominator overlap >70%**: compute `|denom_events(A) ∩ denom_events(B)| / min(|denom(A)|, |denom(B)|)`. If >0.70, they are candidates. To compute this, trace through the detector functions in `compute_baselines.py` and determine which trace events (turns, calls, threads) each denominator iterates over. When denominators are identical sets (same loop, same filter), overlap is 100%.
- **Same skill set**: the metrics map to the exact same set of insight/skill IDs from Stage 1.
- **Logical subsumption**: one metric's positive case is a strict subset of the other's (e.g., "turn has exactly 1 tool call" is a subset of "turn has no user-facing content alongside tool calls" only if every single-call turn also has no content — check this, don't assume it).

For each candidate pair, make an explicit decision with reasoning:

| Pair | Denom overlap | Skill overlap | Subsumption? | Decision | Reasoning |
|------|---------------|---------------|--------------|----------|-----------|
| M1/M2 | 100% (same 29 turns) | identical | No — can violate one without the other | **Keep both** | Independently actionable: batching vs. content leaking are distinct fixes |

Valid decisions: **keep both** (with reasoning why they're independently actionable), **merge** (combine into one metric, specify how), or **drop** (specify which and why). "They feel different" is not sufficient reasoning — cite the specific behavior that one catches and the other misses.

Final count target: 5-7 metrics after redundancy resolution.

### 2. Tier each metric

Use this decision flowchart for every metric:

```
Q1: Can a SINGLE skill/instruction change directly move this metric?
    → If the agent follows one new instruction and the metric improves,
      regardless of other behaviors: LEADING.

Q2: Does moving this metric require MULTIPLE skills to be adopted together?
    → If improvement depends on several upstream behaviors all working
      (e.g., proper turn structure + confirmation flow + execution):
      LAGGING.

Q3: Does moving this metric require domain reasoning beyond following instructions?
    → If the agent needs to correctly interpret policy rules, evaluate
      eligibility criteria, or make judgment calls that can't be reduced
      to a single instruction: QUALITY.
```

Apply the flowchart to each metric and record the Q1/Q2/Q3 answer that determined the tier. If a metric could arguably be two tiers, pick the lower one (Leading < Lagging < Quality) and note the ambiguity.

Tier summary for reference:

| Tier | Purpose | Moves when... | Diagnostic signal |
|------|---------|---------------|-------------------|
| **Leading** | Behaviors a single skill directly changes | Skill is adopted | If leading moves but lagging doesn't → skill adopted but not solving the right problem |
| **Lagging** | Aggregate outcomes requiring multiple skills | Multiple skills coordinate | If lagging moves but leading doesn't → something else improved, not your skills |
| **Quality** | Requires domain understanding, not just instruction-following | Agent reasons correctly | If quality moves but lagging doesn't → agent got lucky or metric is mis-tiered |

### 3. Flag low-confidence baselines

Any metric with denominator < 5 events is a **low-confidence baseline**. These metrics:
- ARE included in the rubric (they measure real behaviors)
- Are marked with `**Confidence: low** (n=X)` in the rubric
- Must NOT drive priority decisions in Stage 5 — they inform direction only
- Should note what denominator size would make them reliable (rule of thumb: n >= 10 for a rate metric to be meaningful, n >= 30 for statistical comparisons)

### 4. Set direction

For each metric, indicate whether it should go **up higher** or **down lower**. Don't set arbitrary numerical targets — baseline + direction is enough.

**Ceiling guard:** If a metric's baseline is already 100%, its direction MUST be `"↑ maintain"` or `"— already optimal"`, never `"↑"` as if it needs to go higher. A 100% metric is at ceiling — the goal is to sustain it, not improve it. Similarly, if a metric is at 0% and the desired direction is `"↓"`, mark it `"↓ maintain"` or `"— already at floor"`. Do not let any downstream stage (Stage 5 action plan, Stage 7 fixes) list a ceiling/floor metric as needing improvement.

### 5. Map insights to metrics (completeness check)

For every insight from `eval/stage1_insights_summary.md`, assign it to one of three categories:

1. **Mapped** — directly linked to one or more metrics. List which ones.
2. **Indirectly mapped** — supports a metric but isn't the primary driver. List the metric and explain the indirect relationship.
3. **Qualitative-only** — no programmatic metric captures this insight. Explicitly mark it and state why (e.g., "requires LLM-as-judge," "measures explanation quality," "efficiency pattern with no clear denominator").

Every insight MUST appear in exactly one category. If you find an insight that should have a metric but doesn't, note it as a gap for future Stage 3 iterations — but do not invent metrics at this stage.

At the end, report:
- `X / N insights mapped to metrics`
- `Y / N insights indirectly mapped`
- `Z / N insights qualitative-only`

### 6. Add invalidation notes

For each metric, write one sentence answering: "What would make this tier assignment wrong?"

Examples:
- M1 (Leading): "Wrong if fixing batching also requires the agent to change its confirmation flow — that would make it Lagging."
- M5 (Quality): "Wrong if cancellation compliance can be fixed by a single checklist instruction without requiring the agent to reason about policy — that would make it Leading."

These notes exist so Stage 5 can catch tier errors. If Stage 5 finds evidence that a tier is wrong (e.g., a single skill would move a "Quality" metric), it should flag the conflict rather than silently inheriting the error.

### 7. Write the rubric

Write to `eval/baseline_metrics.md`:

```markdown
# Eval Rubric — Baseline Metrics

## Summary
| # | Metric | Tier | Baseline | Direction | Confidence |
|---|--------|------|----------|-----------|------------|
| M1 | First-call success rate | Leading | 37.6% | up | ok (n=29) |
| M2 | ... | ... | ... | ... | ... |

## Tier Definitions

- **Leading** — Single skill directly moves this. Should change first after deployment.
- **Lagging** — Multiple skills must coordinate. Improves as a consequence of adoption.
- **Quality** — Requires domain reasoning beyond instruction-following. Hardest to move.

## Metric Details

### M1: [name]
**Tier:** Leading
**Baseline:** 37.6% (685 / 1,821)
**Confidence:** ok (n=1821) | low (n=X) — needs n>=Y for reliable comparison
**Direction:** up higher is better
**What it measures:** [description]
**How it's computed:** [reference to function in compute_baselines.py]
**Skills that should move this:** [list insight/skill IDs from stage 1]
**Tier rationale:** [which flowchart question determined the tier]
**Invalidation note:** [what would make this tier wrong]

### M2: [name]
...

## Redundancy Analysis

| Pair | Denom overlap | Skill overlap | Subsumption? | Decision | Reasoning |
|------|---------------|---------------|--------------|----------|-----------|
| ... | ... | ... | ... | ... | ... |

## Insight Coverage

### Mapped (X / N)
- `insight_id` — [title] → M1, M3

### Indirectly mapped (Y / N)
- `insight_id` — [title] → supports M5 via [explanation]

### Qualitative-only (Z / N)
- `insight_id` — [title] — [why no metric: e.g., "requires LLM-as-judge"]
```

## Outputs

- `eval/baseline_metrics.md` — human-readable tiered rubric with redundancy analysis, confidence flags, insight coverage, and invalidation notes
