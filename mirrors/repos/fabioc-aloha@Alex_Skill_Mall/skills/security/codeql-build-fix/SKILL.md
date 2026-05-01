---
type: skill
lifecycle: stable
inheritance: inheritable
name: build-fix
description: Fix compile-time and build errors introduced by prior agent changes
tier: standard
applyTo: '**/*codeql*,**/*build*,**/*fix*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Build Fix — Instructions

> Scope: Compile-time and build errors introduced by prior agent changes  
> Budget: Maximum **5 fix iterations** before stopping

---

## Core Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | **Own-damage only** | Never fix pre-existing errors. If an error existed before your changes, leave it alone and report it. |
| 2 | **Minimal diff** | Every fix must be the smallest possible change that resolves the error. Do not refactor, reorganize, or "improve" surrounding code. |
| 3 | **Preserve intent** | Your fixes must preserve the semantic intent of the original change. If you cannot fix the error without altering the intended behavior, report it. |
| 4 | **No suppression** | Never suppress, silence, or hide errors (e.g., `#pragma warning disable`, `@ts-ignore`, `# type: ignore`, `catch-all` exception handlers, `noqa`). Fix the root cause. |
| 5 | **No deletion of functional code** | Do not delete working functions, classes, or logic blocks to make the build pass. If code was added intentionally, fix it — don't remove it. |
| 6 | **Bounded iteration** | You have a maximum of **5 fix-build cycles**. If the build still fails after 5 attempts, stop and reported with a diagnostic summary. |
| 7 | **Version alignment** | Make sure not to make major version changes like changing dotnet version, changing typescript version, python version. If some version is not available in current env, better install it and align with what the repository demands.

---

## Execution Protocol

### Phase 0: Establish Baseline

Before attempting any fix, you MUST:

1. **Identify your own changes**: Run `git diff` (or equivalent) to produce the full set of files and lines you modified.
2. **Figure out the build command**: Determine how to build the project by looking for checked-in yaml files, repository README or contributing docs, existing CI or pipeline configuration, then established project conventions.
3. **Setup environment**: If some version (dotnet, pip ...) is required to build, make sure to set it up before running the build command (instead of editing repository build configuration)
4. **Capture the build output**: Run the project's build command and capture the full error output.
5. **Classify each error**: For every error in the build output, determine:
   - `SELF_CAUSED` — The error references a file/line/symbol that you changed, or is a direct consequence of your changes (e.g., you renamed a function and a caller now has an unresolved reference).
   - `PRE_EXISTING` — The error exists in code you did not touch and is not caused by your changes.

**Only proceed to fix `SELF_CAUSED` errors.** Log `PRE_EXISTING` errors for reporting but take no action on them.

### Phase 1: Diagnose

For each `SELF_CAUSED` error:

1. **Parse the error precisely**: Extract the error code, file path, line number, and message. Do not paraphrase — use the exact compiler/build-tool output.
2. **Trace to root cause**: Errors often cascade. A single root cause (e.g., a missing import) can produce many downstream errors. Group related errors and identify the root cause(s).
3. **Plan the fix**: Before writing any code, state:
   - Which file(s) you will modify
   - What specific change you will make
   - Why this resolves the error
   - Confirm the fix does not alter the behavioral intent of the original change

### Phase 2: Apply Fix

1. **Make the minimal edit** to resolve the root-cause error(s).
2. **Do not batch unrelated fixes** into a single edit if they touch different logical areas — apply them as separate, traceable edits.
3. **After each edit, re-run the build** to verify:
   - The targeted error(s) are resolved.
   - No new errors were introduced by the fix itself.

### Phase 3: Verify & Iterate

```
iteration = 0
MAX_ITERATIONS = 5

while build_fails and iteration < MAX_ITERATIONS:
    iteration += 1
    
    1. Run build command
    2. Parse new error output
    3. Filter to SELF_CAUSED errors only
    4. If no SELF_CAUSED errors remain → SUCCESS → exit loop
    5. If same error(s) persist from previous iteration:
       - You MUST try a DIFFERENT fix strategy (do not repeat the same fix)
       - If you have exhausted all reasonable strategies → reported
    6. Diagnose and apply fix (Phase 1 → Phase 2)

if iteration >= MAX_ITERATIONS:
    reported with diagnostic summary
```

### Phase 4: Report

On completion (success or escalation), produce a structured report:

```
## Build Autofix Report

**Status**: SUCCESS | reported
**Iterations used**: N / 5

### Errors Fixed
- [Error Code] in [file:line] — [one-line description of fix]

### Errors Skipped (Pre-existing)
- [Error Code] in [file:line] — [reason: not caused by agent changes]

### Errors Unresolved (if reportedd)
- [Error Code] in [file:line] — [what was tried, why it failed]

### Changes Made
- [file:line] — [description of edit]
```


