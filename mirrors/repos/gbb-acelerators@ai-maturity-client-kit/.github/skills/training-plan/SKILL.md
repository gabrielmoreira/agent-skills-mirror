---
name: training-plan
description: Generates a prioritized learning and training plan from the Learning and Growth Survey. Use for "plano de capacitacao", "training plan", "learning roadmap", "plan de capacitación".
---

# Skill: Training plan

Use the existing survey-learning scripts and outputs. Do not derive cohorts, rankings, or mentor matches by hand when scripts exist.

## Command

```bash
python3 survey-learning/scripts/generate_training_plan.py
```

Pass `--lang pt-br` or `--lang es` for PT-BR or Spanish output (default EN).

## Dimension names

Use `DS-D#` for Developer Survey dimensions in cohorts and cross-survey references. Do not use bare `D2` to `D8` for survey dimensions when v2 assessment dimensions are nearby.

## Cross-reference to v2

Connect the plan to v2 without changing scores:

- D2: enablement, skills, culture.
- D5: review, quality, testing, verification culture.
- D9: measurement, value, AI FinOps.

## Wizard Mode D

After generating the plan, Mode D fills 7 of 11 implementation guide fields:

```bash
python3 wizard/scripts/auto_fill_from_plan.py --lang en
```

## Output

Reference `output/training-plan-<date>.md`. Summarize top topics, cohorts, Champions, mentor pairs, and 90-day plan when present.
