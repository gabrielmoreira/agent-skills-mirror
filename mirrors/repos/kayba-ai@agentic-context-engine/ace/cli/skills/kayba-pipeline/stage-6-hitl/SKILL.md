---
name: kayba-stage-6-hitl
description: Human-In-The-Loop gate that presents the action plan with full context, collects an informed approval/modification/rejection decision, and records the outcome. Trigger when the user says "run stage 6", "HITL review", "approve action plan", or when invoked by the kayba-pipeline orchestrator. Requires eval/action_plan.md and eval/baseline_metrics.md to exist.
---

# Stage 6: Human-In-The-Loop Gate

Present the action plan with enough context for an informed decision, collect the user's approval, and record the outcome.

The goal is not rubber-stamping. The user must receive enough information to genuinely evaluate, modify, or reject the plan -- even if they have not seen Stages 1-5.

## Inputs

- `eval/action_plan.md` -- the prioritized action plan from Stage 5
- `eval/baseline_metrics.md` -- the evaluation rubric with baseline values
- `eval/baseline_metrics.json` -- raw metric data (for exact numerator/denominator counts)
- `eval/stage1_insights_summary.md` -- original insights (for trace evidence references)

Read all four files before starting.

## Process

### 1. Build the executive summary

Compute and present the following counts from the action plan:

- Total insights analyzed (raw count before deduplication)
- Distinct actionable items after deduplication
- Breakdown: prompt fixes, code fixes, discarded
- Discard rate with one-line reason per discard (e.g., "5ac7f4ce: efficiency optimization, conflicts with turn discipline constraint")

Format:

```
EXECUTIVE SUMMARY
-----------------
Insights analyzed:    19 (raw) -> 12 distinct after dedup
Actionable:           9  (8 prompt fixes, 1 code fix)
Discarded:            3  (reasons listed below)

Discards:
  - 5ac7f4ce (Upfront Info Collection): conflicts with higher-priority turn discipline
  - fe2d51cb (Proactive Reservation Lookup): already default behavior, no failure evidence
  - 1fa1b826 (Cancellation Denial Enumeration): subsumed into cancellation checklist
```

### 2. Present the top 3 highest-impact changes

For each of the top 3 fixes by priority, present:

**Before/after behavior** -- use concrete examples from actual traces referenced in the insights. Quote the specific agent behavior that was wrong (before) and describe what the agent should do instead (after). Reference the trace task ID.

**Target metric delta** -- which metric(s) this fix targets, the current baseline value, and the expected direction. Do not fabricate precise target numbers. Use the format: "M1: 41.4% -> higher (target: 90%+)" only when the action plan provides a target; otherwise use "M1: 41.4% -> up".

**Risk rating** -- assess each fix:
- `Low` -- additive prompt instruction, no behavioral side effects expected
- `Medium` -- changes existing behavior, could affect adjacent workflows
- `High` -- modifies code/infrastructure, or could degrade a metric while improving another

Format each as a numbered block:

```
#1: Turn Discipline (covers 55c00c40, d9683144)
    Type:     prompt fix
    Metrics:  M1 (41.4% -> up), M2 (20.7% -> up)
    Risk:     Low

    BEFORE (task_1, task_5, task_7, ...):
      Agent batches 2-3 tool calls per turn (e.g., get_reservation + get_flight_status
      in a single response). Also includes user-facing text alongside tool calls.

    AFTER:
      Exactly one tool call per response. No user-facing content in tool-call turns.
      Agent processes each result before making the next call.
```

### 3. Present the full prioritized fix list

Display all non-discarded fixes in a table:

```
| Priority | Fix Name                          | Type       | Target Metrics  | Risk   | Effort |
|----------|-----------------------------------|------------|-----------------|--------|--------|
| 1        | Turn Discipline                   | prompt fix | M1, M2          | Low    | Low    |
| 2        | Post-Confirmation Execution       | prompt fix | M3              | Low    | Low    |
| 3        | Cancellation Checklist            | prompt fix | M5              | Low    | Low    |
| ...      | ...                               | ...        | ...             | ...    | ...    |
```

Effort ratings:
- `Low` -- single prompt addition, under 5 lines
- `Medium` -- multiple prompt additions or minor code change
- `High` -- significant code changes, new metric implementation, or architectural changes

### 4. Present "What we are NOT fixing and why"

List every discarded insight with:
- Insight ID and name
- One-line reason for discard
- What would change your mind (under what conditions should this be revisited)

This section exists so the user can override a discard if they disagree.

### 5. Flag small-sample and low-confidence items

Any metric with denominator < 5 must be explicitly called out:

```
LOW-CONFIDENCE METRICS (small sample size):
  - M5 (Cancellation Policy Compliance): based on 2 observations -- directional only
  - M6 (Compensation Execution Rate): based on 1 observation -- directional only

Fixes targeting these metrics (Cancellation Checklist, Compensation Rules) are
still recommended because the policy violations are clear from trace evidence,
but the measured improvement may not be statistically meaningful until the
trace corpus grows.
```

Also flag any fix where the action plan notes uncertainty or partial evidence.

### 6. Show the insight-to-fix traceability chain

For each fix, present the chain: insight -> metric -> fix -> expected improvement. This can be a compact list or a table. The purpose is to let the user verify that nothing was lost or invented between stages.

```
TRACEABILITY:
  55c00c40 (Tool Call Discipline) -> M1, M2 -> Skill 1 (Turn Discipline) -> M1 up, M2 up
  6ea141e1 (Execution Discipline) -> M3 -> Skill 2 (Post-Confirmation) -> M3 up
  0f4a952b + 6ce88ebb (Cancellation) -> M5 -> Skill 3 (Cancellation Checklist) -> M5 up
  ...
```

### 7. Collect the decision

Present exactly three options:

```
OPTIONS:
  [A] Approve all -- implement all 9 fixes as described
  [B] Approve with modifications -- review each fix individually
  [C] Reject -- return to Stage 5 with feedback
```

Use the appropriate mechanism to collect the user's choice (direct question or AskUserQuestion if available).

#### If the user selects [A] Approve all

Record the decision and proceed. No further interaction needed.

#### If the user selects [B] Approve with modifications

Walk through each fix individually, in priority order. For each fix, present:
- The fix name, type, and target metrics
- The recommended prompt/code change (quote the exact text from the action plan)
- Risk and effort ratings

Then ask: "Approve / Skip / Modify?"

- **Approve** -- keep as-is
- **Skip** -- remove from the plan, record reason
- **Modify** -- ask the user what to change, record the original and the modification

After walking through all fixes, present a summary of changes:
- Fixes approved as-is: N
- Fixes skipped: M (list with reasons)
- Fixes modified: K (list with what changed)

Ask for final confirmation: "Proceed with this modified plan?"

Then update `eval/action_plan.md`:
- Remove skipped fixes (move to a "Skipped by HITL" section at the bottom with reasons)
- Update modified fixes with the user's changes, preserving the original recommendation in a "Original recommendation" sub-field
- Add a header note: "Modified during HITL review on [date]. See eval/stage6_decision.md for details."

#### If the user selects [C] Reject

Ask the user for specific feedback:
- What was wrong with the plan?
- Which insights or metrics should be reconsidered?
- Any new constraints or priorities?

Record the feedback in `eval/stage6_decision.md` and signal that Stage 5 should be re-run with the user's feedback incorporated.

## Output format

### eval/stage6_decision.md

Write this file regardless of which option was selected.

```markdown
# Stage 6: HITL Decision Record

## Date
[timestamp]

## Decision
[Approve all | Approve with modifications | Reject]

## What was presented
- Total insights: N (M distinct after dedup)
- Actionable fixes: X (Y prompt, Z code)
- Discarded: W
- Metrics: [list metric IDs and baselines]
- Low-confidence flags: [list metrics with small denominators]

## Top 3 changes presented
1. [fix name] -- [type] -- targets [metrics] -- risk [rating]
2. ...
3. ...

## Decision details

### If Approve all:
User approved all N fixes without modification.
Reasoning: [any reasoning the user provided, or "No additional reasoning provided"]

### If Approve with modifications:
| Fix | Original Status | Decision | Reason |
|-----|----------------|----------|--------|
| Turn Discipline | Priority 1 | Approved | -- |
| Compensation Rules | Priority 5 | Modified | User changed wording to... |
| Cabin Change Rules | Priority 8 | Skipped | User considers low priority |

Modifications detail:
- [Fix name]: Original: "..." -> Modified: "..." -- User rationale: "..."

### If Reject:
User feedback: [verbatim feedback]
Specific concerns: [list]
Re-run instructions for Stage 5: [what to change]

## Traceability snapshot
[Copy of the traceability chain from step 6, so the decision record is self-contained]
```

### eval/action_plan.md (updated, only if modifications were made)

If the user selected [B] and made changes:
- Add a modification header at the top of the file
- Update individual fix entries with user changes
- Move skipped fixes to a "Skipped by HITL" section
- Preserve original recommendations as sub-fields for auditability

## Rules

- Do NOT auto-approve. The entire point of this stage is human judgment.
- Do NOT summarize so aggressively that the user cannot evaluate. When in doubt, include more context.
- Do NOT proceed to Stage 7 until a clear approval (full or modified) is recorded.
- Do NOT modify `eval/action_plan.md` unless the user explicitly requests modifications.
- Do NOT skip the small-sample warnings. If M5 has denominator 2 and M6 has denominator 1, the user must know this.
- Do NOT fabricate target metric values. Use targets from the action plan when available; otherwise state direction only.
- Always present the "What we are NOT fixing" section. Omitting discards hides information the user needs.
- If the user asks clarifying questions, answer them fully before re-presenting the decision options.

## Outputs

- `eval/stage6_decision.md` -- full record of what was presented, decided, and why
- `eval/action_plan.md` -- updated only if the user selected "Approve with modifications"
