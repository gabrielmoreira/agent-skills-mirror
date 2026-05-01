# Skill Templates

Use this file for reusable examples and output skeletons to keep SKILL.md concise.

## Progress Manifest Example (`.coverage-progress.json`)

```json
{
  "runId": "20260410-153045-auto-tests",
  "iteration": 0,
  "lastCompletedStage": "Stage 0",
  "target": 100,
  "started": "2026-04-07T12:00:00Z",
  "branch": "auto/unit-tests-20260407",
  "coverageMode": "merged",
  "ciCoverage": {
    "verified": true,
    "source": "azure-pipelines.yml",
    "collection": {
      "csharp": "dotnet test Safefly.sln --settings src/.runsettings --collect:\"XPlat Code Coverage\" --results-directory <dir>",
      "typescript": "npx jest --coverage --coverageReporters=text --coverageReporters=cobertura"
    },
    "settingsFiles": ["src/.runsettings"],
    "exclusions": ["<Exclude pattern>", "coveragePathIgnorePatterns"],
    "mergeStrategy": "merge all generated Cobertura XMLs with scripts/parse-cobertura.ps1",
    "status": "verified"
  },
  "mergedBaseline": { "lines": 62.3, "branches": 48.1, "functions": 71.0 },
  "mergedCurrent": { "lines": 62.3, "branches": 48.1, "functions": 71.0 },
  "modules": {
    "<module-1-path>": {
      "language": "<language-1>",
      "baseline": { "lines": 0, "branches": 0, "functions": 0 },
      "current": { "lines": 0, "branches": 0, "functions": 0 },
      "status": "pending",
      "filesRemaining": 0,
      "iterations": 0,
      "lastUpdated": "2026-04-07T12:00:00Z"
    }
  },
  "completedFiles": [],
  "totalIterations": 0,
  "commits": []
}
```

## Memory Context Template (`/memories/repo/test-gen-context-<repo-name>.md`)

```markdown
# Test Generation Context for <repo-name>

## Source Fingerprint
- copilot-instructions.md git commit: <git log -1 --format="%H" output>
- Repo Context for AI Automation section: FOUND / NOT FOUND
- AGENTS.md git commit: <git log -1 --format="%H" output>
- Last validated: <YYYY-MM-DD HH:MM>

## Languages Detected
- <language 1>: <root path> (framework: <test framework>, coverage tool: <tool>)
- <language 2>: <root path> (framework: <test framework>, coverage tool: <tool>)

## Build & Test (per language)
### <Language 1>
- Build command: <command>
- Test command: <command>
- Coverage command: <command>
- Test framework: <framework>

### <Language 2>
- Build command: <command>
- Test command: <command>
- Coverage command: <command>
- Test framework: <framework>

## Coverage Merge Strategy
- Merge tool: parse-cobertura.ps1
- Local merge command: .\scripts\parse-cobertura.ps1 <all cobertura XMLs>

## CI Coverage Evidence
- Verification status: VERIFIED / PROVISIONAL
- Evidence source: <pipeline file / repo automation doc / checked-in script>
- C# coverage command in CI: <exact command or task>
- TypeScript coverage command in CI: <exact command or task>
- Python coverage command in CI: <exact command or task>
- Rust/C++ coverage command in CI: <exact command or task>
- Settings files used by CI: <paths>
- Exclusion patterns used by CI: <patterns>
- Coverage publish path in CI: <path/task>
- Merge strategy in CI: <how reports are combined>
- Missing evidence (if provisional): <what could not be verified>

## Conventions
- Test project naming: <pattern>
- Test folder layout: <pattern>
- Test naming: <pattern>
- Assertion style: <pattern>
- Branch naming: <pattern>

## CI Pipeline
- Pipeline file: <path>
- Test discovery: <pattern>
- Coverage collection: <method>
- Coverage merge: <method>
- .runsettings file: <path or "none">
- Post-creation actions required: YES / NO
- Post-creation action files: <paths>
- Post-creation action rule: <description from copilot-instructions.md, e.g., CloudTest map registration>

## Project Rules
- ProjectUsageType required: YES / NO
- TreatWarningsAsErrors: YES / NO
- Analyzers enforced: <list>

## Gotchas
- <append discovered gotchas>

## Known Exclusions
- <append discovered exclusions>
```

## Mandatory Stage TODO Checklist

```markdown
### Run TODOs
- [ ] Stage 0: Context, Scope & Branch (once)
- [ ] Stage 1: Pre-Flight (build/test/lint)
- [ ] Iteration N - Stage 2: Coverage Baseline
- [ ] Iteration N - Stage 3: Test Plan
- [ ] Iteration N - Stage 4: Generate Tests
- [ ] Iteration N - Stage 5: Build Verification + Quality Review
- [ ] Iteration N - Stage 6: Post-Generation Verification
- [ ] Iteration N - Stage 7: Coverage Delta + Commit
- [ ] Loop Decision (target reached / continue / stalled)
```

## Stage 2 Output Template

```markdown
### Merged Coverage Baseline: XX.X% line, XX.X% branch (across all languages)

| Language | Module | Line Coverage | Branch Coverage |
|----------|--------|--------------|-----------------|
| <lang-1> | <module-1> | XX.X% | XX.X% |
| <lang-2> | <module-2> | XX.X% | XX.X% |
| ... | ... | ... | ... |
| **Merged** | **all** | **XX.X%** | **XX.X%** |

### Priority Targets (next iteration)

| Priority | Language | File | Current Coverage | Uncovered Lines | Why |
|----------|----------|------|-----------------|-----------------|-----|
| P0 | <lang> | <file> | XX.X% | <lines> | <reason> |
| P1 | <lang> | <file> | XX.X% | <lines> | <reason> |
| ... | ... | ... | ... | ... | ... |
| -- | <lang> | <file> | 0% | all | EXCLUDED (<reason>) |
```

## Per-Iteration Output Template

```markdown
# Iteration N: <ComponentName / file batch>

## Coverage at start of iteration: XX.X% line, XX.X% branch
## Files targeted this iteration: <list>

## Test Plan
<plan from Stage 3>

## Final Test Code
<code>

## Verification
- Build: PASS
- Existing tests: PASS (no regressions)
- New tests: X passed, 0 failed
- Lint: no new violations

## Coverage Delta (this iteration)

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Line Coverage | XX.X% | XX.X% | +X.X% |
| Branch Coverage | XX.X% | XX.X% | +X.X% |

## Remaining Actionable Targets

| Language | Module | Actionable Files Remaining | Excluded/Blocked Files | Reason | Next Candidate Files |
|----------|--------|----------------------------|------------------------|--------|----------------------|
| <lang-1> | <module-1> | N | N | <why actionable or blocked> | <file1>, <file2> |
| <lang-2> | <module-2> | N | N | <why actionable or blocked> | <file3>, <file4> |

## Next Iteration Decision
- Decision: Continuing to Iteration N+1 / Done / Stalled
- Next primary language/module: <language/module>
- Why this target is next: <largest remaining coverage opportunity / lowest coverage / highest priority P0-P1 gaps>

## Commit: <hash> on branch <branch-name>
```

## Final Summary Output Template

```markdown
# Unit Test Generation Complete: <Project/Module>

## Branch: <branch-name>
## Total iterations: N
## Total tests added: N
## Total commits: N

## Models Used
- Primary: <model>
- Additional (if any): <model-2>, <model-3>

## Coverage Journey

| Iteration | Files Targeted | Tests Added | Line Coverage | Branch Coverage |
|-----------|---------------|-------------|---------------|------------------|
| 0 (baseline) | -- | -- | XX.X% | XX.X% |
| 1 | file1, file2 | 12 | XX.X% | XX.X% |
| 2 | file3, file4 | 8 | XX.X% | XX.X% |
| ... | ... | ... | ... | ... |
| Final | -- | -- | XX.X% | XX.X% |

## Overall Delta

| Metric | Start | Final | Delta |
|--------|-------|-------|-------|
| Line Coverage | XX.X% | XX.X% | +X.X% |
| Branch Coverage | XX.X% | XX.X% | +X.X% |
| Total Tests | N | N+X | +X |

## Module / Language Status

| Language | Module | Status | Coverage Start | Coverage Final | Remaining Actionable Files | Notes |
|----------|--------|--------|----------------|----------------|----------------------------|-------|
| <lang-1> | <module-1> | DONE / STALLED / INCOMPLETE | XX.X% | XX.X% | N | <reason or summary> |
| <lang-2> | <module-2> | DONE / STALLED / INCOMPLETE | XX.X% | XX.X% | N | <reason or summary> |

## Remaining Actionable Inventory At Stop

| Language | Module | Actionable Files Remaining | Next Candidate Files | Stop Reason |
|----------|--------|----------------------------|----------------------|-------------|
| <lang-1> | <module-1> | 0 | -- | <done or stalled reason> |
| <lang-2> | <module-2> | 0 | -- | <done or stalled reason> |

## Run Status: DONE / STALLED at XX.X%
## Run Stop Reason (if stalled): <only use when every module/language is terminal and target is still not met>

## CI Pipeline Readiness
- Test project added to solution: YES / NO
- CI auto-discovery: YES / NO / MANUAL CONFIG NEEDED

## PR Tags
- `ofp-auto-generated-test`
- Applied as PR label/tag when supported by the platform

## Quality Gate
- Assertion density: X.X (>= 1.5)
- Assertion quality: X% HIGH (>= 60%)
- Tautological tests: 0
- Coding standards: PASS
- Lint: PASS

## PR Description
Generate the PR body using [references/pr-description-template.md](references/pr-description-template.md).

## Next Steps
- [ ] Review branch: `git log <branch-name>`
- [ ] Push for PR: `git push origin <branch-name>`
- [ ] If stalled: see remaining uncovered files in .coverage-progress.json
```
