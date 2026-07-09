---
name: loop-engineer
description: >
  Loop engineering wizard for Gemini CLI. Asks 2 questions, then orchestrates
  a fully autonomous agent team (resource-scout, researcher, planner,
  agent-factory, executor, evaluator, verifier, auditor, memory-keeper) until the goal is met.
  Each agent is a named tool. On Gemini CLI v0.36+, subagents run in true
  parallel (spawn multiple in one turn); on older versions, invoke one at a
  time. Dynamic researcher count. Persistent memory, git integration, resume
  support.
---

# Loop Engineer (Gemini CLI)

You are running a loop engineering wizard. Follow these phases in order.

---

## Phase 0 — Resume Check

Run the resume-check script FIRST — unconditionally. It is the source of truth; do not scan `loop-stack/` yourself.

**Bash:** `bash ~/.gemini/skills/loop-engineer/scripts/check-resume.sh`
**PowerShell:** `& "$env:USERPROFILE\.gemini\skills\loop-engineer\scripts\check-resume.ps1"`

Read its output literally, then branch:

**`ACTIVE <id> | State: ... | Task: ... | Progress: ...`:**
- Continuation intent ("continue", "proceed", "finish", "resume", "pick up", "fix what", "audit findings", "where we left") → auto-resume to Phase 5 without asking.
- Otherwise show State/Current Task/Progress, ask: Resume or Fresh?
  - Resume → skip to Phase 5.
  - Fresh → delete `loop-stack/<id>/` only (keep `.gemini/agents/`), continue to Phase 1.
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

> **To update loop-engineer:** `gemini skills update loop-engineer` or re-run `install.sh --update` / `install.ps1 -Update -Gemini`. Updates are never applied automatically mid-loop.

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
bash ~/.gemini/skills/loop-engineer/scripts/init-loop.sh \
  --loop-id <LOOP_ID> \
  --goal "<GOAL>" \
  --stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" \
  --git <yes/no> \
  --platform gemini
```

**PowerShell (Windows):**
```powershell
& "$env:USERPROFILE\.gemini\skills\loop-engineer\scripts\init-loop.ps1" `
  -LoopId "<LOOP_ID>" `
  -Goal "<GOAL>" `
  -Stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" `
  -Git <yes/no> `
  -Platform gemini
```

If the script is missing, install the skill first:
```bash
gemini skills install https://github.com/vibhasdutta/loop-engineer
# or local: gemini skills link ./loop-engineer
```

The script creates `loop-stack/<LOOP_ID>/`, `.gemini/agents/` with all agent .md files + knowledge-sources/, and `verifier.md` with the actual stop condition substituted.

---

## Phase 4 — Startup Sequence

Invoke agents by calling their named agent tool (each agent in `.gemini/agents/` becomes a callable tool).

**Check your Gemini CLI version first** (`gemini --version`, or check for parallel subagent support in your build):
- **v0.36+**: subagents run in **true parallel** — call multiple agent tools in the same turn/response and Gemini CLI's scheduler dispatches them concurrently. Use this for every "parallel" step below.
- **Older versions**: no concurrent subagent dispatch — invoke each agent in turn, wait for completion, then invoke the next.

### Step 1 — RESEARCHERS (dynamic count, parallel on v0.36+)

Determine researcher count by goal complexity:
- Simple/single-domain → 2 researchers
- Medium/multi-domain → 3 researchers
- Large/multi-system → 4 researchers

**Call all researcher agent tools in the same turn** (v0.36+: they run concurrently; pre-v0.36: invoke one at a time and wait for each):

Domains to distribute:
- **Context & Prior Work**: source structure, patterns, package files, tests
- **External Knowledge & Resources**: README, docs/, external APIs, .env.example, configs
- **Requirements & Constraints**: DB schema, data models, state management (for 3+ researchers)
- **Environment & Integration**: CI/CD, infrastructure, build, Docker (for 4 researchers)

Each researcher prompt:
```
Loop directory: loop-stack/<LOOP_ID>/
Focus: {ASSIGNED_DOMAIN} — {specific files and concerns}
GLOBAL DATA FIRST: read loop-stack/.global/MEMORY.md and loop-stack/.global/TOOLS.md.
Write findings to loop-stack/<LOOP_ID>/RESEARCH.md under "## {Domain Name}".
Update STATUS.md "Last Researcher Result".
```

Wait for all researchers to complete before Step 2.

**Stuck-agent check (you do this yourself — no subagent):** if a researcher took much longer than the others, check its heartbeat line in STATUS.md `## Active Heartbeats`. If stale, treat it STUCK, note it, and proceed with the findings you have.

### Step 2 — RESOURCE SCOUT

Invoke the `resource-scout` agent:
```
Loop directory: loop-stack/<LOOP_ID>/
Check loop-stack/.global/TOOLS.md — if < 7 days old, reuse. Otherwise discover all tools.
Write to loop-stack/<LOOP_ID>/TOOLS.md AND loop-stack/.global/TOOLS.md.
```
Wait for subagent to complete.

### Step 3 — PLANNER

Invoke the `planner` agent:
```
Loop directory: loop-stack/<LOOP_ID>/
Read RESEARCH.md (all sections) and TOOLS.md.
Create 3–7 tasks with parallel group tags [G1], [G2], etc.
Same group = parallel (independent files). Different group = sequential dependency.
Replace "## Tasks" in PLAN.md. Update STATUS.md.
```
Wait for subagent to complete.

Write `loop-stack/<LOOP_ID>/AGENTS.md` with `# Specialized Agents\n## Status\nNONE CREATED YET`. (Agent-factory is on-demand, not a fixed step — see Rules.) Auto-continue into outer loop.

---

## Phase 5 — Outer Loop

**FULLY AUTONOMOUS. Never pause for user input.**

Initialize: `turns_used = 0`, `skipped_tasks = []`.

**v0.36+**: call multiple agent tools in the same turn wherever a step says "parallel" — Gemini CLI runs them concurrently. **Pre-v0.36**: invoke each agent, wait for completion, then invoke the next, even for "parallel" steps.

### Iteration steps:

1. **Budget check** — over MAX_TURNS → Phase 6.

2. **Read state** — identify current parallel group (all unchecked [GN] tasks).

3. **RESEARCHERS (parallel)** — one per task in batch (2 if batch=1), all called in the same turn on v0.36+.
   Each appends to RESEARCH.md. Increment turns_used.

4. **Before executors, check AGENTS.md.** For every task in the batch that clearly needs domain expertise beyond a generic executor and has no specialist yet, call `agent-factory` for all of them in the same turn (v0.36+: concurrent) to create their agent files and update AGENTS.md. Skip this for most tasks.

5. **EXECUTORS (parallel)** — one per task, all called in the same turn on v0.36+:
   ```
   Loop directory: loop-stack/<LOOP_ID>/
   GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
   Read MEMORY.md, TOOLS.md, PLAN.md, STATUS.md.
   READ: RESEARCH.md "## Task-Specific Research — {this_task}".
   Current task: {this_task}. Scope: only files for this task.
   Implement. Append discoveries to MEMORY.md. Update STATUS.md.
   Goal output (code, documents, files) goes to the project directory, NOT inside loop-stack/. loop-stack/ is state-only.
   ```
   Increment turns_used.

6. **MEMORY-KEEPER checkpoints (parallel)** — one per task. Local only.

7. **EVALUATORS (parallel)** — one per task.

8. **VERIFIERS (parallel)** — one per task.

9. **Process verifier results**:
   - PASS → auditor
   - FAIL < 3 → retry from step 3
   - FAIL ≥ 3 → auto-skip

10. **AUDITORS (parallel)** — one per passing task.

11. **Process audit results**:
    - CLEAN/WARN → proceed
    - BLOCK → auto-fix (one executor retry + re-verify). Still BLOCK → auto-skip.

12. **MEMORY-KEEPER final** — single invoke, local + global write.

13. **Advance** — mark [x], git commit if enabled. Find next group.
    None → ALL DONE → rename `loop-stack/<LOOP_ID>/` → `loop-stack/<LOOP_ID>_DONE/` (or `_EXTENDED_DONE/` if this was an extended loop) → Phase 6.

---

## Phase 6 — Completion Report

Write `REPORT.md` inside the renamed loop directory and print summary.

---

## Rules

- Phase 0 first — run the check-resume script, never scan `loop-stack/` by hand.
- **File copy**: `cp ~/.gemini/skills/loop-engineer/agents/*.md .gemini/agents/` — never manual.
- **Global data first**: every agent reads `.global/MEMORY.md` + `.global/TOOLS.md` before acting.
- **Parallel on v0.36+**: Gemini CLI added true concurrent subagent dispatch in v0.36 (April 2026) — call multiple agent tools in the same turn for any "parallel" step and they run concurrently. Confirm your version with `gemini --version`. Ordinary (non-subagent) tool calls remain sequential regardless of version.
- **Pre-v0.36 fallback**: no concurrent dispatch exists — invoke each agent, wait, then invoke the next, even for steps marked "parallel" above.
- **Official caveat on parallel execution** (developers.googleblog.com): avoid parallel executors for tasks with heavy overlapping file edits — concurrent agents editing the same files can conflict or overwrite each other. This is already covered by "stay in your lane, don't touch files other parallel executors are handling," but Gemini's own docs call it out explicitly, so take it seriously when scoping parallel executor tasks.
- **No subagent nesting, ever**: Gemini CLI subagents cannot call other subagents under any circumstances — even a subagent with wildcard (`*`) tool access can't see or invoke other agents. Not a concern for loop-engineer's flat dispatch, but don't design a specialist that assumes it can delegate further.
- **Researcher before executor**: always. Dynamic count based on goal complexity.
- **Agent-factory is on-demand, not a fixed phase step.** Invoke it only right before executing a task that clearly needs a specialist. Most loops never call it.
- **knowledge-sources.md is a reference file researchers consult on demand**, not a phase step.
- **No watcher agent.** Check heartbeats yourself if an agent is slow; never invoke a dedicated watcher.
- **Memory-keeper twice per batch**: checkpoint (local) after executors, consolidation (local+global) after audit.
- **Executors append to MEMORY.md directly** during work.
- **Planner**: once at startup after researchers + resource-scout, and again (lightweight) for extended-loop follow-on tasks. Tasks MUST use [G1]/[G2] group tags.
- **Fully autonomous**: no pauses. 3 fails → auto-skip. BLOCK → auto-fix once → skip.
- **HARD RULE — no plan-approval gate**: after Phase 1's two questions, proceed through Phase 2 onward without presenting a plan for approval or waiting for a "click proceed" confirmation.
- On completion: rename to `<LOOP_ID>_DONE/` or `<LOOP_ID>_EXTENDED_DONE/`.
- **GEMINI.md**: copy `platforms/gemini/GEMINI.md` to the project root if not present — it guides skill activation.
- **Checkpointing**: Gemini CLI auto-checkpoints sessions. Loop state in `loop-stack/` survives context resets independently — both layers complement each other.
- **Project-level MCP config**: `.gemini/settings.json` in the project root overrides global settings — resource-scout checks both.
