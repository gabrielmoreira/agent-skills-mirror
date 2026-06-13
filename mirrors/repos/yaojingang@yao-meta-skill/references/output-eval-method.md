# Output Eval Method

Output Eval Lab proves whether a skill improves the final user-facing result, not only whether it routes correctly.

## When To Use

Use output evals for production, library, governed, or team-distributed skills. Scaffold skills can start with one smoke case, but production and above should show a positive with-skill vs baseline signal before promotion.

## Case Design

Each case should include:

- a real prompt or task shape
- any required input files
- a baseline output that represents doing the task without the skill
- a with-skill output that represents the skill-guided behavior
- assertions that can be checked without subjective guessing
- optional human review notes for taste, completeness, or judgment

## Assertion Rules

Prefer assertions that catch material quality:

- required deliverable paths
- required sections or contracts
- required boundary or exclusion language
- required evidence paths
- forbidden generic placeholders
- forbidden unsafe actions

Avoid assertions that only reward wording memorization. If a case can pass by parroting one phrase while failing the real job, the assertion is too narrow.

## Score Reading

The first v0 scorecard reports:

- baseline pass rate
- with-skill pass rate
- absolute delta
- failed assertions and failure taxonomy
- recommended next fixes

Production promotion should require the with-skill pass rate to beat baseline and should explain every failed assertion.

## Anti-Overfitting

Keep a small public smoke set and a separate holdout set. Rotate real failures into the taxonomy instead of editing only the prompt that failed. Add near-neighbor cases whenever the output looks good but the boundary is still unclear.
