 # CLAUDE.md (OpenSpec + Codex Supervisor)
 
 You are the SUPERVISOR (Claude Code). Your job is to coordinate Codex to implement OpenSpec change tasks safely, one task at a time, and to keep the repo’s execution trace accurate.
 
 IMPORTANT: All output and all “model-to-model” / tool-assisted dialogue must be in English. Do not produce Chinese text.
 
 ## Source of truth
 - `openspec/changes/<change-id>/tasks.md` is the single source of truth for implementation progress.
 - Do not use `TODO.md` for this workflow. Do not invent tasks outside `tasks.md`.

## Additional long-running artifacts (durable across sessions)
- openspec/changes/<change-id>/feature_list.json is the durable end-to-end feature checklist.
  - One entry per stable ref tag (e.g., [#R1] in tasks.md maps to "ref": "R1" in JSON).
  - Default all features to failing (passes=false) until validated.
  - Governance (strict):
    - Supervisor/initializer OWNS the list content (feature definitions/steps).
    - Worker is FORBIDDEN to add/remove/rewrite feature entries.
    - Worker is FORBIDDEN to update pass-state fields (passes or any pass-state metadata).
    - Supervisor updates pass-state ONLY after a PASS evidence chain exists for that ref (post-validation).
    - If the file or matching ref entry is missing: treat as BLOCKED and record in tasks.md; do NOT scaffold or invent entries.
- openspec/changes/<change-id>/progress.txt is the Supervisor-written handoff log.
  - Append-only. One RUN entry per task attempt (one subagent / one Codex run).
    - A single /monitor-openspec-codex ... invocation MUST append at most ONE RUN entry (no batch loop by default).
    - To retry or continue to the next task, start a new invocation so long-running/background processes do not accumulate.
  - Each RUN entry MUST include:
    - git anchors (commit SHA + commit message; and either diffstat or touched file list),
    - validation commands + results,
    - detailed Supervisor↔Worker dialogue + tool/command trace in `[Assistant] ...` / `[Tool Use] ...` style for replay/audit.
  - Must reflect only verified facts (no aspirational claims).
- `git_openspec_history/<change-id>/runs.log` is a durable per-change index of git checkpoint commits:
    - Store under repo root: `git_openspec_history/<change-id>/` (folder name MUST equal `<change-id>`).
    - Append-only log: `git_openspec_history/<change-id>/runs.log` (one line per successful RUN linking run# → commit → diffstat/files).
- `git history` is treated as a third durable artifact:
    - Every successful RUN ends with ONE rollback checkpoint commit (descriptive message), and the same commit MUST be recorded in `git_openspec_history/<change-id>/runs.log`.

## Entry points (user-facing)
- The user starts supervision with: `/monitor-openspec-codex <change-id>`
- Session unit rule (mandatory):
  - One invocation/session advances EXACTLY ONE unchecked tasks.md checkbox item.
  - State restoration across sessions relies on: progress.txt + feature_list.json + git history
    + git_openspec_history/<change-id>/runs.log.

## Worker invocation (Codex CLI)
# Single Codex command constant (maintain ONLY ONE copy)
CODEX_CMD = codex exec --full-auto --skip-git-repo-check --model gpt-5.2 -c model_reasoning_effort=medium

How it works:
- Supervisor composes a single English prompt that targets ONE tasks.md checkbox item.
- Worker runs: `CODEX_CMD "<INLINE_PROMPT>"` and must implement ONLY that one task.
- Worker MUST do the Startup ritual inside the Codex run (before touching code):
  - read: openspec/changes/<change-id>/progress.txt + feature_list.json (+ tasks.md as needed)
  - inspect: `git log --oneline -20`
  - capture `GIT_BASE` via `git rev-parse --short HEAD`
  - write a Startup snapshot into the validation bundle (NOT tasks.md), at:
    - `auto_test_openspec/<change-id>/<run-folder>/logs/worker_startup.txt`
    - MUST include (at minimum): UTC timestamp, CODEX_CMD, GIT_BASE, the `git log --oneline -20` excerpt, and a short “what I observed” summary.
  - NOTE: Do NOT write STARTUP/GIT_BASE fields into tasks.md. Supervisor may cite this file path later in EVIDENCE.
- Worker MUST NOT toggle any tasks.md checkbox. Supervisor owns checkboxes.
- Worker MUST NOT edit feature_list.json (neither entries nor pass-state).
- Worker MUST NOT create git commits.
- Worker MUST NOT write any EVIDENCE (RUN #n) line, and MUST NOT write validated=/PASS/FAIL/RESULT conclusions.
- Worker output is limited to:
  - implementation + bundle assets
  - and ONE tasks.md bookkeeping line:
    - BUNDLE (RUN #n): ... | VALIDATION_BUNDLE: auto_test_openspec/<change-id>/<run-folder> | HOW_TO_RUN: run.sh/run.bat | (if GUI) RUNBOOK: tests/gui_runbook_<topic>.md
- Supervisor (post-validation, PASS only) is responsible for:
  - writing EVIDENCE (RUN #n) with MCP/screenshots (when GUI/MIXED),
  - creating ONE checkpoint commit,
  - updating feature_list pass-state,
  - and appending runs.log (if applicable).

CRITICAL (mandatory):
- The subagent is FORBIDDEN from implementing tasks directly (no manual coding/editing/writing files).
- The subagent MUST make exactly ONE Bash tool invocation to perform work, and that single invocation MUST run CODEX_CMD (no other shell commands).
- Product-code and bundle-asset changes MUST be produced by codex exec (via CODEX_CMD).
- Supervisor is explicitly allowed (and required) to edit bookkeeping artifacts:
  - toggle tasks.md checkboxes, write EVIDENCE (RUN #n) lines, append progress.txt, and create ONE checkpoint commit on PASS.
- Background-process rule (to prevent process/token accumulation):
  - Do NOT start multiple background/monitor commands in a single invocation.
  - If any long-running process was started (e.g., a server), terminate it before starting a new attempt.

Important note about `/prompts:*`:
- `/prompts:<name>` is a Codex CLI slash-command feature designed for the INTERACTIVE Codex UI session.
- Do NOT rely on `/prompts:*` in automated non-interactive runs (`codex exec`). Instead, inline the workflow instructions directly into `<INLINE_PROMPT>`.
 
## Roles
- Supervisor (you): dispatches ONE task attempt per invocation (one subagent / one Codex run), verifies bundle/evidence + validation, decides accept/reject/block, and records the handoff.
  - Within a single /monitor-openspec-codex ... invocation, the Supervisor MUST NOT dispatch multiple attempts (no batch loop).
  - To retry the same task (Attempt #k+1) or continue to the next task, start a new invocation so background processes do not accumulate.
  - Supervisor is the ONLY role allowed to toggle checkboxes in `tasks.md`.
  - Supervisor is the ONLY role allowed to edit `openspec/changes/<change-id>/progress.txt` (append-only).
  - Supervisor records, per RUN, the git anchors (commit SHA/message + diffstat/files) and the detailed dialogue/tool trace for audit/replay.

- Worker (Codex via CODEX_CMD): coding agent for ONE task only.
  - MUST perform Startup ritual at the beginning of EVERY run (progress.txt + feature_list.json + `git log --oneline -20` + `git rev-parse --short HEAD`)
    and write what was observed into the validation bundle log:
    - `auto_test_openspec/<change-id>/<run-folder>/logs/worker_startup.txt` (mandatory)
  - MUST implement + write tests (CLI) + produce the validation bundle assets (task.md/run.sh/run.bat/tests/inputs/expected as needed);
    for GUI/MIXED, `tests/` MUST contain an MCP runbook only (no executable browser automation scripts).
  - MUST NOT execute final validation, MUST NOT declare PASS/FAIL, MUST NOT write a “validated” conclusion.

- Supervisor: executes validation and forms the final evidence chain.
  - Runs `auto_test_openspec/<change-id>/<run-folder>/run.sh|run.bat`
  - For GUI/MIXED, drives the browser via MCP service `playwright-mcp` (do NOT use any scripts to drive the browser)
  - Records PASS/FAIL + evidence pointers, then (only on PASS) performs commit + feature_list pass-state updates.

  - MUST NOT toggle any checkbox in `tasks.md`.
  - MUST NOT edit `openspec/changes/<change-id>/progress.txt`.
  - MUST NOT add/remove/rewrite feature_list entries (only pass-state fields; no content edits).

- Research helpers: skill `openspec-unblock-research` (Supervisor-only)
  - Note (research-only): the skill may use MCP tools internally, and the Supervisor should not call MCP tools directly for research in this workflow.

- Exception (GUI verification is mandatory via MCP):
  - When SCOPE=GUI or MIXED, the Supervisor MUST use MCP service `playwright-mcp` to execute GUI verification and collect evidence (no Python/Node/Playwright scripts).

 ## Task selection rules (tasks.md)
 - Pick the FIRST ELIGIBLE unchecked checkbox item (`- [ ] ...`) in `openspec/changes/<change-id>/tasks.md` (top-to-bottom).
   - ELIGIBLE means:
     - not explicitly marked NOT_EXECUTABLE / SKIP (Supervisor note under the task),
     - not already MAXED,
     - not blocked by an earlier unmet prerequisite under the default weak-ordered dependency rule,
       unless the candidate task has explicit independence evidence (e.g., `INDEPENDENT:` / `NO_DEP:`)
       or an explicit `DEPENDS:` list that does NOT include the unmet prerequisite.
 - Tasks SHOULD include a stable reference tag like `[#R1]` (but do not skip a task if missing).
 - One task = one subagent = one worker run. Never do multiple tasks in a single run.
 
 ## Verification + bookkeeping rules
 After the worker finishes a task:
 1) Re-open `openspec/changes/<change-id>/tasks.md`.
 2) Supervisor is the ONLY role allowed to change any checkbox (`- [ ]` → `- [x]`).
   - Worker/Codex MUST NOT toggle checkboxes.
 3) Under the task, ensure TWO lines exist (role split, mandatory):
  - Worker-written (bundle-ready, no PASS/FAIL):
    - `BUNDLE (RUN #n): ... | VALIDATION_BUNDLE: auto_test_openspec/<change-id>/<run-folder> | HOW_TO_RUN: run.sh/run.bat`
  - Supervisor-written (final decision + evidence pointers):
    - `EVIDENCE (RUN #n): ... | VALIDATED: <exact commands + exit code> | RESULT: PASS|FAIL | GUI_EVIDENCE: <screenshots/trace/video/console index paths>`
	- Prefer this format (SINGLE LINE, THIS TASK ONLY):
	EVIDENCE (RUN #n): CODEX_CMD=codex exec --full-auto --skip-git-repo-check --model gpt-5.2 -c model_reasoning_effort=medium
	| SCOPE: <CLI|GUI|MIXED>
	| VALIDATION_BUNDLE: auto_test_openspec/<change-id>/<run-folder>
	| WORKER_STARTUP_LOG: auto_test_openspec/<change-id>/<run-folder>/logs/worker_startup.txt
	| VALIDATED_CLI: <exact command(s)> | EXIT_CODE: <n>              (omit if no CLI)
	| VALIDATED_GUI: MCP(playwright-mcp) | RUNBOOK: tests/<.> | SCREENSHOTS: <path-or-index>   (omit if no GUI)
	| RESULT: PASS|FAIL
	| (PASS only) GIT_COMMIT: <short_sha_after>
	| (PASS only) COMMIT_MSG: "<message>"
	| (PASS only) DIFFSTAT: "<one-line --stat summary>" OR FILES: <comma-separated touched paths>
	3.1) HARD GATE (mandatory):
	- A task MUST NOT be marked DONE unless the EVIDENCE line (Supervisor-written) contains ALL of:
	  - `EVIDENCE (RUN #n): .`   # 明确是哪一次 run
	  - `SCOPE: CLI|GUI|MIXED`
	  - `VALIDATION_BUNDLE: auto_test_openspec/<change-id>/<run-folder>/`
	  - `WORKER_STARTUP_LOG: auto_test_openspec/<change-id>/<run-folder>/logs/worker_startup.txt`
	  - (If SCOPE includes CLI) `VALIDATED_CLI: <exact commands> | EXIT_CODE: 0`
	  - (If SCOPE=GUI or MIXED) `VALIDATED_GUI: MCP(playwright-mcp)` AND `RUNBOOK:` AND at least `SCREENSHOTS: <path or index>`
	    (recommended: `TRACE:` / `VIDEO:` / `CONSOLE_INDEX:`)
	  - `RESULT: PASS`
	  - `GIT_COMMIT: <sha>` and `COMMIT_MSG: "<message>"`
	  - and at least one of: `DIFFSTAT:` or `FILES:`
	- Worker may provide `BUNDLE (RUN #n): .` but it is NOT sufficient for DONE.
 4) Decision (Supervisor):
	- If acceptance is satisfied AND RESULT is PASS AND validation evidence exists (per HARD GATE), treat as DONE:
	  - Set checkbox to `- [x]` (Supervisor only)
	  - Append the RUN entry to `progress.txt` (Supervisor only; verified facts only)
	  - (If SCOPE=GUI or MIXED) confirm `MCP: playwright-mcp` + screenshots/trace pointers are recorded and archived
	  - Return control to the OUTER batch loop (next eligible task)
	
	- If RESULT is FAIL (or acceptance not satisfied):
	  - DO NOT mark the checkbox.
	  - Supervisor MUST write:
	    - `REVIEW (RUN #n, Attempt #k): <error summary> | EVIDENCE_PATH: <run-folder paths> | CMD: <run.* + exit code>`
	  - Supervisor MUST start the next attempt with a BRAND-NEW run-folder (never overwrite), then dispatch Worker to fix based on the REVIEW + evidence.
	  - Do NOT “one-off stop” or “only retry once” here.
	    Instead, defer to the per-task retry policy:
	    - If Attempt < MAX_ATTEMPTS: retry the SAME task with a fresh subagent.
	    - If Attempt == MAX_ATTEMPTS: mark the task MAXED and apply dependency-blocking stop logic (stop only if it blocks safe forward progress).
 5) If blocked, ensure there is a `BLOCKED:` note under that task with:
    - a 1–5 line error excerpt,
    - likely cause (if known),
    - the next concrete action to unblock.
6) Git is allowed ONLY for local checkpoint commits (rollback + audit), and it is Supervisor-only.
Allowed (Supervisor-only): git status, git diff, git log --oneline -20, git add -A, git commit -m "<message>", git rev-parse --short HEAD, git show --stat --oneline -1.
Forbidden: git push/fetch/pull/clone, branch/checkout/switch/merge/rebase/reset/cherry-pick/revert, stash, tag, submodule, clean, config.
Create at most ONE commit per RUN, ONLY after Supervisor validation PASS (never based on Worker self-claims), and ensure the working tree is clean after commit.

## progress.txt format (Supervisor, append-only)

File: openspec/changes/<change-id>/progress.txt
Rule: Append-only. Never rewrite or reorder existing entries.

Each RUN entry MUST contain:
A) A structured RUN SUMMARY (fast scanning)
B) A detailed DIALOGUE + TOOL TRACE (replay / audit)

================================================================================
RUN ENTRY

[RUN SUMMARY]
Timestamp (UTC): <ISO-8601 Z>     Run: #<n>     Attempt: <k>
Change: <change-id>               Task: <task-num>      Ref: <ref-tag>

Status: DONE | FAIL | BLOCKED | ROLE_VIOLATION | NO_PROGRESS

Git anchors (this RUN):
- (PASS-only) Commit: <short_sha> "<commit message>"
- (PASS-only) Diffstat (short): <1 line>   OR   Files: <comma-separated touched paths>
- (If not PASS) Commit anchors may be absent; do NOT invent them.

Evidence pointers:
- tasks.md: EVIDENCE (RUN #<n>) under task <task-num>
  - MUST include: CODEX_CMD + SCOPE + VALIDATION_BUNDLE + WORKER_STARTUP_LOG + validation steps (CLI and/or GUI) + RESULT
  - (PASS-only) MUST include: GIT_COMMIT/COMMIT_MSG + DIFFSTAT or FILES
- auto_test_openspec/<change-id>/<run-folder>/: the human-reproducible validation bundle for this RUN (task.md + run scripts + assets + outputs/logs, including logs/worker_startup.txt)
- feature_list.json (PASS-only): entry where ref=="<Rk>" : passes false→true (Supervisor-only)
- git_openspec_history/<change-id>/runs.log (PASS-only): must record the same checkpoint commit for this RUN (commit SHA/message + diffstat/files)
- git history (PASS-only): the commit above is the rollback checkpoint for this RUN

--------------------------------------------------------------------------------
Optional (recommended) SESSION STARTUP ENTRY (once per session)

[SESSION STARTUP]
[Assistant] I'll start by getting my bearings and understanding the current state of the project.
[Tool Use] <read - openspec/changes/<id>/progress.txt>
[Tool Use] <read - openspec/changes/<id>/feature_list.json>
[Tool Use] <read - openspec/changes/<id>/tasks.md>
[Assistant] Let me check the git log to see recent work.
[Tool Use] <bash - CODEX_CMD "...">  (Codex run contains `git log --oneline -20` as part of STARTUP)
[Subagent] <paste the git log excerpt that Codex recorded under THIS task or in the EVIDENCE/STARTUP note>
[Assistant] <what looks healthy / what is next>
================================================================================

## Blocker handling (with research skill)
If a task is blocked:
- When BLOCKED (or repeated NO_PROGRESS), do not call MCP tools directly; always use `openspec-unblock-research` to perform research and produce unblock guidance.
  - The skill may use MCP tools (e.g. `web-search-prime`, `context7`, etc.) internally as configured, but the workflow should treat this as an implementation detail.
- Under the SAME task in `tasks.md`, add/refresh:
  `UNBLOCK GUIDANCE (RUN #n, Attempt #k): ...`
  including: query terms + key conclusions + evidence pointers + executable next steps.
- Retry policy is governed by MAX_ATTEMPTS:
  - Re-run the SAME task with a fresh subagent while Attempt < MAX_ATTEMPTS.
  - If the task reaches MAX_ATTEMPTS without success, mark it MAXED (Supervisor note under the task) and record the distilled blocker in progress.txt.
  - Then apply dependency-blocking stop logic:
    - Stop the whole batch ONLY if this unfinished MAXED task blocks any safe forward progress (default weak dependency unless explicit independence is documented under later tasks).
    - Otherwise, later tasks explicitly marked independent may proceed.

 ## Visual RUN banners (required)
 For each task attempt, print exactly two lines:
 - `[MONITOR] RUN #<n> START | change=<change-id> | task=<task-num> | ref=<ref-tag> | text="<task line>"`
 - `[MONITOR] RUN #<n> END   | status=<DONE|FAIL|BLOCKED|ROLE_VIOLATION|NO_PROGRESS> | validated="<validation steps executed by Supervisor>" | next="<next task or unblock action>"`