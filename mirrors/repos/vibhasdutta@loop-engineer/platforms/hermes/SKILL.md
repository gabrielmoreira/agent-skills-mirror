---
name: loop-engineer
description: >
  Loop engineering wizard for Hermes Agent. Asks 2 questions, then orchestrates
  a fully autonomous parallel agent team (resource-scout, researcher, planner,
  agent-factory, executor, evaluator, verifier, auditor, memory-keeper) for any goal.
  Uses delegate_task for true parallel subagent dispatch. Persistent memory,
  git integration, resume support. Activate with /loop-engineer.
compatibility: Requires git and a terminal backend (local, docker, ssh, modal, or daytona)
metadata:
  author: vibhasdutta
  version: "1.6.0"
  hermes:
    tags: [orchestration, multi-agent, loop-engineering, autonomous, coding]
    category: development
    requires_toolsets: [terminal]
---

# Loop Engineer (Hermes Agent)

You are running a loop engineering wizard. Follow these phases in order.

---

## Phase 0 — Resume Check

Run the resume-check script FIRST — unconditionally. It is the source of truth; do not scan `loop-stack/` yourself.

**Bash:** `bash ~/.hermes/skills/loop-engineer/scripts/check-resume.sh`
**PowerShell:** `& "$env:USERPROFILE\.hermes\skills\loop-engineer\scripts\check-resume.ps1"`

Read its output literally, then branch:

**`ACTIVE <id> | State: ... | Task: ... | Progress: ...`:**
- Continuation intent ("continue", "proceed", "finish", "resume", "pick up", "fix what", "audit findings", "where we left") → auto-resume to Phase 5 without asking.
- Otherwise show State/Current Task/Progress, ask: Resume or Fresh?
  - Resume → skip to Phase 5.
  - Fresh → delete `loop-stack/<id>/` only (keep `.hermes/agents/`), continue to Phase 1.
- Multiple `ACTIVE` lines → list all, ask which to resume or 'fresh'. Continuation intent → auto-resume most recently modified.

**`DONE <id>` or `EXTENDED_DONE <id>` (no `ACTIVE` line) + continuation intent:**
→ **EXTEND SEQUENCE** — reopen in place, don't restart:
1. Rename `loop-stack/<id>_DONE/` (or `_EXTENDED_DONE/`) → `loop-stack/<id>_EXTENDED/`.
2. Reuse existing PLAN.md, RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md, `agents/` as-is — do not re-run researchers, resource-scout, or agent-factory.
3. Ask ONE question: "What's the next task for this loop?" Append under `## Extension {N} Goal` in PLAN.md.
4. Dispatch `planner` once against the new goal (existing RESEARCH.md/TOOLS.md as context) to append new `[GN]` tasks.
5. Reset STATUS.md: State = IN_PROGRESS, Current Task = first new task, Task Progress updated.
6. Go directly to Phase 5 (skip Phase 1–4).

On completion of a loop directory containing `_EXTENDED`: Phase 6 renames it to `_EXTENDED_DONE` instead of plain `_DONE`.

**`NONE`, or `DONE`/`EXTENDED_DONE` with no continuation intent:** → Phase 1 (fresh loop).

**RESUME/EXTEND RULES — always apply when going to Phase 5 this way:**
Skip Phase 2, 3, and 4 entirely. Read STATUS.md + PLAN.md to find where the loop stopped. Reuse existing RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md — do not re-run startup agents.

> **To update loop-engineer:** re-run `install.sh --update` / `install.ps1 -Update -Hermes`. Updates are never applied automatically mid-loop.

---

## Phase 1 — Core Wizard

**Q1:** "What do you want the loop to accomplish? (1-2 sentences)"

Generate LOOP_ID: lowercase slug, first 4 meaningful words, max 24 chars.
Auto-set: `STOP_CONDITION` = "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked", `MAX_TURNS` = 20.

**Q2:** "Should the loop auto-commit after each verified task? (yes / no)"

---

## Phase 2+3 — Initialize Loop

Run the init script — creates all state files, copies agent files, and writes verifier in one command:

**Bash (macOS/Linux):**
```bash
bash ~/.hermes/skills/loop-engineer/scripts/init-loop.sh \
  --loop-id <LOOP_ID> \
  --goal "<GOAL>" \
  --stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" \
  --git <yes/no> \
  --platform hermes
```

**PowerShell (Windows):**
```powershell
& "$env:USERPROFILE\.hermes\skills\loop-engineer\scripts\init-loop.ps1" `
  -LoopId "<LOOP_ID>" `
  -Goal "<GOAL>" `
  -Stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" `
  -Git <yes/no> `
  -Platform hermes
```

If the script is missing, install the skill first:
`git clone https://github.com/vibhasdutta/loop-engineer && bash install.sh --hermes`

The script creates `loop-stack/<LOOP_ID>/`, `.hermes/agents/` with all agent .md files + knowledge-sources/, and `verifier.md` with the actual stop condition substituted.

---

## Phase 4 — Startup Sequence

Use `delegate_task` to spawn isolated child agents. Its real signature (confirmed via hermes-agent.nousresearch.com docs) takes a single `tasks` array parameter — `delegate_task(tasks=[{goal, context, toolsets}, ...])` — one call dispatches every entry in the array concurrently, up to the concurrency cap (see Rules). It is **synchronous**: the call blocks until all tasks in that array return, then you get every result back at once. Each child agent should:
- Read `.hermes/agents/{role}.md` for its full instructions (pass this as part of `context`)
- Write its results back to the loop-stack state files
- Update STATUS.md when done

For parallel steps: put every agent's task definition in one `delegate_task(tasks=[...])` call, then process all results once it returns.

### Step 1 — Parallel RESEARCHERS (dynamic count)

Determine researcher count by goal complexity:
- Simple/single-domain → 2 researchers
- Medium/multi-domain → 3 researchers
- Large/multi-system → 4 researchers

**Dispatch all researchers in one `delegate_task(tasks=[...])` call** — one array entry per researcher:

Each researcher's `context` should include:
```
Loop directory: loop-stack/<LOOP_ID>/
Focus: {ASSIGNED_DOMAIN} — {specific files and concerns}
GLOBAL DATA FIRST: read loop-stack/.global/MEMORY.md and loop-stack/.global/TOOLS.md.
Write findings to loop-stack/<LOOP_ID>/RESEARCH.md under "## {Domain Name}".
Update STATUS.md "Last Researcher Result".
Read .hermes/agents/researcher.md for full instructions.
```

Domains to distribute across researchers:
- **Context & Prior Work**: source structure, patterns, package files, existing tests
- **External Knowledge & Resources**: README, docs/, external APIs, .env.example, configs
- **Requirements & Constraints**: DB schema, data models, state management (for 3+ researchers)
- **Environment & Integration**: CI/CD, infrastructure, build, Docker (for 4 researchers)

**Stuck-agent check (you do this yourself — no watcher subagent):** if a researcher took much longer than the others, check its heartbeat line in STATUS.md `## Active Heartbeats`. If stale, treat it STUCK, note it, and proceed with the findings you have.

Wait for all researcher tasks to complete (check STATUS.md) before Step 2.

### Step 2 — RESOURCE SCOUT

Call `delegate_task` with:
```
Loop directory: loop-stack/<LOOP_ID>/
Check loop-stack/.global/TOOLS.md — if < 7 days old, reuse it.
Otherwise discover all tools. Write to loop-stack/<LOOP_ID>/TOOLS.md AND loop-stack/.global/TOOLS.md.
Read .hermes/agents/resource-scout.md for full instructions.
Do not proceed until resource-scout has written TOOLS.md.
```

### Step 3 — PLANNER

Call `delegate_task` with:
```
Loop directory: loop-stack/<LOOP_ID>/
Read RESEARCH.md (all sections) and TOOLS.md.
Create 3–7 tasks with parallel group tags [G1], [G2], etc.
Same group = parallel (independent files/modules). Different group = sequential dependency.
Replace "## Tasks" in PLAN.md. Update STATUS.md.
Read .hermes/agents/planner.md for full instructions.
```

Write `loop-stack/<LOOP_ID>/AGENTS.md` with `# Specialized Agents\n## Status\nNONE CREATED YET`. (Agent-factory is on-demand, not a fixed step — see Rules.)

---

## Phase 5 — Outer Loop

**FULLY AUTONOMOUS. Never pause for user input.**

Initialize: `turns_used = 0`, `skipped_tasks = []`.

For each dispatch step: put every agent's task definition in one `delegate_task(tasks=[...])` call — this blocks until all of them return, then you have every result at once.

### Iteration steps:

1. **Budget check** — over MAX_TURNS → Phase 6.

2. **Read state** — identify current parallel group (all unchecked [GN] tasks).

3. **Parallel RESEARCHERS** — one `delegate_task(tasks=[...])` call, one array entry per task (2 entries if batch=1):
   ```
   Loop directory: loop-stack/<LOOP_ID>/
   GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
   Focus: {ASSIGNED_DOMAIN} for task: {this_task}
   Append findings to RESEARCH.md under "## Task-Specific Research — {this_task}".
   Update STATUS.md "Last Researcher Result".
   Read .hermes/agents/researcher.md for full instructions.
   ```
   Wait for the call to return. Increment turns_used.

4. **Before executors, check AGENTS.md.** For every task in the batch that clearly needs domain expertise beyond a generic executor and has no specialist yet, put all of them in one `delegate_task(tasks=[...])` call (reads `.hermes/agents/agent-factory.md`, creates 1 agent file per task, updates AGENTS.md) — same parallel-first rule as researchers/executors. Skip this for most tasks.

5. **Parallel EXECUTORS** — one `delegate_task(tasks=[...])` call, one array entry per task:
   ```
   Loop directory: loop-stack/<LOOP_ID>/
   GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
   Read MEMORY.md, TOOLS.md, PLAN.md, STATUS.md.
   READ: RESEARCH.md "## Task-Specific Research — {this_task}".
   Current task: {this_task}. Scope: only files for this task.
   Implement. Append discoveries to MEMORY.md directly. Update STATUS.md.
   Goal output (code, documents, files) goes to the project directory, NOT inside loop-stack/. loop-stack/ is state-only.
   Read .hermes/agents/executor.md for full instructions.
   ```
   Wait for the call to return. Increment turns_used.

6. **MEMORY-KEEPER checkpoints** — one `delegate_task(tasks=[...])` call, one entry per task (local only).

7. **EVALUATORS** — one `delegate_task(tasks=[...])` call, one entry per task.

8. **VERIFIERS** — one `delegate_task(tasks=[...])` call, one entry per task.

9. **Process verifier results**:
   - PASS → auditor
   - FAIL < 3 → retry from step 3
   - FAIL ≥ 3 → auto-skip

10. **AUDITORS** (passing tasks only) — one `delegate_task(tasks=[...])` call, one entry per passing task.

11. **Process audit results**:
    - CLEAN/WARN → proceed
    - BLOCK → auto-fix (dispatch executor once with BLOCK context, re-dispatch verifier). Still BLOCK → auto-skip.

12. **MEMORY-KEEPER final** — single `delegate_task` call, local + global write.

13. **Advance** — mark [x], git commit if enabled. Find next group.
    None → ALL DONE → rename `loop-stack/<LOOP_ID>/` → `loop-stack/<LOOP_ID>_DONE/` (or `_EXTENDED_DONE/` if this was an extended loop) → Phase 6.

---

## Phase 6 — Completion Report

Write `REPORT.md` inside the renamed loop directory and print summary.

---

## Rules

- Phase 0 first — run the check-resume script, never scan `loop-stack/` by hand.
- **File copy**: `~/.hermes/skills/loop-engineer/agents/*.md` → `.hermes/agents/`. Never write manually.
- **Global data first**: every agent reads `.global/MEMORY.md` + `.global/TOOLS.md` before acting.
- **Parallel first**: `delegate_task(tasks=[...])` takes one array of task definitions per call and dispatches every entry concurrently, up to the concurrency cap. It is **synchronous** — the call blocks until every task in the array returns, and if the parent turn is interrupted mid-call, all active children are cancelled and their work discarded. Default cap: **3 concurrent tasks**, configurable via `delegation.max_concurrent_children` in config.yaml (floor of 1, no ceiling).
- **Nested delegation is restricted**: leaf subagents (the default role) cannot call `delegate_task` themselves — only `role="orchestrator"` subagents retain it, and only when `delegation.max_spawn_depth` is raised above its default of 1. Loop-engineer's agents are all leaf subagents; this doesn't affect the design, just don't expect an executor to be able to further delegate sub-tasks.
- **Researcher before executor**: always. Dynamic count based on goal complexity. Executor reads AGENTS.md to determine if a specialized agent should be used instead of the generic executor.
- **Agent-factory is on-demand, not a fixed phase step.** Invoke it only right before executing a task that clearly needs a specialist. Most loops never call it.
- **knowledge-sources.md is a reference file researchers consult on demand**, not a phase step.
- **No watcher agent.** Check heartbeats yourself if an agent is slow; never dispatch a dedicated watcher task.
- **Memory-keeper twice per batch**: checkpoint (local) after executors, consolidation (local+global) after audit.
- **Executors append to MEMORY.md directly** during work.
- **Planner**: once at startup after researchers + resource-scout, and again (lightweight) for extended-loop follow-on tasks. Tasks MUST include [G1]/[G2] parallel group tags.
- **Fully autonomous**: no pauses. 3 fails → auto-skip. BLOCK → auto-fix once → skip.
- **HARD RULE — no plan-approval gate**: after Phase 1's two questions, proceed through Phase 2 onward without presenting a plan for approval or waiting for a "click proceed" confirmation.
- On completion: rename to `<LOOP_ID>_DONE/` or `<LOOP_ID>_EXTENDED_DONE/`.
- **HERMES.md**: ensure `HERMES.md` (from `platforms/hermes/HERMES.md`) is in the project root for workspace context.
- **MCP config**: Hermes reads MCP servers from `~/.hermes/config.yaml` under `mcp_servers`.
- **Skill Curator**: this is a persistent workflow skill — never archive or retire it.
