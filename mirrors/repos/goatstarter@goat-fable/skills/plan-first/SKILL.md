---
name: plan-first
description: Explore-then-plan protocol for complex work. Use before implementing anything that spans multiple files, changes architecture, touches shared interfaces, or has ambiguous requirements. Produces a reviewable plan with acceptance criteria before any code is written. Also invoked manually via /plan-first.
---

# Plan First

You are about to do work that is expensive to redo. The point of this protocol: discover the surprises during exploration, when they cost minutes, not during implementation, when they cost the session. Do not write or edit any production code until step 4.

## 1. Explore

Read the code the task will touch, and its neighbors:

- The files you expect to change, plus 2-3 sibling files of the same kind (to absorb the local conventions you must match).
- The callers/consumers of anything whose interface might change (grep for them; don't rely on memory).
- The existing tests for the area: they encode the behavioral contract, and they tell you how your change will be verified.
- Any prior art in the repo: a similar feature already implemented is your best spec.

Broad "where does X happen?" questions: delegate to a search subagent and keep the conclusions.

## 2. Draft the plan

Write it down (todo list, plan file, or plan mode: whatever the session offers). It must contain:

- **Goal** in one sentence, in your own words. If you can't write this sentence, you don't understand the task yet.
- **Acceptance criteria**: numbered, each independently checkable. These are what "done" will be measured against, so write them as checks you can actually run.
- **File-level changes**: which files change and roughly how; which files are explicitly NOT touched.
- **Sequence**: what order, and where the verification checkpoints are (after which steps do the tests run?).
- **Risks and unknowns**: the parts you're least sure about, and how you'll de-risk each (usually: verify the assumption first, cheaply).

## 3. Surface open questions, once

Collect every requirement ambiguity that materially changes the work, and ask them together in one round, each with your recommended default. One consolidated round of questions is respect for the human's time; a drip of questions across an hour is not. Minor choices don't go here: pick reasonably and note it in the plan.

If the human is unavailable and the ambiguity is non-destructive either way: state your chosen assumption prominently in the plan and proceed.

## 4. Execute against the plan

- One plan item at a time to verified-done; run the checkpoint verifications as scheduled, not batched at the end.
- Reality will disagree with the plan somewhere. When it does, update the written plan and say so; don't silently diverge. If the divergence changes scope or acceptance criteria, that's a question, not a judgment call.
- Finish with the acceptance criteria as your checklist: demonstrate each one.
