---
description: Implement tasks from an OpenSpec change (Experimental)
---

Implement tasks from an OpenSpec change.

**Input**: Optionally specify a change name (e.g., `/opsx:apply add-auth`). If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes and use the **AskUserQuestion tool** to let the user select

   Always announce: "Using change: <name>" and how to override (e.g., `/opsx:apply <other>`).

2. **Check status to understand the schema**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to understand:
   - `schemaName`: The workflow being used (e.g., "spec-driven")
   - Which artifact contains the tasks (typically "tasks" for spec-driven, check status for others)

3. **Get apply instructions**

   ```bash
   openspec instructions apply --change "<name>" --json
   ```

   This returns:
   - Context file paths (varies by schema)
   - Progress (total, complete, remaining)
   - Task list with status
   - Dynamic instruction based on current state

   **Handle states:**
   - If `state: "blocked"` (missing artifacts): show message, suggest using `/opsx:continue`
   - If `state: "needs_verify"`: skip back to Phase 1 and run canonical verification
   - If `state: "needs_seal"`: skip implementation and continue with Phase 2/3
   - If `state: "all_done"`: congratulate, suggest archive
   - Otherwise: proceed to implementation

4. **Read context files**

   Before reading other context files, check whether `openspec/project.opsx.yaml` exists.
- If it exists, read it first for domains → capabilities structure
- Check `openspec/project.opsx.code-map.yaml` for code location references
- Check `openspec/specs/` for behavior documentation
- Treat it as navigation context, not as a replacement for change artifacts

   Read the files listed in `contextFiles` from the apply instructions output.
   The files depend on the schema being used:
   - **spec-driven**: proposal, specs, design, tasks
   - Other schemas: follow the contextFiles from CLI output
   - Build `path.join(changeDir, '.verify-result.json')` and check whether the previous verify result exists
   - Read `.verify-result.json` defensively: newer results may include an `optimization` object in addition to `result`, `issues`, and `verificationContext`
   - If the file exists and `result === 'FAIL_NEEDS_REMEDIATION'`:
     - Read the persisted `issues` array
     - Keep only CRITICAL issues as mandatory remediation context
   - If `optimization.status` is `DEGRADED` or `ABORTED_UNSAFE`, treat it as advisory context only; do NOT let it override the canonical Phase 1 remediation signal
   - If `tasks.md` contains a `## Remediation` section:
     - Parse each checkbox item
     - Track whether the item is tagged `[code_fix]` or `[artifact_fix]`
     - Treat unchecked remediation items as priority work

**Document Language Contract**:
- Treat `openspec/config.yaml` as the compact source of truth, but consume its compiled prompt projection rather than reinterpreting raw keys ad hoc
- If the compiled projection includes `docLanguage`, apply it only to natural-language prose you write in the artifact body
- Follow the existing template structure exactly; do not invent a different layout because the prose language changes
- Keep template headings, IDs, schema keys, relation types, BDD keywords, file paths, commands, and code identifiers in their canonical form
- If no `docLanguage` projection is present, keep the default writing behavior for prose

5. **Show current progress**

   Display:
   - Schema being used
   - Progress: "N/M tasks complete"
   - Remaining tasks overview
   - Summary of prior CRITICAL verify issues when `.verify-result.json` reports `FAIL_NEEDS_REMEDIATION`
   - Summary of open remediation items grouped by `[code_fix]` and `[artifact_fix]`
   - Dynamic instruction from CLI

6. **Phase 0: Implement tasks (loop until done or blocked)**

   For each pending task:
   - Show which task is being worked on
   - If the task was unmarked by verify, inject the matching CRITICAL issue and remediation item into the working context before editing files
   - Prioritize unchecked remediation entries before unrelated polish work
   - Make the code changes required
   - For `[code_fix]` remediation items, update code/tests until the missing behavior is implemented
   - For `[artifact_fix]` remediation items, update the affected spec/design/tasks artifact instead of forcing code changes
   - Keep changes minimal and focused
   - Mark task complete in the tasks file: `- [ ]` → `- [x]`
   - Mark resolved remediation items complete in the `## Remediation` section
   - Continue to next task

   **Pause if:**
   - Task is unclear → ask for clarification
   - Implementation reveals a design issue → suggest updating artifacts
   - Error or blocker encountered → report and wait for guidance
   - User interrupts

7. **Phase 1: Run canonical verification**

   After all implementation tasks and remediation items are complete:
   - Spawn a clean-context reviewer subagent with change artifacts, git evidence, final file contents, and prior `.verify-result.json` when present
   - Instruct the subagent to invoke the `openspec-reviewer` skill, which loads the full reviewer contract (role, constraints, 6-step verification protocol, severity thresholds, three-dimension coverage, structured output schema)
   - Keep completeness, correctness, and coherence judgment inside the reviewer subagent
   - If the reviewer returns `FAIL_NEEDS_REMEDIATION`, write back only CRITICAL issues to `tasks.md`, add typed `## Remediation` entries, and return to Phase 0
   - If the reviewer returns `PASS` or `PASS_WITH_WARNINGS`, persist Phase 1:
     ```bash
     openspec verify phase1 "<change-name>" --input '<json>' --json
     ```

**Verify CLI JSON Schema Reference**:

| CLI call | `--input` JSON |
| --- | --- |
| `openspec verify phase1 "<change-name>" --input '<json>' --json` | `{"result":"PASS","issues":[],"evidenceFiles":["..."],"executionMode":"..."}` |
| `openspec verify phase2 "<change-name>" --type=optimization --input '<json>' --json` | `{"status":"NO_OPTIMIZATION_NEEDED","summary":"..."}` (summary is required, must be non-empty) |
| `openspec verify phase2 "<change-name>" --type=optimization --files "<affected-files>" --input '<json>' --json` | `{"status":"OPTIMIZATION_PROPOSED","summary":"..."}` |
| `openspec verify phase2 "<change-name>" --type=optimization --input '<json>' --json` | `{"status":"SKIPPED"}` |
| `openspec verify phase2 "<change-name>" --type=verification --input '<json>' --json` | `{"result":"PASS","issues":[]}` |
| `openspec verify phase2 "<change-name>" --type=verification --input '<json>' --json` | `{"result":"FAIL_NEEDS_REMEDIATION","issues":[...],"behaviorRetryCounter":N}` |

8. **Phase 2: Optimize under checkpoint protection**

   **Role constraint**: The master agent is an evidence collector and patch applicator in Phase 2. It MUST NOT substitute its own judgment for the optimizer subagent's decision on whether optimization is needed. Always spawn the optimizer subagent as the first action in Phase 2.

   - Skip Phase 2 only when the user requested `--skip-optimization` or `optimization.enabled: false`; record `SKIPPED` through `openspec verify phase2`
   - Read `optimization.optRetries` from `openspec/config.yaml`; default to `2`
   - Before the first optimization attempt, create a checkpoint: `git stash push -u -m "apply-opt-checkpoint-r0"`
   - Each complete proposal + patch + reviewer re-verify loop consumes one `optRetries` budget, whether it passes or fails
   - Format or Search/Replace matching problems are handled by the main agent and do not consume retry budget
   - Optimizer subagent: spawn and instruct to invoke the `openspec-optimizer` skill (loads full optimizer contract: role, constraints, optimization principles, Search/Replace format, failed directions protocol). Proposes Search/Replace blocks only; it MUST NOT edit files
   - **TIMING CONSTRAINT — hashFiles() samples disk state; the following order is mandatory:**
     1. Main agent calls `openspec verify phase2 "<change-name>" --type=optimization --files "<affected-files>" --input '<json>'` to record `OPTIMIZATION_PROPOSED` with pre-patch file hashes (disk MUST still be in pre-patch state at this point)
     2. Main agent applies Search/Replace blocks atomically (disk transitions to post-patch state)
     3. Main agent spawns the reviewer subagent for speculative Phase 1 re-verification
   - On speculative PASS, record `verification PASS`, and continue until no opportunities remain or `optRetries` is exhausted
   - On speculative FAIL, restore the latest checkpoint with `git reset --hard HEAD`, `git clean -fd`, then `git stash apply stash@{0}`; record the failed direction in `.verify-result.json`
   - When all attempts finish, consume all `apply-opt-checkpoint-*` stash entries only after the final safe workspace state is confirmed

**Simple Change Fast Path**:
- You MUST spawn the optimizer subagent at least once for every change, including pure deletions, renames, or parameter removals
- The optimizer subagent (not the master agent) decides whether optimization opportunities exist
- If the optimizer subagent returns "No optimization opportunities found", record `NO_OPTIMIZATION_NEEDED` with the optimizer's conclusion as the `summary` field:
  ```bash
  openspec verify phase2 "<change-name>" --type=optimization --input '{"status":"NO_OPTIMIZATION_NEEDED","summary":"<optimizer conclusion>"}' --json
  ```
- The master agent MUST NOT self-determine that no optimization is needed without spawning the optimizer subagent
- The only conditions that bypass the optimizer subagent are: `--skip-optimization` flag or `optimization.enabled: false` in config

**Verify CLI Error Recovery Guide**:
- If the CLI says `Invalid JSON input`: re-check that `--input` is a JSON string, not a file path; `issues` must be an array and `evidenceFiles` must be an array of strings
- If the CLI says `status must be NO_OPTIMIZATION_NEEDED, OPTIMIZATION_PROPOSED, ABORTED_UNSAFE, or SKIPPED`: fix the `--input.status` value and confirm whether `optimization.status` already has `affectedFileHashes`
- If the CLI says `result must be PASS, PASS_WITH_WARNINGS, or FAIL_NEEDS_REMEDIATION`: fix the `--input.result` value and keep `issues` as an array when provided
- If the CLI says `尚未提交优化结果，请先调用 phase2 --type=optimization`: call `phase2 --type=optimization` before retrying verification
- If the CLI says `FILES_REQUIRED`: add `--files "<affected-files>"` with the space-separated list of files the optimizer subagent declared as affected, then retry the same command

**Verify State Machine**:
```
Phase 1 PASS / PASS_WITH_WARNINGS
  |
  v
PENDING_VERIFICATION
  |-- no affectedFileHashes --> Phase 2 optimization analysis
  |                              |-- NO_OPTIMIZATION_NEEDED --> NOT_NEEDED
  |                              |-- SKIPPED / optimization.enabled=false --> SKIPPED
  |-- affectedFileHashes ------> PENDING_VERIFICATION (optimization proposed)
                                 |-- verification PASS --> IMPROVED
                                 |-- verification FAIL_NEEDS_REMEDIATION --> retry or DEGRADED
                                 |-- retries exhausted --> DEGRADED

Archive gate accepts: SKIPPED | NOT_NEEDED | IMPROVED | DEGRADED
Archive gate rejects: PENDING_VERIFICATION | ABORTED_UNSAFE
```

9. **Phase 3: Seal final result**

   Run:
   ```bash
   openspec verify seal "<change-name>" --json
   ```

   If seal passes, report apply as complete with verified and optimized status. If seal fails, preserve diagnostics and pause for remediation.

10. **On completion or pause, show status**

   Display:
   - Tasks completed this session
   - Overall progress: "N/M tasks complete"
   - If remediation items were resolved, report that Phase 1 must pass before archive
   - If all done: suggest archive
   - If paused: explain why and wait for guidance

**Output During Implementation**

```
## Implementing: <change-name> (schema: <schema-name>)

Working on task 3/7: <task description>
[...implementation happening...]
✓ Task complete

Working on task 4/7: <task description>
[...implementation happening...]
✓ Task complete
```

**Output On Completion**

```
## Implementation Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 7/7 tasks complete ✓

### Completed This Session
- [x] Task 1
- [x] Task 2
...

All tasks complete and sealed. You can archive this change with `/opsx:archive`.
```

**Output On Pause (Issue Encountered)**

```
## Implementation Paused

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 4/7 tasks complete

### Issue Encountered
<description of the issue>

**Options:**
1. <option 1>
2. <option 2>
3. Other approach

What would you like to do?
```

**Guardrails**
- Keep going through tasks until done or blocked
- Always read context files before starting (from the apply instructions output)
- If task is ambiguous, pause and ask before implementing
- If implementation reveals issues, pause and suggest artifact updates
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task
- Pause on errors, blockers, or unclear requirements - don't guess
- Use contextFiles from CLI output, don't assume specific file names

**Fluid Workflow Integration**

This skill supports the "actions on a change" model:

- **Can be invoked anytime**: Before all artifacts are done (if tasks exist), after partial implementation, interleaved with other actions
- **Allows artifact updates**: If implementation reveals design issues, suggest updating artifacts - not phase-locked, work fluidly
