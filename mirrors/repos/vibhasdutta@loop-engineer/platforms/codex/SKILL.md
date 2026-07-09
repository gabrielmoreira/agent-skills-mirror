---
name: loop-engineer
description: >
  Domain-agnostic autonomous loop for OpenAI Codex CLI. Asks 2 questions, scaffolds
  a parallel agent team as TOML files (resource-scout, researcher, planner, agent-factory,
  executor, evaluator, verifier, auditor, memory-keeper), generates loop-stack/<LOOP_ID>/
  state files, and outputs the exact `codex /goal` command for the fully autonomous loop.
---

# Loop Engineer (Codex)

You are running a loop engineering wizard for OpenAI Codex. Follow these phases in order.

---

## Phase 0 — Resume Check

Run the resume-check script FIRST — unconditionally. It is the source of truth; do not scan `loop-stack/` yourself.

**PowerShell:** `& "$env:USERPROFILE\.codex\skills\loop-engineer\scripts\check-resume.ps1"`
**Bash:** `bash ~/.codex/skills/loop-engineer/scripts/check-resume.sh`

Read its output literally, then branch:

**`ACTIVE <id> | State: ... | Task: ... | Progress: ...`:**
- Continuation intent ("continue", "proceed", "finish", "resume", "pick up", "fix what", "audit findings", "where we left") → auto-resume to Phase 5 without asking, output the `/goal` prompt using existing files.
- Otherwise show State/Current Task/Progress, ask: Resume or Fresh?
  - Resume → skip to Phase 5, output `/goal` using existing files.
  - Fresh → delete `loop-stack/<id>/` only (keep `.codex/agents/`), continue to Phase 1.
- Multiple `ACTIVE` lines → list all, ask which to resume or 'fresh'. Continuation intent → auto-resume most recently modified.

**`DONE <id>` or `EXTENDED_DONE <id>` (no `ACTIVE` line) + continuation intent:**
→ **EXTEND SEQUENCE** — reopen in place, don't restart:
1. Rename `loop-stack/<id>_DONE/` (or `_EXTENDED_DONE/`) → `loop-stack/<id>_EXTENDED/`.
2. Reuse existing PLAN.md, RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md, `agents/` as-is — do not re-run researchers, resource-scout, or agent-factory.
3. Ask ONE question: "What's the next task for this loop?" Append under `## Extension {N} Goal` in PLAN.md.
4. Spawn `planner` once against the new goal (existing RESEARCH.md/TOOLS.md as context) to append new `[GN]` tasks.
5. Reset STATUS.md: State = IN_PROGRESS, Current Task = first new task, Task Progress updated.
6. Output the `/goal` prompt directly for the outer loop (skip Phase 1–4).

On completion of a loop directory containing `_EXTENDED`: rename it to `_EXTENDED_DONE` instead of plain `_DONE`.

**`NONE`, or `DONE`/`EXTENDED_DONE` with no continuation intent:** → Phase 1 (fresh loop).

**RESUME/EXTEND RULES — always apply when going to Phase 5 this way:**
Skip Phase 2, 3, and 4 entirely. Read STATUS.md + PLAN.md to find where the loop stopped. Reuse existing RESEARCH.md, MEMORY.md, TOOLS.md, AGENTS.md — do not re-run startup agents.

> **To update loop-engineer:** re-run `install.sh --update` / `install.ps1 -Update -Codex`. Updates are never applied automatically mid-loop.

---

## Phase 1 — Core Wizard

**Q1:** "What do you want the loop to accomplish? (1-2 sentences)"

Generate LOOP_ID: lowercase slug, first 4 meaningful words, max 24 chars.
Auto-set: `STOP_CONDITION` = "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked", `MAX_TURNS` = 20.

**Q2:** "Should the loop auto-commit after each verified task? (yes / no)"

Store: `GOAL`, `LOOP_ID`, `STOP_CONDITION`, `MAX_TURNS`, `USE_GIT`.

---

## Phase 2+3 — Initialize Loop

Run the init script — creates all state files, copies TOML agent files + knowledge-sources, and writes verifier in one command:

**PowerShell (Windows):**
```powershell
& "$env:USERPROFILE\.codex\skills\loop-engineer\scripts\init-loop.ps1" `
  -LoopId "<LOOP_ID>" `
  -Goal "<GOAL>" `
  -Stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" `
  -Git <yes/no> `
  -Platform codex
```

**Bash (macOS/Linux):**
```bash
bash ~/.codex/skills/loop-engineer/scripts/init-loop.sh \
  --loop-id <LOOP_ID> \
  --goal "<GOAL>" \
  --stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" \
  --git <yes/no> \
  --platform codex
```

If the script is missing, install the skill first:
`git clone https://github.com/vibhasdutta/loop-engineer && bash install.sh --codex`

The script creates `loop-stack/<LOOP_ID>/`, `.codex/agents/` with all TOML agent files, `.codex/knowledge-sources/` with all reference .md files, and `verifier.toml` with the actual stop condition substituted.

---

## Phase 4 — Generate /goal Command

Tell the user:

> **Start Codex in your project directory, then paste this `/goal` prompt:**

Print with real values substituted — never print literal placeholders:

```
/goal {GOAL}

Loop directory: loop-stack/<LOOP_ID>/
Agent definitions: .codex/agents/
Budget: 20 turns
FULLY AUTONOMOUS — never pause for user input.

═══ STARTUP SEQUENCE ═══

Step 1 — Determine researcher count based on goal complexity:
- Simple/single-domain goal → 2 researchers
- Medium/multi-domain goal → 3 researchers
- Large/multi-system goal (full-stack, migration, complex refactor) → 4 researchers

Spawn all researchers in parallel using spawn_agent (one call per researcher, all at once):
Divide these domains across however many researchers you spawn:
- Context & Prior Work: source structure, patterns, package files, existing tests
- External Knowledge & Resources: README, docs/, external APIs, .env.example, configs
- Requirements & Constraints: DB schema, data models, state management (for 3+ researchers)
- Environment & Integration: CI/CD, infrastructure, build, Docker (for 4 researchers)

Each researcher prompt:
  Loop directory: loop-stack/<LOOP_ID>/
  Focus: {ASSIGNED_DOMAIN}
  GLOBAL DATA FIRST: read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
  Write findings to loop-stack/<LOOP_ID>/RESEARCH.md under "## {Domain Name}".
  Update STATUS.md "Last Researcher Result".
  Read .codex/agents/researcher.toml for full instructions.
  Call report_agent_job_result when done.

Wait for ALL researchers to complete.

Stuck-agent check (you do this yourself — no watcher agent): if one researcher took much longer than the others, check its heartbeat line in STATUS.md "## Active Heartbeats". If stale, treat it STUCK, note it, and proceed with the findings you have.

Step 2 — spawn_agent: resource-scout
  Loop directory: loop-stack/<LOOP_ID>/
  Check loop-stack/.global/TOOLS.md — if < 7 days old, reuse. Otherwise discover all tools.
  Write to loop-stack/<LOOP_ID>/TOOLS.md AND loop-stack/.global/TOOLS.md.
  Call report_agent_job_result when done.
Wait for resource-scout to complete.

Step 3 — spawn_agent: planner
  Loop directory: loop-stack/<LOOP_ID>/
  Read RESEARCH.md (all sections) and TOOLS.md.
  Create 3–7 tasks with parallel group tags [G1], [G2], etc.
  Same group = can run in parallel (independent files/modules).
  Different group = sequential dependency (later groups depend on earlier ones).
  Replace "## Tasks" in PLAN.md. Update STATUS.md: Current Task = first task, Task Progress = 0/N.
  Call report_agent_job_result when done.
Wait for planner to complete.

Write loop-stack/<LOOP_ID>/AGENTS.md with "# Specialized Agents\n## Status\nNONE CREATED YET". Agent-factory is on-demand, not a fixed startup step — it is invoked later, per-task, inside the outer loop (see step d). Proceed to outer loop.

═══ OUTER LOOP ═══

Step 5 — Loop until all tasks in PLAN.md are checked or budget reached.
Track: turns_used = 0, skipped_tasks = []
Print per iteration: [Task X/N | Turn Y/20]

Each iteration:

a. Budget check: turns_used >= 20 → stop, go to Step 6.

b. Read PLAN.md + STATUS.md. Identify current parallel group: all unchecked tasks with same [GN] tag.

c. Spawn researchers in parallel (one per task in batch, 2 if batch=1):
   For each task: spawn_agent researcher with focus on that task's implementation needs.
   Wait for all. Increment turns_used.

d. Read AGENTS.md — if specialized agents were created for any tasks in this batch, use those agent TOML files instead of executor.toml for those tasks.

   For every task in the batch with no specialist that clearly needs domain expertise beyond a generic executor (security, ML/data science, content production, medical, finance, system design, etc.): spawn agent-factory for all such tasks simultaneously in parallel (same parallel-first rule as researchers/executors) — reads .codex/agents/agent-factory.toml, creates 1 agent TOML file per task in loop-stack/<LOOP_ID>/agents/, updates AGENTS.md. Wait for all to finish. Skip this entirely for most tasks.

   Spawn executors in parallel (one per task in batch):
   For each task: spawn_agent executor (or specialized agent if AGENTS.md designates one) with:
     Loop directory: loop-stack/<LOOP_ID>/
     GLOBAL DATA FIRST: read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
     Read MEMORY.md, TOOLS.md, PLAN.md, STATUS.md.
     READ BEFORE CODING: RESEARCH.md section for "{this_task}".
     Current task: {this_task}. Scope: only files for this task.
     Implement. Append discoveries to MEMORY.md directly.
     Update STATUS.md. Call report_agent_job_result when done.
     Goal output (code, documents, files) goes to the project directory, NOT inside loop-stack/. loop-stack/ is state-only.
   Wait for all. Increment turns_used.

e. Spawn memory-keeper checkpoint for each task in parallel (local only):
   Wait for all.

f. Spawn evaluators in parallel (one per task):
   Wait for all.

g. Spawn verifiers in parallel (one per task):
   Wait for all.

h. Process verifier results per task:
   - VERIFIED_PASS → proceed to auditor
   - FAILED, attempts < 3 → increment attempts, retry from (c) with error context
   - FAILED, attempts >= 3 → AUTO-SKIP: add to skipped_tasks, skip this task

i. Spawn auditors in parallel (one per passing task):
   Wait for all.

j. Process audit results per task:
   - CLEAN/WARN → proceed
   - BLOCK → AUTO-FIX: spawn executor once with BLOCK context, re-verify.
     Still BLOCK → auto-skip.

k. spawn_agent: memory-keeper (single, final consolidation)
   Distill all batch learnings to loop-stack/<LOOP_ID>/MEMORY.md.
   Append most important per-task learning to loop-stack/.global/MEMORY.md.
   Call report_agent_job_result when done.
   Wait for completion.

l. Advance: mark [x] for passed tasks. If USE_GIT=yes: commit PLAN.md + STATUS.md.
   Find next unchecked group. If none → State = ALL DONE.
   Rename: loop-stack/<LOOP_ID>/ → loop-stack/<LOOP_ID>_DONE/ (or _EXTENDED_DONE/ if this loop directory contained _EXTENDED)
   Write REPORT.md in the renamed directory with goal, outcome, tasks, skipped, learnings.
   Stop.

Step 6 — Budget reached:
   Update STATUS.md State to BUDGET_REACHED.
   Rename: loop-stack/<LOOP_ID>/ → loop-stack/<LOOP_ID>_DONE/ (or _EXTENDED_DONE/ if applicable)
   Write REPORT.md. Stop.

HARD RULE — no plan-approval gate: proceed through this entire sequence without presenting a plan for approval or waiting for a "click proceed" confirmation. This loop is fully autonomous from here.
```

> **Requirements:**
> - Current Codex CLI releases enable subagent workflows by default (confirmed via developers.openai.com/codex/subagents) — no feature flag needed on recent versions. If yours is older and `spawn_agent` isn't available, check for `features.multi_agent = true` in `~/.codex/config.toml` or toggle "Multi-agents" via `/experimental`.
> - `/goal` is a TUI slash command — run `codex` first, then paste the prompt
> - Edit `.codex/agents/*.toml` to change models
> - **Concurrency cap**: `agents.max_threads` (default 6) limits how many `spawn_agent` calls run concurrently. If a batch has more tasks than this cap, extra spawns queue rather than run simultaneously — raise `agents.max_threads` in config if you routinely run 4-researcher batches or more.
> - **Nesting cap**: `agents.max_depth` (default 1) allows a direct spawned agent to itself spawn one further layer, but no deeper. Loop-engineer's agents are all flat (no agent spawns another), so this default is fine as-is.
> - Codex only spawns subagents when explicitly asked to — this is baked into the `/goal` prompt's "Spawn all researchers in parallel using spawn_agent" instructions; if Codex doesn't spawn, check that instruction survived verbatim.

---

## Rules

- Phase 0 always first — run the check-resume script, never scan `loop-stack/` by hand.
- **File copy**: shell commands only. Never write TOML agent files manually.
- **Global data first**: every agent reads `.global/MEMORY.md` and `.global/TOOLS.md` before acting.
- **Parallel first**: startup researchers parallel, per-task researchers parallel, on-demand agent-factory parallel, executors parallel, evaluators parallel, verifiers parallel, auditors parallel.
- **Researcher before executor**: always. Dynamic count based on goal complexity.
- **Agent-factory is on-demand, not a fixed startup step.** Invoke it only right before executing a task that clearly needs a specialist, and spawn it for all qualifying tasks in a batch simultaneously. Most loops never call it.
- **knowledge-sources.md (`.codex/knowledge-sources/`) is a reference researchers consult on demand**, not a phase step.
- **No watcher agent.** Check heartbeats yourself if an agent is slow; never spawn a dedicated watcher.
- **Memory-keeper twice per batch**: checkpoint (local) after executors, consolidation (local+global) after audit.
- **Executors append to MEMORY.md directly** during work.
- **Planner**: once at startup, and again (lightweight) for extended-loop follow-on tasks. Creates parallel-group-tagged task list.
- **Fully autonomous**: no user pauses. 3 fails → auto-skip. BLOCK → auto-fix once → skip.
- **HARD RULE — no plan-approval gate**: proceed through Phase 2 onward without presenting a plan for approval or waiting for a "click proceed" confirmation.
- On completion: rename to `<LOOP_ID>_DONE/` or `<LOOP_ID>_EXTENDED_DONE/`.
