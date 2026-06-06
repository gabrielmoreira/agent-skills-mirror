# Heartbeat — Periodic Alignment Check

**Scope**: Project-wide canonical reference
**Last Updated**: 2026-06-03

> Heartbeat fires every 6 agent steps (configurable via `heartbeat_interval` in `.hi/agent-config.yaml`).
> It re-reads the active instruction scope and verifies alignment before the agent continues.

---

## Contents

| Section | What's here |
|---------|-------------|
| [What Is a Step](#what-is-a-step) | How "step" is counted for heartbeat triggering |
| [Heartbeat Procedure](#heartbeat-procedure) | What to do at each heartbeat interval |
| [Post-Execution Learning Triggers](#post-execution-learning-triggers) | Automatic learning and curation after phase completion |
| [Misalignment Response](#misalignment-response) | What to do when a rule violation is detected |
| [Logging](#logging) | How heartbeat checks are recorded |

---

## What Is a Step

A **step** is any discrete agent action:

- Creating, editing, or deleting a file
- Running a terminal command
- Calling a tool
- Making a search (file search, grep, semantic search)

Conversational turns — asking the user a question, reporting a result, waiting for input — do **not** count as steps.

---

## Heartbeat Procedure

At every 6th step, before taking the next action:

1. **Run [`pause-check`](agents/tools/pause-check.json) FIRST.** If `.hi/PAUSE` exists, stop immediately and surface the reason — no further steps. The kill-switch outranks every other heartbeat duty. The same check also runs once at invocation start, before any other tool.
2. **Re-invoke [`load-context`](agents/tools/load-context.json)** — the same governed tool the agent ran at invocation start. This re-validates the envelope, re-reads every file in the agent's [Context Manifest](agents/context.md#per-agent-manifest), reloads persistent state for stateful managers, and re-applies the governance overlay. Heartbeat is **context reload, not just rule reload**.
3. **Identify the current working directory** — which module or submodule is active right now?
4. **Reload the effective instruction scope** — run [`.hi/engine/get_effective_instructions.py`](engine/get_effective_instructions.py) for the current path (or manually re-read the deepest `.hi/instruct.md` in the path hierarchy if the script is unavailable).
5. **Re-read [`agent-config.yaml`](agent-config.yaml)** — confirm safety settings (`requires_approval`, `archive_first`, `log_all_changes`) are still known.
6. **Check for directory drift** — has the working directory changed since the last heartbeat? If yes, a different module's rules are now active — reload immediately, regardless of step count.
7. **Verify task alignment** — is the current task direction still consistent with the reloaded instructions? Check especially: archive-first, credential rules, and any module-specific constraints.
8. **Log the check** — emit a brief entry to `.hi/logs/` using the [`run-heartbeat`](agents/tools/run-heartbeat.json) governed tool format (see below).

If all checks pass: continue with the next action. Report nothing to the user — a passing heartbeat is silent.

---

## Post-Execution Learning Triggers

**After major phases complete** (Phase 2, Phase 3, etc.), automatic learning and curation runs:

1. **Phase completion detected** (exit code 0 from executor)
2. **Invoke `/hip-phase-X-post-learner`** (or auto-trigger if `autonomy-config.yaml.post_execution_hooks.enabled = true`)
3. **Learning pipeline**:
   - **hia-learner**: Capture metrics, patterns, and insights → `.hi/knowledge/phase-X-learnings.md`
   - **hia-curator**: Review findings, propose `.hi/instruct.md` improvements (human approval required)
   - **hia-reviewer**: Validate proposed instruction updates for governance compliance
4. **Human approval gate**: Review curator briefing, approve or request changes
5. **Audit logged** to `.hi/logs/`

**Purpose**: Ensure the instruction system evolves with project discoveries; prevent operational knowledge from being lost.

**See also**: [Phase 2 Post-Learner Prompt](prompts/tier-2/hip-phase-2-post-learner.prompt.md), [Phase 2 Learning Capture](knowledge/phase2-learnings.md)

---

## Misalignment Response

If the heartbeat check reveals a conflict between the current task and active instructions:

1. **Stop the current task immediately.**
2. **Report the misalignment** to the user. Cite:
   - The specific rule being violated
   - The governing file (`.hi/instruct.md` path)
   - The action that would have violated it
3. **Wait for explicit direction.** Do not attempt to self-correct silently.
4. The user may choose to: (a) adjust the task to comply, (b) update the instruction file with `/hip-reflect`, or (c) explicitly override with informed consent.

---

## Logging

Each heartbeat check appends one entry to the session log at `.hi/logs/YYYY-MM-DD-session.md`:

```
- timestamp: <ISO 8601>
  action: heartbeat
  files_affected: []
  safety_level: low
  approval_obtained: n/a
  outcome: aligned | misaligned
  note: "<working dir> — <instruction file checked>"
```
