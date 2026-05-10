# Debugging Discipline

## Purpose

Use this skill when tests fail, builds break, runtime behavior diverges from expectations, or a bug report changes the work from feature delivery to fault isolation. Debugging is a control loop: preserve evidence, find the cause, fix the cause, and add a guard so the same failure cannot return unnoticed.

## Stop-The-Line Rule

Halt feature work when any of these signals appears:

- A reproducible failing test, broken build, lint failure, schema failure, or runtime exception.
- A regression in behavior that previously passed verification.
- An unexpected tool or environment error that affects the validity of current evidence.
- A bug report tied to the same surface being modified.

Do not stack new feature edits on top of an unexplained failure. Capture the exact command, output, environment clues, and recent changes before attempting a fix. Resume feature work only after the failure is explained, corrected or safely rolled back, and guarded by verification.

## Five-Step Triage

| Step | Goal | Evidence To Capture |
| ---- | ---- | ------------------- |
| Reproduce | Make the failure happen on demand or document why it cannot yet be reproduced. | Command, input, log excerpt, browser step, fixture, or data state. |
| Localize | Narrow the failing surface to the smallest likely component, boundary, or change. | Failing file, module, route, schema, dependency, or commit range. |
| Reduce | Strip away unrelated conditions until the smallest failing case remains. | Minimal test, fixture, request, config, or scenario. |
| Fix | Change the underlying cause rather than the visible symptom. | Explanation of cause and the smallest code/config/doc edit that removes it. |
| Guard | Add regression coverage or a deterministic gate that fails without the fix. | Test, schema fixture, validator assertion, or documented verification command. |

## Root-Cause-First Heuristics

Prefer a root-cause fix when:

- The same bad state can appear through multiple callers or workflows.
- The visible error is downstream of an invalid input, contract mismatch, or stale assumption.
- A local guard would hide bad data while leaving the producer broken.
- The proposed fix would still be necessary if the UI, CLI, or test harness changed.

Treat a symptom patch as temporary when it only catches an exception, filters an output, retries blindly, or changes a test expectation without explaining why the failure exists. Temporary containment must be named as such, paired with rollback or follow-up, and never reported as a completed root-cause fix.

## Anti-Rationalization Deltas

Apply the canonical Anti-Rationalization Table in `skills/patterns/llm-behavior-guidelines.md` for generic scope, assumption, and verification rationalizations. For debugging work, also enforce these local deltas:

| Pattern | Required Action |
| ------- | --------------- |
| Add a try/catch and move on | Identify why the exception is thrown, then decide whether containment is still needed. |
| Bug only happens locally | Compare environments and capture a minimal reproduction or documented non-repro conditions. |
| Update the expected output because the test is inconvenient | Prove the requirement changed; otherwise fix the implementation or the faulty test setup. |

## Safe Fallback And Rollback Discipline

- If the failure was introduced by your current edit batch, prefer reverting or narrowing your own change over adding compensating complexity.
- If rollback would remove user work or unrelated changes, stop and return a structured failure with evidence instead of using destructive commands.
- If a temporary fallback is needed, make it explicit, bounded, and observable through logs, tests, or a follow-up task.
- Preserve failing evidence in the execution report when verification cannot pass, including the command and the smallest known reproduction.
- Never declare a bug fixed until the targeted guard and the relevant broader suite both pass or the remaining gap is explicitly classified.
