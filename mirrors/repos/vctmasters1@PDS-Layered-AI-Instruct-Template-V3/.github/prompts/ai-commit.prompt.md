---
mode: agent
description: Pre-commit hygiene — refresh Last Updated dates, run the validator, draft a conventional-commit message, optionally push.
---

# /ai-commit

Stage-aware commit assistant for this template. Enforces date hygiene, validates the AI-INSTRUCT system, drafts a Conventional Commits message, and (only with explicit user consent) pushes.

This command is conservative by design:
- **Never** uses `--no-verify`.
- **Never** uses `git push --force`, `--force-with-lease`, or amend on already-pushed commits.
- **Never** commits files the user did not stage.

## Steps

### 1. Inspect staged state

Run:

```
git status --porcelain=v1
git diff --cached --stat
```

If nothing is staged: stop and tell the user "Nothing staged — stage your changes first, then re-run `/ai-commit`." Do **not** run `git add` on the user's behalf.

### 2. Refresh `Last Updated` on staged instruction files

For each staged file matching any of:

- `.ai/*.md`
- `**/.ai/*.md`
- `.github/copilot-instructions.md`
- `.ai/instruct.md`

read the file. If line 4ish contains `**Last Updated**:` and the date is **not** today (use the host system date; ask for it if unsure), update it to today's date in `YYYY-MM-DD` form. Then re-stage that file.

This mirrors the auto-date rule in [.ai/conventions.md](../../.ai/conventions.md#versioning).

### 3. Detect structural/template changes

If any staged path is one of:

- `.github/copilot-instructions.md`
- `.github/prompts/*.prompt.md`
- `.github/agents/*.agent.md`
- `.github/skills/**/SKILL.md`
- `.github/scripts/validate-instructions.ps1`
- `.ai/conventions.md`
- `.ai/maintenance.md`
- `.ai/credentials.md`

ask the user: "This touches template infrastructure. Bump `Template Version` in `.github/copilot-instructions.md` and cut a `CHANGELOG.md` release block? (recommended)" — then:

- If yes, propose a new version (patch / minor / major based on diff scope; default = minor for feature additions, patch for fixes).
- Update `Template Version: V<old>` to `V<new>` in [.github/copilot-instructions.md](../copilot-instructions.md).
- In [CHANGELOG.md](../../CHANGELOG.md): rename the `## [Unreleased]` heading to `## [<new>] — <today>` and insert a fresh empty `## [Unreleased]` block above it. Generate Added / Changed / Fixed bullets from the diff summary.
- Re-stage these files.

### 4. Validate

Invoke `/ai-validate` (or run the validator directly). If validation fails, stop and ask the user to fix or override. Never bypass.

### 5. Draft a Conventional Commits message

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<optional scope>): <imperative summary, ≤72 chars>

<optional body — what & why, wrapped at ~72 cols>
```

Choose `<type>` from the diff content:

| Type | Use when |
|------|----------|
| `feat` | New capability added (new prompt, agent, skill, module, feature) |
| `fix` | Bug or broken link / reference corrected |
| `docs` | Documentation-only changes (README, CHANGELOG, comments) |
| `chore` | Tooling, config, dependency, or cleanup with no behavior change |
| `refactor` | Code/structure reorganization without behavior change |
| `test` | Test-only additions or changes |
| `ci` | CI/hook/automation changes |

If unclear, ask the user to pick.

### 6. Confirm with the user

Present the drafted message and ask:

1. **Commit only**
2. **Commit and push** (requires upstream branch to exist; if it doesn't, ask for the remote/branch first)
3. **Cancel**

Wait for an explicit choice.

### 7. Execute

- **Commit only**: `git commit -m "<subject>" -m "<body>"`.
- **Commit and push**: commit as above, then `git push` (plain, no force flags). If push is rejected for non-fast-forward, **stop** and report — do **not** suggest force-push. Recommend `git pull --rebase` and re-running `/ai-commit`.

### 8. Report

Print the commit hash and (if pushed) the remote ref.

## Failure modes — what to do

- **Validator failed**: stop. Show the user the failing checks and exit. Do not commit.
- **No staged changes after step 2**: tell the user nothing new to commit (date refresh may have produced no diff).
- **Push rejected**: stop. Do not retry, do not force. Recommend rebase or merge.
- **Pre-commit hook blocked the commit**: relay the hook output. Do not bypass.
