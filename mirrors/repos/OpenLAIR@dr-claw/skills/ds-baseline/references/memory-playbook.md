# Baseline Memory Playbook

Use this reference when deciding what should be stored in quest memory versus global memory during `baseline`.

## Quest memory

Use quest memory for:

- baseline-specific setup failures
- dataset or metric caveats tied to this quest
- route-selection rationale
- paper-to-code mismatch notes
- accepted baseline caveats that later stages must remember

## Global memory

Promote to global only when the lesson is reusable, such as:

- stable environment fixes
- reproducibility heuristics
- verification heuristics
- broadly useful dataset or benchmark caveats

## Kinds

- `episodes`:
  - failures
  - repair attempts
  - environment incidents
- `knowledge`:
  - stable lessons
  - reproducibility rules
  - accepted caveats
- `decisions`:
  - route and acceptance rationale

## Promotion rule

Do not promote a lesson to global just because it was painful.
Promote it only if another quest is likely to benefit from it.
