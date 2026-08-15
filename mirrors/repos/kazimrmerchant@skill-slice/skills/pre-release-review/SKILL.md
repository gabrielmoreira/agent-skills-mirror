---
name: pre-release-review
description: "Runs a read-only go-live review of deploy readiness: migrations, config, secrets redaction, rollout order, rollback risk, and launch blockers, producing a prioritized report. Use when the user asks for a release audit before tagging or deploying. Not for executing migrations, deploying, tagging, or editing release files; never dump live secret values into the report."
version: 1.0.1
category: operations
risk: safe
source: community
source_repo: chaunsin/agent-skills
source_type: community
date_added: "2026-06-29"
tags: [release, deploy-readiness, ci-cd, rollback, production]
tools: [git, gh, rg]
license: "Apache-2.0"
license_source: "https://github.com/chaunsin/agent-skills/blob/master/LICENSE"
---

# Pre-release Review

Run a **read-only** production release readiness review. The goal is to reduce release time and
coordination failures by finding missing deploy materials, unsafe ordering, configuration gaps,
data migration gaps, and ambiguous production risks **before** CI/CD or manual release steps begin.

This skill never mutates source code, configs, migrations, secrets, deployment files, or remote
infrastructure. It produces a concise, prioritized report of confirmed problems and plausible
risks that need confirmation.

## When to Use

- The user asks for a **release audit**, **pre-release review**, **go-live review**, or **deploy readiness check**.
- Before publishing a tag, deploying production services, or merging a release branch.
- A PR or git range may include migrations, environment changes, queues, cache behavior, object
  storage assets, or service contract changes.
- The user asks whether a change is safe to ship and needs a read-only risk report.

## Prerequisites

- **Git** available on `PATH`.
- **`gh` CLI** (optional) — used only when available and authenticated for PR diffs. If missing or
  unauthenticated, fall back to local branch/patch/explicit git range. Do not invent PR contents.
- **`rg` (ripgrep)** — used for pattern-based evidence collection.
- **Windows host (PowerShell)** is the primary environment. Commands below use POSIX-style flags
  that work in PowerShell when wrapped in double quotes or passed via `git`/`rg` directly. On
  Windows, prefer quoting arguments containing `<..>` ranges with double quotes, e.g.
  `git diff --stat "v1.2.3..HEAD"`.

## Non-negotiable Rules

- **Do not modify** source code, configs, migrations, secrets, deployment files, or generated files.
- **Do not execute** migrations, clear or warm caches, upload assets, trigger CI/CD, deploy
  services, publish tags, rotate secrets, or change remote infrastructure.
- Produce a **concise report** that lists only confirmed problems and plausible risks needing
  confirmation. Do not bury the reader in clean checklist items.
- **Sort findings** from highest to lowest priority (P0 → P1 → P2).
- For each finding include: **module, finding, evidence, inferred owner, risk, recommended action**.
- **Never reveal** private keys, account passwords, tokens, certificates, cookies, or full secret
  values. Report only: file path, line number, variable name, secret type, and a redacted hint.
- If evidence is incomplete but the risk could block production, list it as a **confirmation item**.

## Required References

Load these reference files at specific points in the workflow:

| Reference file | When to load |
|---|---|
| `references/checklist.md` | **Before analyzing findings** — ensures important release domains (migrations, config, cache, queues, assets, contracts) are not skipped. |
| `references/report-template.md` | **Before writing the final report** — keeps priorities, owner inference, secret redaction, and output shape consistent. |

If a reference file is missing, note the limitation in the report's "Unable To Verify" section
only when it affects the release review.

## Project Guidance Discovery

Before interpreting the release diff, look for project-local guidance files such as `AGENTS.md`
and `CLAUDE.md` in the repository root and relevant service directories.

- Read them when present so the review respects project-specific conventions, service boundaries,
  release rules, validation expectations, ownership hints, and known operational constraints.
- Treat project guidance as **context** for how to interpret risks, not as permission to perform
  mutating release actions.
- If project guidance conflicts with this skill's non-negotiable safety rules, the **read-only,
  no-secret-disclosure rules in this skill win**.
- If a relevant guidance file cannot be read, note the limitation in "Unable To Verify" only when
  it affects the release review.

## Procedure

### Step 1 — Determine the Review Scope

State the chosen range in the report.

1. **PR provided** (URL or number): review that PR diff first.
   - If `gh` is available and authenticated, use read-only commands:
     ```powershell
     gh pr view <PR_NUMBER>
     gh pr diff <PR_NUMBER>
     ```
   - If the PR cannot be fetched (missing tooling, auth, or network), say so and ask for a local
     branch, patch, or explicit git range. **Do not invent the PR contents.**
2. **Explicit `base..head` range provided**: use it directly.
3. **Only a head commit provided**: compare the previous usable release tag reachable from that
   commit to the head commit.
4. **No scope provided**: compare the previous usable release tag to `HEAD`.
5. **Choosing the previous usable release tag**:
   - Prefer the repository's visible release-tag convention when obvious (semantic versions,
     `v*`, or `release-*`). If tag naming is mixed, state the assumption.
   - If `HEAD` is exactly at one or more tags, treat those as the current release point and compare
     against the **earlier** reachable release tag, not `HEAD`'s own tag.
   - If **no usable previous release tag exists**, review the latest **5 commits** and explicitly
     warn: *"No usable previous release tag found; audit only covers the latest 5 commits.
     Recommend a PR or tag-based range for future reviews."*

### Step 2 — Read-Only Evidence Collection

Run only safe inspection commands, adjusted to the repository and current permissions.

```powershell
git status --short
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
rg --files -g "AGENTS.md" -g "CLAUDE.md"
git tag --merged HEAD --sort=-creatordate
git tag --points-at HEAD
git for-each-ref --sort=-creatordate --format="%(refname:short) %(objectname:short)" refs/tags
git describe --tags --abbrev=0 HEAD
git diff --name-status "<base>..<head>"
git diff --stat "<base>..<head>"
git log --oneline --decorate --no-merges "<base>..<head>"
git diff -U3 "<base>..<head>" -- "<path>"
git blame -L "<start>,<end>" -- "<path>"
git log --format="%h %an %s" -- "<path>"
rg -n "<pattern>" .
```

For PRs, use `gh pr view` and `gh pr diff` only when available and allowed. Do not bypass network,
auth, sandbox, or approval restrictions. If a command cannot run, record the limitation in the
report's "Unable To Verify" section.

### Step 3 — Review Workflow

1. Confirm the git repository root, current branch, dirty state, and selected comparison range.
2. Collect changed file names, file status, diff stats, commit summaries, and touched services.
3. Inspect relevant diffs rather than relying on filenames alone.
4. Load `references/checklist.md` and map changed code to production requirements:
   - **Schema changes** → migrations, indexes, seeds, and backfills.
   - **Config reads** → env examples, deploy secrets, flags, and runtime config.
   - **Cache key or TTL changes** → invalidation, prewarm, and compatibility work.
   - **Queue producers/consumers** → topic setup, DLQ, idempotency, and deploy order.
   - **Asset references** → object storage, CDN, templates, certificates, and permissions.
   - **Service contract changes** → deploy sequence, backward compatibility, and rollback risk.
5. Infer owners with `git blame` on changed lines when possible; otherwise use recent `git log`
   authors for the file or commit. Label them as **inferred owners** and **do not include email
   addresses**.
6. Classify each finding as **P0**, **P1**, or **P2** using `references/report-template.md`.
7. Write the final report in the user's language when practical. Keep conclusion values exactly as
   `BLOCKED`, `NEEDS_CONFIRMATION`, or `NO_BLOCKER_FOUND`.

### Step 4 — Dirty Worktree Handling

By default, review only the selected committed range. Do not silently mix uncommitted or
untracked changes into the release diff unless the user explicitly asks to include worktree
changes.

- **Always report** whether the worktree is dirty.
- If dirty or untracked files touch release-relevant areas (migrations, deployment config, env
  examples, CI/CD, secrets, cache, queues, assets, or service contracts), add a **P2 confirmation
  item** saying those changes are excluded from the committed-range review and must be committed,
  discarded, or reviewed separately before release.
- If the user explicitly asks to include dirty worktree changes, inspect them with read-only
  commands such as `git diff` and `git diff --name-status`, and clearly label them as
  **uncommitted evidence**.

### Step 5 — Evidence Expectations

Every finding should cite concrete evidence:

- File path and line number when available.
- Commit hash or PR reference when line evidence is not enough.
- Command limitation when evidence could not be collected.
- Diff relationship, e.g. *"schema changed but no migration file changed"*.

Do not state that something is safe just because no file matched a pattern. Use **"not verified"**
for areas that cannot be confirmed from local repository evidence.

### Step 6 — Findings vs. Verification Limits

Separate release confirmation items from neutral tool limits:

- A **release confirmation item** is a diff-linked production risk — e.g. a new env var whose
  production secret cannot be verified, a schema change with unclear migration status, or a new
  queue whose infrastructure cannot be confirmed. Classify as P1 or P2 and set conclusion to
  `NEEDS_CONFIRMATION` unless a P0 also exists.
- An **"Unable To Verify"** entry is a neutral limitation — e.g. missing remote access or
  deployment platform credentials when the diff does not introduce a specific release requirement.
  Neutral limitations do not change the conclusion by themselves.
- If a limitation blocks confirmation of a release-critical diff change, **promote it** to a
  P1/P2 finding rather than leaving it only in "Unable To Verify".
- Use `NO_BLOCKER_FOUND` only when no P0–P2 findings or release confirmation items were found from
  available evidence. The report may still include neutral verification limits.

### Step 7 — Output Rules

- Show **P0 and P1** findings first, then **P2** confirmation items.
- **Do not list** clean checklist categories.
- Include a **service deployment order** section only when the diff touches multiple services,
  asynchronous workers, migrations, queues, cache, or public contracts.
- If no P0 blocker is found but P1/P2 confirmation items remain, use `NEEDS_CONFIRMATION`.
- If no P0–P2 findings exist, include the reviewed range and any neutral verification limits.
- Keep the report short enough for a release manager to act on immediately.

## Pitfalls

- **Mixing uncommitted changes into the release diff** — always state whether the worktree is
  dirty and exclude uncommitted changes by default.
- **Inventing PR contents** when `gh` is unavailable — never fabricate diff content; ask for a
  local branch or explicit range instead.
- **Disclosing secrets in the report** — report only file path, line number, variable name, secret
  type, and a redacted hint. Never include full values.
- **Claiming safety from absence of matches** — "no file matched a pattern" is not proof of
  safety; use "not verified" instead.
- **Treating project guidance as permission to mutate** — `AGENTS.md`/`CLAUDE.md` are context only;
  this skill's read-only rules always win.
- **Leaving release-critical limitations as neutral** — if a limitation blocks confirmation of a
  release-critical diff change, promote it to P1/P2.
- **Burying the reader in clean checklist items** — the report lists only confirmed problems and
  plausible risks, not a full pass/fail checklist.
- **Including email addresses in inferred owners** — label as inferred owners and omit emails.

## Verification

After running the review, verify the skill executed correctly:

1. **Confirm read-only compliance** — no files were modified:
   ```powershell
   git status --short
   ```
   Expected: same dirty/clean state as before the review (no new changes introduced by the skill).

2. **Confirm scope was stated** — the report should explicitly name the reviewed range (e.g.
   `v1.2.3..HEAD`, PR #123, or "latest 5 commits — no usable previous release tag").

3. **Confirm conclusion value** — the report's conclusion must be exactly one of:
   - `BLOCKED` — a P0 finding exists.
   - `NEEDS_CONFIRMATION` — P1/P2 items remain but no P0.
   - `NO_BLOCKER_FOUND` — no P0–P2 findings or confirmation items.

4. **Confirm secret redaction** — search the report output for any token-like strings:
   ```powershell
   rg -n "(?i)(api_key|secret|password|token|private_key)\s*[:=]\s*\S+" .
   ```
   Expected: no full secret values in the report; only redacted hints.

5. **Confirm reference files were loaded** — the report should reflect domains from
   `references/checklist.md` and follow the shape from `references/report-template.md`.

## Limitations

- This skill is **read-only** and does not deploy, tag, publish, run migrations, rotate secrets,
  or change infrastructure.
- It can identify release risks from available evidence, but **cannot prove production state**
  without access to the relevant deployment, secrets, database, queue, cache, or observability
  systems.
- It should **not replace service-owner signoff** for high-risk production changes.

## Examples

### Test Prompts

Use these prompts to validate skill behavior:

- *"Run a pre-release review and tell me if this production deploy has risks."*
- *"Review PR #123 before release. Check migrations, configs, and cache work."*
- *"This repo has no tags. Use the default strategy and audit release readiness."*
- *"Check `v1.2.3..HEAD` for backend go-live blockers."*

### Report Conclusion Values

| Conclusion | Meaning |
|---|---|
| `BLOCKED` | A P0 finding exists; do not release until resolved. |
| `NEEDS_CONFIRMATION` | P1/P2 items remain; release may proceed with owner signoff. |
| `NO_BLOCKER_FOUND` | No P0–P2 findings or confirmation items from available evidence. |

## Related Skills

- **ci-cd-preflight** — validate CI/CD pipeline configuration before triggering a release.
- **migration-safety-check** — deep-dive into database migration safety and rollback plans.
- **secret-scan** — scan for leaked secrets in code and configuration files.
