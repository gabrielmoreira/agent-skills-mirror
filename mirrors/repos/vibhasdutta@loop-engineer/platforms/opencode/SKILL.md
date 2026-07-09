---
name: loop-engineer
description: >
  Loop engineering wizard for OpenCode. Asks 2 questions, then orchestrates
  a fully autonomous agent team (resource-scout, researcher, planner, agent-factory, executor,
  evaluator, verifier, auditor, memory-keeper) until the goal is met.
  Agents run sequentially via the task tool. Dynamic researcher count.
  Persistent memory, git integration, resume support.
---

# Loop Engineer (OpenCode)

You are running a loop engineering wizard. Follow these phases in order.

---

## Phase 0 — Resume Check

Run the resume-check script FIRST — unconditionally. It is the source of truth; do not scan `loop-stack/` yourself.

**Bash:**
```bash
CHECK="$HOME/.config/opencode/skills/loop-engineer/scripts/check-resume.sh"
[ ! -f "$CHECK" ] && CHECK="$HOME/.claude/skills/loop-engineer/scripts/check-resume.sh"
bash "$CHECK"
```

**PowerShell:**
```powershell
$check = "$env:USERPROFILE\.config\opencode\skills\loop-engineer\scripts\check-resume.ps1"
if (-not (Test-Path $check)) { $check = "$env:USERPROFILE\.claude\skills\loop-engineer\scripts\check-resume.ps1" }
& $check
```

Read its output literally, then branch:

**`ACTIVE <id> | State: ... | Task: ... | Progress: ...`:**
- Continuation intent ("continue", "proceed", "finish", "resume", "pick up", "fix what", "audit findings", "where we left") → auto-resume to Phase 5 without asking.
- Otherwise show State/Current Task/Progress, ask: Resume or Fresh?
  - Resume → skip to Phase 5.
  - Fresh → delete `loop-stack/<id>/` only (keep `.opencode/agents/`), continue to Phase 1.
- Multiple `ACTIVE` lines → list all, ask which to resume or 'fresh'. Continuation intent → auto-resume most recently modified.

**`DONE <id>` or `EXTENDED_DONE <id>` (no `ACTIVE` line) + continuation intent:**
→ **EXTEND SEQUENCE** — reopen in place, don't restart:
1. Rename `loop-stack/<id>_DONE/` (or `_EXTENDED_DONE/`) → `loop-stack/<id>_EXTENDED/`.
2. Reuse existing PLAN.md, RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md, `agents/` as-is — do not re-run researchers, resource-scout, or agent-factory.
3. Ask ONE question: "What's the next task for this loop?" Append under `## Extension {N} Goal` in PLAN.md.
4. Invoke `planner` once against the new goal (existing RESEARCH.md/TOOLS.md as context) to append new `[GN]` tasks.
5. Reset STATUS.md: State = IN_PROGRESS, Current Task = first new task, Task Progress updated.
6. Go directly to Phase 5 (skip Phase 1–4).

On completion of a loop directory containing `_EXTENDED`: Phase 6 renames it to `_EXTENDED_DONE` instead of plain `_DONE`.

**`NONE`, or `DONE`/`EXTENDED_DONE` with no continuation intent:** → Phase 1 (fresh loop).

**RESUME/EXTEND RULES — always apply when going to Phase 5 this way:**
Skip Phase 2, 3, and 4 entirely. Read STATUS.md + PLAN.md to find where the loop stopped. Reuse existing RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md — do not re-run startup agents.

> **To update loop-engineer:** re-run `install.sh --update` / `install.ps1 -Update -OpenCode`. Updates are never applied automatically mid-loop.

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
# try opencode path first, fall back to claude path
INIT="$HOME/.config/opencode/skills/loop-engineer/scripts/init-loop.sh"
[ ! -f "$INIT" ] && INIT="$HOME/.claude/skills/loop-engineer/scripts/init-loop.sh"
bash "$INIT" \
  --loop-id <LOOP_ID> \
  --goal "<GOAL>" \
  --stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" \
  --git <yes/no> \
  --platform opencode
```

**PowerShell (Windows):**
```powershell
$init = "$env:USERPROFILE\.config\opencode\skills\loop-engineer\scripts\init-loop.ps1"
if (-not (Test-Path $init)) { $init = "$env:USERPROFILE\.claude\skills\loop-engineer\scripts\init-loop.ps1" }
& $init -LoopId "<LOOP_ID>" -Goal "<GOAL>" `
  -Stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" `
  -Git <yes/no> -Platform opencode
```

If the script is missing, install the skill first:
`git clone https://github.com/vibhasdutta/loop-engineer && bash install.sh --opencode`

The script creates `loop-stack/<LOOP_ID>/`, `.opencode/agents/` with all agent .md files + knowledge-sources/, and `verifier.md` with the actual stop condition substituted.

---

## Phase 4 — Startup Sequence

Use the `task` tool to invoke each agent. Agents run sequentially — invoke each, wait for completion, then invoke the next.

### Step 1 — RESEARCHERS (dynamic count, sequential)

Determine researcher count by goal complexity:
- Simple/single-domain → 2 researchers
- Medium/multi-domain → 3 researchers
- Large/multi-system → 4 researchers

Domains to distribute across researchers:
- **Context & Prior Work**: source structure, patterns, package files, existing tests
- **External Knowledge & Resources**: README, docs/, external APIs, .env.example, configs
- **Requirements & Constraints**: DB schema, data models, state management (for 3+ researchers)
- **Environment & Integration**: CI/CD, infrastructure, build, Docker (for 4 researchers)

Invoke each researcher sequentially using the `task` tool:
```
agent: researcher
prompt: |
  Loop directory: loop-stack/<LOOP_ID>/
  Focus: {ASSIGNED_DOMAIN} — {specific files and concerns}
  GLOBAL DATA FIRST: read loop-stack/.global/MEMORY.md and loop-stack/.global/TOOLS.md.
  Write findings to loop-stack/<LOOP_ID>/RESEARCH.md under "## {Domain Name}".
  Update STATUS.md "Last Researcher Result".
```

**Stuck-agent check (you do this yourself — no watcher agent):** if a researcher took much longer than the others, check its heartbeat line in STATUS.md `## Active Heartbeats`. If stale, treat it STUCK, note it, and proceed with the findings you have.

### Step 2 — RESOURCE SCOUT

Invoke using the `task` tool:
```
agent: resource-scout
prompt: |
  Loop directory: loop-stack/<LOOP_ID>/
  Check loop-stack/.global/TOOLS.md — if < 7 days old, reuse. Otherwise discover all tools.
  Write to loop-stack/<LOOP_ID>/TOOLS.md AND loop-stack/.global/TOOLS.md.
```

### Step 3 — PLANNER

Invoke using the `task` tool:
```
agent: planner
prompt: |
  Loop directory: loop-stack/<LOOP_ID>/
  Read RESEARCH.md (all sections) and TOOLS.md.
  Create 3–7 tasks with parallel group tags [G1], [G2], etc.
  Same group = independent tasks (can conceptually run in parallel).
  Different group = sequential dependency.
  Replace "## Tasks" in PLAN.md. Update STATUS.md.
```

Write `loop-stack/<LOOP_ID>/AGENTS.md` with `# Specialized Agents\n## Status\nNONE CREATED YET`. (Agent-factory is on-demand, not a fixed step — see Rules.)

Auto-continue into outer loop immediately.

---

## Phase 5 — Outer Loop

**FULLY AUTONOMOUS. Never pause for user input.**

Initialize: `turns_used = 0`, `skipped_tasks = []`.

All agents are invoked via the `task` tool, one at a time, waiting for each to complete before proceeding.

### Iteration steps:

1. **Budget check** — over MAX_TURNS → Phase 6.

2. **Read state** — identify current parallel group (all unchecked [GN] tasks).

3. **RESEARCHERS** — invoke one per task in batch sequentially (2 if batch=1):
   ```
   agent: researcher
   prompt: |
     Loop directory: loop-stack/<LOOP_ID>/
     GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
     Then read loop-stack/<LOOP_ID>/MEMORY.md, TOOLS.md, PLAN.md, STATUS.md.
     Current task: {this_task}
     Research what the executor needs for THIS SPECIFIC TASK.
     Append findings to loop-stack/<LOOP_ID>/RESEARCH.md under "## Task-Specific Research — {this_task}".
   ```
   Increment turns_used.

4. **Before executors, check AGENTS.md.** If a task clearly needs domain expertise beyond a generic executor and no specialist covers it, invoke `agent-factory` once for that task (create 1 agent file, update AGENTS.md). Skip this for most tasks.

5. **EXECUTORS** — invoke one per task sequentially:
   ```
   agent: executor
   prompt: |
     Loop directory: loop-stack/<LOOP_ID>/
     GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
     Read MEMORY.md, TOOLS.md, PLAN.md, STATUS.md.
     READ: RESEARCH.md "## Task-Specific Research — {this_task}".
     Current task: {this_task}. Scope: only files for this task.
     Implement. Append discoveries to MEMORY.md. Update STATUS.md.
     Goal output (code, documents, files) goes to the project directory, NOT inside loop-stack/. loop-stack/ is state-only.
   ```
   Increment turns_used.

6. **MEMORY-KEEPER checkpoints** — invoke one per task sequentially. Local only.

7. **EVALUATORS** — invoke one per task sequentially.

8. **VERIFIERS** — invoke one per task sequentially.

9. **Process verifier results**:
   - VERIFIED_PASS → auditor
   - FAILED, attempts < 3 → increment attempts in STATUS.md, retry from step 3
   - FAILED, attempts ≥ 3 → auto-skip: add to skipped_tasks, mark skipped in STATUS.md

10. **AUDITORS** — invoke one per passing task sequentially.

11. **Process audit results**:
    - CLEAN/WARN → proceed
    - BLOCK → auto-fix: invoke executor once more with BLOCK context + re-verify. Still BLOCK → auto-skip.

12. **MEMORY-KEEPER final** — single invoke, local + global write.

13. **Advance** — mark [x] in PLAN.md, increment done_tasks, reset attempts.
    - If `USE_GIT`: commit PLAN.md + STATUS.md.
    - Find next unchecked group.
    - None → ALL DONE → rename `loop-stack/<LOOP_ID>/` → `loop-stack/<LOOP_ID>_DONE/` (or `_EXTENDED_DONE/` if this was an extended loop) → Phase 6.
    - Else → update STATUS.md → continue loop.

---

## Phase 6 — Completion Report

Write `REPORT.md` inside the renamed loop directory and print summary to user.

---

## Rules

- Phase 0 first — run the check-resume script, never scan `loop-stack/` by hand.
- **File copy**: `cp ~/.config/opencode/skills/loop-engineer/agents/*.md .opencode/agents/` — never manual.
- **Global data first**: every agent reads `.global/MEMORY.md` + `.global/TOOLS.md` before acting.
- **Sequential execution**: OpenCode's `task` tool runs one agent at a time — invoke each, wait, then proceed. This is an upstream bug, not a permanent platform limitation. Status is genuinely in flux: the original report ([#14195](https://github.com/anomalyco/opencode/issues/14195)) was closed as fixed, but sequential dispatch was reported again in a follow-up issue ([#29638](https://github.com/anomalyco/opencode/issues/29638)) with competing fix PRs (#29819, #29848) opened in late May 2026 — check that issue for current merge status before assuming this is still broken, and revisit this file if it's confirmed fixed.
- **Researcher before executor**: always. Dynamic count based on goal complexity.
- **Agent-factory is on-demand, not a fixed phase step.** Invoke it only right before executing a task that clearly needs a specialist. Most loops never call it.
- **knowledge-sources.md is a reference file researchers consult on demand**, not a phase step.
- **No watcher agent.** Check heartbeats yourself if an agent is slow; never invoke a dedicated watcher.
- **Memory-keeper twice per batch**: checkpoint (local) after executors, consolidation (local+global) after audit.
- **Executors append to MEMORY.md directly** during work.
- **Planner**: once at startup after researchers + resource-scout, and again (lightweight) for extended-loop follow-on tasks. Tasks MUST use [G1]/[G2] group tags.
- **Fully autonomous**: no pauses. 3 fails → auto-skip. BLOCK → auto-fix once → skip.
- **doom_loop**: if OpenCode triggers doom_loop detection (3 identical tool calls), the executor agent has `doom_loop: allow` — the loop continues.
- **HARD RULE — no plan-approval gate**: after Phase 1's two questions, proceed through Phase 2 onward without presenting a plan for approval or waiting for a "click proceed" confirmation.
- On completion: rename to `<LOOP_ID>_DONE/` or `<LOOP_ID>_EXTENDED_DONE/`.
- **AGENTS.md**: copy `platforms/opencode/AGENTS.md` to the project root if not present — it gives OpenCode context about the loop.
