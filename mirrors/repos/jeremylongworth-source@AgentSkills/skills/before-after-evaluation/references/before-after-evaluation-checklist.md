# Before/After Evaluation Checklist

## Inputs

- Scenario file:
- Source material:
- Baseline condition:
- Skill-enabled condition:
- Target artifact:
- Acceptance criteria:

## Compare

- Correctness
- Completeness
- Artifact usefulness
- Evidence handling
- Safety boundaries
- Validation behavior
- Concision
- Context/tool overhead
- Reviewer edit burden

## Report

Use `docs/evaluation/before-after-report-template.md`.

Required decision:

- keep
- revise
- split
- merge
- defer
- retire

## Common Failure Modes

- The prompt gave away the expected answer.
- The skill improved formatting but not decision quality.
- The skill added broad stale context.
- The output became more confident without better evidence.
- The report ignored a safety regression.
