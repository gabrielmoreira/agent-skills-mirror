---
name: loop-engineer
description: >
  Domain-agnostic autonomous loop for OpenAI Codex CLI. Asks 3 questions, scaffolds
  a parallel agent team as TOML files (resource-scout, researcher, planner, agent-factory,
  executor, verifier, auditor, memory-keeper), generates loop-stack/<LOOP_ID>/
  state files, and outputs the exact `codex /goal` command for the fully autonomous loop.
  Modes: build (from scratch), research (investigate only), patch (fix/extend
  existing code), audit (review only, no changes).
---

# Loop Engineer (Codex)

You are running a loop engineering wizard for OpenAI Codex. Follow these phases in order.

---

> **To update loop-engineer:** re-run `install.sh --update` / `install.ps1 -Update -Codex`. Updates are never applied automatically mid-loop.

---

## Phase 1 — Core Wizard

**Q1 — Mode:** if invoked with an argument matching `build`/`research`/`patch`/`audit`, use it as MODE and skip this question. Otherwise ask: "Mode? build (new from scratch) / research (investigate and report, no code changes) / patch (fix or add a feature using the existing codebase) / audit (review existing code/output only, no changes)". Default to `build` if unclear.

**Q2:** "What do you want the loop to accomplish? (1-2 sentences)"

Generate LOOP_ID: lowercase slug, first 4 meaningful words, max 24 chars.
Auto-set: `STOP_CONDITION` = "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked", `MAX_TURNS` = 20.

**Q3:** "Should the loop auto-commit after each verified task? (yes / no)"

Store: `MODE`, `GOAL`, `LOOP_ID`, `STOP_CONDITION`, `MAX_TURNS`, `USE_GIT`.

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
  -Mode <MODE> `
  -Platform codex
```

**Bash (macOS/Linux):**
```bash
bash ~/.codex/skills/loop-engineer/scripts/init-loop.sh \
  --loop-id <LOOP_ID> \
  --goal "<GOAL>" \
  --stop "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked" \
  --git <yes/no> \
  --mode <MODE> \
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
Mode: {MODE}
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
  Task type depends on MODE: build/patch → implementation tasks; research → research/writing tasks only, no code changes; audit → review tasks only, no code changes.
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

Mode gating: build (default) — full flow, every step below runs. patch — same steps, but every researcher/executor prompt adds "existing codebase is ground truth — fix/extend, don't rewrite from scratch." research — skip step (d) executors and steps (e)-(f) audit entirely; the researcher (step c) writes each task's final deliverable directly; the verifier (step g) checks that instead of built code. audit — skip step (d) executors; the auditor step (e) IS the task (read-only review, findings to RESEARCH.md); a BLOCK verdict (step f) is just recorded, never auto-fixed, always proceeds to the verifier.

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

e. Spawn auditors in parallel (one per task just built):
   Wait for all.

f. Process audit results per task:
   - CLEAN/WARN → proceed to verifier
   - BLOCK → AUTO-FIX: spawn executor once with BLOCK context, re-audit once.
     Still BLOCK → auto-skip.

g. Spawn verifiers in parallel (one per task that passed audit) — verifier is the final gate, checking both jobs in one pass (researcher-criteria check + stop condition):
   For each task: spawn_agent verifier with:
     Loop directory: loop-stack/<LOOP_ID>/
     Current task: {this_task}
     Read .codex/agents/verifier.toml for full instructions (checks RESEARCH.md's "## Verification Criteria"/"## Requirements & Constraints" AND runs the stop condition).
     Call report_agent_job_result when done.
   Wait for all. Increment turns_used.

h. Process verifier results per task:
   - VERIFIED_PASS → proceed to memory-keeper
   - FAILED, attempts < 3 → increment attempts, retry from (c) with error context
   - FAILED, attempts >= 3 → AUTO-SKIP: add to skipped_tasks, skip this task

i. spawn_agent: memory-keeper (single, final consolidation)
   Distill all batch learnings to loop-stack/<LOOP_ID>/MEMORY.md.
   Append most important per-task learning to loop-stack/.global/MEMORY.md.
   Call report_agent_job_result when done.
   Wait for completion.

j. Advance: mark [x] for passed tasks. If USE_GIT=yes: commit PLAN.md + STATUS.md.
   Find next unchecked group. If none → State = ALL DONE.
   Rename: loop-stack/<LOOP_ID>/ → loop-stack/<LOOP_ID>_DONE/
   Write REPORT.md in the renamed directory with goal, outcome, tasks, skipped, learnings.
   Stop.

Step 6 — Budget reached:
   Update STATUS.md State to BUDGET_REACHED.
   Rename: loop-stack/<LOOP_ID>/ → loop-stack/<LOOP_ID>_DONE/
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

- **File copy**: shell commands only. Never write TOML agent files manually.
- **Global data first**: every agent reads `.global/MEMORY.md` and `.global/TOOLS.md` before acting.
- **Parallel first**: startup researchers parallel, per-task researchers parallel, on-demand agent-factory parallel, executors parallel, verifiers parallel, auditors parallel.
- **Researcher before executor**: always. Dynamic count based on goal complexity.
- **Agent-factory is on-demand, not a fixed startup step.** Invoke it only right before executing a task that clearly needs a specialist, and spawn it for all qualifying tasks in a batch simultaneously. Most loops never call it.
- **knowledge-sources.md (`.codex/knowledge-sources/`) is a reference researchers consult on demand**, not a phase step.
- **No watcher agent.** Check heartbeats yourself if an agent is slow; never spawn a dedicated watcher.
- **No separate evaluator.** Verifier is the final gate — checks RESEARCH.md's "## Verification Criteria"/"## Requirements & Constraints" AND runs the stop condition.
- **Audit before verify.** Auditor reviews the build first (step e); verifier runs last as the final pass/fail gate (step g) and is what triggers retry.
- **Memory-keeper runs once per task batch**: single final consolidation (local+global) after verify. Executors already append learnings to MEMORY.md inline, so no mid-batch checkpoint call is needed. Its only job is capturing learnings/context — never executes the goal or writes goal output.
- **Executors append to MEMORY.md directly** during work.
- **Planner**: once at startup. Creates parallel-group-tagged task list.
- **Fully autonomous**: no user pauses. Audit BLOCK → auto-fix once → skip. 3 verifier fails → auto-skip.
- **Modes**: `build` (default), `research`, `patch`, `audit` — set once in Phase 1, gates the outer loop (see Mode gating above).
- **HARD RULE — no plan-approval gate**: proceed through Phase 2 onward without presenting a plan for approval or waiting for a "click proceed" confirmation.
- No resume support: every invocation starts a fresh loop. On completion: rename to `<LOOP_ID>_DONE/` (bookkeeping only).
