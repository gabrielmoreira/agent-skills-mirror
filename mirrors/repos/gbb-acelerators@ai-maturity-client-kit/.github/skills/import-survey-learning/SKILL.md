---
name: import-survey-learning
description: Imports Learning and Growth Survey Microsoft Forms exports using the existing survey-learning tooling. Use for "import learning survey", "learning survey import", "importar survey learning", "importar la encuesta de aprendizaje".
---

# Skill: Import Learning and Growth Survey

Use existing survey-learning tooling. The Learning Survey is identified and supports the training plan and implementation guide wizard.

## Dimension names

Learning Survey question labels use `L#-Q#`. When they reference Developer Survey dimensions, use `DS-D#`, for example `L2-Q1: DS-D2 Copilot Adoption ...`.

## Procedure

Run the repository script documented under [survey-learning/](../../../survey-learning/). Keep outputs in `output/` and report respondent count, warnings, and next step.

## Cross-reference to v2

Use learning demand and cohort data to enrich v2 D2, D5, and D9 narrative. Do not change assessment scores from this survey.
