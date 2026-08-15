---
name: bug-hunt-swarm
description: "Runs a read-only four-agent swarm that ranks root-cause hypotheses for bugs, regressions, crashes, and flakes. Use when the failure is large or ambiguous and the user wants a diagnosis plus proof path. Not for applying patches or implementing the fix (bug-hunter, systematic-debugging). Never launch four investigators for a tiny obvious bug."
version: 1.0.1
risk: unknown
source: https://github.com/Dimillian/Skills/tree/main/bug-hunt-swarm
source_repo: Dimillian/Skills
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/Dimillian/Skills/blob/main/LICENSE
---

# Bug Hunt Swarm

## Overview

Investigate a bug with four read-only sub-agents in parallel, then have the main agent rank the likely causes and recommend the fastest path to prove or fix the issue. This skill is **diagnosis-first**: do not edit files, apply patches, stage changes, commit, or implement fixes as part of this workflow.

## When to Use

Use this skill when you need parallel read-only multi-agent root-cause investigation for:

- **Bugs** — unexpected behavior, broken features, wrong output
- **Regressions** — something that used to work and now doesn't
- **Crashes** — runtime errors, panics, segfaults, unhandled exceptions
- **Flaky behavior** — intermittent failures, race conditions, timing-sensitive issues
- **Unexplained failures** — test failures with no obvious cause, production incidents

**Trigger keywords:** investigate, root cause, why did this break, regression, trace this bug, diagnose, what changed, flaky test, crash analysis, ranked diagnosis, find the cause.

**Do NOT use when:**
- The bug is tiny and obvious — investigate locally instead.
- The user wants an immediate fix, not a diagnosis — use a fix-oriented skill instead.
- The task requires editing files or implementing changes — this skill is read-only by design.

## Prerequisites

- A workspace with the codebase under investigation accessible to all sub-agents.
- Git history available for regression analysis (`git log`, `git diff`, `git show`).
- `rg` (ripgrep) installed for fast code search.
- Ability to launch parallel sub-agents (Cursor multi-agent or equivalent).
- Windows host is primary (PowerShell). All commands below are PowerShell-compatible.

## Procedure

### Step 1: Build the Bug Packet

Collect the smallest useful investigation packet before launching any sub-agent.

1. **Symptom** — one-sentence description of what is wrong
2. **Expected behavior** — what should happen
3. **Actual behavior** — what actually happens
4. **Reproduction steps** — if known; otherwise mark as unknown
5. **Scope of impact** — local, cross-cutting, deterministic, or flaky
6. **Relevant evidence** — logs, stack traces, failing tests, screenshots, recent diffs, environment details

**Source priority order (use the first available):**

1. Direct user description
2. Explicit files, stack traces, logs, tests, or screenshots provided by the user
3. Current git changes or recent repo history when the bug appears regression-like
4. The smallest relevant code path or subsystem surrounding the failure

If the bug report is underspecified, infer a minimal problem statement and explicitly state what is still unknown.

**Read project instructions before launching sub-agents.** Check for and read the closest of:

- `AGENTS.md`
- Repo workflow docs (e.g., `CONTRIBUTING.md`, `README.md`)
- Architecture, state-model, routing, schema, or runtime docs in the **target repo** for the affected subsystem

> **When to load extra docs:** Before composing the investigation brief, load architecture or state-model notes from the codebase under investigation if they exist. This skill does not ship those files.

### Step 2: Bound the Investigation

Write a short investigation brief for the swarm. Include:

1. What appears broken
2. What is not yet proven
3. What part of the system is most likely involved
4. What evidence already exists
5. What kind of proof would count as confirmation

**Use read-only evidence gathering commands:**

```powershell
# Search codebase for relevant symbols or error strings
rg "ErrorSymbolOrMessage" --type py -n

# Check recent changes
git log --oneline -20
git diff HEAD~5..HEAD --stat

# Inspect a specific commit
git show <commit-sha>

# View current uncommitted changes
git diff
git diff --cached

# Run the smallest safe reproduction (if one exists and is non-mutating)
# Example: run a single failing test
# pytest tests/test_failing.py::test_case -x -v
```

**HARD RULES — do not do any of the following as part of this skill:**

- Do NOT edit files
- Do NOT inject new instrumentation
- Do NOT implement fixes
- Do NOT run `apply_patch`
- Do NOT stage, commit, or push changes
- Do NOT run any state-mutating command

### Step 3: Launch Four Read-Only Investigators in Parallel

Launch four sub-agents **only when** the problem is large or ambiguous enough that parallel investigation helps. For a tiny and obvious issue, investigate locally instead.

**For every sub-agent, include these constraints in the prompt:**

- State explicitly that the sub-agent is **read-only**
- The sub-agent must NOT edit files, run `apply_patch`, stage changes, commit, or perform any other state-mutating action
- Ask for **concise** investigation output only
- Ask for: hypothesis, supporting evidence, missing evidence, smallest proof step, and confidence (high/medium/low)
- Tell the sub-agent to avoid generic code quality feedback, nits, or speculative guesses without evidence
- Tell the sub-agent to send findings back to the main agent only — no side-channel communication

**Give every sub-agent the same bug packet and investigation brief.**

---

#### Sub-Agent 1: Reproduction and Scope Investigation

**Goal:** Clarify the exact failure shape and its boundaries.

Check for:

1. The narrowest reliable trigger
2. Conditions that make the bug appear or disappear
3. Expected versus actual behavior at the failure boundary
4. Whether the impact is local, cross-cutting, deterministic, or flaky

**Recommended sub-agent role:** `reviewer`

This sub-agent is read-only. It must not edit files, apply patches, or make any other workspace changes.

---

#### Sub-Agent 2: Code Path and Failure Seam Investigation

**Goal:** Trace the most likely execution path and identify the seam where behavior diverges.

Check for:

1. State transitions, lifecycle edges, or ordering problems
2. Mismatched assumptions between caller and callee
3. Data-flow or control-flow breaks
4. The smallest code region most likely responsible for the failure

**Recommended sub-agent role:** `explorer` for broad tracing, or `reviewer` when a stronger local reasoning pass is more useful

This sub-agent is read-only. It must not edit files, apply patches, or make any other workspace changes.

---

#### Sub-Agent 3: Recent Change and Regression Investigation

**Goal:** Look for likely regressors in nearby history or changed contracts.

Check for:

1. Recent diffs that correlate with the symptom
2. Config, flag, dependency, schema, or migration drift
3. Partial updates where several entry points should have changed together
4. Behavior changes that fit the timing of the bug report

**Recommended sub-agent role:** `reviewer`

This sub-agent is read-only. It must not edit files, apply patches, or make any other workspace changes.

---

#### Sub-Agent 4: Proof Plan and Observability Investigation

**Goal:** Determine the fastest way to confirm or reject the leading hypotheses.

Check for:

1. The smallest existing test or reproduction that should fail
2. The most useful current logs, traces, metrics, or assertions
3. A minimal non-mutating command that could raise confidence quickly
4. What evidence is missing and how to collect it without broad churn

**Recommended sub-agent role:** `reviewer`

This sub-agent is read-only. It must not edit files, apply patches, or make any other workspace changes.

---

**Quality gate:** Report only hypotheses that materially improve the odds of finding the real cause. It is better to return two evidence-backed theories than six vague guesses.

### Step 4: Synthesize Ranked Hypotheses

The **main agent owns synthesis**. Treat sub-agent output as raw investigation input, not final output.

Merge and rank the hypotheses:

- Combine duplicates across sub-agents
- Discard weak speculation
- Prefer evidence over elegance
- Separate likely root causes from mere contributing factors
- Keep alternate theories only when they remain plausible

Normalize surviving hypotheses into this shape:

| # | Hypothesis | Supporting Evidence | Missing / Conflicting Evidence | Smallest Proof Step | Confidence |
|---|------------|-------------------|-------------------------------|-------------------|------------|
| 1 | ...        | ...               | ...                           | ...               | high/medium/low |
| 2 | ...        | ...               | ...                           | ...               | high/medium/low |

If the evidence is too weak for a real ranking, **say so directly** and present the leading open questions instead of fabricating confidence.

### Step 5: Output a Clear Diagnosis Path

Present the result in this order:

1. **Most likely root cause**
2. **Plausible alternate causes** (if any)
3. **Fastest proof step**
4. **Recommended fix path**
5. **Open questions or blockers**

When the fix is not yet clear, recommend the next proving step instead of pretending the diagnosis is complete.

When helpful, group actions into:

- **`prove now`** — immediate non-mutating steps to confirm or reject the leading hypothesis
- **`fix next`** — the recommended fix once proven (do NOT implement as part of this skill)
- **`follow up later`** — secondary investigations, observability improvements, or hardening

**Do NOT implement fixes as part of this skill.** The output is a read-only diagnosis with a prioritized path forward.

## Examples

### Example Bug Packet

```
Symptom: User profile page crashes on load for admin users only.
Expected: Profile page renders for all users.
Actual: 500 error, stack trace points to permission check in ProfileController.
Reproduction: Log in as admin, navigate to /profile.
Scope: Cross-cutting — affects all admin users, deterministic.
Evidence: Stack trace in logs/2026-07-01.log, failing test test_profile_admin_load.
```

### Example Investigation Brief

```
Broken: Admin profile page crashes on load.
Unproven: Whether the crash is in the permission check itself or downstream.
Likely area: ProfileController + permission middleware.
Existing evidence: Stack trace, one failing test.
Proof that counts: A non-mutating command that reproduces the 500 for admin
  users and a code path trace showing where the null dereference occurs.
```

### Example Synthesized Output

```
## Diagnosis

### Most likely root cause (confidence: high)
ProfileController.getPermissions() returns null for admin role because the
admin role was added to the role table in migration 0042 but not to the
permission seed data. The permission check dereferences the null.

Supporting evidence:
- Stack trace points to line 87 of ProfileController.cs
- Migration 0042 adds admin role but has no corresponding permission seed
- Failing test test_profile_admin_load confirms the 500

Missing evidence:
- No confirmation that non-admin roles still have permission data (likely fine
  but unverified)

### Fastest proof step
Run: SELECT role, permissions FROM role_permissions WHERE role = 'admin';
If empty, hypothesis is confirmed.

### Recommended fix path (fix next — do NOT implement here)
Add admin role permission seed to migration 0042 or a new migration 0043.

### Open questions
- Was the admin role intentionally added without permissions (feature flag)?
- Are there other endpoints that will hit the same null path?
```

## Pitfalls

- **Sub-agents mutating state:** Every sub-agent prompt must explicitly state read-only constraints. If a sub-agent attempts to edit files or run `apply_patch`, the main agent must discard that output and re-launch with reinforced constraints.
- **Vague hypotheses without evidence:** Discard any hypothesis that lacks supporting evidence from code, logs, tests, or git history. Two evidence-backed theories beat six guesses.
- **Skipping project instructions:** Always read `AGENTS.md` and relevant subsystem docs before launching sub-agents. Missing project context leads to investigations that ignore known constraints.
- **Treating sub-agent output as final:** The main agent must synthesize, deduplicate, and rank. Raw sub-agent findings are input, not the deliverable.
- **Fabricating confidence:** If evidence is weak, say so. Do not assign "high" confidence to a hypothesis with no supporting evidence.
- **Implementing fixes during diagnosis:** This skill is read-only. If the user asks for a fix, complete the diagnosis first, then switch to a fix-oriented workflow.
- **Over-launching for trivial bugs:** Do not launch four sub-agents for a one-line typo. Investigate locally when the problem is small and obvious.
- **Windows path issues:** On Windows (PowerShell), use backslash paths or forward-slash paths consistently within a single command. Avoid mixing. Use `rg` with `--path` explicitly when searching specific directories.

## Verification

After completing the diagnosis, verify the output quality:

1. **Every hypothesis has evidence.** Check that each surviving hypothesis cites at least one concrete piece of evidence (file:line, commit SHA, log entry, test name).

   ```powershell
   # Verify a cited file:line exists
   rg -n "pattern" path/to/file.ext
   ```

2. **No state was mutated.** Confirm the working tree is clean:

   ```powershell
   git status
   # Expected: nothing to commit, working tree clean
   ```

3. **Proof steps are non-mutating.** Review every recommended proof step and confirm it does not edit files, run migrations, deploy, or change state.

4. **Confidence levels are justified.** Review each confidence rating and confirm it maps to the strength of evidence:
   - **high** — direct evidence (failing test, reproducible crash, clear code path)
   - **medium** — circumstantial evidence (correlated commit, plausible code path)
   - **low** — hypothesis only, no direct evidence yet

5. **Open questions are explicit.** If anything is unknown or unverified, it must appear in the open questions section — not be silently omitted.

## Related Skills

- **code-review** — for reviewing changes before merge, not diagnosing bugs
- **test-writer** — for writing tests to prove a hypothesis after diagnosis
- **git-bisect** — for binary-search regression hunting when timing is known

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
- This skill produces a diagnosis and recommended path forward — it does not implement fixes.
