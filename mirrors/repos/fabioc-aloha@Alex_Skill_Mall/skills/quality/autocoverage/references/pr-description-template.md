# PR Description Template

Use this template for the final PR description output in Stage 7.
Render this template exactly once per run, only after loop completion (all modules are `done` or `stalled`). Do not render it in per-iteration updates.

## Global Link Format Rule
Applies to every `File` / `File Under Test` column in this entire template:
- Use a markdown link: `[<repo-relative-path#Lnn>](<host-file-url>)`
- Supported hosts:
	- Azure DevOps: `https://<org>.visualstudio.com/<project>/_git/<repo>?path=/<repo-relative-path>&version=GB<branch>&line=<n>&lineEnd=<n>&lineStartColumn=1&lineEndColumn=200&_a=contents`
	- GitHub: `https://github.com/<org>/<repo>/blob/<branch>/<repo-relative-path>#L<n>`
- Default branch when unknown: `main`.
- Plain text filenames are FORBIDDEN in any File column.
- Bullet-list format for findings is FORBIDDEN. Always use a markdown table.

```markdown
**PR Title**: `[AI-Generated] Add unit tests for <component/module> to increase code coverage`

**PR Tags**: `ofp-auto-generated-test`

## Summary
Auto-generated unit tests for `<component/module>` to increase code coverage.

## What was added
- **N new test files** covering M source files
- **X new test methods** (list top-level test classes added)
- Test project: `<test project path>` (new / existing)

## What was NOT changed
- No production code modifications
- No folder renames or project restructuring
- No package reference changes in production projects
- Dead/unreachable code was not auto-removed by this skill

## Test Plan
| File Under Test | Tests Added | Key Scenarios Covered |
|----------------|-------------|----------------------|
| `[<path/file1.cs#Lnn>](<host-file-url>)` | N | exception handling, validation, error paths |
| `[<path/file2.cs#Lnn>](<host-file-url>)` | N | business logic, edge cases |

## Validations Performed
- [x] Full solution builds with zero errors and zero warnings
- [x] All existing tests pass (no regressions)
- [x] All new tests pass
- [x] Linter/formatter passes with no new violations
- [x] Coverage increased: line XX.X% -> YY.Y% (+Z.Z%), branch XX.X% -> YY.Y% (+Z.Z%)
- [x] Dead/unreachable code scan completed and findings documented (if any)
- [x] Latent bug scan completed and findings documented (if any)

## Insights (Informational)

> All file links in this section follow the Global Link Format Rule defined above.

## Coverage Delta
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Line Coverage | XX.X% | YY.Y% | +Z.Z% |
| Branch Coverage | XX.X% | YY.Y% | +Z.Z% |

## Dead Code Findings (Informational)
- Dead code items found: N
- Confirmed dead: N
- Possibly dead (verify): N

FORBIDDEN: Do NOT use bullet points to list findings. Findings MUST be rendered as a markdown table with clickable File links.

| File | Symbol/Block | Classification | Suggested Action |
|------|--------------|----------------|------------------|
| `[<path/file1.cs#Lnn>](<host-file-url>)` | `<method/class>` | Confirmed Dead / Possibly Dead | Remove / Verify |
| `[<path/file2.cs#Lnn>](<host-file-url>)` | `<branch/block>` | Possibly Dead | Verify with owner |

## Latent Bugs Found (Informational)
- Latent bugs found: N

If `Latent bugs found: 0`, output ONLY the line below and omit severity counts and the table:
- No latent bugs were identified in this run.

If `Latent bugs found > 0`, include:
- High severity: N | Medium severity: N | Low severity: N

FORBIDDEN: Do NOT use bullet points to list findings. Findings MUST be rendered as a markdown table with clickable File links.

| File | Area | Severity | Symptom | Suggested Follow-up |
|------|------|----------|---------|---------------------|
| `[<path/file1.cs#Lnn>](<host-file-url>)` | `<method/class>` | High/Medium/Low | `<what may go wrong>` | Create follow-up bug/work item |
| `[<path/file2.cs#Lnn>](<host-file-url>)` | `<branch/path>` | Medium/Low | `<edge case or logic risk>` | Add focused fix + test |

## Existing Test Issues Observed (Informational)
- Existing test issues found: N

If `Existing test issues found: 0`, output ONLY the line below and omit severity counts and the table:
- No issues were observed in pre-existing tests during this run.

If `Existing test issues found > 0`, include:
- Critical: N | Warning: N | Info: N

FORBIDDEN: Do NOT use bullet points to list findings. Findings MUST be rendered as a markdown table with clickable File links.

| File | Existing Test | Severity | Issue Type | Why It Is Risky | Suggested Follow-up |
|------|---------------|----------|------------|------------------|---------------------|
| `[<path/test1.cs#Lnn>](<host-file-url>)` | `<TestName>` | Critical/Warning/Info | Incorrect assertion / Always-passing / Tautological / Flaky / Obsolete | `<risk summary>` | Fix existing test in follow-up PR/work item |
| `[<path/test2.cs#Lnn>](<host-file-url>)` | `<TestName>` | Warning/Info | Low-value assertion / Non-deterministic setup | `<risk summary>` | Improve assertion quality or determinism |

## Why Stalled

> Include this section ONLY when the run ends STALLED. Omit entirely for DONE runs.

⚠️ **Stalled at XX.X% line coverage** (target: XX.X%, gap: X.X%). See the **"Why Stalled & How to Improve"** PR comment below for a breakdown of blockers and actionable steps to close the gap.

## How to review
1. Each test file has a header comment with the plan IDs it implements
2. Tests follow `MethodName_Scenario_ExpectedBehavior` naming
3. Focus review on assertion quality -- are the expected values independently derived?
4. Check for any tautological patterns (test mirrors production logic)

## Generated by
autocoverage skill | <date>

## Models Used
- Primary: <model>
- Additional (if any): <model-2>, <model-3>
```

For large PRs spanning multiple modules, consider splitting into one PR per module for easier review. The iterative commit structure supports this; each commit targets a specific file batch and can be cherry-picked into a separate PR if needed.

## Compacting Lengthy PR Descriptions

If the rendered PR description is lengthy (e.g., many source files under test), apply the compaction rule below. All other sections remain unchanged.

### Test Plan Compaction
Instead of one row per file, list all `File Under Test` links as comma-separated values in a single row with an aggregated test count and merged scenario keywords.

**Before (one row per file):**
```markdown
| File Under Test | Tests Added | Key Scenarios Covered |
|----------------|-------------|----------------------|
| `[<path/file1.cs#Lnn>](<host-file-url>)` | 5 | exception handling, validation |
| `[<path/file2.cs#Lnn>](<host-file-url>)` | 3 | business logic, edge cases |
| `[<path/file3.cs#Lnn>](<host-file-url>)` | 4 | null checks, retry logic |
```

**After (comma-separated):**
```markdown
| Files Under Test | Tests Added | Key Scenarios Covered |
|-----------------|-------------|----------------------|
| `[<path/file1.cs#Lnn>](<url>)`, `[<path/file2.cs#Lnn>](<url>)`, `[<path/file3.cs#Lnn>](<url>)` | 12 | exception handling, validation, business logic, edge cases, null checks, retry logic |
```

Rules:
- The Global Link Format Rule still applies to every file link in the comma-separated list.
- `Tests Added` is the total count across all listed files.
- `Key Scenarios Covered` merges all per-file scenarios into one comma-separated list (deduplicate identical keywords).
