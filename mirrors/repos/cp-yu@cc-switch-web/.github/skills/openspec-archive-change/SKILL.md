---
name: openspec-archive-change
description: Archive a completed change in the experimental workflow. Use when the user wants to finalize and archive a completed change after implementation is complete.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.2.0-cpyu.9"
---

Archive a completed change in the experimental workflow.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

When archive guidance discusses embedded sync or artifact write-back, treat `openspec/config.yaml` as the compact source of truth and follow the shared prompt/runtime projection contract rather than reinterpreting raw config keys inside the template body.

**Steps**

1. **If no change name provided, prompt for selection**

   Run `openspec list --json` to get available changes. Use the **AskUserQuestion tool** to let the user select.

   Show only active changes (not already archived).
   Include the schema used for each change if available.

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose.

2. **Unified Full Verify Gate**

   Run the CLI gate:
   ```bash
   openspec verify status "<change-name>" --json
   ```

**Verify Result Freshness Rules**:

A verify result is considered **FRESH** if ALL of the following hold:
- `.verify-result.json` exists in the change directory
- `verificationContext.evidenceFingerprint` matches the current workspace fingerprint
- `verificationContext.contractVersion` is `"1.0"`
- `result` is `PASS` or `PASS_WITH_WARNINGS`

A verify result is considered **STALE** if ANY of the following hold:
- `verificationContext.evidenceFiles` is missing or the file list changed
- `verificationContext.evidenceFingerprint` does not match the recomputed fingerprint
- `verificationContext.gitHeadCommit` does not match the current HEAD (if recorded)
- `verificationContext.contractVersion` is missing or not `"1.0"`
- `result` is not `PASS` or `PASS_WITH_WARNINGS`

**Optimization metadata compatibility**:
- `optimization` metadata is advisory for archive gating, not part of the freshness hash inputs
- Legacy verify results without `optimization` may still be fresh if every freshness rule above passes
- If `optimization.status` exists, evaluate its acceptability separately from freshness

**When verify result is STALE or MISSING**:
- Archive MUST execute full verify before continuing
- Do NOT attempt to repair or reuse a stale verify result

**Fingerprint Computation**:
- Sort `evidenceFiles` alphabetically before hashing
- For each evidence file, collect normalized relative POSIX path + content hash
- Hash the JSON-serialized entries with SHA-256
- Use `path.join()`, `path.resolve()`, and `path.normalize()` for all path handling
- Persist `evidenceFiles` as relative POSIX paths for cross-platform comparison

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

**Verify CLI JSON Schema Reference**:

| CLI call | `--input` JSON |
| --- | --- |
| `openspec verify phase1 "<change-name>" --input '<json>' --json` | `{"result":"PASS","issues":[],"evidenceFiles":["..."],"executionMode":"..."}` |
| `openspec verify phase2 "<change-name>" --type=optimization --input '<json>' --json` | `{"status":"NO_OPTIMIZATION_NEEDED","summary":"..."}` (summary is required, must be non-empty) |
| `openspec verify phase2 "<change-name>" --type=optimization --files "<affected-files>" --input '<json>' --json` | `{"status":"OPTIMIZATION_PROPOSED","summary":"..."}` |
| `openspec verify phase2 "<change-name>" --type=optimization --input '<json>' --json` | `{"status":"SKIPPED"}` |
| `openspec verify phase2 "<change-name>" --type=verification --input '<json>' --json` | `{"result":"PASS","issues":[]}` |
| `openspec verify phase2 "<change-name>" --type=verification --input '<json>' --json` | `{"result":"FAIL_NEEDS_REMEDIATION","issues":[...],"behaviorRetryCounter":N}` |

   - If the command exits 0, treat the persisted `.verify-result.json` as fresh and archive-compatible, then continue to Step 3
   - If the command exits non-zero because the result is MISSING or STALE, execute the full verify contract in Step 2.5 and then rerun `openspec verify status "<change-name>" --json`
   - If `result === 'FAIL_NEEDS_REMEDIATION'`, HARD-BLOCK archive, display CRITICAL issues from `issues[]`, and instruct the user to fix remediation items before rerunning verify
   - **If `optimization.status` is `PENDING_VERIFICATION`** — do NOT stop. Follow the recovery table below to resolve the incomplete state:

     | 子状态 | 恢复路径 |
     |--------|---------|
     | `PENDING_VERIFICATION` 且 **无** `affectedFileHashes` (或为空) | Phase 1 刚完成，尚未进入 Phase 2。Agent 应判断变更复杂度：若为简单变更（纯删除/重命名/参数移除），直接调用 `openspec verify phase2 "<name>" --type=optimization --input '{"status":"NO_OPTIMIZATION_NEEDED"}' --json`。否则执行 Phase 2 优化分析后调用同命令。完成后 `optimization.status` 变为 `NOT_NEEDED`，archive 门禁通过 |
     | `PENDING_VERIFICATION` 且 **有** `affectedFileHashes` | 优化提案已生成，等待验证确认。先执行 verification：`openspec verify phase2 "<name>" --type=verification --input '{"result":"PASS","issues":[]}' --json`。完成后 `optimization.status` 变为 `IMPROVED` 或 `DEGRADED`，archive 门禁通过 |

     After resolving `PENDING_VERIFICATION`, re-run `openspec verify status "<change-name>" --json` to confirm the gate passes.
   - **If `optimization.status` is `ABORTED_UNSAFE`** — HARD STOP. 工作区状态不安全，需人工恢复。不提供自动恢复路径

2.5. **Execute Full Verify**

   When the verify result is missing or stale, execute the same verify contract as `/opsx:verify` using the `current-agent-reread` skeleton:
   - Re-read change artifacts, git evidence, and final file contents in the current agent before any verify judgment
   - Run completeness, git-evidence, correctness, and coherence checks in the current agent
   - Execute the verify workflow end-to-end, including Phase 2 whenever the `/opsx:verify` contract would make it eligible
   - In `P1_SPECULATIVE_FENCE`, the current agent re-runs the reread contract against the speculative worktree
   - If the canonical Phase 1 `result` is `PASS` or `PASS_WITH_WARNINGS`, and optimization is not disabled by config or an explicit `--skip-optimization` request, archive-time full verify MUST continue into Phase 2
   - Archive-time caution about speculative edits is NOT a valid reason to downgrade the run into a Phase-1-only verify
   - `optimization.status = 'SKIPPED'` is only valid when config disables optimization or the user explicitly requested `--skip-optimization`
   - Persist a fresh `.verify-result.json` before returning to archive
   - In `core`, this verify contract is embedded inside archive because there is no standalone verify surface
   - In `expanded`, you MAY invoke `/opsx:verify` or execute the same contract inline, but the semantics MUST stay identical

   **Important**:
   - This is the ONLY verify gate for archive
   - There is no archive-only mini check
   - There is no bypass path after a failed verify
   - `core` and `expanded` modes use the same archive gate logic

3. **Check artifact completion status**

   Run `openspec status --change "<name>" --json` to check artifact completion.

   Parse the JSON to understand:
   - `schemaName`: The workflow being used
   - `artifacts`: List of artifacts with their status (`done` or other)

   **If any artifacts are not `done`**:
   - Display warning listing incomplete artifacts
   - Use the **AskUserQuestion tool** to confirm the user wants to proceed
   - Proceed only if the user confirms

4. **Check task completion status**

   Read the tasks file (typically `tasks.md`) to check for incomplete tasks.

   Count tasks marked with `- [ ]` (incomplete) vs `- [x]` (complete).

   **If incomplete tasks are found**:
   - Display a warning showing the count of incomplete tasks
   - Use the **AskUserQuestion tool** to confirm the user wants to proceed
   - Proceed only if the user confirms

   **If no tasks file exists**: proceed without task-related warning.

5. **Assess delta sync state**

   Check for delta specs at `openspec/changes/<name>/specs/` and for `openspec/changes/<name>/opsx-delta.yaml`. If neither exists, proceed directly to archive.

   **If any delta exists**:
   - Run `openspec sync "<change-name>"` before archive so standalone sync and archive consume the same verify gate and sync contract
   - Abort archive if `openspec sync` fails, leaving main specs, OPSX files, and the active change directory unchanged
   - In `expanded`, `/opsx:sync` may still exist as a standalone workflow, but archive MUST follow the same sync-state contract

6. **Perform the archive**

   Create the archive directory if it does not exist:
   ```bash
   mkdir -p openspec/changes/archive
   ```

   Generate the target name using the current date: `YYYY-MM-DD-<change-name>`

   **Check if the target already exists**:
   - If yes: fail with an error and suggest renaming or removing the existing archive entry
   - If no: move the change directory to archive

   ```bash
   mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-DD-<name>
   ```

7. **Display summary**

   Show archive completion summary including:
   - Change name
   - Schema that was used
   - Archive location
   - Whether specs / OPSX were synced (if applicable)
   - Whether a fresh verify result was reused or archive had to execute full verify
   - Any warnings about incomplete artifacts or tasks

**Output On Success**

```
## Archive Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Archived to:** openspec/changes/archive/YYYY-MM-DD-<name>/
**Verify Gate:** Fresh PASS or PASS_WITH_WARNINGS result confirmed
**Specs / OPSX:** ✓ Synced to main specs and project OPSX (or "No deltas" or "Skipped all archive-time sync writes")

Archive completed after satisfying the unified full verify gate.
```

**Guardrails**
- Always prompt for change selection if not provided
- Use artifact graph (`openspec status --json`) for completion checking
- Do not downgrade the verify gate into a lightweight archive-only check
- Preserve `.openspec.yaml` when moving to archive (it moves with the directory)
- Show clearly whether verify was reused or re-executed
- In `core`, use `openspec sync "<change-name>"` rather than manual inline sync
- If delta specs or `opsx-delta.yaml` exist, always run the shared sync assessment before moving the change directory
