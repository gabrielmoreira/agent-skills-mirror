---
name: insights-developer-survey
description: Generates Developer Survey insights from imported survey outputs. Use for "developer survey insights", "insights survey devs", "maturidade dos devs", "insights de la encuesta de desarrolladores", "madurez de los desarrolladores".
---

# Skill: Developer Survey insights

The Developer Survey is a companion signal for v2. It is not a scoring input.

## Deterministic rule

Use the existing survey-devs scripts and generated JSON or Markdown artifacts. Do not score responses by hand.

## Languages

`python3 survey-devs/scripts/generate_insights.py --lang en|pt-br|es` writes the report in that language and shows answer options in it, whatever language the form used.

## Dimension naming

Developer Survey dimensions are `DS-D2` to `DS-D8`. Reserve `D1` to `D9` for the v2 assessment.

## Crosswalk to v2

Use the crosswalk from `framework.v2.json`:

- `DS-D2`: D4-Q1, D4-Q2, D9-Q1.
- `DS-D3`: D4-Q3, D4-Q6, D3-Q2, D6-Q1.
- `DS-D4`: D3-Q2, D5-Q5, D2-Q6.
- `DS-D5`: D2-Q4, D4-Q5.
- `DS-D6`: D4-Q4, D4-Q5.
- `DS-D7`: D2-Q2, D9-Q4.
- `DS-D8`: D1-Q2, D6-Q1, D6-Q4, D6-Q5, D6-Q7.

The insights report section 12 links to v2 questions, not v1 capabilities.

## Output

Write or reference `output/insights-developer-survey-<date>.md` and `output/developer-survey-maturity-<date>.json`. Re-run `make pipeline` if the user wants Developer Survey context in the v2 summary PDF.
