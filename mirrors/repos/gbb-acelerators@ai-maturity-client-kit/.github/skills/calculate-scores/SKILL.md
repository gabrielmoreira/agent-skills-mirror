---
name: calculate-scores
description: Computes v2 dimension and overall scores, or archived v1 scores, by invoking scripts/assessment_engine.py. Use for "calcular scores", "computar pontuacao", "rodar scoring", "compute scores", "calculate maturity scores", "calcular puntajes", "calcular la puntuación".
---

# Skill: Compute scores

Always invoke the deterministic engine. Do not compute scores in chat or Excel.

## Command

```bash
python3 scripts/assessment_engine.py all
```

`make scores` is equivalent. Use `all` so `scores.json`, `gaps.json`, and `recommendations.json` stay consistent.

## v2 scoring facts

- Question score is the pooled mean of respondent values, excluding blank and `NA` (`level: null`).
- Dimension score is the mean of answered question scores.
- Overall score is the weighted mean of dimensions.
- Default dimension weight is `1.0`; `dimension_weights` may set values from `0.5` to `2.0`.
- Bands: L0 `[0,0.8)`, L1 `[0.8,1.6)`, L2 `[1.6,2.4)`, L3 `[2.4,3.2)`, L4 `[3.2,4.0]`.
- Coverage: OK at 37 or more answered questions, WARNING at 25 to 36, BLOCKED below 25.
- Priority thresholds and band comparisons ignore floating-point noise below `1e-9`.
- Respondent divergence is flagged when at least 3 respondents have a dimension score and the standard deviation of their own dimension scores is 1.0 or more.

## Evidence cross-checks

If `output/repo-scan.json`, `output/telemetry.json` or `output/dora-metrics.json` exists, report any evidence cap or warning surfaced by the engine. These files challenge answers but do not change scores.

## Output

- `output/scores.json`
- Also refreshed by `all`: `output/gaps.json`, `output/recommendations.json`

## Chat response

Report framework detected, overall score and band, coverage status, respondent divergence, evidence warnings, and next step. If the script lists invalid levels or schema issues, stop and show those IDs.
