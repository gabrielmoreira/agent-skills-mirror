---
name: powertoys-issue-to-design
description: "Fork-first workflow that turns a microsoft/PowerToys bug issue into an APPROVED fix DESIGN before any code is written. Given an upstream issue number, it: (0) syncs the user's fork (MuyuanMS/PowerToys) with upstream and resumes any prior design work on the issue instead of duplicating; (1) triage-checks for red flags (linked PRs, duplicates, someone already working) and pauses for approval if found; (2) runs an INVESTIGATOR agent that reads the code + issue evidence and produces an inferred root cause and a concrete fix plan; (3) runs an ADVERSARY agent that judges whether the root cause actually matches the reported issue and whether the fix plan is sound, listing concrete objections; (4) loops investigator↔adversary until the adversary raises no blocking objections (a converged design); (5) creates (or updates) the fork mirror issue whose body carries BOTH the sanitized original report AND the final design (root cause + fix plan + how-to-verify), with NO #<number> back-reference to upstream; and (6) STOPS at a design-approval gate, presenting the root cause + fix plan for the user to approve — on the dashboard or via ask_user. Because the design lives on the user's own fork, it is safe to display in full publicly. On approval, hand off to powertoys-design-to-pr to build the PR from the approved design. Nothing touches microsoft/PowerToys."
---

## When to Use

Use this skill as the **first half** of the fix pipeline for a PowerToys **bug** (not features): when you want a well-investigated, adversarially-reviewed **fix design** before spending a coding-agent session on an implementation. It replaces jumping straight from an issue to a PR. Trigger phrases: "design a fix for issue M", "investigate root cause of M", "what's the fix plan for M", "run issue-to-design for M".

This skill produces an **approved design captured in a fork mirror issue**. Its output is consumed by **`powertoys-design-to-pr`**, which assigns the coding agent and drives the review loop to a ready-to-publish PR. Together they replace the old single-step issue→PR flow with **issue → design (approve) → PR (approve)**.

## Core Principles (read first)

1. **Fork-first, always.** Every artifact — the investigation notes, the design, the mirror issue — lives in the user's fork (`<FORK_REPO>`, e.g. `MuyuanMS/PowerToys`). Nothing touches `microsoft/PowerToys`.
2. **Never leak a back-reference to the upstream issue.** In the fork mirror issue, in commit messages, and in any comment, **NEVER** write `#<M>` or any GitHub auto-link form (`GH-M`, `microsoft/PowerToys#M`, a full issue URL, or "fixes/closes/resolves #M"). GitHub turns those into cross-references that notify the upstream thread. Refer to the issue as plain text: `Issue M` / `[Issue M]`.
3. **Design before code.** Do NOT assign the coding agent or open any PR here — that is `powertoys-design-to-pr`'s job, and only after the design-approval gate. This skill stops at an approved design.
4. **Adversarial by construction.** The design is only "done" when a separate **adversary** agent — reasoning independently from the investigator — cannot find a blocking objection to either the inferred root cause or the fix plan. Do not let the investigator grade its own work.
5. **Evidence over assumption.** Diagnose from the actual code and the issue's attachments/logs, not from the issue title. If key evidence (diagnostic bundle, logs, repro) exists upstream, pull it in (Phase 2) before concluding a root cause.
6. **Two gates only.** Pause for explicit user approval (a) after triage if red flags are found (Phase 1), and (b) at the design-approval gate (Phase 6). Otherwise, in autopilot, proceed and state your assumptions.
7. **Resume, don't duplicate.** Always run Phase 0 first: sync the fork's `main` and check whether a design/mirror issue already exists for Issue M, then pick up from the correct phase.
8. **The design is public-safe.** Because it lives on the user's own fork (only plain-text `Issue M`, no upstream cross-ref), the root cause + fix plan may be shown **in full** on the triage dashboard's public layer.

## Configuration & Prerequisites (verify on first run)

Reuse the **Fork Configuration** and **Prerequisites** from `powertoys-design-to-pr` (formerly `powertoys-issue-to-pr`). Auto-detect then confirm:

- `<FORK_OWNER>` — GitHub login (`gh api user --jq '.login'`, e.g. `MuyuanMS`).
- `<FORK_REPO>` — `<FORK_OWNER>/PowerToys`.
- `<CLONE_PATH>` — local PowerToys clone for code investigation (e.g. `C:\PowerToys`).

```powershell
gh auth status                                   # USER token with repo scope
gh repo view <FORK_REPO> --json nameWithOwner
```

Labels: bugs carry `Issue-Bug`; untriaged carry `Needs-Triage`. Command Palette lives under `src/modules/cmdpal/` (label `Product-Command Palette`).

---

## Phase 0 — Resume check & fork sync (ALWAYS run first)

### 0a. Sync the fork's `main` with upstream

Identical to `powertoys-design-to-pr` Phase 0a. Keeps investigation grounded on current code.

```powershell
gh api repos/microsoft/PowerToys/compare/main...<FORK_OWNER>:main --jq '{behind_by, ahead_by, status}'
# If behind_by > 0, fast-forward via merge-upstream:
'{ "branch": "main" }' | Set-Content "$env:TEMP\syncfork.json" -Encoding utf8
gh api --method POST /repos/<FORK_REPO>/merge-upstream --input "$env:TEMP\syncfork.json"
```

### 0b. Detect prior design work for Issue M

```powershell
# Is there already a mirrored issue "[Issue M] ..." in the fork?
gh issue list --repo <FORK_REPO> --state all --search '"[Issue M]" in:title' `
  --json number,title,state,body,url
```

Inspect the mirror body for a `## Fix design` section (this skill writes one). Determine the resume point:

| Resume state | Signal | Jump to |
| --- | --- | --- |
| **None** | No `[Issue M]` issue in fork | Phase 1 (fresh) |
| **Triaged, no design** | Notes exist but no converged `## Fix design` | Phase 2 (investigate) |
| **Design drafted, not converged** | A design exists but the last adversary pass had open objections | Phase 3/4 (resume the loop) |
| **Design converged, mirror written** | Mirror issue body has a `## Fix design` marked converged | Phase 6 (design-approval gate) |
| **Design approved** | User already approved (dashboard/`approvals.json` or prior turn) | Hand off to `powertoys-design-to-pr` |

---

## Phase 1 — Triage the upstream issue

Reuse `powertoys-design-to-pr` Phase 1 verbatim (pull the issue + full context; run the red-flag checklist: already-linked PR, duplicate, someone assigned/"I'm working on this", closed/by-design, `Needs-Design`/feature, hardware/external-service scope).

- **Clear (no red flags):** state "Clear to design" and continue to Phase 2.
- **Red flags:** summarize them and **stop** (`ask_user`) before investigating. Bugs only — never design a feature.

Capture the issue's acceptance criteria (expected vs actual behavior) — the adversary will check the root cause against these.

---

## Phase 2 — Investigator pass (root cause + fix plan)

Produce an inferred **root cause** and a concrete **fix plan**, grounded in the actual code and the issue's evidence.

### 2a. Gather evidence

- Pull the issue body + comments (`gh issue view M --repo microsoft/PowerToys --json body,comments`).
- **Download and analyze any attachments** (diagnostic bundle `PowerToysReport_*.zip`, logs, screenshots, repro files) — grep the issue/comment JSON for `user-attachments` URLs and `Invoke-WebRequest` them. These usually pin the real root cause; without them you are guessing.

### 2b. Investigate

Drive an **investigator** working thread over the local clone (`<CLONE_PATH>`). Prefer delegating the heavy code-reading to a sub-agent (the `task` tool's `explore` or `general-purpose` agent, or code-intelligence search) so it can range over the codebase with its own context, then bring back findings. The investigator must output:

- **Inferred root cause** — the specific mechanism (component, file(s)/area, and *why* the bug happens), tied to evidence (log line, code path, stack).
- **Evidence ledger** — concrete issue statements, log/stack evidence, and code
  observations. Mark each item as observed or inferred.
- **Affected files** — exact repository-relative paths, each file's role, and
  exact relevant classes/functions/symbols.
- **Implementation steps** — an ordered plan where every step identifies the
  file and symbol, explains current and new control/data flow, includes a
  focused pseudo-diff or code-block sketch for the key logic, and calls out
  error handling, threading/lifetime/state concerns, edge cases, and tests.
- **How to verify** — the e2e steps that would confirm the fix (launch path, trigger, expected result) and, where possible, how to reproduce the bug first.
- **Build/test commands** — the narrowest existing PowerToys commands that
  cover the affected module and tests. Do not invent a command when it cannot
  be verified; state what must be discovered during implementation.
- **Risks and alternatives** — blast radius, compatibility/migration concerns,
  and why plausible alternatives were rejected.
- **Confidence** — High/Medium/Low that this root cause is correct.

Keep these as a structured **design draft** (you will store it in the mirror
issue in Phase 5). “Change X to handle Y” is not sufficient. Another engineer
must be able to locate and implement the key change without repeating the
investigation. The code sketch is design guidance, not an apply-ready patch.

---

## Phase 3 — Adversary pass (independent critique)

Run a **separate** adversary thread that did NOT produce the design, so it reasons independently. Prefer the `task` tool's `rubber-duck` or `code-review` agent, given the issue text + acceptance criteria + the investigator's design draft. Its job is to find blocking problems, specifically judging:

1. **Does the root cause actually match the reported issue?** Could the described symptom occur even after this "cause" is removed? Is the evidence consistent, or is the investigator anchoring on a plausible-but-wrong mechanism? Are there alternative root causes not ruled out?
2. **Is the fix plan sound?** Does it address the root cause (not just the symptom)? Missing edge cases, regressions, wrong layer, incomplete coverage, or a simpler/correct-er approach? Are the verify steps sufficient to prove it?
3. **Is it implementation-ready?** Are exact files and symbols identified?
   Does every key step explain current/new flow and show the core code shape?
   Are tests, errors, state/lifetime/threading, risks, and alternatives covered?
   If an implementer would need to rediscover the design, raise a blocking
   objection.

The adversary returns a list of **objections**, each tagged **blocking** (must resolve) or **non-blocking** (note it). If it has none, it says "no blocking objections."

---

## Phase 4 — Iterate the loop until converged

Loop Phase 2 (investigator) ↔ Phase 3 (adversary):

1. Feed the adversary's **blocking** objections back to the investigator; it revises the root cause and/or fix plan (re-reading code/evidence as needed).
2. Re-run the adversary on the revised design.
3. Repeat until the adversary reports **no blocking objections** → the design is **converged**.

Guardrails:
- **Cap rounds** (default 4). If not converged after the cap, stop and present the current design plus the unresolved objections to the user — do not loop forever.
- Track `rounds` and keep the adversary's final verdict + any non-blocking notes — these surface on the dashboard.
- If the adversary keeps finding the root cause unproven because evidence is missing (e.g. no logs), say so: the honest outcome may be "needs more info / not confidently designable," which is a valid stop (report it; don't fabricate a root cause).

---

## Phase 5 — Write the design into the fork mirror issue

Create (or update, on resume) the fork mirror issue carrying the sanitized original report **and** the converged design.

### 5a. Compose the mirror issue

- **Title:** `[Issue M] <original title>` (bracketed plain number — never `#M`).
- **Body:** sanitize the original (replace every `#<n>` / URL / "closes #n" with plain `Issue <n>` / `PR <n>`), then append the design:

  ```markdown
  > Mirrored from a PowerToys issue for AI-assisted fixing. Upstream reference: Issue M (plain text, intentionally not linked).

  ## Original report
  <sanitized original body>

  ## Key details from the discussion
  - <repro, expected vs actual, environment, maintainer guidance>

  ## Fix design  (converged after <rounds> adversary rounds)
  ### Inferred root cause
  <the mechanism, tied to evidence>
  ### Evidence
  - [Observed|Inferred] <issue/log/code evidence>
  ### Affected files and symbols
  - `src/.../File.cpp` — <role>; symbols: `Type::Method`, `Helper`
  ### Implementation steps
  1. **`src/.../File.cpp` — `Type::Method`**
     - Current flow: <what happens now>
     - Change: <new behavior and data/control flow>
     - Key code shape:
       ```text
       <focused pseudo-diff or code sketch>
       ```
     - Edge/error/state handling: <details>
     - Tests: <tests proving this step>
  ### How to verify
  - Build/test: `<verified command or explicit discovery requirement>`
  1. <repro the bug>  2. <apply/observe>  3. <expected result>
  ### Risks and alternatives
  - Risks: <blast radius, compatibility, migration>
  - Alternatives considered: <option and why rejected>
  ### Confidence
  <High/Medium/Low> — <one-line rationale>
  ### Adversary sign-off
  No blocking objections after <rounds> rounds. Non-blocking notes: <…/none>.

  ## Task for Copilot
  Implement the fix plan above. Diagnose from the evidence; keep the change atomic and buildable.
  ```

Re-host any diagnostic attachments as fork **release assets** and link them in the body (same technique as the old mirror step) so the coding agent can fetch them later.

### 5b. Create/update it

```powershell
$issueUrl = gh issue create --repo <FORK_REPO> --title "[Issue M] <title>" --body-file <design-body-file>
$F = ($issueUrl -split '/')[-1]     # forked issue number; on resume, gh issue edit instead
```

Record the **forked issue number `F`** and node id — `powertoys-design-to-pr` starts from here.

### 5c. Return the dashboard handoff

When this skill is invoked by `powertoys-dashboard-update`, return the same
design as structured data, not only Markdown. The orchestrator writes it to
`data/items/M.json` with:

- `evaluated_at` and the upstream `source_updated_at` covered;
- the prior fast `judgment`;
- `design.root_cause`, `design.evidence`, `design.affected_files`,
  `design.implementation_steps`, `design.verify`, `design.risks`, and
  `design.alternatives`;
- mirror issue, adversary rounds/sign-off, confidence, and approval actions.

Do not collapse the structured fields back into one `fix_plan` paragraph.

---

## Phase 6 — Design-approval gate (MANDATORY STOP)

Present the converged design and **stop** for approval. This is the key new checkpoint: the user reviews the **root cause + fix plan** before any code is written.

Show:
- **Inferred root cause** and **fix plan** (the crux),
- **how-to-verify** steps and **confidence** + rationale,
- **adversary sign-off** (rounds + any non-blocking notes),
- the **fork mirror issue link** (`https://github.com/<FORK_REPO>/issues/F`) — the design is public there.

Approval can arrive two ways:
- **Dashboard:** the design surfaces on the triage board's public layer (root cause, fix plan, adversary status) with an **Approve design** button; the exported `approvals.json` carries an `approve_design` decision that the daily skill consumes.
- **Inline:** ask via `ask_user`: *"Approve this fix design for Issue M so I can build the PR, or do you have changes?"*

On **changes requested**, feed them in as additional adversary objections and re-loop (Phase 4), then re-write the mirror (Phase 5) and re-brief.

On **approval**, hand off to **`powertoys-design-to-pr`** for Issue M (it resumes from the design-bearing mirror issue and assigns the coding agent). Do not proceed to code here.

---

## Critical Rules (summary)

1. **Always run Phase 0 first:** sync the fork's `main` and check for a prior design/mirror for Issue M so you resume instead of duplicating.
2. **Design only — no code, no PR, no coding-agent assignment here.** That is `powertoys-design-to-pr`, and only after the Phase 6 design approval.
3. **Independent adversary.** The design converges only when a separate adversary agent — not the investigator — has no blocking objection to the root cause or the fix plan. Cap the loop (default 4 rounds) and report honestly if it doesn't converge.
4. **Evidence-driven root cause.** Pull and analyze upstream attachments/logs before concluding; never fabricate a root cause to satisfy the loop.
5. **Never** emit `#M` / `microsoft/PowerToys#M` / issue URL / "closes #M" anywhere. Use plain `Issue M`. The design lives only on the fork.
6. **Stop at the design-approval gate (Phase 6).** The user approves the root cause + fix plan (dashboard or inline) before `powertoys-design-to-pr` writes any code.
7. **Bugs only** — never design a feature. Triage red flags pause the skill (Phase 1).
8. **The design is public-safe** (fork-only, plain-text) and may be shown in full on the dashboard's public layer.
