---
name: kayba-pipeline
description: End-to-end agent evaluation and improvement pipeline. Takes a traces folder and optional HITL flag, then orchestrates sub-agents through 7 stages — each stage is its own skill invoked by a dedicated sub-agent. Trigger when the user says "run the pipeline", "kayba pipeline", "evaluate and fix", "full eval", "analyze traces and fix", or provides a traces folder with intent to improve their agent.
---

# kayba-pipeline

End-to-end pipeline: analyze traces → define metrics → build rubric → plan fixes → implement fixes.

Each stage is a separate skill file that can be run independently or as part of this pipeline.

## Inputs

The user provides two things:

1. **`TRACES_FOLDER`** — path to a directory containing trace JSON files
2. **`HITL`** — `true` or `false` — whether to pause for human review before implementing fixes

If the user doesn't specify HITL, default to `true` (safe default).

---

## Pipeline overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Stage 1: Kayba API Analysis        → skill: kayba-pipeline:stage-1-api-analysis   │
│  Stage 2: Domain Context Gathering  → skill: kayba-pipeline:stage-2-domain-context │
│  ─── stages 1 & 2 run in parallel ───                                              │
│  Stage 3: Metrics & Analysis        → skill: kayba-pipeline:stage-3-metrics        │
│  Stage 4: Rubric Definition         → skill: kayba-pipeline:stage-4-rubric         │
│  Stage 5: Action Plan               → skill: kayba-pipeline:stage-5-action-plan    │
│  Stage 6: HITL Gate                 → skill: kayba-pipeline:stage-6-hitl           │
│  Stage 7: Fix Implementation        → skill: kayba-pipeline:stage-7-fixer          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Orchestration instructions

You are the orchestrator. Your job is to:
1. Create the `eval/` directory and `eval/pipeline_log.md`
2. Spawn sub-agents that invoke stage skills via the Skill tool
3. Coordinate stage ordering and handle the HITL gate

### Setup

Create `eval/` directory and initialize `eval/pipeline_log.md`:

```markdown
# Pipeline Log

| Stage | Name | Status | Started | Completed | Notes |
|-------|------|--------|---------|-----------|-------|
| 1 | Kayba API Analysis | pending | | | |
| 2 | Domain Context | pending | | | |
| 3 | Metrics & Analysis | pending | | | |
| 4 | Rubric Definition | pending | | | |
| 5 | Action Plan | pending | | | |
| 6 | HITL Gate | pending | | | |
| 7 | Fix Implementation | pending | | | |
```

### Stages 1 & 2 — run in parallel

Spawn two sub-agents in parallel using the Agent tool:

**Agent 1:**
- Name: `api-analyst`
- Type: `general-purpose`
- Prompt: `Invoke the skill "kayba-pipeline:stage-1-api-analysis" using the Skill tool. The traces folder is: {TRACES_FOLDER}. Follow the skill instructions completely.`

**Agent 2:**
- Name: `domain-scout`
- Type: `general-purpose`
- Prompt: `Invoke the skill "kayba-pipeline:stage-2-domain-context" using the Skill tool. The traces folder is: {TRACES_FOLDER}. Follow the skill instructions completely.`

Wait for both to complete before proceeding.

### Stage 3 — sequential

Spawn one sub-agent after stages 1 & 2 complete:

- Name: `metric-engineer`
- Type: `general-purpose`
- Prompt: `Invoke the skill "kayba-pipeline:stage-3-metrics" using the Skill tool. The traces folder is: {TRACES_FOLDER}. Follow the skill instructions completely — this includes iterating on the metrics until you're satisfied.`

### Stage 4 — sequential

Spawn one sub-agent after stage 3 completes:

- Name: `rubric-builder`
- Type: `general-purpose`
- Prompt: `Invoke the skill "kayba-pipeline:stage-4-rubric" using the Skill tool. Follow the skill instructions completely.`

### Stage 5 — sequential

Spawn one sub-agent after stage 4 completes:

- Name: `action-planner`
- Type: `general-purpose`
- Prompt: `Invoke the skill "kayba-pipeline:stage-5-action-plan" using the Skill tool. Follow the skill instructions completely.`

### Stage 6 — HITL Gate

**If `HITL` is `true`:**

Spawn one sub-agent after stage 5 completes:

- Name: `hitl-reviewer`
- Type: `general-purpose`
- Prompt: `Invoke the skill "kayba-pipeline:stage-6-hitl" using the Skill tool. Follow the skill instructions completely. Present the full review to the user and collect their decision before proceeding.`

Wait for the sub-agent to complete. Check `eval/stage6_decision.md` for the outcome:
- If decision is "Approve all" or "Approve with modifications" — proceed to Stage 7
- If decision is "Reject" — re-run Stage 5 with the user feedback recorded in `eval/stage6_decision.md`, then re-run Stage 6
- Only proceed to Stage 7 after a clear approval is recorded

**If `HITL` is `false`:**
- Skip to Stage 7
- Log "HITL skipped" in `eval/pipeline_log.md`

### Stage 7 — sequential

Spawn one sub-agent after stage 6 completes (or is skipped):

- Name: `fixer`
- Type: `general-purpose`
- Prompt: `Invoke the skill "kayba-pipeline:stage-7-fixer" using the Skill tool. Follow the skill instructions completely.`

---

## Error handling

- If any stage fails, log the failure in `eval/pipeline_log.md` with the stage number and error
- Do not proceed to dependent stages if a prerequisite failed
- If Stage 1 fails (kayba CLI issues), ask the user whether to proceed without API insights — if yes, skip Stage 1 and have Stage 3 work from domain context + raw traces only

## After completion

Update `eval/pipeline_log.md` with final status for all stages. Report to the user:
- How many stages completed successfully
- Summary of metrics (from rubric)
- Summary of fixes applied (from changes log)
