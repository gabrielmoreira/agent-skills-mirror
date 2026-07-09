---
name: loop-engineer
description: >
  Loop engineering wizard for Cursor. Asks 2 questions, then orchestrates
  a fully autonomous parallel agent team (resource-scout, researcher, planner,
  agent-factory, executor, evaluator, verifier, auditor, memory-keeper) for any goal.
  Multiple agents run in parallel — dynamic researcher count, multiple executors
  on independent parts simultaneously. Persistent memory, git integration, resume support.
---

# Loop Engineer (Cursor)

You are running a loop engineering wizard. Follow these phases in order.

---

## Phase 0 — Resume Check

Run the resume-check script FIRST — unconditionally. It is the source of truth; do not scan `loop-stack/` yourself.

**Bash:** `bash ~/.cursor/skills/loop-engineer/scripts/check-resume.sh`
**PowerShell:** `& "$env:USERPROFILE\.cursor\skills\loop-engineer\scripts\check-resume.ps1"`

Read its output literally, then branch:

**`ACTIVE <id> | State: ... | Task: ... | Progress: ...`:**
- Continuation intent ("continue", "proceed", "finish", "resume", "pick up", "fix what", "audit findings", "where we left") → auto-resume to Phase 5 without asking.
- Otherwise show State/Current Task/Progress, ask: Resume or Fresh?
  - Resume → skip to Phase 5 using existing files.
  - Fresh → delete `loop-stack/<id>/` only (keep `.cursor/agents/`), continue to Phase 1.
- Multiple `ACTIVE` lines → list all, ask which to resume or 'fresh'. Continuation intent → auto-resume most recently modified.

**`DONE <id>` or `EXTENDED_DONE <id>` (no `ACTIVE` line) + continuation intent:**
→ **EXTEND SEQUENCE** — reopen in place, don't restart:
1. Rename `loop-stack/<id>_DONE/` (or `_EXTENDED_DONE/`) → `loop-stack/<id>_EXTENDED/`.
2. Reuse existing PLAN.md, RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md, `agents/` as-is — do not re-run researchers, resource-scout, or agent-factory.
3. Ask ONE question: "What's the next task for this loop?" Append under `## Extension {N} Goal` in PLAN.md.
4. Run planner once against the new goal (existing RESEARCH.md/TOOLS.md as context) to append new `[GN]` tasks.
5. Reset STATUS.md: State = IN_PROGRESS, Current Task = first new task, Task Progress updated.
6. Go directly to Phase 5 (skip Phase 1–4).

On completion of a loop directory containing `_EXTENDED`: Phase 6 renames it to `_EXTENDED_DONE` instead of plain `_DONE`.

**`NONE`, or `DONE`/`EXTENDED_DONE` with no continuation intent:** → Phase 1 (fresh loop).

**RESUME/EXTEND RULES — always apply when going to Phase 5 this way:**
Skip Phase 2, 3, and 4 entirely. Read STATUS.md + PLAN.md to find where the loop stopped. Reuse existing RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md — do not re-run startup agents.

> **To update loop-engineer:** re-run `install.sh --update` / `install.ps1 -Update -Cursor` (manual install). Updates are never applied automatically mid-loop.

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
bash ~/.cursor/skills/loop-engineer/scripts/init-loop.sh \
  --loop-id <LOOP_ID> \
  --goal "<GOAL>" \
  --stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" \
  --git <yes/no> \
  --platform cursor
```

**PowerShell (Windows):**
```powershell
& "$env:USERPROFILE\.cursor\skills\loop-engineer\scripts\init-loop.ps1" `
  -LoopId "<LOOP_ID>" `
  -Goal "<GOAL>" `
  -Stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" `
  -Git <yes/no> `
  -Platform cursor
```

If the script is missing, install the skill first:
`git clone https://github.com/vibhasdutta/loop-engineer && bash install.sh --cursor`

The script creates `loop-stack/<LOOP_ID>/`, `.cursor/agents/` with all agent .md files + knowledge-sources/, and `verifier.md` with the actual stop condition substituted.

---

## Phase 4 — Startup Sequence

**FULLY AUTONOMOUS from this point. Never pause or ask the user anything.**

**How parallel dispatch actually works in Cursor:** confirmed via official docs (cursor.com/docs/subagents) — subagents are dispatched through the **`Task` tool**. Sending multiple `Task` tool calls in a single message/response runs them simultaneously: *"Agent sends multiple Task tool calls in a single message, so subagents run simultaneously."* Calling `Task` once, waiting, then calling it again runs sequentially — the concurrency comes specifically from batching multiple calls into one message, exactly like the steps below describe.

### Step 1 — Parallel RESEARCHERS (dynamic count)

Determine researcher count by goal complexity:
- Simple/single-domain → 2
- Medium/multi-domain → 3
- Large/multi-system → 4

**Spawn all simultaneously** (call the `Task` tool N times in one response — that's what makes them concurrent, per Cursor's docs).

Divide domains across researchers:
- **Context & Prior Work**: source structure, patterns, package.json/pyproject.toml/go.mod, tests
- **External Knowledge & Resources**: README, docs/, external APIs, .env.example, configs, integrations
- **Requirements & Constraints**: DB schema, data models, state management (for 3+ researchers)
- **Environment & Integration**: CI/CD, infrastructure, build, Docker (for 4 researchers)

Each researcher prompt:
```
Loop directory: loop-stack/<LOOP_ID>/
Focus: {ASSIGNED_DOMAIN} — {specific files and concerns}
GLOBAL DATA FIRST: read loop-stack/.global/MEMORY.md and loop-stack/.global/TOOLS.md.
Write findings to loop-stack/<LOOP_ID>/RESEARCH.md under "## {Domain Name}".
Update STATUS.md "Last Researcher Result".
Follow .cursor/agents/researcher.md.
```

**Stuck-agent check (you do this yourself — no subagent):** if one researcher takes much longer than its peers, check its heartbeat line in STATUS.md `## Active Heartbeats`. If stale, treat it STUCK, note it, and proceed without it.

Wait for ALL to complete.

### Step 2 — RESOURCE SCOUT

```
Loop directory: loop-stack/<LOOP_ID>/
Check loop-stack/.global/TOOLS.md — if < 7 days old, reuse. Otherwise discover all tools.
Write to loop-stack/<LOOP_ID>/TOOLS.md AND loop-stack/.global/TOOLS.md.
Follow .cursor/agents/resource-scout.md.
```

### Step 3 — PLANNER

```
Loop directory: loop-stack/<LOOP_ID>/
Read RESEARCH.md (all sections) and TOOLS.md.
Create 3–7 tasks with parallel group tags [G1], [G2], etc.
Same group = can run in parallel (independent files/modules).
Different group = sequential dependency.
Example:
  - [ ] [G1] Set up project config and database schema
  - [ ] [G2] Implement API authentication endpoints
  - [ ] [G2] Implement user profile frontend component
  - [ ] [G3] Integration tests
Replace "## Tasks" in PLAN.md. Update STATUS.md.
Follow .cursor/agents/planner.md.
```

Write `loop-stack/<LOOP_ID>/AGENTS.md` with `# Specialized Agents\n## Status\nNONE CREATED YET`. (Agent-factory is on-demand, not a fixed step — see Rules.)

Auto-continue into outer loop.

---

## Phase 5 — Outer Loop

**FULLY AUTONOMOUS. Never pause for user input.**

Initialize: `turns_used = 0`, `skipped_tasks = []`, read total_tasks.

Print per iteration: `[Task {done+1}/{total} — {pct}% | Turn {turn}/{MAX_TURNS}]`

### Step 1 — Budget check → over MAX_TURNS → Phase 6.

### Step 2 — Read state. Identify current parallel group (all unchecked [GN] tasks).

### Step 3 — Parallel RESEARCHERS
Spawn one per task in batch (2 if batch=1, more if task is complex). Each appends to RESEARCH.md. Wait for all. Increment turns_used.

**Before executors, check AGENTS.md.** For every task in the batch that clearly needs domain expertise beyond a generic executor and has no specialist yet, spawn agent-factory for all of them simultaneously in the same response (same parallel-first rule as researchers/executors — create 1 agent file per task in `loop-stack/<LOOP_ID>/agents/`, update AGENTS.md). Wait for all to finish. Skip this for most tasks.

### Step 4 — Parallel EXECUTORS
Spawn one per task simultaneously:
```
Loop directory: loop-stack/<LOOP_ID>/
GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
Read MEMORY.md, TOOLS.md, PLAN.md, STATUS.md.
READ: RESEARCH.md section "## Task-Specific Research — {this_task}".
Current task: {this_task}. Scope: only files for this task.
Implement. Append discoveries directly to MEMORY.md. Update STATUS.md.
Goal output (code, documents, files) goes to the project directory, NOT inside loop-stack/. loop-stack/ is state-only.
Follow .cursor/agents/executor.md.
```
Wait for all. Increment turns_used.

### Step 5 — Parallel MEMORY-KEEPER checkpoints
One per task: local MEMORY.md only. Wait for all.

### Step 6 — Parallel EVALUATORS. One per task. Wait for all.

### Step 7 — Parallel VERIFIERS. One per task. Wait for all.

### Step 8 — Process results
- PASS → auditor
- FAIL < 3 attempts → retry from Step 3
- FAIL ≥ 3 → auto-skip

### Step 9 — Parallel AUDITORS (per passing task). Wait for all.

### Step 10 — Process audit results
- CLEAN/WARN → proceed
- BLOCK → auto-fix (one executor retry + re-verify). Still BLOCK → auto-skip.

### Step 11 — MEMORY-KEEPER final consolidation (single)
Distill all completed tasks. Write to MEMORY.md + loop-stack/.global/MEMORY.md.

### Step 12 — Advance
Mark [x]. Git commit if enabled. Find next group. None → ALL DONE →
rename `loop-stack/<LOOP_ID>/` → `loop-stack/<LOOP_ID>_DONE/` (or `_EXTENDED_DONE/` if this was an extended loop) → Phase 6.

---

## Phase 6 — Completion Report

Write `REPORT.md` inside the renamed loop directory and print summary.

---

## Rules

- Phase 0 first — run the check-resume script, never scan `loop-stack/` by hand.
- **File copy**: shell commands only. Never write agent files manually.
- **Global data first**: every agent reads `.global/MEMORY.md` + `.global/TOOLS.md`.
- **Parallel first**: same group = spawn simultaneously. Different group = sequential. Confirmed native mechanism (cursor.com/docs/subagents): multiple `Task` tool calls sent in one message run concurrently. One call, wait, another call runs sequentially — batching into a single message/response is what makes it parallel.
- **Custom subagent files**: Cursor reads `.cursor/agents/*.md` (project) or `~/.cursor/agents/*.md` (user). It also recognizes `.claude/agents/` and `.codex/agents/` for cross-tool compatibility, with `.cursor/` taking precedence on name conflicts — loop-engineer installs to `.cursor/agents/` directly, so this doesn't change anything, just avoids confusion if you see those other dirs referenced elsewhere.
- **Nesting**: the main agent and its direct subagents can launch further subagents; a subagent launched by another subagent cannot launch its own (effectively 2 levels deep).
- **Researcher before executor**: always. Dynamic count.
- **Agent-factory is on-demand, not a fixed phase step.** Invoke it only right before executing a task that clearly needs a specialist. Most loops never call it.
- **knowledge-sources.md is a reference file researchers consult on demand**, not a phase step.
- **No watcher agent.** Check heartbeats yourself if an agent is slow; never spawn a dedicated watcher.
- **Memory-keeper twice per batch**: checkpoint (local) after executors, consolidation (local+global) after audit.
- **Executors append to MEMORY.md directly** during work.
- **Planner**: once at startup after researchers + resource-scout, and again (lightweight) for extended-loop follow-on tasks.
- **Fully autonomous**: no pauses. 3 fails → auto-skip. BLOCK → auto-fix once → skip.
- **HARD RULE — no plan-approval gate**: after Phase 1's two questions, proceed through Phase 2 onward without presenting a plan for approval or waiting for a "click proceed" confirmation.
- On completion: rename to `<LOOP_ID>_DONE/` or `<LOOP_ID>_EXTENDED_DONE/`.
