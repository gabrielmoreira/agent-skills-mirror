---
name: gap-analysis
description: Computes v2 dimension gaps and priorities, or archived v1 capability gaps, by invoking scripts/assessment_engine.py. Use for "gap analysis", "analise de gaps", "prioritize gaps", "where are my gaps", "análisis de brechas", "priorizar brechas".
---

# Skill: Gap analysis

Always use the deterministic engine. Do not calculate gaps manually.

## Command

```bash
python3 scripts/assessment_engine.py all
```

`make scores` is also acceptable.

## v2 rules documented by the script

- Gap is `target - score`.
- Default target is `3.0`.
- `target_overrides` can override per dimension.
- Priority score is `dimension_weight x gap`.
- Priority bands: P0 at `>= 2.4`, P1 at `>= 1.6`, P2 at `>= 0.9`, else P3.
- Band and priority comparisons ignore floating-point noise below `1e-9`.
- Phases and horizons used by the implementation guide come from the engine: P0 first 30 days, P1 next quarter, P2 semester, P3 backlog.

## Flags to report

Report low confidence, amplification risk, perception gap, respondent divergence, scope caveat, unverified L3/L4, evidence cross-check warnings, persona summaries, and backlog items when present in `output/gaps.json` or related output.

## v2 output

- `output/gaps.json`
- Top gaps by dimension and question.
- Backlog questions with L3 anchors, evidence to collect, and KPI where present.

## Chat response

Summarize the P0 to P3 distribution, top priorities, coverage status, and flags. Include the next command: `python3 reports/scripts/build_payload_and_render.py` after recommendations are ready.
