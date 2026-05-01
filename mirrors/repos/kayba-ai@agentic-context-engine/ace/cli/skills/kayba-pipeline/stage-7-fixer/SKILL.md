---
name: kayba-stage-7-fixer
description: Implement the approved fixes from the action plan and log all changes. Trigger when the user says "run stage 7", "implement fixes", "apply action plan", or when invoked by the kayba-pipeline orchestrator. Requires eval/action_plan.md to exist.
---

# Stage 7: Fix Implementation

Implement every non-discarded fix from the approved action plan.

## Inputs

- `eval/action_plan.md` -- the approved action plan from Stage 5 (possibly modified during HITL in Stage 6)
- `eval/stage6_decision.md` -- if it exists, the HITL decision record from Stage 6 (contains user modifications)
- `eval/baseline_metrics.json` -- the pre-fix baseline metrics from Stage 3 (for reference in changes log)

Read the action plan and stage6 decision (if present) before starting.

## Pre-flight: Git Safety Checkpoint

Before making ANY changes to source files:

1. Run `git status` to confirm the working tree state
2. Create a safety commit or stash:
   ```
   git stash push -m "pre-pipeline-fixes-$(date +%Y%m%d-%H%M%S)"
   ```
   If there are no uncommitted changes to stash, create a lightweight tag instead:
   ```
   git tag pre-pipeline-fixes-$(date +%Y%m%d-%H%M%S)
   ```
3. Record the stash ref or tag name in `eval/changes_log.md` under a "Rollback" section so the user can restore if needed

This ensures every fix is reversible with a single `git stash pop` or `git checkout`.

## Pre-flight: HITL Modification Check

If `eval/stage6_decision.md` exists:

1. Read it and identify any items the user modified, added, or re-prioritized during Stage 6
2. Build a set of `HITL_MODIFIED_IDS` -- the insight/skill IDs that the user changed
3. When logging each fix later, tag modified items with `[HITL-MODIFIED]` in the changes log so reviewers know which fixes reflect user judgment vs. the original pipeline output

If the file does not exist, assume no HITL modifications were made.

## Pre-flight: Conflict Scan

Before implementing any fixes, scan the action plan for potential conflicts:

1. Build a map of `file_path -> [fix IDs that touch it]`
2. If two or more fixes modify the same file, flag them as **co-located**
3. If two or more fixes modify the same section (within ~20 lines of each other), flag them as **overlapping**
4. For overlapping fixes: plan to apply them sequentially in priority order, re-reading the file between each edit to ensure the second fix still makes sense on top of the first
5. Log any detected conflicts at the top of `eval/changes_log.md` under a "Conflict Notes" section

## Process

Work through the action plan in priority order. For each non-discarded fix:

### 1. Understand the fix

- Read the recommendation carefully
- Read the referenced files in the codebase
- Understand the surrounding code before making changes
- Check if this fix was flagged as co-located or overlapping in the conflict scan. If overlapping with a previously-applied fix, re-read the target file to see the current state after prior edits

### 2. Implement the change

**For code fixes:**
- Find the relevant files
- Make the minimal, targeted change described in the recommendation
- Do not refactor surrounding code unless the fix obviously breaks without light adjacent cleanup (e.g., an import is missing, a variable was renamed). If you make adjacent cleanup, log it explicitly as "adjacent cleanup" in the change entry
- Do not add features beyond what was recommended

**For prompt fixes:**
- Find the system prompt file (use domain context from Stage 2 if needed)
- Add the recommended instruction at the appropriate location
- Do not rewrite existing prompt text unless the recommendation explicitly says to

### 3. Log the change

Append to `eval/changes_log.md`:

```markdown
## Fix N: [skill/insight name] [HITL-MODIFIED if applicable]
**Type:** code fix | prompt fix
**Verdict from action plan:** [quote the recommendation]
**Files modified:**
- `path/to/file.py` -- [what changed and why]
**Before:**
\```
[relevant snippet before change]
\```
**After:**
\```
[relevant snippet after change]
\```
**Linked metrics:** [which metrics this should improve]
**Conflict notes:** [if this fix overlapped with another, note it here; otherwise "none"]
```

### 4. Handle uncertainty (NEEDS REVIEW workflow)

If a fix requires changes you are unsure about:

1. Do NOT implement it
2. Log it as `NEEDS REVIEW` in the changes log with:
   - What specifically is unclear
   - What information would resolve the ambiguity
   - The files and lines you examined
3. **Continue to the next fix** -- do not block the pipeline
4. At the end of all fixes, collect all NEEDS REVIEW items into a dedicated section (see Output format below). The pipeline does NOT stop; these items are presented to the user after all other fixes are applied.

## Post-Fix: Next Steps (Do NOT Re-run Baselines)

Do NOT re-run `compute_baselines.py` as part of this stage. The baseline metrics were computed against the original traces, which reflect old agent behavior. Re-running against the same traces will show zero movement for prompt-only fixes and is misleading.

Instead, after all fixes are applied, include a **Next Steps** section in the changes log that tells the user:

1. Generate new traces by running the agent with the updated prompts/code
2. Then re-run baselines against the new traces:
   ```bash
   python eval/compute_baselines.py --traces-dir <new_traces_folder> --output eval/post_fix_metrics.json
   ```
3. Compare `eval/post_fix_metrics.json` against `eval/baseline_metrics.json` to measure actual improvement

## Rules

- Do NOT modify trace files
- Do NOT make changes beyond what the action plan recommends (except adjacent cleanup logged explicitly)
- Make minimal, targeted changes -- don't clean up or refactor surrounding code
- If the action plan says "discard", skip that entry entirely
- You MAY write `eval/changes_log.md` as the primary output
- Do NOT run `eval/compute_baselines.py` -- baselines should only be re-computed after new traces are generated with the updated agent

## Output format

Write `eval/changes_log.md`:

```markdown
# Changes Log

## Rollback
- **Safety ref:** `git stash` ref or tag name
- **To undo all fixes:** `git stash pop` or `git checkout <tag>`

## Conflict Notes
- [any file/region conflicts detected, or "No conflicts detected"]

## Summary
- Code fixes applied: N
- Prompt fixes applied: M
- Skipped / needs review: K
- HITL-modified items: J

---

## Fix 1: [skill name]
...

## Fix 2: [skill name]
...

---

## Needs Review
[Collected list of all NEEDS REVIEW items with context, or "None -- all fixes applied successfully"]

For each NEEDS REVIEW item:
- **Fix N: [skill name]**
- **What is unclear:** [specific ambiguity]
- **What would resolve it:** [information needed]
- **Files examined:** [paths and lines]

---

## Next Steps

To measure actual improvement:
1. Generate new traces by running the agent with the updated prompts/code
2. Re-run baselines:
\```bash
python eval/compute_baselines.py --traces-dir <new_traces_folder> --output eval/post_fix_metrics.json
\```
3. Compare `eval/post_fix_metrics.json` against `eval/baseline_metrics.json` to measure metric deltas
```

## Outputs

- `eval/changes_log.md` -- full log of all changes, conflicts, NEEDS REVIEW items, and next steps
- The actual code/prompt changes in the repository
- A git stash or tag for rollback
