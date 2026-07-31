---
name: "mutation-testing"
description: "Meta-test your test harness — apply small intentional defects to production code, expect the suite to catch each one. Surfaces silent coverage gaps that 100% line coverage hides."
lastReviewed: 2026-05-31
---

# Mutation Testing

A green test suite tells you the tests passed. It does not tell you whether the tests would have caught a real defect. Mutation testing closes that gap: introduce a one-character defect in production code, run the suite, expect at least one test to fail. Survivors are coverage gaps.

> **Coverage measures whether the line was executed. Mutation measures whether the line was meaningfully asserted on.** The two are not the same.

## When to fire

- After authoring a new test file, before declaring it "covers" the module
- After adding tests to a previously-untested module
- Before publishing any release that newly depends on a module's correctness
- When a code review surfaces "this is tested, but I'm not sure the tests assert what we think they do"

**Do NOT fire** when:

- The code under test is throwaway (one-off scripts, scratch experiments)
- A formal mutation-testing tool (`stryker`, `mutmut`) is already in CI — that supersedes the manual protocol below
- The cost of running the suite once is high (long integration tests) — sample the high-risk mutations instead of running all of them

## The protocol

For each load-bearing branch / guard / constant in the module:

1. **Apply a one-character defect** that flips the behavior (invert a comparison, change a numeric literal, replace a guard with `if (false)`)
2. **Run the suite** — `npm test` or whatever your canonical entry point is
3. **Expect ≥ 1 failure.** If the suite still passes, that branch has no real coverage
4. **Revert the defect** before applying the next one
5. **Record the result** — caught / survived / precondition-not-found

## PowerShell harness (zero deps)

```pwsh
function Test-Mutation {
    param($file, $find, $replace, $name)
    $orig = Get-Content $file -Raw
    if (-not $orig.Contains($find)) { "[$name] PRECONDITION-NOT-FOUND"; return }
    $mut = $orig.Replace($find, $replace)
    Set-Content -Path $file -Value $mut -NoNewline
    $out = npm test 2>&1
    Set-Content -Path $file -Value $orig -NoNewline   # always restore
    $failMatch = ($out | Select-String -Pattern "fail (\d+)" | Select-Object -Last 1)
    if ($failMatch -and $failMatch.Matches[0].Groups[1].Value -ne '0') {
        "[$name] CAUGHT  (fail=$($failMatch.Matches[0].Groups[1].Value))"
    } else {
        "[$name] *** SURVIVED ***"
    }
}

# Apply a battery of mutations in one shot.
Test-Mutation 'lib/semver.js' 'if (pa.major !== pb.major)' 'if (pa.major === pb.major)' 'M2 major-equality inverted'
Test-Mutation 'lib/edition-install.js' 'marker_schema_version: 2' 'marker_schema_version: 1' 'M5 marker schema version wrong'
```

The function always restores the file (even on failure), so a Ctrl+C mid-batch is safe.

## High-value mutation patterns

| Production-code shape | Mutation that catches a real defect |
| --- | --- |
| `if (cond) return X` (guard) | Replace `cond` with `false` — proves the guard fires |
| `a < b ? -1 : 1` (compare) | Swap the branches — proves ordering is asserted |
| `a !== b` (inequality) | Replace with `a === b` — proves the inequality matters |
| `Object.freeze(X)` | Strip the freeze — proves callers depend on immutability |
| `flag === 'specific-value'` | Change the literal — proves the value matters, not just truthiness |
| `Object.assign({}, src, ...)` (immutable merge) | Drop the `{}` (mutates `src`) — proves no-mutation is asserted |
| `arr.filter(x => x.kind === 'edition')` (filter) | Replace with `true` — proves the filter has data to filter against |
| `fs.writeFileSync(p, v, { flag: 'wx' })` (exclusive write) | Drop the flag — proves exclusivity matters |

## Anti-patterns the protocol catches

**1. Filter with no input data.** A `.filter(e => e.name !== 'local')` test passes trivially when the test data contains zero `local/` entries. Mutation: replace with `e => true`. If no test fails, the filter is unverified. Fix by **seeding test data that would be filtered out** and asserting it doesn't appear in the output.

**2. Exports that production never calls.** Easy to grep: `Select-String -Path src/,extension.js -Pattern "exportedName"` — if production callers are zero, the unit tests are testing dead code. Either wire the export into production or remove it.

**3. Platform-skipped tests with no fallback.** A symlink-cycle test that skips on Windows is no coverage on Windows. Look for `t.skip(...)` and ask: does the protected behavior have a deterministic, platform-independent test alongside it?

**4. "Didn't throw" assertions.** A test that builds a 60-level deep tree and asserts the call "didn't throw" is true even with the depth cap removed. Add a sharp assertion: with cap=50, the depth-60 leaf must be **unreachable**.

**5. Frontmatter-only tests.** A test that JSON.parse's a manifest and asserts `keys.includes('spec_version')` passes even when the field has the wrong value. Assert on the **value**, not just key presence.

## What "good coverage" looks like

For each production module:

- **Every load-bearing branch has a mutation that catches its removal.** Not "every line is covered" — every branch where flipping the condition would ship a real defect.
- **The mutation that catches it names the behavior** (e.g., "stale-lock breaking disabled" → caught by `stale lock (>10min mtime) broken atomically` test).
- **Active-filter tests where source data doesn't naturally exercise the filter.** Seed the data; verify the filter fires.
- **Reference-equality tests for null-result fast paths** (e.g., a pure function that returns the input unchanged on null provenance — assert `out === input`).

## Worked examples from the field

| Mutation | Production code | Test that caught it | Lesson |
| --- | --- | --- | --- |
| `marker_schema_version: 2` → `1` | `lib/edition-install.js applyStaticFetchMarkerFields` | "all six v2 fields" asserts `marker_schema_version === 2` | Assert on the literal value, not just presence |
| `if (_seen.has(real))` → `if (false)` | `lib/fs-utils.js listFilesRecursive` | "pre-populated _seen short-circuits the walk" | Exploit the function's internal parameters (`_seen`, `_depth`) for deterministic platform-independent coverage |
| `e.name !== 'local'` → `e.isDirectory()` (filter removed) | `.github/scripts/build-edition-manifest.cjs` | "regenerates without leaking local/ entries (active filter test)" | When the source tree has no `local/` dirs, the filter has nothing to filter against — seed temp `local/` subdirs to make the filter measurable |
| `Object.assign({}, marker, ...)` → `Object.assign(marker, ...)` | `lib/edition-install.js applyStaticFetchMarkerFields` | "does not mutate the input marker" | The `{}` is load-bearing; mutate it to prove the test asserts immutability |

## Quality bar

A mutation-testing pass is complete when:

- Every named branch in the production module has a mutation entry in your run log
- Every survivor was either closed by a new test or explicitly accepted with a reason (e.g., "behavior is internal-only, no public contract")
- The total mutations-caught ratio is recorded (e.g., "15 of 16 mutations caught; M8 deferred")
- The final state has the source file BIT-IDENTICAL to before the run (your harness always restores)

## Anti-patterns

| Anti-pattern | Correction |
| --- | --- |
| Running mutations on throwaway code | Use the protocol on production modules with real consumers; throwaway code is throwaway |
| Reading "coverage 100%" as "tests are good" | Coverage is a necessary but insufficient signal; mutation tells you whether the assertion was meaningful |
| Skipping the restore step | The harness must always restore — a bug-restore on commit will ship the mutation |
| Manually running 20 mutations one at a time | Use the batch function above; it handles restore + result aggregation |
| Treating a SURVIVED mutation as a test-quality problem alone | Often it surfaces a production-code design problem (dead export, untestable branch) |

## Falsifiability — would revise if

- Date-based: 2026-08-31 (90 days from authorship). If by then no shipped commit cites this skill as the source of a found defect, revisit whether the protocol is being run.
- Event-based: if a formal mutation-testing tool (Stryker, mutmut) is adopted in CI, this skill becomes documentation for the manual fallback only; trim the protocol section accordingly.
- Counter-evidence: if applying the protocol consistently catches zero mutations on three consecutive new test files, either the tests are unusually rigorous (good — note it) or the mutation set is too shallow (revise the "high-value patterns" table).

## Origin

Codified 2026-05-31 after meta-testing the Alex_ACT_Extension static-fetch test harness (commit `4163f67`). The protocol caught two real coverage gaps (symlink-cycle protection and depth-cap enforcement in `lib/fs-utils.js`) that platform-skipped tests had been silently hiding. Applied a second time to the Alex_ACT_Edition test harness (commit `b8de5a5`) where it caught two more gaps (local/ filter on skills and instructions in `build-edition-manifest.cjs`). 12 of 12 caught after gap-closing — the protocol is the reason the final harnesses are trustworthy.

## Related

- [code-review/SKILL.md](../code-review/SKILL.md) — pre-publish review; mutation testing is the final layer when code review surfaces test-quality concerns
- Release preflight discipline — releases that newly depend on a module's correctness should mutation-test it first (Alex ACT itself formalizes this in the Steward release ritual)
