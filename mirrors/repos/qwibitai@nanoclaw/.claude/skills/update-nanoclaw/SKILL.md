---
name: update-nanoclaw
description: Efficiently bring upstream NanoClaw updates into a customized install, with preview, selective cherry-pick, and low token usage.
---

# About

Your NanoClaw fork drifts from upstream as you customize it. This skill pulls upstream changes into your install without losing your modifications.

Run `/update-nanoclaw` in Claude Code.

## How it works

**Preflight**: checks for clean working tree (`git status --porcelain`). If `upstream` remote is missing, asks you for the URL (defaults to `https://github.com/nanocoai/nanoclaw.git`) and adds it. Detects the upstream branch name (`main` or `master`).

**Backup**: creates a timestamped backup branch and tag (`backup/pre-update-<hash>-<timestamp>`, `pre-update-<hash>-<timestamp>`) before touching anything. Safe to run multiple times.

**Preview**: runs `git log` and `git diff` against the merge base to show upstream changes since your last sync. Groups changed files into categories:
- **Skills** (`.claude/skills/`): unlikely to conflict unless you edited an upstream skill
- **Host source** (`src/`): may conflict if you modified the same files
- **Container** (`container/`): triggers container rebuild
- **Build/config** (`package.json`, `pnpm-lock.yaml`, `tsconfig*.json`): lockfile changes trigger dep install

**Update paths** (you pick one):
- `merge` (default): `git merge upstream/<branch>`. Resolves all conflicts in one pass.
- `cherry-pick`: `git cherry-pick <hashes>`. Pull in only the commits you want.
- `rebase`: `git rebase upstream/<branch>`. Linear history, but conflicts resolve per-commit.
- `abort`: just view the changelog, change nothing.

**Conflict preview**: before merging, runs a dry-run (`git merge --no-commit --no-ff`) to show which files would conflict. You can still abort at this point.

**Conflict resolution**: opens only conflicted files, resolves the conflict markers, keeps your local customizations intact.

**Validation**: runs `pnpm run build` and `pnpm test`. If container files changed, also runs the container typecheck and `./container/build.sh`.

**Breaking changes check**: after validation, reads CHANGELOG.md for any `[BREAKING]` entries introduced by the update and diffs `versions.json` for moved component pins. Each entry carries its migration path — a skill to run or a `docs/` page to follow (per CONTRIBUTING.md, "Breaking Changes") — and the skill walks you through them.

## Rollback

The backup tag is printed at the end of each run:
```
git reset --hard pre-update-<hash>-<timestamp>
```

Backup branch `backup/pre-update-<hash>-<timestamp>` also exists.

## Token usage

Only opens files with actual conflicts. Uses `git log`, `git diff`, and `git status` for everything else. Does not scan or refactor unrelated code.

---

# Goal
Help a user with a customized NanoClaw install safely incorporate upstream changes without a fresh reinstall and without blowing tokens.

# Operating principles
- Never proceed with a dirty working tree.
- Always create a rollback point (backup branch + tag) before touching anything.
- Prefer git-native operations (fetch, merge, cherry-pick). Do not manually rewrite files except conflict markers.
- Default to MERGE (one-pass conflict resolution). Offer REBASE as an explicit option.
- Keep token usage low: rely on `git status`, `git log`, `git diff`, and open only conflicted files.

# Step 0a: Refresh this skill first
The update process itself evolves, so run its newest version before doing anything else:
- Ensure the `upstream` remote exists (default `https://github.com/nanocoai/nanoclaw.git`) and fetch: `git fetch upstream --prune`. Detect the upstream branch (`main` or `master`).
- Refresh this skill from upstream: `git checkout upstream/<branch> -- .claude/skills/update-nanoclaw/`
- Re-read `.claude/skills/update-nanoclaw/SKILL.md`. If it changed, **follow the updated version from the top** instead of this one.

This is the only working-tree change expected before the preflight check; the full update commits it along with everything else.

# Step 0: Preflight (stop early if unsafe)
Run:
- `git status --porcelain`
If output is non-empty:
- Tell the user to commit or stash first, then stop.
- Exception: changes limited to `.claude/skills/update-nanoclaw/` are the Step 0a self-refresh — ignore those and proceed.

Confirm remotes:
- `git remote -v`
If `upstream` is missing:
- Ask the user for the upstream repo URL (default: `https://github.com/nanocoai/nanoclaw.git`).
- Add it: `git remote add upstream <user-provided-url>`
- Then: `git fetch upstream --prune`

Determine the upstream branch name:
- `git branch -r | grep upstream/`
- If `upstream/main` exists, use `main`.
- If only `upstream/master` exists, use `master`.
- Otherwise, ask the user which branch to use.
- Store this as UPSTREAM_BRANCH for all subsequent commands. Every command below that references `upstream/main` should use `upstream/$UPSTREAM_BRANCH` instead.

Fetch:
- `git fetch upstream --prune`

# Step 1: Create a safety net
Capture current state:
- `HASH=$(git rev-parse --short HEAD)`
- `TIMESTAMP=$(date +%Y%m%d-%H%M%S)`

Create backup branch and tag (using timestamp to avoid collisions on retry):
- `git branch backup/pre-update-$HASH-$TIMESTAMP`
- `git tag pre-update-$HASH-$TIMESTAMP`

Save the tag name for later reference in the summary and rollback instructions.

# Step 2: Preview what upstream changed (no edits yet)
Compute common base:
- `BASE=$(git merge-base HEAD upstream/$UPSTREAM_BRANCH)`

Show upstream commits since BASE:
- `git log --oneline $BASE..upstream/$UPSTREAM_BRANCH`

Show local commits since BASE (custom drift):
- `git log --oneline $BASE..HEAD`

Show file-level impact from upstream:
- `git diff --name-only $BASE..upstream/$UPSTREAM_BRANCH`

Bucket the upstream changed files:
- **Skills** (`.claude/skills/`): unlikely to conflict unless the user edited an upstream skill
- **Host source** (`src/`): may conflict if user modified the same files
- **Container** (`container/`): triggers container rebuild (+ typecheck if `agent-runner/src/` changed)
- **Build/config** (`package.json`, `pnpm-lock.yaml`, `tsconfig*.json`): lockfile changes trigger dep install
- **Other**: docs, tests, setup scripts, misc

**Large drift check:** If the upstream commit count and age suggest the user has a lot of catching up to do, mention that `/migrate-nanoclaw` might be a better fit — it extracts customizations and reapplies them on clean upstream instead of merging. Offer it as an option but don't push.

Present these buckets to the user and ask them to choose one path using AskUserQuestion:
- A) **Full update**: merge all upstream changes
- B) **Selective update**: cherry-pick specific upstream commits
- C) **Abort**: they only wanted the preview
- D) **Rebase mode**: advanced, linear history (warn: resolves conflicts per-commit)

If Abort: stop here.

# Step 3: Conflict preview (before committing anything)
If Full update or Rebase:
- Dry-run merge to preview conflicts. Run these as a single chained command so the abort always executes:
  ```
  git merge --no-commit --no-ff upstream/$UPSTREAM_BRANCH; git diff --name-only --diff-filter=U; git merge --abort
  ```
- If conflicts were listed: show them and ask user if they want to proceed.
- If no conflicts: tell user it is clean and proceed.

# Step 4A: Full update (MERGE, default)
Run:
- `git merge upstream/$UPSTREAM_BRANCH --no-edit`

If conflicts occur:
- Run `git status` and identify conflicted files.
- For each conflicted file:
  - Open the file.
  - Resolve only conflict markers.
  - Preserve intentional local customizations.
  - Incorporate upstream fixes/improvements.
  - Do not refactor surrounding code.
  - `git add <file>`
- When all resolved:
  - If merge did not auto-commit: `git commit --no-edit`

# Step 4B: Selective update (CHERRY-PICK)
If user chose Selective:
- Recompute BASE if needed: `BASE=$(git merge-base HEAD upstream/$UPSTREAM_BRANCH)`
- Show commit list again: `git log --oneline $BASE..upstream/$UPSTREAM_BRANCH`
- Ask user which commit hashes they want.
- Apply: `git cherry-pick <hash1> <hash2> ...`

If conflicts during cherry-pick:
- Resolve only conflict markers, then:
  - `git add <file>`
  - `git cherry-pick --continue`
If user wants to stop:
  - `git cherry-pick --abort`

# Step 4C: Rebase (only if user explicitly chose option D)
Run:
- `git rebase upstream/$UPSTREAM_BRANCH`

If conflicts:
- Resolve conflict markers only, then:
  - `git add <file>`
  - `git rebase --continue`
If it gets messy (more than 3 rounds of conflicts):
  - `git rebase --abort`
  - Recommend merge instead.

# Step 4.5: Install dependencies (if lockfiles changed)
Check if the merge changed any lockfiles or package manifests:
- `git diff <backup-tag-from-step-1>..HEAD --name-only | grep -E '^(pnpm-lock\.yaml|package\.json)$'`
  - If matched: `pnpm install`
- `git diff <backup-tag-from-step-1>..HEAD --name-only | grep -E '^container/agent-runner/(bun\.lock|package\.json)$'`
  - If matched AND `command -v bun` succeeds: `cd container/agent-runner && bun install`
  - If bun is not installed on the host, skip — container deps will be installed during `./container/build.sh`

Skip this step if neither lockfile changed.

# Step 5: Validation
Check which areas changed to determine what to validate:
- `CHANGED_FILES=$(git diff --name-only <backup-tag-from-step-1>..HEAD)`

**Host build** (always):
- `pnpm run build`
- `pnpm test` (do not fail the flow if tests are not configured)

**Container typecheck** (only if `container/agent-runner/src/` files are in CHANGED_FILES AND bun types are available):
- Check: `pnpm exec tsc -p container/agent-runner/tsconfig.json --noEmit`
- If this fails because bun types are missing (`Cannot find type definition file for 'bun'`), skip with a note — type errors will surface at container runtime instead

**Container image rebuild** (only if any `container/` files are in CHANGED_FILES):
- `./container/build.sh`

If build fails:
- Show the error.
- Only fix issues clearly caused by the merge (missing imports, type mismatches from merged code).
- Do not refactor unrelated code.
- If unclear, ask the user before making changes.

# Step 6: Breaking changes check
After validation succeeds, check if the update introduced any breaking changes.

Determine which CHANGELOG entries are new by diffing against the backup tag:
- `git diff <backup-tag-from-step-1>..HEAD -- CHANGELOG.md`

Parse the diff output for lines that contain `[BREAKING]` anywhere in the line. Each such line is one breaking change entry, and per CONTRIBUTING.md ("Breaking Changes") it references its migration path in one of two forms:
```
[BREAKING] <description>. Run `/<skill-name>` to <action>.
[BREAKING] <description>. **Migration:** follow [docs/<page>.md](docs/<page>.md) ...
```

Also diff the component version pins:
- `git diff <backup-tag-from-step-1>..HEAD -- versions.json`

Each changed pin is a breaking component update (e.g. `onecli-gateway` moving means the OneCLI gateway must be upgraded). Its migration path is the `[BREAKING]` CHANGELOG entry covering it; if no new entry mentions it, search `docs/` for the pin name (convention: `docs/<component>-upgrades.md`) and treat that doc as the migration path.

If no `[BREAKING]` lines are found and `versions.json` did not change:
- Skip this step silently. Proceed to Step 7 (skill updates check).

Otherwise:
- Display a warning header to the user: "This update includes breaking changes that may require action:"
- For each breaking change, display the full description (for a moved pin without its own entry: the component name, old → new version, and the doc that covers it).
- Use AskUserQuestion to ask the user which migrations to run now. Options:
  - One option per referenced skill (e.g., "Run /add-whatsapp to re-add WhatsApp channel")
  - One option per referenced doc (e.g., "Upgrade the OneCLI gateway (docs/onecli-upgrades.md)")
  - "Skip — I'll handle these manually"
- Set `multiSelect: true` so the user can pick multiple migrations if there are several breaking changes.
- For each skill the user selects, invoke it using the Skill tool.
- For each doc the user selects, read the doc and execute it top to bottom — these docs are written to be executed verbatim by a coding agent (detect → fix → verify → rollback). Stop and report if a verify step fails.
- After all selected migrations complete (or if user chose Skip), proceed to Step 7 (skill updates check).

# Step 7: Check for skill and channel/provider updates

## 7a: Skill branches
Check if skills are distributed as branches in this repo:
- `git branch -r --list 'upstream/skill/*'`

If any `upstream/skill/*` branches exist:
- Use AskUserQuestion to ask: "Upstream has skill branches. Would you like to check for skill updates?"
  - Option 1: "Yes, check for updates" (description: "Runs /update-skills to check for and apply skill branch updates")
  - Option 2: "No, skip" (description: "You can run /update-skills later any time")
- If user selects yes, invoke `/update-skills` using the Skill tool.

## 7b: Channel and provider updates
Detect installed channels by reading `src/channels/index.ts` and collecting all `import './<name>.js';` lines (excluding `cli`). For providers, check `src/providers/index.ts` the same way.

If any channels/providers are installed AND `upstream/channels` or `upstream/providers` branches exist:
- List the installed channels/providers.
- Use AskUserQuestion to ask: "Would you like to update your installed channels/providers? Re-running `/add-<name>` is safe — it only updates code files, credentials and wiring are untouched."
  - One option per installed channel/provider (e.g., "Update Slack (/add-slack)")
  - "Skip — I'll update them later"
  - Set `multiSelect: true`
- For each selected option, invoke the corresponding `/add-<channel>` or `/add-<provider>` skill.

If no channels/providers are installed, skip silently.

Proceed to Step 7.9.

# Step 7.9: Stamp the upgrade marker (required)
After validation has **succeeded**, record that this install reached the new version through the supported path. Without this, the startup tripwire stops the host on its next start.

- `pnpm exec tsx scripts/upgrade-state.ts set "" update-nanoclaw`
  - The empty version argument stamps the current `package.json` version.

If validation did NOT succeed, do not stamp — leave the tripwire to catch the broken state.

Proceed to Step 8.

# Step 8: Summary + rollback instructions
Show:
- Backup tag: the tag name created in Step 1
- New HEAD: `git rev-parse --short HEAD`
- Upstream HEAD: `git rev-parse --short upstream/$UPSTREAM_BRANCH`
- Conflicts resolved (list files, if any)
- Breaking changes applied (list skills run, if any)
- Remaining local diff vs upstream: `git diff --name-only upstream/$UPSTREAM_BRANCH..HEAD`

Tell the user:
- To rollback: `git reset --hard <backup-tag-from-step-1>`
- Backup branch also exists: `backup/pre-update-<HASH>-<TIMESTAMP>`
- Restart the service to apply changes. The unit/label names are per-install — derive them with `setup/lib/install-slug.sh`. Run from your NanoClaw project root:
  - **macOS (Darwin)**: `source setup/lib/install-slug.sh && launchctl kickstart -k gui/$(id -u)/$(launchd_label)`
  - **Linux**: `source setup/lib/install-slug.sh && systemctl --user restart $(systemd_unit)` (or, if you want to confirm the unit name first: `systemctl --user list-units --type=service | grep "$(. setup/lib/install-slug.sh && systemd_unit)"`)
  - **Manual** (no service found): restart `pnpm run dev`


## Diagnostics

1. Use the Read tool to read `.claude/skills/update-nanoclaw/diagnostics.md`.
2. Follow every step in that file before finishing.
