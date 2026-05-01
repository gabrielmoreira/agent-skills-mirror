---
description: "Pull the latest Edition into this heir — apply directly, summarize, surface notable changes"
mode: agent
lastReviewed: 2026-04-30
---

# Upgrade

Run `upgrade-self.cjs --apply` and report what changed. The script is non-destructive (heir-owned files are preserved, no commits, major bumps require explicit `--allow-major`), so dry-run-then-confirm adds friction without safety. Apply, then summarize.

## Steps

1. **Verify heir** — confirm `.github/.act-heir.json` exists. If not, refuse and suggest bootstrap.

2. **Apply** — execute directly:

   ```bash
   node .github/scripts/upgrade-self.cjs --apply
   ```

   Capture stdout/stderr.

3. **If the script refuses** — handle the two known cases:
   - **Major bump**: stop, surface the version jump (e.g., `0.x → 1.x`), and ask the user if they want to re-run with `--allow-major`. Do NOT add `--allow-major` automatically.
   - **Refusal for any other reason** (downgrade, missing marker, etc.): stop and surface the script's error.

4. **Summarize the change** in plain English. Group by category:
   - **Instructions**: N changed, M new, K deleted
   - **Skills**: …
   - **Prompts**: …
   - **Muscles**: …
   - **Scripts** (`upgrade-self.cjs`, `bootstrap-heir.cjs`): if changed, flag as **mechanical changes** — usually safe but worth noting
   - **Version bump**: current → new

5. **Surface anything notable**:
   - Files that were deleted (heir-owned files should NEVER appear here — if they do, it's a bug, raise it)
   - Files under `local/` paths in the change list (heir-owned should be untouched — flag as bug)
   - New instructions whose `applyTo` matches files this heir actually has — mention them so the user knows new behaviors are now active

6. **Stage but do NOT commit** — show `git status` and let the user pick the commit message. Suggest: `chore: sync to Alex_ACT_Edition vX.Y.Z`.

## Refuse if

- The change list shows files under `.github/skills/local/`, `.github/instructions/local/`, `.github/muscles/local/`, or `.github/prompts/local/` being changed — that's an Edition bug, not an upgrade
- `.github/.act-heir.json` would be overwritten (it's heir-owned)
- Major bump without explicit user consent (the script enforces this; don't bypass it)

## Why apply-first instead of dry-run-then-confirm?

The script's own safeguards (heir-owned preservation, no git operations, major-bump gate, downgrade refusal) already make it safe. The previous flow ran the script twice — once to preview, once to apply — to confirm changes the user almost always wanted. Apply directly, then summarize. If the user disagrees with what landed, `git checkout -- .github/` is one command away (nothing is committed yet).
