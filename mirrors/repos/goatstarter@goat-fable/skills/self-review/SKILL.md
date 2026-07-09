---
name: self-review
description: Quality review of your own diff before handing it over. Use after completing any multi-file or non-trivial change, before reporting it done. Catches AI-accent code (noise comments, debug leftovers, scope creep, orphan files) and diff-level bugs. Complements verify-done, which checks that the work RUNS; this checks that the code is CLEAN. Also invoked manually via /self-review.
---

# Self Review

Review your own diff as if a stranger wrote it and your name goes on the approval. Your context is biased toward what you *meant* to write, so this pass works from artifacts only: the actual diff and files, not your memory of editing them.

## 1. The full diff, top to bottom

Run `git diff` (and `git status` for untracked files). Read every hunk. You are hunting, in order of frequency:

- **Debug leftovers**: `console.log` / `print` / dump statements added while working; temporary sleeps; verbose flags.
- **Scratch artifacts**: test scripts, fixtures, output files you created to iterate and forgot. Untracked files you can't name a reason for: delete.
- **Commented-out code** and TODOs you could resolve right now.
- **Hardcoded temporaries**: paths, ports, ids, credentials, dates that were placeholders.
- **Orphans**: imports/variables/functions your later edits made unused.
- **Accidents**: deleted lines you don't remember deleting, files changed that the task had no business touching, formatting churn on untouched lines.

## 2. The AI-accent sweep

Would a reviewer smell generated code? Remove the accent:

- Comments that narrate ("// fetch the user"), explain the change ("// updated to new API"), or tutor. Keep only constraint comments the code can't express.
- Defensive bloat: null checks and try/catch on paths that cannot fail, validation of internal calls. Boundaries validate; internals trust.
- Speculative generality: parameters nothing passes, options nothing sets, abstractions with one caller.
- Convention mismatch: naming style, error idiom, file layout diverging from the neighboring code. The codebase's way wins over yours.

## 3. The requirements cross-check

Re-read the original request word by word. For each explicit and implicit requirement, point at the diff hunk that satisfies it. No hunk → it's not done, no matter how done it feels. This is where multi-part requests silently lose part 3 of 4.

Also the inverse: for each diff hunk, name the requirement it serves. Hunks serving no requirement are scope creep: revert them or justify them explicitly in the report.

## 4. The adversarial minute

Assume this diff contains exactly one bug and you must find it before the reviewer does. Best places to look: boundaries between changed and unchanged code, error paths you never exercised, the caller you updated from memory instead of grep, off-by-one at edges (empty list, first/last item, missing key).

For changes above ~150 lines or touching shared interfaces, don't trust your own adversarial minute: spawn the fresh-context verifier (`agents/verifier.md` pattern) and give it the requirements + diff, not your reasoning.

## 5. Close

Fix what you found (each fix re-enters this review), then proceed to verification (`/verify-done`) if you haven't run it. In the report, mention anything you noticed but deliberately left alone.
