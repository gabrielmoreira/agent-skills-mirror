---
name: incremental-change-cycle
description: Use when the user explicitly asks to run the incremental change cycle after adding code or changing function behavior, especially for long-running or high-token work where checklist continuity and repeated review checkpoints matter.
---

# Incremental Change Cycle

## Overview

Run the explicit workflow for incremental code changes: reconcile task state, perform a review checkpoint, run `simplify`, verify the touched code, and keep every checklist synchronized. This skill is the workflow controller; `simplify` remains the cleanup pass.

## When to Use

Use this skill only when the user explicitly asks for the incremental change cycle or clearly requests the review-checklist-simplify-verify workflow after an incremental edit.

Do not use this skill for:
- a standalone simplify pass
- broad feature planning
- full PR authoring unless the user explicitly asks for PR creation

## Role Boundaries

- `review checkpoint` checks correctness, scope, regressions, and readiness to continue.
- `simplify` performs behavior-preserving cleanup on the changed scope.
- this skill coordinates the workflow and task-state continuity across those steps.

If the user says `PR`, interpret it as a review checkpoint unless they clearly mean an actual pull request.

## Workflow

1. Identify the current change scope.
2. Load the active checklist or create one if none exists.
3. If multiple checklists exist for the same workflow, reconcile them before continuing.
4. Mark the current task as `in_progress` if a checklist supports explicit states.
5. Run a review checkpoint on the changed scope.
6. Address any blocking findings from the review checkpoint.
7. Run `simplify` on the changed scope.
8. Run the most relevant verification for the touched code.
9. Immediately update every relevant checklist after each completed task or checkpoint.
10. Before stopping, confirm the checklists agree on what is done and what remains.

## Checklist Rules

- Always reuse an existing checklist if it already tracks the current workflow.
- Keep completed and remaining items explicit.
- Consult the checklist before starting the next task.
- Re-check the checklist after interruptions or context compression.
- Never leave a task completed in one checklist and incomplete in another.

## Multiple Checklist Synchronization

If multiple checklists exist for the same workflow:

1. Treat them as synchronized views of the same task set.
2. After completing any task, update every relevant checklist before moving on.
3. If a task is only partially done, do not mark it complete anywhere.
4. Resolve status mismatches first; do not continue while checklists disagree.
5. If one checklist is the source of truth, update it first and propagate the same state immediately.

## Continuity And Recovery

Because Codex does not provide a public hooks system for this workflow, this skill must perform the continuity checks itself.

Before resuming work after a pause, interruption, or context compression:

1. Re-read the active checklist or checklists.
2. Reconstruct the current task, completed tasks, and remaining tasks from those checklists.
3. Confirm that the current change scope still matches the recorded task state.
4. Resolve any checklist drift before doing more implementation work.

If state cannot be reconstructed confidently:

- stop and ask for clarification rather than guessing
- do not restart already completed work just because context is thin

## Stop-Time Guard

Do not conclude the workflow while any of these are still missing for the current incremental change:

- review checkpoint
- simplify pass
- relevant verification
- checklist synchronization

Before stopping, explicitly confirm:

1. the current task is actually complete
2. review checkpoint has been performed
3. `simplify` has been run on the changed scope
4. verification has been run or its absence has been stated
5. all relevant checklists reflect the same state

## Review Checkpoint

The review checkpoint should answer:

- did the change implement the intended scope?
- is the behavior correct?
- are there regressions or obvious risk gaps?
- is the current task actually complete?
- do the checklists match the real execution state?

Use a local review pass by default. Only escalate to an actual pull request flow if the user asked for it.

## Common Mistakes

- treating `simplify` as a substitute for review checkpoint
- generating a fresh checklist when a valid one already exists
- forgetting to sync multiple checklists after finishing a task
- using `PR` to mean actual PR creation when the user only wanted a review gate
- stopping after code changes without a review checkpoint, simplify pass, and verification
- resuming after interruption without re-reading the checklist state
- trusting memory over checklist state when the two disagree
