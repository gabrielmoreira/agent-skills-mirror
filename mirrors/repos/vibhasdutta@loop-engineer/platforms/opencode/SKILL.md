---
name: loop-engineer
description: >
  Loop engineering wizard for OpenCode. Asks 3 questions, then orchestrates
  a fully autonomous agent team (resource-scout, researcher, planner, agent-factory, executor,
  verifier, auditor, memory-keeper) until the goal is met.
  Agents run sequentially via the task tool. Dynamic researcher count. Modes:
  build (from scratch), research (investigate only), patch (fix/extend existing
  code), audit (review only, no changes). Persistent memory, git integration.
---

# Loop Engineer (OpenCode)

You are running a loop engineering wizard. Follow these phases in order.

---

> **To update loop-engineer:** re-run `install.sh --update` / `install.ps1 -Update -OpenCode`. Updates are never applied automatically mid-loop.

---

## Phase 1 — Core Wizard

**Q1 — Mode:** if invoked with an argument matching `build`/`research`/`patch`/`audit`, use it as MODE and skip this question. Otherwise ask: "Mode? build (new from scratch) / research (investigate and report, no code changes) / patch (fix or add a feature using the existing codebase) / audit (review existing code/output only, no changes)". Default to `build` if unclear.

**Q2:** "What do you want the loop to accomplish? (1-2 sentences)"

Generate LOOP_ID: lowercase slug, first 4 meaningful words, max 24 chars.
Auto-set: `STOP_CONDITION` = "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked", `MAX_TURNS` = 20.

**Q3:** "Should the loop auto-commit after each verified task? (yes / no)"

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
  --mode <MODE> \
  --platform opencode
```

**PowerShell (Windows):**
```powershell
$init = "$env:USERPROFILE\.config\opencode\skills\loop-engineer\scripts\init-loop.ps1"
if (-not (Test-Path $init)) { $init = "$env:USERPROFILE\.claude\skills\loop-engineer\scripts\init-loop.ps1" }
& $init -LoopId "<LOOP_ID>" -Goal "<GOAL>" `
  -Stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" `
  -Git <yes/no> -Mode <MODE> -Platform opencode
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
  Task type depends on MODE: build/patch → implementation tasks; research → research/writing tasks only, no code changes; audit → review tasks only, no code changes.
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

**Mode gating:** build (default) — full flow. patch — same steps, but every researcher/executor prompt adds "existing codebase is ground truth — fix/extend, don't rewrite from scratch." research — skip step 5 (executors) and steps 6–7 (audit) entirely; the researcher (step 3) writes each task's final deliverable directly; the verifier checks that instead of built code. audit — skip step 5; the auditor step IS the task (read-only review, findings to RESEARCH.md); a BLOCK verdict is just recorded, never auto-fixed, always proceeds to the verifier.

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

6. **AUDITORS** — invoke one per task just built, sequentially.

7. **Process audit results**:
   - CLEAN/WARN → proceed to verifier
   - BLOCK → auto-fix: invoke executor once more with BLOCK context + re-audit once. Still BLOCK → auto-skip.

8. **VERIFIERS** — invoke one per task that passed audit, sequentially. Verifier is the final gate: checks the task against RESEARCH.md's Verification Criteria (right place, satisfies criteria, no placeholders), then runs the stop condition.

9. **Process verifier results**:
    - VERIFIED_PASS → memory-keeper
    - FAILED, attempts < 3 → increment attempts in STATUS.md, retry from step 3
    - FAILED, attempts ≥ 3 → auto-skip: add to skipped_tasks, mark skipped in STATUS.md

10. **MEMORY-KEEPER consolidation** — single invoke, local + global write. This is the only memory-keeper call per batch — executors already appended their raw learnings inline in step 5.

11. **Advance** — mark [x] in PLAN.md, increment done_tasks, reset attempts.
    - If `USE_GIT`: commit PLAN.md + STATUS.md.
    - Find next unchecked group.
    - None → ALL DONE → rename `loop-stack/<LOOP_ID>/` → `loop-stack/<LOOP_ID>_DONE/` → Phase 6.
    - Else → update STATUS.md → continue loop.

---

## Phase 6 — Completion Report

Write `REPORT.md` inside the renamed loop directory and print summary to user.

---

## Rules

- **File copy**: `cp ~/.config/opencode/skills/loop-engineer/agents/*.md .opencode/agents/` — never manual.
- **Global data first**: every agent reads `.global/MEMORY.md` + `.global/TOOLS.md` before acting.
- **Sequential execution**: OpenCode's `task` tool runs one agent at a time — invoke each, wait, then proceed. This is an upstream bug, not a permanent platform limitation. Status is genuinely in flux: the original report ([#14195](https://github.com/anomalyco/opencode/issues/14195)) was closed as fixed, but sequential dispatch was reported again in a follow-up issue ([#29638](https://github.com/anomalyco/opencode/issues/29638)) with competing fix PRs (#29819, #29848) opened in late May 2026 — check that issue for current merge status before assuming this is still broken, and revisit this file if it's confirmed fixed.
- **Researcher before executor**: always. Dynamic count based on goal complexity.
- **Agent-factory is on-demand, not a fixed phase step.** Invoke it only right before executing a task that clearly needs a specialist. Most loops never call it.
- **knowledge-sources.md is a reference file researchers consult on demand**, not a phase step.
- **No watcher agent.** Check heartbeats yourself if an agent is slow; never invoke a dedicated watcher.
- **No separate evaluator.** Verifier is the final gate: checks the task against RESEARCH.md's Verification Criteria, then runs the stop condition. One agent, one call, same rigor.
- **Audit before verify.** Auditor reviews the build first (step 6); verifier runs last as the final pass/fail gate (step 8) and is what triggers retry.
- **Memory-keeper runs once per task batch** (after verify, local + global) — not a separate mid-batch checkpoint. Executors already append their own learnings to MEMORY.md directly as they work. Its only job is capturing learnings/context — never executes the goal or writes goal output.
- **Executors append to MEMORY.md directly** during work.
- **Planner**: once at startup after researchers + resource-scout. Tasks MUST use [G1]/[G2] group tags.
- **Fully autonomous**: no pauses. Audit BLOCK → auto-fix once → skip. 3 verifier fails → auto-skip.
- **Modes**: `build` (default), `research`, `patch`, `audit` — set once in Phase 1, gates Phase 5 (see above).
- **doom_loop**: if OpenCode triggers doom_loop detection (3 identical tool calls), the executor agent has `doom_loop: allow` — the loop continues.
- **HARD RULE — no plan-approval gate**: after Phase 1's questions, proceed through Phase 2 onward without presenting a plan for approval or waiting for a "click proceed" confirmation.
- No resume support: every invocation starts a fresh loop. On completion: rename to `<LOOP_ID>_DONE/` (bookkeeping only).
- **AGENTS.md**: copy `platforms/opencode/AGENTS.md` to the project root if not present — it gives OpenCode context about the loop.
