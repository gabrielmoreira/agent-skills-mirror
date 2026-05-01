---
type: skill
lifecycle: stable
inheritance: inheritable
name: coverage-guidelines
description: >-
tier: standard
applyTo: '**/*deployment*,**/*coverage*,**/*guidelines*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Coverage Improvement Guidelines

## Production Code Boundary

**NEVER modify production code during coverage work.** Tests must cover existing behavior, not reshape it. If code is untestable, document it in `testability.yaml` — don't refactor to make it testable during a coverage campaign.

## Difficulty Mix

Every coverage iteration must include a mix of difficulty levels:
- **Easy** (30-40%): Simple methods, DTOs, utility functions
- **Medium** (40-50%): Methods with dependencies, conditional logic
- **Hard** (10-20%): Complex orchestrations, error paths, integration points

Never skip hard files to inflate coverage numbers.

## Iteration Quality Gate

Before committing each test file:
1. **Build passes** — `dotnet build` / `npm run build` with zero errors
2. **All tests pass** — `dotnet test` / `npm test` with zero failures
3. **No pre-existing tests broken** — compare before/after test count
4. **Coverage increased** — verify with coverage tool

## Pre-Commit Test Quality Analysis

For every test file before commit, verify:
- Tests assert behavior, not implementation details
- No `Assert.IsTrue(true)` or trivially passing tests
- Mock setup reflects real dependencies
- Edge cases and error paths are covered, not just happy path
- Test names describe the scenario: `MethodName_Scenario_ExpectedResult`

## Coverage Bar Enforcement

- **Diff coverage target:** 80% of changed lines must be covered
- **Overall coverage:** must not decrease from baseline
- If a PR is below target, write more tests — don't merge below bar

## Zero Failures Gate

**NEVER dismiss test failures as "pre-existing."** Every failure must be:
1. Investigated — is it a real bug, a flaky test, or a test environment issue?
2. Fixed if possible in the same PR
3. Documented if it's genuinely pre-existing (file name, test name, reason)

## Pre-Generation Verification

Before writing tests for a file, verify:
- The source file exists and compiles
- You understand the class/method signatures (read them, don't assume)
- Required dependencies are available (NuGet packages, project references)
- The test project can reference the source project

## Run-As-You-Go Testing

After writing each test file, immediately run:
```powershell
dotnet test --filter "FullyQualifiedName~ClassName" --no-build
```
Fix failures before moving to the next file. Don't batch-generate tests.

## Pipeline Coverage Assessment

When assessing a repo's coverage pipeline:
1. Does the pipeline run tests? Which test command?
2. Does it collect coverage? Which tool (coverlet, Istanbul, pytest-cov)?
3. Does it publish coverage to ADO? Check for `PublishCodeCoverageResults` task
4. Is coverage merging correct? Multiple test projects need merge before publish

## Standards Enforcement

- **coverlet.collector** for .NET (not coverlet.msbuild)
- **Istanbul/nyc** for TypeScript/JavaScript
- **pytest-cov** for Python
- Coverage format: Cobertura XML for ADO integration

## Worker Guardrails

When running parallel coverage workers:
- Never assign the same file to multiple workers
- Each worker gets exclusive file ownership via task CSV
- Workers must not modify files outside their assigned list
- Time limit per file: 10 minutes. Skip and log if exceeded

