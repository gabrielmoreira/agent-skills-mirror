# CI Pipeline Readiness Checklist

## Pre-PR Verification Steps

Before submitting a PR with generated tests, verify ALL of the following:

### 1. Solution Inclusion
- [ ] New test project is added to the `.sln` file (`dotnet sln add`)
- [ ] Project reference to the source project is correct
- [ ] No circular references introduced

### 2. Build Verification
- [ ] Build commands run successfully for all detected language modules (for example: `dotnet build <Solution.sln>`, `npm run build`, `cargo build`, `python -m pytest --collect-only`)
- [ ] Full solution builds with zero warnings (if `TreatWarningsAsErrors` is enabled)
- [ ] No new NuGet package restore failures

### 3. Test Execution
- [ ] All existing tests still pass (no regressions)
- [ ] All new tests pass for each detected language module (for example: `dotnet test <Solution.sln>`, `npx jest`, `pytest`, `cargo test`, `ctest`)
- [ ] No tests are accidentally skipped or ignored

### 4. Naming Conventions
- [ ] Test project follows the repo's existing naming pattern (e.g., `<Source>.Tests`, `<Source>.UnitTests`)
- [ ] Test project is in the same folder layout as other test projects in the repo (e.g., `test/`, `src/`, `tests/`)
- [ ] Test project is NOT co-located in the same directory as a source project
- [ ] Assembly name matches project name

### 5. Project File Compliance
- [ ] `<ProjectUsageType>UnitTest</ProjectUsageType>` is present (see project-file-rules)
- [ ] Target framework matches existing test projects in the solution
- [ ] Package versions match existing test projects (MSTest, Moq versions)

### 6. CI Auto-Discovery
- [ ] Check pipeline YAML for test project discovery patterns (e.g., `**/*.Tests.csproj`)
- [ ] Verify new project name matches the discovery pattern
- [ ] If pipeline uses explicit project lists, note that manual update is required

### 7. Repo-Specific Post-Creation Actions
- [ ] Use Stage 0 context to identify any repo-specific actions required when a new test project is created (e.g., CloudTest map file registration, workspace config updates, explicit project lists)
- [ ] If Stage 0 context specifies registration files, add the new test project to the required file(s)
- [ ] Verify any registration matches the format, naming, and variants (e.g., debug/release) of existing entries exactly
- [ ] If Stage 0 context found no post-creation actions, confirm the pipeline uses auto-discovery and no manual steps are needed

### 8. Code Coverage Integration
- [ ] If pipeline collects coverage, verify new test project is included in coverage runs
- [ ] Extract the exact CI coverage commands or tasks per language from pipeline YAML or checked-in scripts
- [ ] Check `.runsettings` for include/exclude patterns that may affect the new project
- [ ] Use the SAME `.runsettings` file locally as CI uses -- prevents local vs CI coverage number mismatches
- [ ] Do NOT generate tests for code excluded from coverage via `.runsettings` `<Exclude>` patterns or `ExcludeByAttribute`
- [ ] If CI pipeline has additional quality gates (e.g., `TreatWarningsAsErrors`, specific analyzers), replicate them in local build command
- [ ] **Multi-language coverage**: If CI merges coverage from multiple languages (e.g., C# + Rust), verify the skill collects and merges ALL languages locally using `parse-cobertura.ps1`
- [ ] Replicate the CI coverage collection flags, settings files, report paths, and merge steps locally so merged numbers match
- [ ] If CI coverage behavior cannot be fully verified, mark local coverage as provisional and do not claim CI parity
- [ ] Verify that adding tests for one language does not regress the merged coverage of another language

### 9. Coding Standards
- [ ] `.editorconfig` rules are followed
- [ ] Analyzer warnings are resolved (not suppressed)
- [ ] Import/using order matches existing conventions
- [ ] Formatting matches existing test files

## Common CI Failures to Prevent

| Failure | Cause | Prevention |
|---------|-------|------------|
| `NETSDK1045: The current .NET SDK does not support targeting` | Wrong target framework | Match existing test projects' TFM |
| `CS0234: The type or namespace name does not exist` | Missing project reference | Add `<ProjectReference>` to source project |
| `Multiple projects in same folder` | Co-located .csproj files | Follow repo's existing test folder convention (test/, src/, tests/) |
| `MSB4025: The project file could not be loaded` | Malformed .csproj | Validate XML structure before committing |
| `Test run failed: 0 tests executed` | Tests not discovered | Check `[TestClass]`/`[TestMethod]` attributes |
| CI run misses new tests | New test project not registered per Stage 0 context instructions | Check Stage 0 context for required registration steps (e.g., CloudTest map files, workspace configs, explicit project lists) |
| `warning CS0618: is obsolete` | Using obsolete APIs | Check for `[Obsolete]` and use replacements |
| Local coverage doesn't match CI | CI merges multiple languages (e.g., C# + Rust) but skill only collects one | Collect coverage for ALL languages and merge reports using `parse-cobertura.ps1` |
