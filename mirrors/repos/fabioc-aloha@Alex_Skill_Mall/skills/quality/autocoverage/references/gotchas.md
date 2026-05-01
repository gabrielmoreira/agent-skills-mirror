# Gotchas

Compact troubleshooting catalog. Keep entries short and update from observed failures.

| Anti-pattern | Symptom | Root Cause | One Fix | Rule IDs |
|--------------|---------|------------|---------|----------|
| Stage jump to generation | Tests created before a plan | Stage transition skipped | Return to Stage 3 and produce plan artifact first | R1, R2 |
| Single-module build/coverage only | Regressions or gaps found later in full run | Partial scope hid dependency failures | Re-run Stage 1/2 on full project scope | R3, R6 |
| One-language-only planning | Other language modules never improve | Multi-language scope collapsed | Add plan rows for every detected language (or explicit no-target reason) | R4 |
| Exploration treated as approval | Plan/checkpoint missing but generation starts | Discovery output used as stage evidence | Treat exploration as input only; emit Stage 3 artifacts | R5 |
| Missing checkpoint behavior | Unexpected continuation or blocking | Mode semantics not applied consistently | Follow mode rules for Stage 0 and first Stage 3 checkpoint | R8 |
| Missing progress state updates | Resume behavior inconsistent | Stage completion not persisted | Update `.coverage-progress.json` after each stage | R9 |
| Wrong test framework API | Compile failures in tests | Framework inferred incorrectly | Detect from existing test projects and match exactly | R6 |
| Namespace/assembly mismatch | Type resolution errors | Assumed namespace values | Read source namespace declarations before generation | R6 |
| Coverage-only assertions | High line hits, low behavioral confidence | Assertions validate execution, not outcomes | Require at least one meaningful behavioral assertion per test | R2 |
| Tautological expected values | Tests pass while behavior is wrong | Expected result recomputed from prod logic | Replace with independent expected values/invariants | R2 |
| Co-located test project | CI/test discovery failures | Test project placement ignored repo convention | Place tests using discovered repo layout conventions | R6 |
| Lint/test regressions after generation | Green compile but failed pipeline | Stage 6 verification incomplete | Run full post-generation build/test/lint and report before/after counts | R6 |
| CI coverage mismatch | Local and CI coverage diverge | Different exclusions/settings/merge strategy | Mirror CI settings and merge strategy in Stage 2/7 | R3, R6 |
| Oversized PR batches | Review friction and slow merge | Too many files changed per iteration | Keep iteration commits scoped; split by module when needed | R7 |
| Inflated baseline coverage | Coverage numbers higher than expected | Stale bin/obj artifacts from prior builds included in coverage | Clean build artifacts before baseline (`dotnet clean`, `cargo clean`, etc.) | R1 |
| Early stop + ask permission | Skill stops after N iterations and asks "shall I continue?" | CONTINUE decision not executed -- response ended instead of looping | On CONTINUE, immediately start next iteration in the same response. Never ask, never summarize, never yield. | R1 |
| Vague coverage reporting | "0% -> covered" instead of actual numbers | Coverage delta not measured or reported precisely | Always report actual percentages: "0% -> 91.4%" with merged numbers from .coverage-progress.json | R7 |
| Skipped state persistence | .coverage-progress.json not updated after iteration | Step B skipped or deferred past commit/decision | Step B is BLOCKING -- must write mergedCurrent, gap, totalIterations before Step C or D can execute | R9 |
| Output limit disguised as completion | Skill emits summary/history table when hitting output ceiling | Model runs out of output tokens and produces terminal output instead of checkpointing | Persist state, emit one-line status, no summary. | R1 |
| Coverage files inside repo | `coverage-iter1/` directory appears in repo root | coverageDir set to repo path instead of $env:TEMP | Use `[System.IO.Path]::GetTempPath()` for coverageDir. NEVER use a repo subdirectory. | R6 |
| Duplicate test project for same source | Two test projects both reference the same source .csproj | Existing test project not found due to naming mismatch (e.g., `Foo.UnitTest.csproj` vs `Foo.Test.csproj`) | In Stage 0 step 6, search ALL test .csproj files by `<ProjectReference>` target, not by name convention. In Stage 4, check references before creating. | R6 |
| Behavioral duplicate tests | New tests retest scenarios already covered by existing tests | Existing tests not read before planning | In Stage 3, read existing test files for each source class and skip scenarios already validated. | R2, R6 |
| Multi-class test files | All test classes dumped into one giant file | No file-organization rule enforced | One test class per file, named `<SourceClass>Tests.cs`. Split unrelated classes into separate files. | R6 |
