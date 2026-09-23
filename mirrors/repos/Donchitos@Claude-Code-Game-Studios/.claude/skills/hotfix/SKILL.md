---
name: hotfix
description: "Emergency fix bypassing normal sprint process — hotfix branch, approvals tracked, backport verified, full audit trail."
argument-hint: "[bug-id or description]"
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, AskUserQuestion
model: sonnet
---

> **Explicit invocation only**: This skill should only run when the user explicitly requests it with `/hotfix`. Do not auto-invoke based on context matching.

## Phase 1: Assess Severity

Read the bug description or ID. Assess severity using these criteria:

- **S1 (Critical)**: Game unplayable, data loss, security vulnerability
- **S2 (Major)**: Significant feature broken, workaround exists
- **S3 or lower**: Minor issue — normal bug fix workflow applies

Confirm with `AskUserQuestion`:
- Prompt: "I've assessed this as **[assessed severity]** — [brief rationale]. Confirm severity to proceed:"
- Options:
  - `[A] S1 (Critical) — game unplayable, data loss, or security issue`
  - `[B] S2 (Major) — significant feature broken, workaround exists`
  - `[C] S3 or lower — redirect to normal bug fix workflow`

If [C]: stop. Verdict: **REDIRECTED** — use the normal bug fix workflow for S3 and below.

---

## Phase 2: Create Hotfix Record

Draft the hotfix record:

```markdown
## Hotfix: [Short Description]
Date: [Date]
Severity: [S1/S2]
Reporter: [Who found it]
Status: IN PROGRESS

### Problem
[Clear description of what is broken and the player impact]

### Root Cause
[To be filled during investigation]

### Fix
[To be filled during implementation]

### Testing
[What was tested and how]

### Approvals
- [ ] Fix reviewed by lead-programmer
- [ ] Regression test passed (qa-tester)
- [ ] Release approved (producer)

### Rollback Plan
[How to revert if the fix causes new issues]
```

Ask: "May I write this to `production/hotfixes/hotfix-[date]-[short-name].md`?"

If yes, write the file, creating the directory if needed.

---

## Phase 3: Create Hotfix Branch

Check whether this is a git repository:

`Bash: git rev-parse --is-inside-work-tree 2>/dev/null`

If this command fails or returns empty: note "Not a git repository — create the branch manually." and skip branch creation.

If the check passes, use `AskUserQuestion` before creating the branch:
- Prompt: "Ready to create hotfix branch 'hotfix/[short-name]' from [base-ref]?"
- Options:
  - `[A] Yes — create branch`
  - `[B] Use a different base ref — I'll specify it`
  - `[C] Skip — I'll create the branch myself`

Only run `git checkout -b hotfix/[short-name] [base-ref]` if user selects [A]. If [B]: ask the user for the base ref, then run the command with that ref. If [C]: skip branch creation and proceed to Phase 4.

---

## Phase 4: Investigate and Propose

Find the root cause. Draft the minimal fix: which files change, what the change does, and what it deliberately leaves alone. Do NOT refactor, clean up, or add features alongside the hotfix.

Present the root cause and proposed fix, then ask: "May I implement this fix?" Do not modify any code before this approval — an emergency flow earns its audit trail by approving the change *before* it exists, not after.

---

## Phase 4b: Implement (only after approval)

Implement the approved minimal change. Validate the fix by running targeted tests for the affected system. Check for regressions in adjacent systems.

Update the hotfix record with root cause, fix details, and test results.

---

## Phase 5: Collect Approvals

Use the `Agent` tool to request sign-off in parallel:

- `subagent_type: lead-programmer` — Review the fix for correctness and side effects
- `subagent_type: qa-tester` — Run targeted regression tests on the affected system
- `subagent_type: producer` — Approve deployment timing and communication plan

All three must return APPROVE before proceeding. If any returns CONCERNS or REJECT, do not deploy — surface the issue and resolve it first.

---

## Phase 5b: QA Re-Entry Gate

After approvals, determine the QA scope required before deploying the hotfix. Spawn `qa-lead` via `Agent` with:
- The hotfix description and affected system
- The regression test results from Phase 5
- A list of all systems that touch the changed files (use Grep to find callers)

Ask qa-lead: **Is a full smoke check sufficient, or does this fix require a targeted team-qa pass?**

Apply the verdict:
- **Smoke check sufficient** — run `/smoke-check` against the hotfix build. If PASS, proceed to Phase 6.
- **Targeted QA pass required** — run `/team-qa [affected-system]` scoped to the changed system only. If QA returns APPROVED or APPROVED WITH CONDITIONS, proceed to Phase 6.
- **Full QA required** — S1 fixes that touch core systems may require a full `/team-qa sprint`. This delays deployment but prevents a bad patch.

**If the QA step returns `NOT ASSESSED`, the gate did not run — treat it as unmet,
not as met.** `/smoke-check` returns it when the suite never executed and
`/team-qa` when a cycle produced no executed evidence. **A NOT ASSESSED result is
not a pass** — from either skill — and under time pressure the permissive reading
is the one that will feel reasonable,
which is exactly why it is written down here. Either obtain the missing result —
the verdict names what would make it runnable — or take the decision to the
producer explicitly, as a decision to deploy an unverified hotfix rather than as a
gate that quietly cleared.

Do not skip this gate. A hotfix that breaks something else is worse than the original bug.

---

## Phase 6: Update Bug Status and Deploy

> **STOP — deployment requires explicit approval, unconditionally.** Merging a
> hotfix to a release branch is the one irreversible act in this skill, so it is
> gated even though branch creation (reversible) already is. Before any merge,
> tag, or deploy, use `AskUserQuestion`:
>
> - Prompt: "Hotfix validated and approved. Merge to the release branch and
>   deploy?"
> - Options: `[A] Yes — merge and deploy` / `[B] Merge to development only — hold
>   the release` / `[C] Stop here`
>
> This holds regardless of `modes.automation`, including `autonomous`. An
> emergency process is exactly where an unreviewed irreversible step is most
> likely and least recoverable.

> **Backport is not verified unless you verify it.** The frontmatter advertises
> "backport verified", and until this note the word `backport` appeared **once in
> this file — in that claim**. After merging, confirm the fix is present on BOTH
> the release branch and the development branch, and state the result. An
> unbackported hotfix means the bug returns in the next release from development,
> which is the single most common hotfix regression.

Update the original bug file if one exists:

```markdown
## Fix Record
**Fixed in**: hotfix/[branch-name] — [commit hash or description]
**Fixed date**: [date]
**Status**: Fixed — Pending Verification
```

Set `**Status**: Fixed — Pending Verification` in the bug file header.

Output a deployment summary:

```
## Hotfix Ready to Deploy: [short-name]

**Severity**: [S1/S2]
**Root cause**: [one line]
**Fix**: [one line]
**QA gate**: [Smoke check PASS / Team-QA APPROVED / NOT ASSESSED — [why, and whose
             explicit decision it was to deploy anyway]]
**Approvals**: lead-programmer ✓ / qa-tester ✓ / producer ✓
**Backport**: [verified present on release AND development — or NOT VERIFIED, with
              what was not checked]
**Rollback plan**: [from Phase 2 record]

Merge to: release branch AND development branch
Next: /bug-report verify [BUG-ID] after deploy to confirm resolution
```

### Rules
- Hotfixes must be the MINIMUM change to fix the issue — no cleanup, no refactoring
- Every hotfix must have a rollback plan documented before deployment
- Hotfix branches merge to BOTH the release branch AND the development branch
- All hotfixes require a post-incident review within 48 hours
- If the fix is complex enough to need more than 4 hours, escalate to `technical-director`

---

## Phase 7: Post-Deploy Verification

After deploying, run `/bug-report verify [BUG-ID]` to confirm the fix resolved the issue in the deployed build.

If VERIFIED FIXED: run `/bug-report close [BUG-ID]` to formally close it.
If STILL PRESENT: the hotfix failed — immediately re-open, assess rollback, and escalate.

Schedule a post-incident review within 48 hours using `/retrospective hotfix`.

Use `AskUserQuestion`:
- Prompt: "Hotfix complete. What's the next step?"
- Options:
  - `[A] Run /smoke-check to verify the fix`
  - `[B] Run /patch-notes to document this hotfix`
  - `[C] Stop here`
