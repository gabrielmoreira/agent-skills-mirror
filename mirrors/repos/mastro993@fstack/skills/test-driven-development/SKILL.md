---
name: test-driven-development
description: Use when writing code that adds or changes behavior (building a feature, fixing a bug, changing a business rule) or when the user asks for TDD, test-first, red-green-refactor, or tests alongside a change.
compatibility: Needs the project's test runner. The fstack feature-design skill hands its implementation sessions to it.
---

# Test-driven development

Change behavior in small, verified steps: a **test list**, then one **red → green → refactor** cycle per item, until your fear about the behavior has turned into boredom.

- **Red**: one new test, seen failing for the right reason.
- **Green**: the smallest code change that passes the whole fast suite.
- **Refactor**: a better design on green, behavior unchanged. **Two hats**: you add behavior or change structure, one at a time.
- **Budget**: every test costs CI time and upkeep for years. One test per behavior a caller would notice breaking; the tests you touch end leaner than you found them.

Read [references/tests.md](references/tests.md) before the first test.

## 1. Ground

- Find the fast and full test commands and run the suite once: the **baseline**. Record what already fails or flakes, so you never take it for your own red or fix it silently.
- **Placement**: the repo's convention for that kind of code (the tests beside the file, the runner config), else the language's (Go `_test.go` beside the file, Rust's inline `mod tests`, `src/test/` under Maven and Gradle), else co-locate (`pricing.test.ts` beside `pricing.ts`). Prefer the unit's existing test file.
- A bug fix, untested code, a UI, a feature across layers, or a third-party library: read its part of [references/situations.md](references/situations.md).

Done when you hold the commands, the baseline, each new test's file, and the existing tests that cover the code you'll change.

## 2. Test list

List behaviors, not methods. Walk **ZOMBIES**: Zero, One, Many, Boundaries, Interface, Exceptions, Simple first. A bug fix starts with a test on the reported input and its expected result. Then spend the budget:

- Cut what a type, the framework, or an existing test already guarantees.
- Inputs of one behavior become rows of one table (`it.each`, `parametrize`, or a table the file already has).
- Test at the cheapest level that gives confidence.
- Mark the existing tests the change makes wrong or redundant.

An expected outcome the task, code, and docs leave open (exactly at a limit, rounding, empty input) is the user's call: ask in one round, your recommendation first, and carry on with the rest. With no one to answer, take your recommendation and list it as an open question.

Done when every item has a behavior, an expected outcome from the spec, and a file.

## 3. Cycle

One item at a time; tests written ahead mean rework and no feedback.

**Red.** Name the test as a sentence in domain words. Write it backwards: assertion, call, then only the setup it needs, against the API you wish existed. Write expected values by hand from the spec; a value copied from the code's output checks the code against itself. Run it and watch it fail on an assertion about the behavior, after stubbing away any compile or import error. A test that passes at once is covered: drop it, or, when it pins a decision such as a boundary, break the code to watch it go red, then restore.

**Green.** The smallest change: Fake It, Triangulate, or Obvious Implementation. Run the whole fast suite. A case you discover goes on the list. Stuck after a couple of tries: revert to the last green and take a smaller test.

Existing tests are the spec, so green comes from changing code. An existing assertion changes only when the task changes the behavior it pins; then change it first, as this cycle's red, and report it. Skipping, deleting, or loosening a failing test to get green removes the safety net the method stands on.

**Refactor.** On green only, running the suite after each step. Remove duplication, including between test and code (a faked constant). In the tests you added, fold triangulation examples into one table and drop the starter test it covers. Tests you didn't add keep their shape; offer a restyle in the report.

Done when every item's test was seen red for the right reason, the fast suite is green, and the list is empty.

## 4. Prune

Sweep the touched test files and the tests that cover the code you changed, nothing wider. Prune removes or fixes; the tests that stay keep their shape.

- **Redundant**: the same behavior is asserted elsewhere at the same or a cheaper level. Delete or merge.
- **Obsolete**: pins removed behavior, deleted code, or a private detail. Delete, or rewrite through the public behavior when nothing else covers it. Production code that only tests reach goes too.
- **Flaky**: real clock, sleeps, network, randomness, shared state, test order. Fix the cause: inject the clock or random source, fake timers, intercept the network, reset state. Unfixable: delete it if it adds nothing, otherwise keep and report it.
- **Weak**: no assertion, only mock-call checks, a large unread snapshot. Assert the outcome a caller sees, or delete.

A test that fails because of your change is a red, never a prune.

Done when each swept test is kept, merged, fixed, or deleted, and each removal names its reason and what still covers the behavior.

## 5. Verify and report

Run the full suite, lint, and type check, and match or beat the baseline. When the repo already runs mutation testing, run it on the changed files. Commit only when asked, with behavior changes apart from refactoring and pruning.

Report in this shape, dropping empty lines:

```
<what changed, one line>
Test list: ✓ <behavior> — <test>, <file> · ✗ cut <behavior> — <why>
Tests: +<added> −<removed> ~<changed> (suite <before> → <after>)
Changed assertions · Removed or merged · Fixed flaky · Kept flaky: <test> — <reason; what still covers it>
Open questions: <outcomes you assumed>
Verified: <commands and results against the baseline>
```
