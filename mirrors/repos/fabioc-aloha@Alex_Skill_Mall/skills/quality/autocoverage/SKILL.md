---
type: skill
lifecycle: stable
inheritance: inheritable
name: autocoverage
description: Use when a user asks to generate or improve unit tests with measurable coverage gains using a strict staged workflow (build -> baseline -> plan -> generate -> verify -> coverage delta). Trigger phrases: generate unit tests, improve coverage, write tests for uncovered code, make PR-ready tests. Do not use for integration/E2E testing, production refactoring, or planning-only requests without code generation intent.
tier: standard
applyTo: '**/*autocoverage*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Auto Unit Test Generator

## Constraints (apply at ALL stages)

**DO**:
- Run until target coverage is reached or all modules are terminal (done/stalled)
- Use measured coverage gaps as input -- never guess
- Prioritize exception handlers, error paths, retry logic, validation
- Build and pass all tests locally before every commit
- Prove a measured coverage delta each iteration
- Branch from default integration branch; atomic commits per iteration
- Stick to verified facts from repo files, commands, and recorded artifacts -- never assume

**NEVER**:
- Generate tests on a broken build
- Test constants, DTOs, constructors, properties, default values, or logging
- Create a test project in the same folder as an existing project
- Rename folders, move files, rename projects, or change production code

## Skill structure

```
SKILL.md                        -- Pipeline (this file)
scripts/
  parse-cobertura.ps1           -- Parse Cobertura XML into JSON
  parse-coverage-text.ps1       -- Parse pytest/Jest/Vitest text coverage into JSON
references/
  code-coverage.md              -- Coverage commands, tools, parsing
  test-planning.md              -- Prioritization + plan format
  test-generation.md            -- Code gen rules, framework compat, Moq, metadata
  test-quality.md               -- Anti-patterns, review checklist, quality gate
  test-finalization.md          -- Incorporate feedback, produce final code
  ci-pipeline-checklist.md      -- PR/pipeline readiness
  skill-templates.md            -- Reusable output templates
  pr-description-template.md    -- Final PR description template
```

## Reference Lookup

Load the reference file(s) when entering the listed stage.

| Stage | Reference file(s) |
|-------|--------------------|
| 2, 7 | [code-coverage.md](references/code-coverage.md) |
| 3 | [test-planning.md](references/test-planning.md) |
| 4 | [test-generation.md](references/test-generation.md), [test-quality.md](references/test-quality.md) |
| 5 | [test-quality.md](references/test-quality.md), [test-finalization.md](references/test-finalization.md) |
| 7 (PR) | [pr-description-template.md](references/pr-description-template.md) |
| Pre-PR | [test-quality.md](references/test-quality.md), [test-finalization.md](references/test-finalization.md) |
| CI | [ci-pipeline-checklist.md](references/ci-pipeline-checklist.md) |
| any | [skill-templates.md](references/skill-templates.md) |

---

## Progress Manifest

Create `.coverage-progress.json` at the repo root to persist state across iterations and sessions:

**Local-state only rule**: `.coverage-progress.json` is runtime state. Never stage or commit this file.

See the "Progress Manifest Example" section in [references/skill-templates.md](references/skill-templates.md).

Add one module entry per detected language/project. Examples: C# (`dotnet test`), Rust (`cargo test`), TypeScript (`npx jest`), Python (`pytest`), C++ (`ctest`).

### Resuming from interruption

On every invocation, check for `.coverage-progress.json` at the repo root:

| Status | Action |
|--------|--------|
| `in-progress` | Re-run coverage to get current state, continue from where it left off |
| `pending` | Start from Stage 0 for that module |
| `done` | Skip this module |
| `stalled` | Skip (report why it stalled in previous session) |
| `skipped` | Skip |

After completing each stage, update the manifest with current coverage numbers, status, and `lastUpdated` timestamp. This makes the skill resilient across sessions -- a 50-module monorepo processes over multiple sessions without losing progress.

If the file does not exist, create it during Stage 0. If a branch is recorded in the manifest, check it out before resuming.

---

## Memory (Cross-Session Context)

Use `/memories/repo/` to cache context discovered during Stage 0 so it persists across sessions. This avoids re-discovering the same information every time.

### Memory path resolution (tool path vs shell path)

- `/memories/repo/...` is the logical memory path for the memory tool.
- **Local (interactive)**: `$env:USERPROFILE\.copilot\memories\repo\...`; use APPDATA fallback only if needed.
- **CI environment**: Use `$env:AGENT_TEMPDIRECTORY` (ADO Pipelines — available in all Azure DevOps pipeline agents) or `$env:RUNNER_TEMP` (GitHub Actions) as the memory root. Never write to user profile paths in CI — they may not exist or persist. Memory files are ephemeral in CI and must not be checked in.

### On first run (Stage 0), save to `/memories/repo/test-gen-context-<repo-name>.md`:

Derive `<repo-name>` from the repo root folder name (e.g., for `C:\repos\MyService`, use `test-gen-context-MyService.md`). This allows multiple repos to have their own context without overwriting each other.

**Use exactly ONE memory file per repo.** If you find multiple files (e.g., both `test-gen-context.md` and `test-gen-context-MyService.md`), merge them into the `test-gen-context-<repo-name>.md` file and delete the other. Do not maintain duplicates.

See the "Memory Context Template" section in [references/skill-templates.md](references/skill-templates.md).

### On every invocation, check memory FIRST:

1. Read `/memories/repo/test-gen-context-<repo-name>.md` -- if it exists, check the **Source Fingerprint** section:
   - Compare the stored git commit hash of `copilot-instructions.md` and `AGENTS.md` against the current git log for those files:
     ```
     git log -1 --format="%H" -- .github/copilot-instructions.md
     git log -1 --format="%H" -- AGENTS.md
     ```
   - If hashes match: memory is valid. Use cached context, skip full Stage 0 discovery.
   - If hashes differ (files were updated in a newer commit): repo instructions have changed. Re-run full Stage 0 discovery and overwrite the memory (preserve the Gotchas and Known Exclusions sections -- only regenerate Build & Test, Conventions, CI Pipeline, and Project Rules).
2. If the memory file does not exist, run full Stage 0 discovery and save the results.
3. **After every iteration**, if you learned something not already in memory -- a new gotcha, a convention, an exclusion, a workaround -- append it. The memory should get smarter over time so the next session starts where this one left off.

---

## Pipeline Stages

**STRICT SEQUENTIAL EXECUTION**: 0 --> 1 --> [ 2 --> 3 --> 4 --> 5 --> 6 --> 7 --> loop ]

**Model requirement**: Both the orchestrator and all subagents MUST use **Claude Opus 4.6 (1M context)**. When spawning subagents, explicitly specify `model: "Claude Opus 4.6 (1M context)"` to ensure the same model with full 1M token context window is used for iteration execution.

**Context management**: Each iteration generates substantial terminal output (build, test, coverage commands) that is never needed again. To prevent context rot:
- **Subagent per iteration**: When looping (CONTINUE), delegate the next iteration (Stages 2-7) to a subagent using **Claude Opus 4.6 (1M context)** model. The subagent gets a fresh context window, executes the full stage sequence, and returns ONLY the coverage scoreboard, loop decision, commit hash, and any errors. The parent context stays clean.
- **Proactive compact**: If subagents are unavailable, compact after every 3-5 iterations with focus: "keep coverage scoreboard, gap, next targets, completedFiles, gotchas; drop terminal output, build logs, and file contents."
- **Required artifacts are never optional**: Stage 3 plan table, Stage 5 verdict table, and Stage 7 scoreboard must always be emitted (by the subagent or inline), even in compact mode.

### Allowed Stage Transitions (Explicit Matrix)

| Current Stage | Allowed Next Stage(s) |
|---------------|------------------------|
| Stage 0 | Stage 1 |
| Stage 1 | Stage 2 |
| Stage 2 | Stage 3 |
| Stage 3 | Stage 4 |
| Stage 4 | Stage 5 |
| Stage 5 | Stage 6 |
| Stage 6 | Stage 7 |
| Stage 7 | Stage 2 (next iteration) OR End (Done/Stalled) |

Transitions not listed above are invalid and must be treated as `blocked`.

## Normative Rules (Single Source of Truth)

- **R1 Sequential stages only**: Do not skip stages. Stage 2 must be followed by Stage 3 before Stage 4.
- **R2 Generation gate**: Do not generate code before Stage 4. Stage 4 is blocked without a valid Stage 3 plan artifact.
- **R3 Full-scope verification**: Stage 1 and Stage 2 must run against the full project/workspace scope, not isolated modules unless dependency-complete equivalence is proven and documented.
- **R4 Multi-language completeness**: Stage 3 planning must cover all detected language modules. If a language has no actionable targets, record the reason explicitly.
- **R5 Exploration is input, not approval**: Discovery/subagent output cannot replace Stage 3 planning artifacts.
- **R6 Verification is mandatory**: Build verification cannot be skipped (Stages 1 and 6).
- **R7 Explicit stage reporting**: Every progress update must include iteration and stage labels.
- **R8 Checkpoint behavior**: Stage 0 and first-iteration Stage 3 checkpoints stop in interactive mode, continue in auto mode after emitting checkpoint output.
- **R9 State persistence**: Update `.coverage-progress.json` after each completed stage.

### Mandatory Stage TODO Contract

Before Stage 0, create this checklist and use it as a hard gate:

See the "Mandatory Stage TODO Checklist" section in [references/skill-templates.md](references/skill-templates.md).

Rules:
- Only one stage can be active at a time; do not advance with an unchecked TODO.
- Each TODO is bound to its stage instructions: execute ALL required steps in that stage before marking the TODO complete.
- Mark complete only when that stage's required output and completion checks are satisfied.
- If a stage fails, mark `blocked` with one-line reason and stop.
- Include TODO delta in each user-facing update.

### Execution Integrity Guards (Prevent False Completion)

Only current-run evidence can close a TODO.

- Create `runId` (`YYYYMMDD-HHMMSS-<short-branch>`) and store it in `.coverage-progress.json`.
- Every stage artifact must carry the same `runId`.
- Memory/previous logs can prefill context but never count as proof.
- Resume only when branch + `runId` + prior stage artifacts all match; else restart from earliest incomplete stage.
- Narrative text is not evidence; missing required table/artifact means stage stays unchecked.
- For each stage start/end, print: `runId`, `iteration`, `stage`, TODO delta, and artifact names.
- If Stage 0 or first-iteration Stage 3 checkpoint output is missing, mark `blocked` and stop. In auto mode, output is still mandatory even though user confirmation is not.
- If Stage 4 starts without a Stage 3 plan artifact for the same `runId` and iteration, mark `blocked` and return to Stage 3.

### Stage Artifact Contract (Machine-Checkable)

A stage is complete only when its required artifact exists for the current `runId` and `iteration`.

| Stage | Required Artifact (must be emitted in output) |
|-------|-----------------------------------------------|
| Stage 0 | Context checkpoint table (languages/modules/commands/scope/branch/target) |
| Stage 1 | Baseline verification summary (build/test/lint counts) |
| Stage 2 | Coverage baseline table + priority targets table |
| Stage 3 | Structured per-language plan table with TP IDs |
| Stage 4 | Generated test file list mapped to TP IDs |
| Stage 5 | Per-test verdict table (APPROVED/NEEDS REVISION/REJECT) |
| Stage 6 | Before/after regression summary (tests + lint) |
| Stage 7 | Coverage delta table + loop decision row |
| Pre-PR Gate | Post-fix verdict scorecard (per-file verdicts, dimension scores, fix summary, build+test verification) |

Missing artifact => stage remains incomplete.

---

### Stage 0: Context, Scope & Branch (runs ONCE)

**Goal**: Understand how the project builds, tests, and lints. Create the working branch.

**Subagent usage (allowed in Stage 0)**:
- You MAY use a read-only subagent (for example `Explore`) to accelerate file/context discovery in Stage 0.
- Scope subagent tasks to discovery only (instructions, project files, test inventory, CI pipeline files, language detection).
- Do NOT delegate code generation, file edits, commits, or stage completion decisions to a subagent.
- You remain responsible for validating findings against actual files and producing the required Stage 0 checkpoint output.

1. **Check memory and existing progress**:
   - Read `/memories/repo/test-gen-context-<repo-name>.md` (derive `<repo-name>` from the repo root folder name) -- if it exists, load cached build commands, conventions, CI details. Skip steps 2-7 below (just verify with a quick build in Stage 1).
   - If memory tool access is unavailable and you must use shell checks, use the Memory path resolution rules above. Do not assume APPDATA path is authoritative.
   - If `.coverage-progress.json` exists, read it. If a `branch` is recorded, check it out (`git checkout <branch>`). Resume from the last incomplete stage -- do not repeat Stage 0.
   - If neither exists, proceed with full discovery below.

2. **Read repo instructions** (MANDATORY first step):
   - `.github/copilot-instructions.md` -- **look for the `## Repo Context for AI Automation` section first**; it contains pre-curated build commands, test commands, coverage commands, CI pipeline details, and known gotchas specifically for AI automation. Use these values directly without re-discovering them.
   - `AGENTS.md` -- setup, code style, gotchas
   - If neither exists, read the root directory, `README.md`, and project config files

3. **Extract from the instructions**:
   - If `## Repo Context for AI Automation` exists in `copilot-instructions.md`: read it fully and treat its values as authoritative. Skip manual discovery for any field already specified there.
   - **Build command** (e.g., `dotnet build`, `npm run build`, `cargo build`)
   - **Test command** (e.g., `dotnet test`, `npx vitest run`, `pytest`)
   - **Lint/format command** (e.g., `dotnet format`, `npx eslint .`, `ruff check .`) -- if available
   - **Custom CI lint checks** -- look for line-length validators, custom PowerShell/bash scripts in CI that enforce max line length or other code style rules beyond standard linters. Record these as additional lint commands.
   - **Max line length** -- check `.editorconfig` (`max_line_length`), CI pipeline scripts (e.g., line-length validation steps), and linter configs. Record the discovered limit in memory.
   - **Test framework** and mocking library
   - **Target framework** / runtime version

3b. **Discover ALL languages in the repository** (MANDATORY):
   The skill must detect every language that has source code AND tests, not just one. Scan for:
   - **C#**: `*.sln`, `*.csproj` files
   - **Rust**: `Cargo.toml`, `Cargo.lock` files
   - **TypeScript/JavaScript**: `package.json` with test scripts, `jest.config.*`, `vitest.config.*`
   - **Python**: `setup.py`, `pyproject.toml`, `pytest.ini`, `tox.ini`
   - **C++**: `CMakeLists.txt`, `*.vcxproj`

   For EACH detected language, record:
   - Build command
   - Test command
   - Coverage collection command (see `references/code-coverage.md`)
   - Test framework

   **If the repo has multiple languages, create a module entry in `.coverage-progress.json` for EACH language.** The skill runs through the full pipeline for each language module, and coverage is merged across all of them to match what CI reports.

   **Check the CI pipeline YAML** to see how CI collects and merges coverage across languages. The skill must collect coverage for all languages locally and merge them using `scripts/parse-cobertura.ps1` so that local and CI coverage numbers match.

4. **Target scoping**: Determine what the user wants to test. Skip: bin, obj, node_modules, generated code, lock files, DTOs, constants.
   - Stage 0 scope must be recorded **per language module**. If multiple languages are detected, do NOT collapse scope to one language in the Stage 0 checkpoint.

5. **Read source files**: Read full content only for files to be tested and their direct dependency interfaces.

6. **Existing test inventory**: Grep for existing test files to understand test patterns, naming conventions, assertion styles, and project structure.
   - **CRITICAL — Source-to-test-project mapping**: For every source project in scope, identify ALL existing test projects that reference or test it — regardless of naming convention. Test project names often differ from their source project (e.g., `SystemActivities.UnitTest.csproj` tests `Workflow.SystemActivities.csproj`). Search by `<ProjectReference>` targets, not just by name matching. Record the mapping in the Stage 0 checkpoint so Stage 4 never creates a duplicate test project for an already-tested source project.

7. **CI pipeline check**: Look for pipeline definitions (`.yml`, `.yaml` in `.pipelines/`, `.azure-pipelines/`, `.github/workflows/`). Note how tests are discovered and executed.
   - **CRITICAL**: Identify how CI collects coverage for EACH language and how reports are merged.
   - Extract the ACTUAL CI coverage commands, task names, flags, report paths, publish steps, and merge steps from pipeline files or repo automation docs. Do not substitute preferred local defaults unless CI explicitly uses them.
   - Note the exact flags, `.runsettings`, and exclusion patterns CI uses per language.
   - Record the CI coverage merge strategy in `.coverage-progress.json` (`coverageMode: "merged"`).
   - If CI merges multiple languages into a single Cobertura report, the skill MUST replicate this locally.
   - If CI coverage behavior cannot be proven from pipeline files, repo automation docs, or checked-in scripts, mark coverage mode as `provisional`, record the missing evidence, and tell the user that local coverage may diverge from CI until verified.
   - Check `copilot-instructions.md` for any repo-specific actions required when a new test project is created (e.g., CloudTest map file registration, workspace config updates, explicit project lists). Record the actions and target files.

8. **Discover branch naming convention**: Check existing branches for patterns:
   ```
   git branch -a --list '*test*' '*unit*' '*coverage*' | head -20
   git log --oneline -20 --format='%D' | grep -oP '[^,\s]+' | head -20
   ```
   Common conventions to look for:
   - `feature/<description>` / `feat/<description>`
   - `dev/<alias>/<description>`
   - `user/<alias>/<description>`
   - `dev/<description>`
   - `<alias>/<description>`
   Determine the best matching convention from existing active branches and recent merged branches, then use that convention for this run.
   If no clear convention, default to: `dev/<alias>/auto-unit-tests-<YYYYMMDD>`.
   - `<alias>` should come from the repo's observed branch prefixes first.
   - If no prefix is observable, use the current git user alias.
   - If still unknown, use `auto`.

9. **Create working branch**:
   - Create from the repository default integration branch (for example `main`, `master`, or `dev`) -- not from a feature branch.
   - Ensure local default branch is up to date before branching.
   - Branch name MUST follow the discovered convention from step 8.
   ```
   git checkout <default-branch>
   git pull --ff-only
   git checkout -b <branch-name>
   ```
   - If `<branch-name>` already exists, append an incrementing suffix (for example `-v2`, `-v3`) while preserving the same convention.
   Record the branch name in `.coverage-progress.json`.

10. **Create or update `.coverage-progress.json`** with all discovered modules set to `pending`, target coverage, and the branch name.
   - Default `target` is **100** unless the user explicitly requests a different target.
   - Default `maxIterations` is **100**. The user may override with a lower value.

11. **Save context to memory**: Write `/memories/repo/test-gen-context-<repo-name>.md` (derive `<repo-name>` from the repo root folder name) with all discovered information (build commands, test framework, conventions, CI pipeline, .runsettings, gotchas). See the "Memory Context Template" section in [references/skill-templates.md](references/skill-templates.md). This ensures future sessions start with full context.

**[STOP] CHECKPOINT**: Present to the user:
- **Languages detected** and modules per language
- Files to test and files excluded (per language)
- Build, test, coverage, and lint commands discovered (per language)
- Target framework per language
- CI pipeline info (including the exact coverage collection commands/tasks/settings, exclusions, report paths, and coverage merge strategy)
- Repo-specific post-creation actions from Stage 0 context (e.g., CI registration files, CloudTest map updates, workspace configs)
- Branch name created
- Coverage target
- Module manifest (for monorepos / multi-language repos)

Checkpoint validity rule:
- If CI coverage collection details are missing, inferred, or only partially known, Stage 0 must label coverage as `provisional` and list the missing evidence explicitly. Do not present local coverage numbers as CI-equivalent unless the CI collection path has been verified.

Checkpoint validity rule:
- If multiple languages were detected but the checkpoint scope is reported as single-language (for example "C# module only"), Stage 0 is INCOMPLETE and must be redone before Stage 1.

In interactive mode: **End your response and wait for user confirmation.** In auto mode: report the checkpoint, then continue to Stage 1.

---

### Stage 1: Pre-Flight (Build + Test + Lint)

Verify the codebase is healthy before generating anything. Run for ALL language modules discovered in Stage 0.

Note: All required commands and details are already captured in Stage 0 Repo Context memory (`/memories/repo/test-gen-context-<repo-name>.md`).

1. **Clean and build locally** (ALL languages): clean stale build artifacts before building (`dotnet clean`, `cargo clean`, `rm -rf dist/`, `npm run clean`, etc.) to prevent inflated coverage from outdated binaries. Then run the build command for EVERY module from repo context memory. If any build fails: diagnose, report, STOP.

2. **Run existing tests** (ALL languages): record per-language total, passed, failed, skipped. If tests fail, report and wait for acknowledgment.

3. **Run linter/formatter** (if discovered in Stage 0): record existing lint warnings/errors as baseline. Generated tests must not introduce new violations.

4. **Record baseline state**: exact counts of passing tests, failing tests, skipped tests, lint violations.

---

### Stage 2: Coverage Baseline

**Reference**: Read `references/code-coverage.md` for tool-specific commands, parsing, and **multi-language report merging**.

Note: All required coverage commands and settings are already captured in Stage 0 Repo Context memory (`/memories/repo/test-gen-context-<repo-name>.md`).

Execution guard for stored coverage commands (mandatory): execute the stored command as-is; if quoting fails, fix only shell escaping (not command intent), and prefer `$env:TEMP` for coverage outputs.

1. Create a temp directory for coverage output (never write into the repo).
2. **Honor coverage exclusions/settings first**:
   - If the repo has `.runsettings`, `coverlet` config, `.nycrc`, or `coverage.config`, read exclusions before collecting coverage.
   - Use the same settings as CI when running local coverage.
   - Record which coverage settings file was used in `.coverage-progress.json`.
3. **Collect coverage for EVERY language module** discovered in Stage 0 (not just one):
   - For each module, run its coverage command from repo context memory and produce a Cobertura XML.
   - Run coverage for ALL detected languages, not just one.
   - Store each language's Cobertura XML separately (e.g., `<language>-coverage.cobertura.xml`).
4. **Merge all Cobertura reports** into a single combined report (mirrors CI behavior):
   - Use `scripts/parse-cobertura.ps1` with ALL report files as input (it merges automatically):
     ```powershell
     $allReports = Get-ChildItem $coverageDir -Recurse -Filter "*.cobertura.xml" | ForEach-Object { $_.FullName }
     .\scripts\parse-cobertura.ps1 @allReports
     ```
   - The **merged** coverage number is the baseline, not any single language's number.
5. Parse merged results into structured data.
6. Record baseline: overall line/branch coverage, per-file breakdown (all languages), uncovered line ranges.
7. Update `mergedBaseline` in `.coverage-progress.json` and each module's individual `baseline`.
8. **Classify uncovered code by priority** (P0-P3), while excluding known exclusions (constants, DTOs, properties, logging, simple constructors, dead code):
   - P0 -- Critical: business logic with < 50% coverage
   - P1 -- Critical: exception handlers, error paths, retry logic, catch blocks
   - P2 -- Medium: utility methods with < 50% coverage
   - P3 -- Low: branch gaps in already-covered methods
9. **Exclude from gap list** (do NOT target these for tests):
   - Constants, constant classes, constant fields
   - Default value assignments
   - Auto-properties (get/set only)
   - DTO/POCO classes, records, and data containers (properties only, no logic)
   - Logging convention code, logger providers, log formatters
   - Constructors (unless they contain branching logic)
   - Classes or methods marked `[Obsolete]` — do not generate tests for deprecated code
   - Dead code: unreachable methods, unused classes, orphaned code paths, commented-out blocks (distinguish dead from rare -- exception handlers and fallback logic are NOT dead code)
10. **Align local and CI coverage behavior**:
    - Validate CI coverage collection and merge strategy per language from pipeline config.
   - Match the actual CI collector/tool choice per language before running local coverage (for example built-in `Code Coverage`, `XPlat Code Coverage`, `dotnet-coverage`, Jest/Vitest coverage reporters, pytest `--cov`, `cargo-llvm-cov`).
   - Match CI settings files, include/exclude patterns, output formats, report paths, and publish-time merge assumptions.
    - If CI merges N language reports, local baseline must also merge N reports.
   - If CI settings are unknown, record that explicitly in output and mark the result `provisional`; do not claim parity with CI.
11. Clean up temp directory.

**Stage 2 output**: Present a summary table showing where the skill will focus next:

See the "Stage 2 Output Template" section in [references/skill-templates.md](references/skill-templates.md).

Include rows for EVERY detected language. Show **ALL actionable targets** (every file/module where coverage can be increased) plus any notable exclusions. Do NOT cap the list at any fixed number — the plan and each iteration must cover the maximum possible files.

**COMPLETION CHECK**: If your Stage 2 output does not contain the Priority Targets table, you have not completed Stage 2. The raw coverage numbers alone are not enough -- the agent and user need to see the prioritized file list before planning.

**This coverage data is the PRIMARY INPUT for test planning.**

If tests cannot run (build failures, missing deps), note the blocker, skip this stage, proceed without baseline. If coverage is already 90%+, focus only on remaining hotspots.

---

### Stage 3: Plan

**Reference**: Read `references/test-planning.md` for prioritization rules, plan format, and categories.

**This is a SEPARATE stage. Do NOT generate code here.**

1. Use coverage gaps from Stage 2 as PRIMARY input, prioritized P0-P3.
1a. Build the Stage 3 plan across ALL detected language modules in `.coverage-progress.json`, not just the current/lowest-coverage language.
1b. **Batch multiple files per iteration**: Plan tests for 10-15 source files per iteration (grouped by module or dependency proximity). More files per iteration = fewer loop cycles = more coverage per session. Do not plan for only 1 file when multiple actionable files exist.
2. **Critical path first**:
   - Exception handlers and catch blocks --> MUST have tests
   - Error return paths --> MUST have tests
   - Retry/fallback logic --> MUST have tests
   - Validation logic --> MUST have tests
   - Happy path business logic --> standard coverage
3. **Do NOT plan tests for**: constants, default values, properties, DTOs, logging, simple constructors, dead code, already-covered code.
3b. **Behavioral deduplication (MANDATORY)**: Before planning tests for any source file, read the existing test files that cover it. If an existing test already validates the same scenario/behavior (even if lines are marked uncovered due to mocking differences), do NOT plan a duplicate. New tests must add incremental behavioral value — covering a genuinely untested code path or scenario — not re-test what existing tests already verify.
4. **If deferring a plan item**, document WHY (e.g., "requires integration test", "testability blocker -- static factory with no seam", "external dependency cannot be mocked"). Every `TP-<SourceFile>-<ShortName>` ID must be either implemented or have an explicit skip reason.
   - ID format: `TP-<SourceFile>-<ShortName>` where `<SourceFile>` is the short source file name (no extension, no path) and `<ShortName>` is a ≤5-word camel-case description of the scenario (e.g., `TP-OrderService-PaymentFailurePath`, `TP-LeaseHook-NullInputReturnsError`).
5. Each test case: ID, Name, Priority, Coverage Target (file:lines), Arrange, Act, Assert.
6. Map every test to a specific coverage gap.
7. Flag latent bugs with **WARNING**.

**Plan output**: structured markdown table with ID, Language, Test Name, Priority (P0-P3), Coverage Target, Arrange, Act, Assert.

**Stage 3 Plan Quality Gate (MANDATORY before Stage 4)**:
- Verify each planned test has a meaningful assertion strategy (not coverage-only / not assert-free).
- Verify planned tests target real behavioral contracts — not assumed behavior. Each test's expected outcome must be derivable from the source code, not guessed.
- Verify planned tests comply with "Do NOT generate" exclusions.
- Verify each planned test maps to a concrete Stage 2 coverage gap.
- Verify the plan includes entries for every detected language module that still has actionable uncovered targets, or explicitly records why a language has no planned items.
- If any planned item violates quality/exclusion rules, revise the plan before proceeding.

**[STOP] CHECKPOINT**: Show the complete per-language test plan. Include a short language coverage summary (planned items per language, or explicit "no actionable targets" reason). In interactive mode: end your response and wait for user confirmation before proceeding to Stage 4. In auto mode: report the checkpoint and continue to Stage 4 automatically.
---

### Stage 4: Generate

**Reference**: Read `references/test-generation.md` for framework rules, namespace verification, test framework compatibility, Moq workarounds, metadata, and project file rules. Read `references/test-quality.md` Part 2 for anti-patterns to avoid.

**Canonical Gate Check (single source)**: You must have a written, quality-gated Stage 3 plan for the current iteration. Required:
- TP IDs for each planned test
- Structured Stage 3 per-language plan table
- Stage 3 quality gate pass
- Current runId and iteration number
- Plan entries for all detected language modules

If any are missing, stop and return to Stage 3.

**Step 0 — Think Before Generating (MANDATORY per source file)**:

Before writing ANY test code for a source file, reason explicitly:

1. **Read the source file fully** — understand its purpose, dependencies, and behavioral contracts.
2. **State assumptions** — list what you believe the method/class does and what constitutes correct vs incorrect behavior. If uncertain about any behavior, flag it — do not guess and run with it.
3. **Surface ambiguities** — if multiple interpretations of behavior exist (e.g., "does null input throw or return empty?"), check the source code, existing tests, or documentation to resolve. If unresolvable, pick the interpretation supported by the code and note it as a comment in the test.
4. **Identify tradeoffs** — if a simpler test approach exists (fewer mocks, less setup), prefer it. If 200 lines of setup could be 50, rewrite the approach before generating.
5. **Push back on the plan** — if a planned test item is untestable, redundant, or would produce a low-value test, skip it with a documented reason rather than generating junk.

This step produces no file output — it is internal reasoning that makes generated code accurate on the first attempt. Skip this step only for trivially simple tests (e.g., single-line validation methods).

1. Generate compilable test code implementing every planned test case.
2. Follow AAA pattern (Arrange-Act-Assert) with explicit comments.
3. Test names: `MethodName_Scenario_ExpectedBehavior`.
3b. **Plan ID comments** (RECOMMENDED): Add a comment mapping each test method to its plan item: `// TP-<SourceFile>-<ShortName>`. This aids traceability but missing TP comments do not block the quality gate or Stage 5 review.
3c. **Line length limit** (MANDATORY): Keep all generated lines within the repo's max line length (from `.editorconfig` or CI checks). Break long lines — split string literals, chain method calls across lines, use intermediate variables. This is a common CI gate failure.
4. **Read actual source files** before generating -- verify namespaces, types, method signatures. Never assume.
5. **Match the repo's test framework AND assertion library exactly** -- detect from existing test projects (NUnit, MSTest, xUnit, Jest, pytest, etc.). Also detect the assertion library (FluentAssertions `.Should()`, Shouldly, built-in `Assert.*`). Use whichever the repo already uses — do NOT mix assertion styles. Follow the version-specific API rules from `test-generation.md`.
6. Apply Moq expression tree workarounds for optional parameters.
7. If creating a new `.csproj`: apply project file rules, set `<ProjectUsageType>UnitTest</ProjectUsageType>`.

**Project placement**: NEVER create a `.csproj` in the same folder as another project. Before creating a test project, discover the repo's existing convention:
1. Search for existing `*.Tests.csproj` or `*.UnitTests.csproj` files and note where they live relative to their source projects.
2. **Check if a test project already exists for the source project** — search ALL existing test `.csproj` files for `<ProjectReference>` elements pointing to the source project. Test project names frequently differ from their source (e.g., `SystemActivities.UnitTest.csproj` tests `Workflow.SystemActivities.csproj`). If an existing test project already references the source, add new tests to THAT project instead of creating a new one.
3. Match that pattern exactly. Common conventions (in order of prevalence):
   - `test/<Source>.Tests/` (separate test root: `src/MyService/` --> `test/MyService.Tests/`)
   - `src/<Source>.Tests/` (sibling under src: `src/MyService/` --> `src/MyService.Tests/`)
   - `tests/<Source>.Tests/` (plural test root)
   - `<Source>/tests/` (tests subfolder per project)
4. If no existing test projects exist, prefer the `test/` or `tests/` root convention if those directories exist, otherwise use sibling folder under `src/`.
5. Check the target directory contents before creating -- if any `.csproj` already exists there, choose a different folder.

**Traceability attributes** (MANDATORY):
- NUnit: `[Category("AutoGenerated")]` and `[Category("CopilotSkill:autocoverage")]`
- MSTest: `[TestCategory("AutoGenerated")]` and `[TestCategory("CopilotSkill:autocoverage")]`
- xUnit: use `[Trait("Category", "AutoGenerated")]` and `[Trait("Category", "CopilotSkill:autocoverage")]`
- Jest/Vitest: add `// @category AutoGenerated CopilotSkill:autocoverage` at top of file
- pytest: use `@pytest.mark.auto_generated` marker

**Placement rule**: Always place traceability attributes on each **new test method**, never on the class. This ensures only generated methods are tagged, regardless of whether the class is new or pre-existing.

**File organization**: One test class per source class, one test file per test class. Never combine test classes for unrelated source classes in a single file.
- Test file name must match the source class: `OrderService.cs` → `OrderServiceTests.cs`.
- **NEVER prefix file or class names with tool/skill/iteration identifiers** (`AutoCoverage_`, `Iter<N>_`, `Generated_`, etc.). Traceability goes in attributes and comments, not filenames. See `references/test-generation.md` "File Naming" and "Coexistence with Existing Test Files" sections.
- If a test file already exists for the source class, add methods to it or create `<SourceClass>ExtendedTests.cs` — never a tool-prefixed duplicate.
- If a source file contains multiple public classes, each gets its own test file.
- Never create a single "catch-all" test file that tests multiple unrelated classes.

**Do NOT generate tests that**:
- Re-compute expected values from production logic (tautological)
- Exist only to increase coverage without validating behavior (coverage-only tests)
- Have no meaningful assertions (including assertion-free tests or exception-only smoke tests)
- Only assert `IsNotNull` without checking values
- Mock the class under test
- Use reflection to test private methods
- Have 50+ lines of setup for one assertion
- Duplicate production code in the test
- Duplicate behavior already tested by existing tests (same scenario, same assertions on same class)
- Test constants, DTOs, records, constructors, properties, logging, or `[Obsolete]` classes/methods
- Target methods with unbounded `while` loops or gRPC/async stream consumers — they deadlock test runners
- Test pure delegation methods (`return await x.Method()`) — only proves the mock works
- Assert on log-message string fragments — breaks on any message rewording

---

### Stage 5: Review + Finalize

**Reference**: Read `references/test-quality.md` for the full review checklist and quality gate. Read `references/test-finalization.md` for the compliance checklist.

**This stage has TWO mandatory parts. Completing only Part A is a VIOLATION. You MUST complete Part B before proceeding to Stage 6.**

**Part A -- Build**: Build the test project. Fix all compilation errors (StyleCop, analyzers, missing usings, wrong APIs). Iterate until clean build. Do not proceed to Part B with broken code.

**Part B -- Quality Review (MANDATORY -- build passing is NOT enough)**: After the build passes, evaluate EACH generated test against the checklist in `test-quality.md` Part 3. Check every test for:
- **Reasoning accuracy** — does the test demonstrate correct understanding of the source behavior? If assertions test the wrong expected values or misinterpret method contracts, the test is REJECT regardless of whether it passes.
- Assertion quality (HIGH/MEDIUM/LOW) -- are assertions validating behavior or just checking not-null?
- Coverage-only pattern -- does the test exist only to execute lines without validating outcomes?
- Assertion presence -- does the test include at least one meaningful behavioral assertion?
- Tautological patterns -- does any test re-compute expected values from production logic?
- Exclusion violations -- does any test target constants, DTOs, constructors, properties, or logging?
- Mock correctness -- is the class under test being mocked? Are mocks set up and verified properly?
- Edge cases -- null, empty, boundary inputs covered?
- Determinism -- any time/random/network dependence?

Produce a per-test verdict table:

| Test Name | Plan Item | Assertion Quality | Issues | Verdict |
|-----------|-----------|-------------------|--------|---------|

Verdicts: APPROVED / NEEDS REVISION / REJECT.

**Part C -- Quality Gate (MANDATORY HARD GATE before Stage 6)**: Run the quality gate from `test-quality.md` Part 4 against all generated tests in this iteration. Produce the scorecard:

| Dimension | Target | Actual | Status |
|-----------|--------|--------|--------|
| Assertion Density | >= 1.5/test | X.X | PASS/FAIL |
| Assertion Quality | >= 60% HIGH | X% | PASS/FAIL |
| Determinism | 100% | X% | PASS/FAIL |
| Flakiness | 0 patterns | N | PASS/FAIL |
| Exclusion Compliance | 0 violations | N | PASS/FAIL |
| Tautological Tests | 0% | X% | PASS/FAIL |

**GATE RULE: ALL dimensions must report PASS (not FAIL, not CONDITIONAL PASS)**. Any FAIL dimension blocks Stage 6 unconditionally.

**Rejection/Revision Loop** (mandatory until PASS):
1. For each FAIL dimension, identify contributing tests from the verdict table
2. Remove all REJECT tests that caused FAIL dimensions
3. For each NEEDS REVISION test marked in verdict table, apply fixes from `references/test-finalization.md`
4. If FAIL dimension persists after fixes, remove those tests too
5. Rebuild test project and re-run quality gate
6. Repeat until ALL dimensions report PASS
7. This loop runs up to 3 iterations per iteration cycle. If PASS not achieved by iteration 3, mark the iteration as STALLED and move to next batch

**COMPLETION CHECK**: Stage 5 is NOT complete until ALL THREE parts are present:
- Part A: Build clean
- Part B: Verdict table with per-test results
- Part C: Quality gate scorecard with **ALL dimensions PASS** (not CONDITIONAL, not FAIL)

**STAGE 6 ENTRY GATE**: Stage 6 is BLOCKED if:
- Quality gate scorecard is missing, OR
- Any dimension shows FAIL or CONDITIONAL PASS status, OR
- Verdict table shows rejected/unresolved NEEDS REVISION tests

If any gate condition is true: DO NOT proceed to Stage 6. Loop back to Part B and apply rejection/revision fixes above.

| Stage | Status |
|-------|--------|
| ... | ... |
| Stage 5: Build + Quality Review | PASS Build clean \| Quality: N approved, N needs-revision (fixed), N rejected \| Gate: ALL DIMENSIONS PASS |

---

### Stage 6: Post-Generation Verification (Build + Test + Lint)

After review and fixes, verify everything end-to-end.

1. **Build the entire solution/workspace** (not just the test project).
2. **Run ALL tests** (existing + new):
   - All previously-passing tests must still pass (no regressions)
   - All new tests must pass
   - If a new test fails after 2 fix attempts: remove it and document why
3. **Run linter/formatter** (MANDATORY if lint/format command exists in Stage 0 context):
   - Run the EXACT lint/format command from Stage 0 context against all new/modified test files.
   - For repos with Prettier: run the Prettier check command (e.g., `npx prettier --check`) against generated files.
   - For repos with ESLint: run ESLint against generated files.
   - For repos with `dotnet format`: run `dotnet format --verify-no-changes`.
   - **Run any custom CI lint checks** discovered in Stage 0 (e.g., line-length validators, custom scripts). These are often separate from standard linters and catch issues like max line length that `dotnet format` does not enforce.
   - If violations found: fix them and re-run until clean.
   - Stage 6 is NOT complete if the lint/format check was skipped when a command exists.
   - If lint/format was not discovered in Stage 0, record "no lint command found" explicitly.
4. **Compare counts**:
   - Before: X passed, Y failed, Z skipped, W lint violations
   - After: X+N passed, Y failed (same or fewer), Z skipped, W lint violations (same or fewer)
   - Report: "Added N new passing tests. No regressions. No new lint violations."

---

### Stage 7: Measure, Commit, Loop Decision

**Reference**: Read `references/code-coverage.md` for commands, parsing, and multi-language report merging.

Stage 7 runs four steps in order. Every step must complete before the next begins.

#### Step A — Measure

1. Collect coverage for ALL language modules (not just this iteration's language).
2. Merge all Cobertura reports (same strategy as Stage 2 / CI).
3. Compute and emit the **coverage scoreboard** — this is the primary Stage 7 output:

| Metric | Original Baseline | Current (merged) | Total Gain | Target | Gap |
|--------|-------------------|------------------|------------|--------|-----|
| Lines  | XX.X%             | XX.X%            | +X.X%      | 100%   | X.X% |
| Branch | XX.X%             | XX.X%            | +X.X%      | 100%   | X.X% |

- `Original Baseline` = coverage at run start (iteration 1 Stage 2). Set once, never overwritten (`originalBaseline` in manifest).
- `Gap` = Target - Current. If Gap > 0, the run is not done.
- This-iteration delta: `Iteration Start: XX.X% → Iteration End: XX.X% (+X.X%)`.
- Per-language breakdown (if multi-language): include `Current`, `Delta`, `Gap to Target` per module.
- Always report actual percentages. Never use "covered" or approximate language.

4. If coverage did NOT increase this iteration: warn and explain which tests may be redundant.
5. If any file's coverage decreased: investigate before proceeding.
6. Run quality gate from `references/test-quality.md` Part 4.

#### Step B — Persist State (BLOCKING — must complete before Step C or D)

7. Update `.coverage-progress.json` **before committing or deciding**:
   - `originalBaseline`: set ONCE in iteration 1. Never overwrite.
   - `baseline`: start-of-iteration coverage.
   - `current`: end-of-iteration coverage.
   - `mergedCurrent`: merged values across all languages.
   - `gap`: `target - mergedCurrent.lines`.
   - Increment `totalIterations`. Update `completedFiles`, `filesRemaining`, `lastUpdated`.
   - **Verification**: after writing, read back `mergedCurrent` and `gap` from the file to confirm the write succeeded. If the file was not updated, Stage 7 is blocked.
8. Append new learnings to `/memories/repo/test-gen-context-<repo-name>.md` (if any). Skip if nothing new.
9. **Proactive compact** (if running inline, not as subagent): After every 3rd iteration completed in this session, trigger a context compact focused on: "keep coverage scoreboard, gap, .coverage-progress.json state, next targets, gotchas. Drop all terminal output, build logs, file contents, and stage-status tables from previous iterations."

#### Step C — Commit

9. **Pre-commit gate**: Stage 6 lint/format must have been run (when a lint command exists). If not, re-run Stage 6 step 3 before committing.
10. Stage test files only. Never stage `.coverage-progress.json` or production code.
11. Commit: `test(<scope>): add unit tests for <component> [iteration N]` with coverage delta in the message.
12. Record commit hash in `.coverage-progress.json` `commits` array.

#### Step D — Loop Decision

**Gate**: Step D cannot execute unless Step B has written `mergedCurrent`, `gap`, and `totalIterations` to `.coverage-progress.json`. If these fields are missing or stale, return to Step B.

13. Recompute actionable inventory across ALL languages/modules. Produce the **Remaining Actionable Targets** table:

| Language | Module | Actionable Files | Excluded/Blocked | Next Candidates |
|----------|--------|------------------|------------------|-----------------|

Narrative claims are not evidence. Only this table is evidence.

14. Execute the decision algorithm:

```
gap = target - mergedCurrent.lines
globalActionable = SUM(actionableFiles) across ALL modules

IF gap <= 0:                    decision = DONE
ELIF globalActionable == 0:     decision = STALLED
ELIF totalIterations >= maxIterations: decision = STALLED
ELSE:                           decision = CONTINUE
```

15. Branch on decision:

- **CONTINUE**: Unconditional branch — start the next iteration immediately.
  - **Preferred: delegate to subagent** using **Claude Opus 4.6 (1M context)** model and the prompt template below (defined once, reused every iteration):

    > **Model: Claude Opus 4.6 (1M context).** Execute iteration N+1 (Stages 2-7) on branch `<branch>`. Read `.coverage-progress.json` and repo context memory. Target: `<target>`%. Current: `<current>`%. Gap: `<gap>`%. Batch 10-15 files. Execute ALL stages in order: Stage 2 (coverage baseline), Stage 3 (plan with TP IDs), Stage 4 (generate tests), Stage 5 (build + quality review + quality gate), Stage 6 (full verification + lint), Stage 7 (measure + commit + loop decision). At Stage 5, read `references/test-quality.md` and `references/test-finalization.md` — apply EVERY check from both files. Honor `.editorconfig` and repo coding standards in all generated code. Ensure traceability: every new test method gets `[TestCategory("AutoGenerated")]` at method level (never class level). Add `// TP-<SourceFile>-<ShortName>` comments where practical (recommended, not blocking). Only commit APPROVED tests with ALL-PASS quality gate; delete the rest before commit. NEVER generate tests for: logging conventions, simple constructors, DTOs, constants, properties, default values, `[Obsolete]` code, generated code, pure delegation methods (`return await x.Method()`), or methods with unbounded `while`/gRPC async stream loops. NEVER assert on log-message string fragments. Use `$env:TEMP` for coverage output, NEVER a repo subdirectory. Update `.coverage-progress.json` before committing. If spawning further subagents (multi-language fan-out), use **Claude Opus 4.6 (1M context)** model. Return RETAIN block (scoreboard table, commit hash, decision, manifest fields) and VERIFY-THEN-DISCARD block (plan table, verdict table, quality gate scorecard, errors).

    RETAIN format the subagent must use:
    ```
    | Metric | Baseline | Current | Gain | Target | Gap |
    | Lines  | XX.X%    | XX.X%   | +X.X%| 100%   | X.X%|
    Commit: <hash>  Decision: CONTINUE/DONE/STALLED
    ```

  - **Multi-language fan-out**: If `.coverage-progress.json` has 2+ modules with actionable files, spawn one subagent per language in parallel using **Claude Opus 4.6 (1M context)** model (e.g., C# subagent + TypeScript subagent simultaneously). Each subagent targets only its language module. Parent collects both RETAIN blocks, merges coverage, then decides CONTINUE/DONE/STALLED on the merged result.
  - **Parent gate** (MANDATORY validation): confirm each subagent report has (1) scoreboard with Gap, (2) commit hash, (3) plan table, (4) verdict table, (5) quality gate scorecard with **ALL dimensions PASS**, (6) manifest updated. Missing any → re-run that subagent. **Quality gate check is critical**: if scorecard shows ANY FAIL or CONDITIONAL PASS dimension, that subagent iteration did not complete Stage 5 properly — re-run. Discard VERIFY-THEN-DISCARD, then **emit the RETAIN scoreboard table as-is** — do not paraphrase into a one-liner. Do NOT accumulate iteration history.
  - **Fallback**: Execute inline if subagents unavailable.
  - Use NEW merged coverage as baseline. Exclude `completedFiles`.
  - No summary, no question, no pause. Terminal output while CONTINUE is a blocking violation.
- **DONE / STALLED**: Emit Loop Decision row. Report final summary.
  - **If STALLED**: Before the Pre-PR Quality Gate, build the "Why Stalled & How to Improve" analysis:
    1. Classify each remaining uncovered file into a stall category (testability blocker, external dependency, integration test needed, quality gate rejection, dead/unreachable code, max iterations reached).
    2. For each category, derive a concrete unblock action with effort (S/M/L) and estimated coverage gain.
    3. Store in `.coverage-progress.json` under `stallAnalysis: [{category, files[], action, effort, estGain}]`.
    4. This data is posted as a **PR comment** (not in the description) during PR Creation step 6. The PR description contains only a short pointer line.
  - Run Pre-PR Quality Gate (see section below). Once the gate completes (APPROVED or max fix cycles exhausted), proceed to PR Creation. Clean up temp directory.

Stage 7 is incomplete without both the coverage scoreboard AND the Loop Decision row.

---

## Exclusion Rules (ALL stages)

Do NOT generate tests for:

| Exclusion | Rationale |
|-----------|-----------|
| Constants and constant fields | Compile-time fixed; no behavior |
| Default value assignments | No logic; just initialization |
| Auto-properties (get/set only) | No behavior beyond storage |
| DTO/POCO classes | Data containers with no logic |
| Logging conventions | Infrastructure concern, not business logic |
| Simple constructors | Assignment-only; no branching |
| Generated code files | Maintained by tooling |

**Exception**: constructors with branching logic (if/switch/validation) ARE eligible.

---

## No-Refactoring Rule (ALL stages)

The following are **STRICTLY PROHIBITED** during test generation:

- Renaming folders
- Moving files to different directories
- Renaming project files (.csproj, .vbproj, etc.)
- Renaming assembly names
- Changing namespaces in production code
- Restructuring project layout
- Adding/removing package references in production projects (test projects are OK)
- Modifying production code in any way

**If any of these seem necessary**: STOP, report to the user, let them decide. Do not propose refactoring plans.

---

## CI Pipeline Readiness

**Reference**: Read `references/ci-pipeline-checklist.md`.

Before delivering output:
1. Check pipeline definitions for test project auto-discovery patterns
2. Ensure new test project name matches the discovery pattern
3. Add test project to `.sln` if applicable: `dotnet sln add <TestProject.csproj>`
4. Execute any repo-specific post-creation actions recorded in Stage 0 context (e.g., CloudTest map file registration, workspace config updates, explicit project lists)
5. Report whether CI will automatically pick up the new tests and whether any manual registration was required, using Stage 0 context as the source of truth

---

## Gotchas

See [references/gotchas.md](references/gotchas.md) for known anti-patterns, symptoms, and fixes.

---

## Output (Per Iteration)

Each iteration through Stages 2-7 produces:

Do NOT include the final PR description in per-iteration output.

See the "Per-Iteration Output Template" section in [references/skill-templates.md](references/skill-templates.md).

## Final Summary (after all iterations)

See the "Final Summary Output Template" section in [references/skill-templates.md](references/skill-templates.md).

## Pre-PR Quality Gate (MANDATORY before PR Creation)

A quality sweep over **only the test files generated during this run** that executes **once**, after the loop terminates (`DONE` or `STALLED`), before any push or PR. Stage 5 reviews each iteration's batch in isolation; this gate re-evaluates all files generated across iterations together and **automatically fixes** every issue it finds — catching cross-iteration drift, inconsistencies, and problems that only surface at aggregate scope.

**Scope**: Only test files created or modified across all iterations of this run (tracked in `.coverage-progress.json` `completedFiles`). Do NOT audit pre-existing test files that were not generated by this run.

**Checklist**: Stage 5 quality checklist (`references/test-quality.md` Parts 1-4) plus `references/test-finalization.md` compliance checklist — applied branch-wide. Same bar, wider lens.

### Subagent: Audit → Fix → Verify

Delegate to a subagent (**Claude Opus 4.6 (1M context)**) that audits, fixes, and verifies in a single pass:

> **Model: Claude Opus 4.6 (1M context).** You are a test quality enforcer. Read `references/test-quality.md` (all Parts) and `references/test-finalization.md`. Read ALL test files generated across all iterations of this run (listed in `.coverage-progress.json` `completedFiles`). Do NOT audit pre-existing tests that were not generated by this run. For each file, evaluate against both checklists. Then:
>
> **Phase 1 — Audit**: Produce a per-file verdict table and quality gate scorecard (see dimensions below). Identify every issue with file:line references.
>
> **Phase 2 — Fix**: For every issue found, apply the prescribed fix from `references/test-quality.md` (anti-patterns → remediation) and `references/test-finalization.md` (compliance checklist). Remove tests that violate exclusion rules entirely; fix everything else in-place.
>
> **Phase 3 — Verify**: After all fixes, build the full solution and run all tests. Confirm zero regressions and zero new lint violations. Re-score the quality gate. If any dimension still FAILs, loop back to Phase 2 (max 3 fix-verify cycles).
>
> **Return exactly:**
>
> 1. **Per-File Verdict Table** (post-fix state):
>
> | File | Tests | Assertion Quality (H/M/L) | Issues Fixed | Remaining Issues | Verdict |
> |------|-------|---------------------------|--------------|------------------|---------|
>
> 2. **Quality Gate Scorecard** (post-fix state):
>
> | Dimension | Target | Actual | Status |
> |-----------|--------|--------|--------|
> | Assertion Density | >= 1.5/test | | PASS/FAIL |
> | Assertion Quality | >= 60% HIGH | | PASS/FAIL |
> | Determinism | 100% | | PASS/FAIL |
> | Flakiness | 0 patterns | | PASS/FAIL |
> | Exclusion Compliance | 0 violations | | PASS/FAIL |
> | Tautological Tests | 0% | | PASS/FAIL |
> | Verify-Only Tests (no Assert) | 0 | | PASS/FAIL |
> | Deprecated Patterns ([ExpectedException]) | 0 | | PASS/FAIL |
> | Traceability Tags | 100% | | PASS/FAIL |
> | Doc Comments on test class | 100% | | PASS/FAIL |
>
> 3. **Overall Verdict**: APPROVED / CONDITIONAL PASS / REJECT
> 4. **Fix Summary**: total issues found, fixed, remaining (with file:line for any remaining).
> 5. **Build + Test Verification**: test count, pass/fail, regressions (must be zero).

### Gate Rules

- **APPROVED** (all dimensions PASS, all files APPROVED) → proceed to PR Creation.
- **CONDITIONAL PASS / REJECT after max fix cycles** → proceed to PR Creation with the final scorecard as a `## Quality Gate` disclosure in the PR description listing unresolved findings.
- **Commit fixes**: stage only test files. Message: `test(<scope>): pre-PR quality fixes`. Record commit hash in `.coverage-progress.json`.
- **Record final scorecard** in `.coverage-progress.json` under `prQualityGate` (overall verdict + dimension scores).

---

## PR Creation

When the Pre-PR Quality Gate completes (APPROVED or max fix iterations exhausted):

1. Push the branch: `git push -u origin <branch-name>`
2. Render the PR description using [references/pr-description-template.md](references/pr-description-template.md). Do NOT inline a custom format.
3. Write the rendered description to a temp file, then pass it to `az repos pr create`:
   ```powershell
   $prDescFile = Join-Path $env:TEMP "pr-description-$runId.md"
   Set-Content -Path $prDescFile -Value $prDescription -Encoding utf8
   # Create (new PR):
   az repos pr create --title "test(<scope>): add unit tests [auto-generated]" --description "@$prDescFile" --source-branch <branch> --target-branch <default-branch> --draft --output json
   # Update (existing PR):
   az repos pr update --id <pr-id> --description "@$prDescFile"
   Remove-Item $prDescFile -ErrorAction SilentlyContinue
   ```
   The `@<filepath>` syntax tells `az` CLI to read the description from a file — this avoids shell argument length limits and special character escaping issues that cause empty descriptions.
4. If `az` CLI is not available, push branch only and output the rendered description for manual paste.
5. Record the PR ID in `.coverage-progress.json` so resumed runs update the same PR.
6. **If STALLED — post "Why Stalled & How to Improve" as a PR comment**:
   The full stall analysis is too large for the PR description (ADO character limits). Post it as a separate PR comment thread so reviewers see actionable next steps without description bloat.
   - Build the comment body from `stallAnalysis` in `.coverage-progress.json`.
   - Use `repo_create_pull_request_thread` (ado MCP) or `az repos pr thread create`.
   - Comment format (see template below).
   - The PR description contains a short pointer: "See the **Why Stalled & How to Improve** PR comment below."

   **Comment template**:
   ```markdown
   ## Why Stalled & How to Improve

   **Stalled at XX.X% line coverage** (target: XX.X%, gap: X.X%)

   | Category | Files | Action to Unblock | Effort | Est. Gain |
   |----------|-------|-------------------|--------|----------|
   | Testability blocker | `[<file1.cs#Lnn>](<url>)`, `[<file2.cs#Lnn>](<url>)` | Extract interface / add DI seam for `<Symbol>` | S | +X.X% |
   | External dependency | `[<file3.cs#Lnn>](<url>)` | Wrap `<ExternalCall>` behind abstraction | M | +X.X% |
   | Integration test needed | `[<file4.cs#Lnn>](<url>)` | Add integration test for `<Component>` | L | +X.X% |
   | Quality gate rejection | `[<file5.cs#Lnn>](<url>)` | Refactor to make assertions meaningful | S | +X.X% |
   | Dead/unreachable code | `[<file6.cs#Lnn>](<url>)` | Remove dead code (reduces denominator) | S | +X.X% |
   | Max iterations reached | N files remaining | Re-run with higher `maxIterations` | None | +X.X% |

   **Effort**: S (< 1 hr) · M (1-4 hrs) · L (> 4 hrs / architectural)

   ---
   Categories: testability blocker · external dependency · integration test needed · quality gate rejection · dead/unreachable code · max iterations reached
   ```

   Compaction rules:
   - ONE row per category (not per file). Comma-separate file links within the `Files` cell.
   - Keep `Action to Unblock` under 80 chars. Merge related actions per category.
   - `Est. Gain` is the combined gain for all files in that row.
   - If a category has > 10 files, show top 5 by coverage impact and append `+ N more`.
   - Omit rows with zero files.
   - Global Link Format Rule applies to every file link.

---

## Post-PR Pipeline Monitoring

After PR creation, monitor CI and self-heal using `ado` MCP server tools.

### Prerequisites

The `ado` MCP server must be configured. Add to `~/.copilot/mcp-config.json` (or VS Code MCP settings):

```json
{
  "mcpServers": {
    "ado": {
      "command": "agency",
      "args": ["mcp", "ado"]
    }
  }
}
```
**Key tools** (server: `ado`):
- `repo_get_pull_request_by_id` — PR details, merge status
- `pipelines_get_builds` — find PR build (branch: `refs/pull/<prId>/merge`, requires repo GUID)
- `pipelines_get_build_status` — build result with stage/job breakdown
- `pipelines_get_build_log` — list all log entries for a build
- `pipelines_get_build_log_by_id` — read a specific log by ID (supports `startLine` for large logs)
- `pipelines_run_pipeline` — re-queue a pipeline run
- `repo_list_pull_request_threads` — CI-posted comments (test results, coverage reports)

### Workflow

1. **Find build**: `pipelines_get_builds` with `refs/pull/<prId>/merge`. Check result via `pipelines_get_build_status`.

2. **On failure** — diagnose:
   - `pipelines_get_build_status` → find which stage/job failed
   - `pipelines_get_build_log` → list log entries, identify the failed step's log ID
   - `pipelines_get_build_log_by_id` → read the actual error output

   | Type | Action |
   |------|--------|
   | Build/test error in files from this PR | Fix locally, verify against `references/test-quality.md` and `references/test-finalization.md`, rebuild, re-run tests, push (auto-retriggers) |
   | Error in files NOT modified by this PR | Report to user — do not fix |
   | Timeout | Report to user — cannot self-heal |
   | Infra/agent issue | Re-queue via `pipelines_run_pipeline` or report |

3. **Fix-push-monitor loop**: max 3 cycles. After 3 failures, report to user.

4. **On success**: `repo_get_pull_request_by_id` to confirm merge readiness. PR is ready for review.