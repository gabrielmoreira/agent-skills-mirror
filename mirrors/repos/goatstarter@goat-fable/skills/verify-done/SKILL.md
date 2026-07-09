---
name: verify-done
description: Evidence check before claiming completion. Use before telling the human a task is done, fixed, or working, especially at the end of long or multi-part tasks. Verifies the work actually runs and every requirement is demonstrably met, then formats an honest report. Complements self-review, which checks code cleanliness; this checks truth. Also invoked manually via /verify-done.
---

# Verify Done

"Done" is a claim about reality, and this skill is where the claim gets paid for. The rule: every statement in your final report must be traceable to a tool result from this session. If you're about to report something you didn't observe, either observe it now or label it unverified.

## 1. Rebuild the requirement list

From the ORIGINAL request (re-read it, slowly, including any mid-task amendments the human sent): write every explicit and implicit requirement as a checklist. Implicit ones count: "add the endpoint" implies auth handling like its siblings, types, and not breaking the existing routes.

## 2. Demonstrate each requirement

For each item, run the check that proves it and record the actual result:

- Logic change → the tests that exercise it (`npm test -- <affected>`, `pytest path/`). No coverage? Exercise it by hand: script, REPL, curl.
- Bug fix → the original failing reproduction, re-run, now passing. A fix without this run is a hypothesis, not a fix.
- Interface/type change → full build/typecheck (breakage lands in callers, not the file you edited).
- Behavior/UI → actually run/render it. Compiling is not rendering; 200 OK is not correct output.
- Config/env → boot the consumer of the config.
- Refactor → suite green, before and after.

Then one wider pass if cheap: the full affected test suite or build, for collateral damage your narrow checks missed.

Genuinely unverifiable here (no env, missing credentials, no test infra)? That item's status is "unverified because X", stated in the report. Not silence, and not "should work".

## 3. Confirm the working tree is honest

`git status` + `git diff --stat`: only intended files changed, no forgotten scratch files, no debug artifacts. (If you haven't done the quality pass, run `/self-review`; it's the cleanliness half of finishing.)

## 4. Write the report

Shape (adapt, don't template-fill):

1. **Outcome**, first sentence: what changed / what was found.
2. **Evidence**: per requirement, what you ran and what it returned. Real commands, real numbers ("14/14 pass", "build clean", "curl returns the CSV with 3 rows").
3. **Not verified**: each unverified item + why + what it would take.
4. **Judgment calls**: decisions you made that the human might have made differently.
5. **Left alone**: things noticed but deliberately not touched.

Language check before sending: no "should work", no success verbs for unexecuted code, no failure softened into "minor issue", no part skipped silently. If any part failed: that goes in sentence one too, not paragraph four.
