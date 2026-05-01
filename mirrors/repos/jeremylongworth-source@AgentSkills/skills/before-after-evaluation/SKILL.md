---
name: before-after-evaluation
description: Compare baseline and skill-enabled agent outputs. Use when Codex is asked to run, simulate, or document a before/after skill evaluation, decide whether a skill improved an output, or write a skill evaluation report.
license: MIT
---

# Before/After Evaluation

## Core Workflow

1. Confirm the scenario, target artifact, acceptance criteria, and compared
   conditions.
2. Summarize the baseline output and the skill-enabled output using the same
   criteria.
3. Score improvements and regressions with the project rubric.
4. Separate missing context from skill failure.
5. Record safety issues, reviewer edits, validation evidence, and overhead.
6. Recommend keep, revise, split, merge, defer, or retire.

## Safety Rules

- Do not hide regressions or unsafe assumptions because the skill helped other
  criteria.
- Do not publish private prompts, customer data, or sensitive outputs in public
  reports.
- Do not claim a skill works broadly from one easy scenario.
- Require human review for high-risk domains and production-impacting outputs.

## Deliverable Shape

For before/after reports, provide:

- Scenario and target artifact
- Baseline result summary
- Skill-enabled result summary
- Rubric scores
- Improvements and regressions
- Safety and evidence notes
- Overhead notes
- Promotion decision and follow-up changes

## References

- Read `references/before-after-evaluation-checklist.md` when preparing a
  before/after skill evaluation.
