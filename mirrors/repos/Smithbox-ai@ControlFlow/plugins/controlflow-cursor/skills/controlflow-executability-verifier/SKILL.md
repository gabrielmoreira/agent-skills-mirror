---
name: controlflow-executability-verifier
description: "Use when a saved plan should be tested for cold-start executability before coding, especially for large tasks, weak-confidence plans, or plans whose early phases may be too vague for a fresh executor to follow without hidden context."
---

# ControlFlow Executability Verifier

## Overview

Simulate the plan as if a fresh agent had only the saved artifact and the repository. This skill adapts ControlFlow's ExecutabilityVerifier to Codex by identifying whether the first tasks are specific enough to execute without invisible assumptions.

## Workflow

1. Read the saved plan artifact first.
2. Simulate only the first few phases or tasks that matter for cold-start execution.
3. For each task, apply an 8-point checklist from [references/executability-checklist.md](references/executability-checklist.md):
   - what_clear
   - where_clear
   - how_clear
   - inputs_defined
   - outputs_defined
   - dependencies_met
   - verify_command_complete
   - test_specifics_concrete
4. Walk through the task using the TDD walk-through from [references/executability-checklist.md](references/executability-checklist.md):
   - open_file
   - read_existing_code
   - write_test_red
   - run_test
   - write_implementation_green
   - run_test_again
   - refactor
5. Stop at the first real blocker for a task and record exactly why it blocks execution.
6. Save the verdict to `plans/artifacts/<task-slug>/executability-verifier.md` using `../../templates/executability-verifier-report-template.md`.
7. Return a structured verdict:
   - `PASS`
   - `FAIL`
   - `WARN`
   - `ABSTAIN`

## Output Shape

- **Status**
- **Tasks Simulated**
- **Per-Task Checklist**
- **Walkthrough Summary**
- **Blocked Steps**
- **Recommendation**
- **Failure Classification** when needed

## Common Mistakes

- Simulating the plan with extra unstated context from memory.
- Continuing a task after a genuine blocker instead of stopping and recording it.
- Treating vague instructions as executable just because an experienced human could guess the intent.

## References

- `references/executability-checklist.md`
- `../../templates/executability-verifier-report-template.md`
