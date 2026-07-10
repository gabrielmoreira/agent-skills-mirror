---
name: loop-engineer
description: >
  Loop engineering wizard for Antigravity. Asks 2 questions, then orchestrates
  a fully autonomous parallel agent team (resource-scout, researcher, planner,
  agent-factory, executor, verifier, auditor, memory-keeper) until the goal is met.
  Uses invoke_subagent for true parallel dispatch. Researcher agents use the
  built-in research TypeName. Persistent memory, git integration, resume support.
---

# Loop Engineer (Antigravity)

You are running a loop engineering wizard. Follow these phases in order.

**Prerequisite — reduce permission friction:** confirmed via antigravity.google/docs/permissions — file reads/writes inside your active project are auto-allowed by default, so that part shouldn't interrupt you. `command(...)` actions (every terminal/bash call — including the init and check-resume scripts, and every `git commit` the executor makes) default to **Ask** unless you've added an allow rule. Before running an autonomous loop, add an Allow rule for the commands this loop needs (at minimum `command(bash)`, or `command(*)` for zero friction) via Antigravity's permission settings — either the in-editor approval-card "expand scope" option the first time a command prompts, or your project/user settings directly. Without this, the loop will pause on every single Bash call, which defeats "fully autonomous."

---

## Phase 0 — Resume Check

Run the resume-check script FIRST — unconditionally. It is the source of truth; do not scan `loop-stack/` yourself.

**Bash:**
```bash
CHECK="$(ls \
  "$HOME/.gemini/antigravity-cli/skills/loop-engineer/scripts/check-resume.sh" \
  "$HOME/.gemini/antigravity/skills/loop-engineer/scripts/check-resume.sh" \
  "$HOME/.gemini/config/skills/loop-engineer/scripts/check-resume.sh" 2>/dev/null | head -1)"
bash "$CHECK"
```

**PowerShell:**
```powershell
$check = @(
  "$env:USERPROFILE\.gemini\antigravity-cli\skills\loop-engineer\scripts\check-resume.ps1",
  "$env:USERPROFILE\.gemini\antigravity\skills\loop-engineer\scripts\check-resume.ps1",
  "$env:USERPROFILE\.gemini\config\skills\loop-engineer\scripts\check-resume.ps1"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
& $check
```

Read its output literally, then branch:

**`ACTIVE <id> | State: ... | Task: ... | Progress: ...`:**
- Continuation intent ("continue", "proceed", "finish", "resume", "pick up", "fix what", "audit findings", "where we left") → auto-resume to Phase 5 without asking.
- Otherwise show State/Current Task/Progress, ask: Resume or Fresh?
  - Resume → skip to Phase 5.
  - Fresh → delete `loop-stack/<id>/` only (keep `.agents/`), continue to Phase 1.
- Multiple `ACTIVE` lines → list all, ask which to resume or 'fresh'. Continuation intent → auto-resume most recently modified.

**`DONE <id>` or `EXTENDED_DONE <id>` (no `ACTIVE` line) + continuation intent:**
→ **EXTEND SEQUENCE** — reopen in place, don't restart:
1. Rename `loop-stack/<id>_DONE/` (or `_EXTENDED_DONE/`) → `loop-stack/<id>_EXTENDED/`.
2. Reuse existing PLAN.md, RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md, `agents/` as-is — do not re-run researchers, resource-scout, or agent-factory.
3. Ask ONE question: "What's the next task for this loop?" Append under `## Extension {N} Goal` in PLAN.md.
4. Invoke `planner` (`TypeName: "self"`) once against the new goal (existing RESEARCH.md/TOOLS.md as context) to append new `[GN]` tasks.
5. Reset STATUS.md: State = IN_PROGRESS, Current Task = first new task, Task Progress updated.
6. Go directly to Phase 5 (skip Phase 1–4).

On completion of a loop directory containing `_EXTENDED`: Phase 6 renames it to `_EXTENDED_DONE` instead of plain `_DONE`.

**`NONE`, or `DONE`/`EXTENDED_DONE` with no continuation intent:** → Phase 1 (fresh loop).

**RESUME/EXTEND RULES — always apply when going to Phase 5 this way:**
Skip Phase 2, 3, and 4 entirely. Read STATUS.md + PLAN.md to find where the loop stopped. Reuse existing RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md — do not re-run startup agents.

> **To update loop-engineer:** re-run `install.sh --update` / `install.ps1 -Update -Antigravity`. Updates are never applied automatically mid-loop.

---

## Phase 1 — Core Wizard

**Q1:** "What do you want the loop to accomplish? (1-2 sentences)"

Generate LOOP_ID: lowercase slug, first 4 meaningful words, max 24 chars.
Auto-set: `STOP_CONDITION` = "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked", `MAX_TURNS` = 20.

**Q2:** "Should the loop auto-commit after each verified task? (yes / no)"

---

## Phase 2+3 — Initialize Loop

Run the init script — tries all three Antigravity surface paths automatically:

**Bash (macOS/Linux):**
```bash
INIT_SCRIPT="$(ls \
  "$HOME/.gemini/antigravity-cli/skills/loop-engineer/scripts/init-loop.sh" \
  "$HOME/.gemini/antigravity/skills/loop-engineer/scripts/init-loop.sh" \
  "$HOME/.gemini/config/skills/loop-engineer/scripts/init-loop.sh" 2>/dev/null | head -1)"
bash "$INIT_SCRIPT" \
  --loop-id <LOOP_ID> \
  --goal "<GOAL>" \
  --stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" \
  --git <yes/no> \
  --platform antigravity
```

**PowerShell (Windows):**
```powershell
$init = @(
  "$env:USERPROFILE\.gemini\antigravity-cli\skills\loop-engineer\scripts\init-loop.ps1",
  "$env:USERPROFILE\.gemini\antigravity\skills\loop-engineer\scripts\init-loop.ps1",
  "$env:USERPROFILE\.gemini\config\skills\loop-engineer\scripts\init-loop.ps1"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
& $init -LoopId "<LOOP_ID>" -Goal "<GOAL>" `
  -Stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" `
  -Git <yes/no> -Platform antigravity
```

If the script is missing, install the skill first:
`git clone https://github.com/vibhasdutta/loop-engineer && bash install.sh --antigravity`

The script creates `loop-stack/<LOOP_ID>/`, `.agents/` with all agent .md files + knowledge-sources/, and `verifier.md` with the actual stop condition substituted.

---

## Phase 4 — Startup Sequence

**How parallel dispatch actually works in Antigravity:** confirmed via official docs (antigravity.google/docs/subagents) — there is no "Subagents array" parameter. The real mechanism: calling `invoke_subagent` spawns a subagent that "immediately begins executing its task" and "runs asynchronously in the background, allowing the parent agent to delegate a task and immediately resume its own work." So to get true concurrency, call `invoke_subagent` multiple times back-to-back in the same turn — each call returns right away without blocking, so N calls in a row dispatch N subagents running concurrently. Then wait for all of them to send their completion messages before proceeding to the next step.

**Nesting limit:** a maximum depth of 10 levels of subagents-of-subagents is enforced. Not a concern for loop-engineer's flat dispatch pattern, but worth knowing if an agent-factory-created specialist tries to spawn its own subagents.

**IMPORTANT:** Subagents start with a clean slate — no parent context. Every `Prompt` must be fully self-contained with the loop directory path, what to read, what to write, and a reference to the agent's instruction file in `.agents/`.

### Step 1 — Parallel RESEARCHERS (dynamic count)

Determine researcher count by goal complexity:
- Simple/single-domain → 2 researchers
- Medium/multi-domain → 3 researchers
- Large/multi-system → 4 researchers

Call `invoke_subagent` once per researcher, back-to-back in the same turn (each call returns immediately, so this dispatches all of them concurrently — see note above).
Use `TypeName: "research"` — the built-in type optimized for codebase exploration.

Domains to distribute:
- **Context & Prior Work**: source structure, patterns, package files, existing tests
- **External Knowledge & Resources**: README, docs/, external APIs, .env.example, configs
- **Requirements & Constraints**: DB schema, data models, state management (for 3+ researchers)
- **Environment & Integration**: CI/CD, infrastructure, build, Docker (for 4 researchers)

Each researcher Prompt:
```
Loop directory: loop-stack/<LOOP_ID>/
Focus: {ASSIGNED_DOMAIN} — {specific files and concerns}
GLOBAL DATA FIRST: read loop-stack/.global/MEMORY.md and loop-stack/.global/TOOLS.md.
Write findings to loop-stack/<LOOP_ID>/RESEARCH.md under "## {Domain Name}".
Update loop-stack/<LOOP_ID>/STATUS.md "Last Researcher Result".
Read .agents/researcher.md for full instructions.
```

**Stuck-agent check (no watcher subagent needed):** Antigravity already exposes `manage_subagents(Action: "list")` — use it directly if one researcher is taking noticeably longer than its peers, to see whether it's still running or has stalled. If stalled, proceed without it and note `{agent}: STUCK — no output` in STATUS.md `## Active Heartbeats`.

Wait for all researcher subagents to complete before Step 2.

### Step 2 — RESOURCE SCOUT

Call `invoke_subagent` with one entry, `TypeName: "self"`:
```
Loop directory: loop-stack/<LOOP_ID>/
Check loop-stack/.global/TOOLS.md — if < 7 days old, reuse it.
Otherwise discover all tools. Write to loop-stack/<LOOP_ID>/TOOLS.md AND loop-stack/.global/TOOLS.md.
Read .agents/resource-scout.md for full instructions.
```
Wait for resource-scout to send its completion message.

### Step 3 — PLANNER

Call `invoke_subagent` with one entry, `TypeName: "self"`:
```
Loop directory: loop-stack/<LOOP_ID>/
Read RESEARCH.md (all sections) and TOOLS.md.
Create 3–7 tasks with parallel group tags [G1], [G2], etc.
Same group = parallel (independent files/modules). Different group = sequential dependency.
Replace "## Tasks" in PLAN.md. Update STATUS.md.
Read .agents/planner.md for full instructions.
```
Wait for planner to send its completion message.

Write `loop-stack/<LOOP_ID>/AGENTS.md` with `# Specialized Agents\n## Status\nNONE CREATED YET`. (Agent-factory is on-demand, not a fixed step — see Rules.) Proceed to Phase 5.

---

## Phase 5 — Outer Loop

**FULLY AUTONOMOUS. Never pause for user input.**

Initialize: `turns_used = 0`, `skipped_tasks = []`.

For parallel steps: call `invoke_subagent` once per agent, back-to-back in the same turn (each call returns immediately without blocking — see Phase 4 note). Wait for all to send completion messages before proceeding.

### Iteration steps:

1. **Budget check** — over MAX_TURNS → Phase 6.

2. **Read state** — identify current parallel group (all unchecked [GN] tasks).

3. **Parallel RESEARCHERS** — one per task (2 if batch=1). Call `invoke_subagent` once per task, back-to-back in the same turn, `TypeName: "research"`:
   ```
   Loop directory: loop-stack/<LOOP_ID>/
   GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
   Focus: {ASSIGNED_DOMAIN} for task: {this_task}
   Append findings to RESEARCH.md under "## Task-Specific Research — {this_task}".
   Update STATUS.md "Last Researcher Result".
   Read .agents/researcher.md for full instructions.
   ```
   Wait for all. Increment turns_used.

4. **Before executors, check AGENTS.md.** For every task in the batch that clearly needs domain expertise beyond a generic executor and has no specialist yet, call `invoke_subagent` once per such task, back-to-back in the same turn (`TypeName: "self"`, each reads `.agents/agent-factory.md`) to create their agent files and update AGENTS.md — same parallel-first rule as researchers/executors. Wait for all to finish. Skip this for most tasks.

5. **Parallel EXECUTORS** — one per task. Call `invoke_subagent` once per task, back-to-back in the same turn, `TypeName: "self"`:
   ```
   Loop directory: loop-stack/<LOOP_ID>/
   GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
   Read MEMORY.md, TOOLS.md, PLAN.md, STATUS.md.
   READ: RESEARCH.md "## Task-Specific Research — {this_task}".
   Current task: {this_task}. Scope: only files for this task.
   Implement. Append discoveries to MEMORY.md directly. Update STATUS.md.
   Goal output (code, documents, files) goes to the project directory, NOT inside loop-stack/. loop-stack/ is state-only.
   Read .agents/executor.md for full instructions.
   ```
   Wait for all. Increment turns_used.

6. **Parallel VERIFIERS** — one per task. Verifier now does both jobs in one pass: checks the task against RESEARCH.md's Verification Criteria (right place, satisfies criteria, no placeholders), then runs the stop condition. `TypeName: "self"`. Wait for all.

7. **Process verifier results**:
   - PASS → auditor
   - FAIL < 3 → retry from step 3
   - FAIL ≥ 3 → auto-skip

8. **Parallel AUDITORS** (passing tasks only) — one per task. `TypeName: "self"`. Wait for all.

9. **Process audit results**:
    - CLEAN/WARN → proceed
    - BLOCK → auto-fix (one executor with BLOCK context, `TypeName: "self"`, re-run verifier). Still BLOCK → auto-skip.

10. **MEMORY-KEEPER consolidation** — single `invoke_subagent`, `TypeName: "self"`, local + global write. This is the only memory-keeper call per batch — executors already appended their raw learnings inline during step 5. Wait.

11. **Advance** — mark [x], git commit if enabled. Find next group.
    None → ALL DONE → rename `loop-stack/<LOOP_ID>/` → `loop-stack/<LOOP_ID>_DONE/` (or `_EXTENDED_DONE/` if this was an extended loop) → Phase 6.

---

## Phase 6 — Completion Report

Write `REPORT.md` inside the renamed loop directory and print summary.

---

## Rules

- Phase 0 first — run the check-resume script, never scan `loop-stack/` by hand.
- **File copy**: try CLI path (`~/.gemini/antigravity-cli/skills/`), then IDE path (`~/.gemini/antigravity/skills/`), then 2.0 path (`~/.gemini/config/skills/`). Never write manually.
- **Global data first**: every agent reads `.global/MEMORY.md` + `.global/TOOLS.md` before acting.
- **invoke_subagent**: parallel = multiple calls back-to-back in the same turn (each returns immediately, no "Subagents array" parameter exists). Sequential = deliberately waiting for one to finish before calling the next. Wait for completion messages between steps.
- **TypeNames**: use `"research"` for researcher agents (built-in, codebase-optimized). Use `"self"` for all others.
- **Self-contained prompts**: subagents have a clean context slate — every Prompt must include loop dir, files to read/write, and `.agents/{role}.md` reference.
- **Researcher before executor**: always. Dynamic count based on goal complexity.
- **Agent-factory is on-demand, not a fixed phase step.** Invoke it only right before executing a task that clearly needs a specialist. Most loops never call it.
- **knowledge-sources.md is a reference file researchers consult on demand**, not a phase step.
- **No watcher agent.** Use `manage_subagents(Action: "list")` directly if you need to check whether an agent is still running; never spawn a dedicated watcher subagent.
- **No separate evaluator.** Verifier does both jobs in one pass: checks the task against RESEARCH.md's Verification Criteria, then runs the stop condition. One agent, one call, same rigor — not two sequential subagents for what's really one quality gate.
- **Memory-keeper runs once per task batch** (after audit, local + global) — not a separate mid-batch checkpoint. Executors already append their own learnings to MEMORY.md directly as they work, so there's nothing left for a checkpoint pass to do that isn't already written.
- **Executors append to MEMORY.md directly** during work.
- **Planner**: once at startup, and again (lightweight) for extended-loop follow-on tasks. Tasks MUST include [G1]/[G2] parallel group tags.
- **Fully autonomous**: no pauses. 3 fails → auto-skip. BLOCK → auto-fix once → skip.
- **HARD RULE — no plan-approval gate**: after Phase 1's two questions, proceed through Phase 2 onward without presenting a plan for approval or waiting for a "click proceed" confirmation. Do not use any native plan-then-approve UX for this loop.
- On completion: rename to `<LOOP_ID>_DONE/` or `<LOOP_ID>_EXTENDED_DONE/`.
- **Monitor**: use `manage_subagents(Action: "list")` to check running subagents if needed.
- **AGENTS.md**: ensure `AGENTS.md` is in the project root for workspace context.
- **MCP config**: remote servers require `serverUrl` field (not `url` or `httpUrl`).
