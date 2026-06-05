---
mode: agent
description: Automatic post-Phase-2 learning pipeline — reflects, learns, and curates instruction updates without manual intervention.
---

# Phase 2 Post-Learner — Automatic Reflection & Curation

> Runs automatically after Phase 2 completes. Routes Phase 2 findings through **pds-meta-learner** → **pds-man-curator** → **pds-pipe-reviewer**. No manual prompt needed.

## Scope

**Trigger**: Phase 2 executor completes with exit code 0 (all 22 files generated).

**Invocation**:
```bash
/ai-phase-2-post-learner
```

Or programmatically:
```python
# In phase2_executor.py post-execution
subprocess.run([
    sys.executable,
    ".ai/engine/phase2_post_learner.py",
    ".github/tmp/phase2-completion-report.md"
])
```

## Pipeline

### Step 1: **pds-meta-learner** — Capture Findings
- Reads: `.github/tmp/phase2-completion-report.md`
- Extracts:
  - LLM performance metrics (100% success, 30-40s execution)
  - Patterns that worked (credential .gitignore, governance links)
  - Optimization opportunities (parallelization, batching)
  - Failures + rejected approaches (none in Phase 2)
- **Produces**: `.ai/knowledge/phase2-learnings.md`
  - Durable insights for future phases
  - Performance baseline (22 files in 30-40s)
  - Hybrid LLM routing validation
- **No approval needed** — read-only learning capture

### Step 2: **pds-man-curator** — Apply Instruction Updates
- Reads: `.ai/knowledge/phase2-learnings.md`
- Updates:
  - `.ai/instruct.md` → Add hybrid LLM routing best practices section
  - `.ai/heartbeat.md` → Document when to trigger post-execution learning
  - `.ai/index.md` → Register new knowledge entry
- **Produces**: Proposed diffs for human review
- **Approval needed**: Human confirms instruction changes before commit

### Step 3: **pds-pipe-reviewer** — Final Gate
- Validates:
  - No instruction drift detected
  - All updates follow V5 conventions
  - Archive-first rule respected (knowledge entry only appended, never overwritten)
  - Governance rules not relaxed
- **Produces**: Approval report
- **Approval needed**: Final sign-off before merge

## Automation Trigger

After Phase 2 executor completes:

1. **Immediately** (no delay):
   - Check exit code = 0
   - Verify `.github/tmp/phase2-execution.log` has "Phase 2 execution complete"
   - Queue post-learner task in `.ai/autonomous/queue.jsonl`

2. **Execute learning pipeline**:
   - Invoke pds-meta-learner (read-only, no approval needed)
   - Wait for `.ai/knowledge/phase2-learnings.md` to be created
   - Invoke pds-man-curator with findings (produces diffs)
   - **Pause for human approval** on instruction updates

3. **On Approval**:
   - Apply curator updates to `.ai/instruct.md`, `.ai/index.md`
   - Invoke pds-pipe-reviewer for final validation
   - Commit audit trail to `.ai/logs/phase-2-learner-*.jsonl`

## Configuration

Add to `.ai/autonomous/autonomy-config.yaml`:

```yaml
post_execution_hooks:
  phase_2:
    enabled: true
    trigger_on: "phase2_executor_exit_0"
    pipeline:
      - agent: pds-meta-learner
        approval: none
      - agent: pds-man-curator
        approval: human_confirmation
      - agent: pds-pipe-reviewer
        approval: human_confirmation
    timeout_minutes: 15
    max_files_modified: 5  # only .ai/ files
```

## Success Criteria

✅ `.ai/knowledge/phase2-learnings.md` created (durable insights)
✅ `.ai/instruct.md` updated with hybrid LLM routing section
✅ `.ai/index.md` reflects new knowledge entry
✅ No instruction drift detected
✅ All updates V5-compliant
✅ Audit trail logged to `.ai/logs/`

## Human Approval Points

| Step | Decision | Recommendation |
|------|----------|-----------------|
| **pds-meta-learner** | None | Auto-proceed |
| **pds-man-curator** (diffs) | Review instruction changes | **APPROVE** if:  - Updates avoid duplication  - Links to canonical rules  - Archive-first respected |
| **pds-pipe-reviewer** | Final validation | **APPROVE** if no drift detected |

## If No Changes Needed

If curator finds no instruction gaps:
- Log: "Phase 2 execution: No instruction updates needed"
- Create minimal entry in `.ai/knowledge/phase2-learnings.md` (performance metrics only)
- Return control to user with summary

## Implementation Path

1. **Immediate** (this session): Manually invoke `/ai-phase-2-post-learner` for Phase 2
2. **Short-term** (Phase 3): Add `post_execution_hooks` to autonomy config
3. **Medium-term** (Phase 4+): Enable autonomous orchestrator with auto-trigger

---

**Usage**:
```bash
# Manual invocation (recommended for now)
/ai-phase-2-post-learner

# Programmatic (from phase2_executor.py)
# Will be added in Phase 3 infrastructure update
```

**See Also**:
- [pds-meta-learner](../agents/pds-meta-learner.agent.md)
- [pds-man-curator](../agents/pds-man-curator.agent.md)
- [Autonomous Orchestrator](../../.ai/autonomous/orchestrator.md)
