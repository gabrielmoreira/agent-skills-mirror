---
name: loop-engineer
description: >
  Domain-agnostic autonomous loop for any goal — coding, research, content, data,
  automation, or any objective. Asks 2 questions, then orchestrates a self-assembling
  agent team (resource-scout, researcher, planner, agent-factory, executor, evaluator,
  verifier, auditor, memory-keeper) that researches, discovers resources, builds
  specialized agents for the goal, executes, and iterates until done. Supports
  resume, persistent memory, git integration, and generates a completion report.
---

# Loop Engineer

You are running a loop engineering wizard. Follow these phases in order.

---

## Phase 0 — Resume Check

Before anything else, scan for any `loop-stack/*/STATUS.md` files in the current directory.
**Skip any directory whose name ends with `_DONE` — those loops are already complete.**

**If none found (excluding `_DONE` folders):** continue to Phase 1.

**If one found:** Read it and tell the user:
> "Found an existing loop: loop-stack/{loop-id}/
> State: {State}  |  Current task: {Current Task}  |  Progress: {Task Progress}
>
> Resume this loop or start fresh?"

- **Resume** → skip to Phase 5 (Outer Loop) using existing files in `loop-stack/{loop-id}/`.
- **Fresh** → delete only `loop-stack/<loop-id>/` directory (do NOT delete `.claude/agents/`), continue to Phase 1.

**If multiple found:** List them all and ask which to resume or type 'fresh'.

---

## Phase 1 — Core Wizard

Ask **one at a time**. Wait for the full answer.

**Q1 — Goal:**
> "What do you want the loop to accomplish? (1-2 sentences)"

After storing GOAL, generate LOOP_ID:
- lowercase, replace non-alphanumeric runs with hyphens
- Take first 4 meaningful words (skip: a, an, the, to, for, of, in, on, with, and, or)
- Max 24 chars, strip trailing hyphen
- Example: "Add authentication flow to the REST API" → "add-auth-flow-api"

Auto-set: `STOP_CONDITION` = "all tasks in loop-stack/<LOOP_ID>/PLAN.md checked", `BUDGET_STRING` = "20 turns", `MAX_TURNS` = 20.

**Q2 — Git integration:**
> "Should the loop auto-commit after each verified task? (yes / no)"

Store: `GOAL`, `LOOP_ID`, `STOP_CONDITION`, `BUDGET_STRING`, `MAX_TURNS`, `USE_GIT`.

---

## Phase 2 — State File Creation

Create `loop-stack/<LOOP_ID>/` directory and write these files:

**loop-stack/<LOOP_ID>/PLAN.md** (tasks section is a stub — planner will fill it in Phase 4):

    # Loop Plan
    ## Goal
    {GOAL}
    ## Stop Condition
    {STOP_CONDITION}
    ## Budget
    {BUDGET_STRING}
    ## Git Integration
    {yes / no}
    ## Tasks
    (will be created by the planner agent)

**loop-stack/<LOOP_ID>/STATUS.md:**

    # Loop Status
    ## State
    IN_PROGRESS
    ## Current Task
    (planning in progress)
    ## Task Progress
    0 / ? complete
    ## Attempts On Current Task
    0
    ## Completed Tasks
    (none)
    ## Skipped Tasks
    (none)
    ## Last Researcher Result
    (none)
    ## Last Executor Result
    (none)
    ## Last Evaluator Result
    (none)
    ## Last Audit Result
    (none)
    ## Blocked Reason
    (none)

**loop-stack/<LOOP_ID>/MEMORY.md:**

    # Loop Memory
    Updated continuously by all agents as they discover things.
    ## Learnings
    (none yet)

**loop-stack/<LOOP_ID>/TOOLS.md:**

    # Discovered Tools
    ## Status
    PENDING

**loop-stack/<LOOP_ID>/RESEARCH.md:**

    # Research Log
    ## Context & Prior Work
    (pending)
    ## External Knowledge & Resources
    (pending)
    ## Requirements & Constraints
    (pending)
    ## Task-Specific Research
    (pending)

**loop-stack/<LOOP_ID>/AGENTS.md:**

    # Specialized Agents
    ## Status
    PENDING (agent-factory will populate after planning)

Create `loop-stack/<LOOP_ID>/agents/` directory (agent-factory will write specialist agents here).

Initialize global memory if not present:
- `loop-stack/.global/MEMORY.md` — create with header if missing

---

## Phase 3 — Agent File Setup

**CRITICAL: Use shell commands to copy agent files. Do NOT write them manually — they must be copied exactly from the installed templates.**

Create `.claude/agents/` if it does not exist, then run:

**Bash (macOS/Linux):**
```bash
mkdir -p .claude/agents
mkdir -p .claude/agents/knowledge-sources
cp ~/.claude/skills/loop-engineer/agents/resource-scout.md .claude/agents/
cp ~/.claude/skills/loop-engineer/agents/researcher.md .claude/agents/
cp ~/.claude/skills/loop-engineer/agents/planner.md .claude/agents/
cp ~/.claude/skills/loop-engineer/agents/agent-factory.md .claude/agents/
cp ~/.claude/skills/loop-engineer/agents/executor.md .claude/agents/
cp ~/.claude/skills/loop-engineer/agents/evaluator.md .claude/agents/
cp ~/.claude/skills/loop-engineer/agents/auditor.md .claude/agents/
cp ~/.claude/skills/loop-engineer/agents/memory-keeper.md .claude/agents/
cp ~/.claude/skills/loop-engineer/agents/knowledge-sources/*.md .claude/agents/knowledge-sources/
```

**PowerShell (Windows):**
```powershell
New-Item -ItemType Directory -Force .claude\agents | Out-Null
New-Item -ItemType Directory -Force ".claude\agents\knowledge-sources" | Out-Null
Copy-Item "$env:USERPROFILE\.claude\skills\loop-engineer\agents\*.md" ".claude\agents\"
Copy-Item "$env:USERPROFILE\.claude\skills\loop-engineer\agents\knowledge-sources\*.md" ".claude\agents\knowledge-sources\"
```

After copying, write **only** `verifier.md` — substituting the actual STOP_CONDITION (never write the literal placeholder):

**`.claude/agents/verifier.md`:**

    ---
    name: verifier
    description: Runs the stop condition. Marks tasks done or failed. Never executes the goal itself.
    ---
    You are the verifier agent.
    1. Read loop-stack/.global/MEMORY.md FIRST — cross-loop verification gotchas.
    2. Read [LOOP_DIR]/MEMORY.md — verification gotchas for this loop.
    3. Read [LOOP_DIR]/STATUS.md and [LOOP_DIR]/PLAN.md.
    4. Run: {STOP_CONDITION}
    5. PASSES → set State VERIFIED_PASS, mark task [x] in PLAN.md, update Task Progress. If all done: ALL DONE.
    6. FAILS → set State FAILED, write exact error to Last Executor Result.
    HARD RULE: Never execute the goal or write output files for the goal.
    HARD RULE: Never mark done unless verification actually passed.

Confirm to user:
> "loop-stack/<LOOP_ID>/ created: PLAN.md · STATUS.md · MEMORY.md · TOOLS.md · RESEARCH.md · AGENTS.md
> .claude/agents/ ready: resource-scout · researcher · planner · agent-factory · executor · evaluator · verifier · auditor · memory-keeper
> Starting startup sequence..."

---

## Phase 4 — Startup Sequence

Run in this order. Each step waits for completion before the next.

### Step 1 — PARALLEL RESEARCHERS (dynamic count)

**Determine how many researchers to spawn based on goal complexity:**
- Simple, single-domain goal → 2 researchers
- Medium complexity or multi-domain goal → 3 researchers
- Large or multi-system goal (e.g. full-stack app, migration, complex refactor) → 4 researchers

**Spawn all researchers simultaneously in a single response** (call Agent tool N times at once).

Always assign each researcher a distinct focus area. Divide the following domains across however many you spawn — these apply to ANY goal type (coding, research, content, data, automation, etc.):

- **Context & Prior Work**: what already exists relevant to this goal — source files, documents, prior research, existing assets, related work, knowledge bases, prior loop learnings
- **External Knowledge & Resources**: what's available externally — APIs, documentation, datasets, libraries, services, reference materials, skills, MCP capabilities (use WebSearch/WebFetch)
- **Requirements & Constraints**: what must be true about the output — quality standards, format requirements, accuracy, edge cases, stakeholder needs, access restrictions, performance criteria (include this for 3+ researchers)
- **Environment & Integration**: how everything fits together — tools available, configuration, system dependencies, data flow, integration points, deployment targets (include this for 4 researchers)

For each researcher spawn:
```
Loop directory: loop-stack/<LOOP_ID>/
Focus: {ASSIGNED_DOMAIN} — {specific files and concerns for that domain}
GLOBAL DATA FIRST: read loop-stack/.global/MEMORY.md and loop-stack/.global/TOOLS.md.
Write findings to loop-stack/<LOOP_ID>/RESEARCH.md under "## {Domain Name}".
Update STATUS.md "Last Researcher Result".
Follow .claude/agents/researcher.md.
```

Wait for ALL researchers to finish before Step 2.

### Step 2 — TOOL SCOUT

```
Loop directory: loop-stack/<LOOP_ID>/
GLOBAL DATA FIRST: Check loop-stack/.global/TOOLS.md:
- If exists and < 7 days old: copy to loop-stack/<LOOP_ID>/TOOLS.md (Status: REUSED FROM GLOBAL)
- Otherwise: discover all tools, MCPs, plugins, project scripts. Write to BOTH loop-stack/<LOOP_ID>/TOOLS.md AND loop-stack/.global/TOOLS.md.
Follow .claude/agents/resource-scout.md.
```

### Step 3 — PLANNER

```
Loop directory: loop-stack/<LOOP_ID>/
Read loop-stack/<LOOP_ID>/RESEARCH.md and loop-stack/<LOOP_ID>/TOOLS.md.
Create 3–7 atomic, ordered tasks appropriate to the goal type. Mark parallelism with [G1], [G2], etc.:
- Same group number = can run in parallel (independent work, no shared output state)
- Different group number = must run sequentially (later groups depend on earlier ones)
Example (research goal):
  - [ ] [G1] Gather sources on {topic} using WebSearch
  - [ ] [G1] Identify available datasets and reference materials
  - [ ] [G2] Synthesize findings into structured outline
  - [ ] [G2] Draft analysis for each section
  - [ ] [G3] Fact-check, finalize, and write output document
Replace the "## Tasks" section in loop-stack/<LOOP_ID>/PLAN.md with the task list.
Update STATUS.md: Current Task = first task, Task Progress = 0 / N.
Follow .claude/agents/planner.md.
```

### Step 4 — AGENT FACTORY

```
Loop directory: loop-stack/<LOOP_ID>/
Read loop-stack/<LOOP_ID>/PLAN.md (goal + tasks), RESEARCH.md, and TOOLS.md.
Analyze the goal domain and determine what specialized agents (beyond the core team) would improve execution quality.
Create 1–3 purpose-built agent files in loop-stack/<LOOP_ID>/agents/ tailored to this goal's domain and tasks.
Write loop-stack/<LOOP_ID>/AGENTS.md listing each created agent and which tasks it handles.
If the generic agents are sufficient, write AGENTS.md with "NONE CREATED" and skip creating files.
Follow .claude/agents/agent-factory.md.
```

Auto-continue into the outer loop immediately — no user confirmation needed.

---

## Phase 5 — Outer Loop

You (Claude, main session) are the outer loop controller.
**FULLY AUTONOMOUS — never pause for user input. Handle all failures automatically.**

**Initialize:**
- `turns_used = 0`, `skipped_tasks = []`
- Read PLAN.md → `total_tasks`
- `done_tasks = count of [x] tasks`

**Loop condition:** Continue while STATUS.md State ≠ `ALL DONE`.

Print each iteration: `[Task {done_tasks + 1}/{total_tasks} — {pct}% | Turn {turns_used + 1}/{MAX_TURNS}]`

---

### Step 1 — Budget check
`turns_used >= MAX_TURNS` → stop, go to Phase 6.

### Step 2 — Read state + identify current parallel group
Read STATUS.md and PLAN.md. Find all unchecked tasks with the same group tag (e.g., all `[G2]` tasks) — this is the current batch. Skip already-checked tasks.

### Step 3 — Parallel RESEARCHERS (dynamic — one per task, or more for complex tasks)

**Determine researcher count dynamically:**
- N tasks in batch → N researchers (one per task), all spawned simultaneously
- If batch has only 1 task → spawn 2 researchers for that task (implementation details + edge cases)
- If a single task is particularly complex (e.g. "implement payment system") → spawn 3 researchers for it

**Spawn all researchers simultaneously** (call Agent tool N times in one response):

For each task in the batch, spawn one researcher:
```
Loop directory: loop-stack/<LOOP_ID>/
GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
Then read loop-stack/<LOOP_ID>/MEMORY.md, TOOLS.md, PLAN.md, STATUS.md.
Current task: {this_task}
Research what the executor needs for THIS SPECIFIC TASK. Adapt to the goal type — relevant existing work, required resources, constraints, edge cases, prior failed attempts (STATUS.md).
If research surfaces a resource the team hasn't catalogued yet that could help this or future tasks, add it to loop-stack/<LOOP_ID>/TOOLS.md.
Append findings to loop-stack/<LOOP_ID>/RESEARCH.md under "## Task-Specific Research — {this_task}".
Follow .claude/agents/researcher.md.
```

Wait for ALL researchers to finish. Increment `turns_used`.

### Step 4 — Parallel EXECUTORS (one per task in batch)

**Spawn one executor per task in the current batch simultaneously:**

For each task in the batch:
```
Loop directory: loop-stack/<LOOP_ID>/
GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
Then read loop-stack/<LOOP_ID>/MEMORY.md, TOOLS.md, PLAN.md, STATUS.md.
READ BEFORE ACTING: loop-stack/<LOOP_ID>/RESEARCH.md — specifically "## Task-Specific Research — {this_task}".
Also read loop-stack/<LOOP_ID>/AGENTS.md — if a specialized agent is defined for this task type, adopt that agent's approach.
Current task: {this_task}
Scope: work ONLY on output related to {this_task} — do not touch work being handled by other parallel tasks.
Previous attempt: {Last Executor Result for this task from STATUS.md}
Execute fully. Append any new discoveries (patterns, gotchas, tool behaviors, domain learnings) directly to loop-stack/<LOOP_ID>/MEMORY.md.
Update STATUS.md "Last Executor Result" for this task.
Goal output (code, documents, files) goes to the project directory, NOT inside loop-stack/. loop-stack/ is state-only.
Follow .claude/agents/executor.md (or the specialized agent from AGENTS.md if applicable).
```

Wait for ALL executors to finish. Increment `turns_used`.

### Step 5 — Parallel MEMORY-KEEPER checkpoints

Spawn one memory-keeper per task in the batch simultaneously:
```
Loop directory: loop-stack/<LOOP_ID>/
Checkpoint: executor just completed "{this_task}".
Capture new learnings to loop-stack/<LOOP_ID>/MEMORY.md (local only, no global write yet).
Follow .claude/agents/memory-keeper.md.
```

Wait for all to finish.

### Step 6 — Parallel EVALUATORS (one per task in batch)

Spawn one evaluator per task simultaneously:
```
Loop directory: loop-stack/<LOOP_ID>/
GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
Read loop-stack/<LOOP_ID>/RESEARCH.md — constraints and edge cases flagged for "{this_task}".
Current task: {this_task}. Evaluate quality for this specific task only. Adapt verification approach to the goal type.
Follow .claude/agents/evaluator.md.
```

Wait for ALL to finish.

### Step 7 — Parallel VERIFIERS (one per task in batch)

Spawn one verifier per task simultaneously:
```
Loop directory: loop-stack/<LOOP_ID>/
GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md.
Current task: {this_task}.
Follow .claude/agents/verifier.md.
```

Wait for ALL to finish.

### Step 8 — Process verifier results (per task)

For each task in the batch:
- **VERIFIED_PASS** → proceed to auditor
- **FAILED, attempts < 3** → increment attempts in STATUS.md, queue for retry (back to Step 3 for this task with error context)
- **FAILED, attempts ≥ 3** → **auto-skip**: add to `skipped_tasks`, mark as skipped in STATUS.md

### Step 9 — Parallel AUDITORS (one per verified-pass task)

For each task that passed verification, spawn an auditor simultaneously:
```
Loop directory: loop-stack/<LOOP_ID>/
GLOBAL DATA FIRST — read loop-stack/.global/MEMORY.md AND loop-stack/.global/TOOLS.md.
Read loop-stack/<LOOP_ID>/RESEARCH.md — constraints identified for "{this_task}".
Task just verified: {this_task}. Review for security, tech debt, pattern violations.
Follow .claude/agents/auditor.md.
```

Wait for ALL auditors to finish.

### Step 10 — Process audit results (per task)

For each task:
- **CLEAN or WARN** → proceed
- **BLOCK** → **auto-fix**: spawn executor once more with BLOCK context + re-verify. If still BLOCK → auto-skip.

### Step 11 — MEMORY-KEEPER final consolidation (single)

One memory-keeper consolidates all completed tasks in this batch:
```
Loop directory: loop-stack/<LOOP_ID>/
Tasks just completed: {all tasks in this batch that passed}
Final consolidation: distill key learnings to loop-stack/<LOOP_ID>/MEMORY.md.
Global write: append the most important new learning per completed task to loop-stack/.global/MEMORY.md.
Follow .claude/agents/memory-keeper.md.
```

### Step 12 — Advance

- Mark each passed task [x] in PLAN.md, increment `done_tasks`, reset attempts.
- If `USE_GIT`: commit PLAN.md + STATUS.md.
- Find next unchecked group.
- If none → ALL DONE → rename `loop-stack/<LOOP_ID>/` → `loop-stack/<LOOP_ID>_DONE/` → Phase 6.
- Else → update STATUS.md → continue loop.

---

## Phase 6 — Completion Report

Write `loop-stack/<LOOP_ID>_DONE/REPORT.md` and print summary to user.

---

## Rules

- Phase 0 always first. Skip `_DONE` folders.
- **File copy**: ALWAYS use shell commands to copy agent files. Never write them manually.
- **Global data first**: Every spawn reads `loop-stack/.global/MEMORY.md` AND `loop-stack/.global/TOOLS.md` before acting.
- **Parallel first**: Spawn multiple agents simultaneously wherever possible. Same group = parallel. Different group = sequential.
- **Researcher before executor**: Always. Prevents hallucination. 2–4 researchers for startup, 1+ per task during loop.
- **Researcher propagates new resources**: If a researcher discovers a new skill, MCP, dataset, API, or tool, it appends it to TOOLS.md immediately so executors can use it.
- **Memory-keeper runs twice per task batch**: checkpoint after executors (local), consolidation after audit (local + global).
- **Each executor appends discoveries to MEMORY.md directly** — continuous memory, don't wait for memory-keeper.
- **Planner**: runs once at startup after researchers + resource-scout. Creates parallel-group-tagged task list.
- **Fully autonomous**: Never pause. 3 failures → auto-skip. Audit BLOCK → auto-fix once → skip.
- On completion: rename directory to `<LOOP_ID>_DONE/`. Phase 0 skips these.
