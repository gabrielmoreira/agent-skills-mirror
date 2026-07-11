# Goal Alignment And Candidate Task Design

## Contents

- Boundary With task-clarifier
- Goal Alignment Workflow
- Task Fit Assessment
- Candidate Plan Format
- Writing To task-forest
- Anti-Patterns And Fallbacks

## Boundary With task-clarifier

`task-clarifier` decides:

- whether to ask the user;
- whether to ask one question, batch questions, offer method choices, or run an intent interview;
- whether to research, confirm risk, or block before execution.

`task-forest` decides:

- what the current work means inside the global task graph;
- which global goal it serves;
- whether the proposed task can achieve the user's purpose;
- which candidate task plan would serve the purpose more effectively;
- how candidate plans compare on feasibility, effectiveness, accuracy, completeness, stability, robustness, and complexity.

Keep task-clarifier focused on need alignment. Keep task-forest focused on graph structure, candidate task plans, and purpose-to-task fit.

## Goal Alignment Workflow

When the user proposes a new task, changes a task, asks to generate tasks, or the current session purpose is unclear:

1. Read the current graph:

```bash
python3 scripts/task_forest.py list --json
python3 scripts/task_forest.py todo --json
```

2. Apply `$task-clarifier` rules for any decision about asking the user, researching first, offering method choices, confirming risk, or blocking. This file must not define its own clarification route.

3. Convert the confirmed purpose into structured fields:

```text
user_goal: the result the user wants
why_now: why this matters now
success_metrics: how success will be recognized
constraints: hard boundaries
non_goals: explicit exclusions
risk_tolerance: preference across complexity, accuracy, speed, and stability
```

4. Align the purpose with the task forest:

- If it fits an existing global task, use `child_of` or update the existing node.
- If it serves multiple goals, choose one primary parent and connect the rest with `contributes_to`.
- If it does not belong under any existing global task, create a `global_task`.
- If the existing task cannot achieve the purpose, create a better candidate plan.

## Task Fit Assessment

Assess each candidate task with at least:

```text
fit: aligned | partial | weak | misaligned | unknown
why_this_task: how it serves the user's purpose
why_not_enough: uncovered needs or risks
feasibility: low | medium | high
effectiveness: low | medium | high
accuracy: low | medium | high
completeness: low | medium | high
stability: low | medium | high
robustness: low | medium | high
complexity: low | medium | high
confidence: 0.0-1.0
validation_plan: how to verify the task achieved the purpose
```

For `weak`, `misaligned`, or `unknown` fit, ask a clarifying question, record a risk, or propose a stronger candidate. Do not mark the task as `ready`.

## Candidate Plan Format

When the user needs to choose among task plans, offer 2-3 meaningfully different options.

```text
I understand your real goal as: ...

Option A: Low-complexity quick version
- Task:
- Why it fits:
- Coverage:
- Gaps:
- Feasibility:
- Effectiveness:
- Accuracy:
- Completeness:
- Stability/robustness:
- Cost:
- Validation:

Option B: Balanced version (recommended)
...

Option C: High-completeness version
...

My recommendation: B, because ...
The decision needed from you is: speed first, balanced, or completeness first.
```

Each option must be executable. Avoid filler options.

## Writing To task-forest

After confirmation, create a proposal. Important node fields should include:

```json
{
  "purpose": "the user's real goal",
  "desired_outcomes": ["expected result"],
  "success_metrics": ["signals that the goal is achieved"],
  "non_goals": ["explicit exclusions"],
  "assumptions": ["key assumptions"],
  "alignment": {
    "user_goal": "the user's real goal",
    "fit": "aligned",
    "fit_confidence": 0.85,
    "why_this_task": "why this task serves the goal",
    "why_not_enough": "remaining gaps",
    "validation_plan": ["verification steps"]
  }
}
```

To preserve an alignment audit, add this to the proposal:

```json
{
  "action": "record_alignment",
  "alignment": {
    "related_task_ids": ["TF-0001"],
    "user_goal": "the user's real goal",
    "candidate_summary": "summary of candidate task plans",
    "selected_option": "B",
    "rejected_options": ["A", "C"],
    "reason": "why B was selected",
    "node_alignment": {
      "user_goal": "the user's real goal",
      "fit": "aligned",
      "fit_confidence": 0.85,
      "why_this_task": "why it fits",
      "why_not_enough": "remaining boundary",
      "validation_plan": ["how to verify"]
    },
    "confidence": 0.85
  }
}
```

## Anti-Patterns And Fallbacks

Avoid:

- creating a task while the user's purpose is unclear;
- treating the requested action as the user's real outcome without checking fit;
- generating weak options to reach an option count;
- describing the task without describing how it serves the global purpose;
- ignoring the risk that a task may fail to achieve the purpose.

Fallbacks:

- Unclear purpose: ask one `$task-clarifier` style question.
- Unreliable plans: say the information is insufficient and save a `question` node or proposal.
- Task-purpose conflict: record `record_deviation` or add a `risk` node.
- User wants quick progress: give one recommended plan and two brief alternatives with assumptions.
