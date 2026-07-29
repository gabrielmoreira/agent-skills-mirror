---
name: cherry-pick-pro
description: Cherry-pick commits from chatbox-pro repo to the open chatbox repo, handling mobile-only files, package name differences, and other repo-specific exclusions.
user_invocable: true
read_when:
  - Cherry-picking from pro to open repo
  - Syncing pro commits to open source repo
  - Releasing open source version
---

# Cherry Pick Pro

Cherry-pick commits from the `chatbox-pro` repo (`pro` remote) to the open `chatbox` repo, filtering out mobile-only changes and adjusting for repo differences.

## Usage

```
/cherry-pick-pro [from_commit] [to_commit]
```

- `from_commit`: (optional) A **`pro/main` commit hash** to start from (exclusive). Must be a commit on `pro/main`, not an open-repo commit — see step 2. Defaults to auto-detecting the last synced pro commit.
- `to_commit`: (optional) The commit hash to end at (inclusive). Defaults to `pro/main` HEAD.

## Workflow

### 1. Sync remotes first
```bash
git fetch pro
git fetch origin
```

⚠️ **Tag pollution**: `git fetch pro` also fetches pro's tags (e.g. `vX.Y.Z` created on pro's release branch). These local tags point at **pro commits**, not open repo commits. Never push them as-is — see step 8.

### 2. Identify commits to cherry-pick

⚠️ The range bound **must be a `pro/main` commit**. The open repo and `pro/main` share no history (cherry-picks create new SHAs), so an open-repo commit hash as the lower bound makes `A..pro/main` return *all* of pro's history, not the increment.

Find the last synced pro commit by reading the `cherry picked from pro commit <hash>` footer that step 5 writes into each open-repo commit, then list pro commits after it:
```bash
# last synced pro commit (the lower bound)
last=$(git log --grep="cherry picked from pro commit" -1 --pretty=%B HEAD \
  | grep -oE 'pro commit [0-9a-f]+' | awk '{print $3}')
git log "$last"..pro/main --oneline --reverse  # commits to pick
```
If no footer is found (first-ever sync), pass `from_commit` explicitly.

### 3. Analyze each commit
For each commit, check the files it touches:
```bash
git diff-tree --no-commit-id --name-only -r <commit>
```

### 4. Cherry-pick rules

#### Files/directories to SKIP (delete if conflict):
- `android/` - mobile-only, not in open repo
- `ios/` - mobile-only, not in open repo
- `capacitor.config.ts` - mobile config
- `.github/` - open repo has no CI; workflow/config differs (see step 8)
- `CLAUDE.md`, `AGENTS.md` - pro-specific AI config
- `.cursorrules` - pro-specific
- `.claude/` - pro-specific skills/config (including this skill itself), never sync to open repo

#### Package name differences:
- Pro uses: `xyz.chatboxapp.app`
- Open uses: `xyz.chatboxapp.ce`
- When resolving conflicts in `package.json` or `release/app/package.json`, always keep the open repo name (`xyz.chatboxapp.ce`)

#### Pro-only dependencies to remove if added:
- `@playwright/test` - pro testing only
- `playwright` - pro testing only
- `@ruguoapp/jk-analytics` - pro analytics only

#### `pnpm-lock.yaml`:
- Will almost always conflict. Accept either side, then run `pnpm install --no-frozen-lockfile` at the end to regenerate.

### 5. Cherry-pick process
For each commit:
1. Try `git cherry-pick <hash>` directly first
2. If conflicts occur, use `--no-commit` and resolve:
   - Remove mobile-only files with `git rm`
   - Fix package name conflicts (keep `ce`)
   - Remove pro-only dependencies
   - Accept either side for `pnpm-lock.yaml`
3. Commit with original message + `(cherry picked from pro commit <hash>)` note

### 6. Finalize
After all cherry-picks:
```bash
pnpm install --no-frozen-lockfile  # regenerate lockfile
git add pnpm-lock.yaml
git commit -m "chore: regenerate pnpm-lock.yaml for open repo"
```

### 7. Verify
```bash
git log --oneline <start>..HEAD  # review all new commits
pnpm install  # ensure deps resolve
```

### 8. Release (if syncing a version release)

The open repo has **no CI workflows** — releases are manual:

1. Push the sync branch to `origin/main`
2. Re-create the version tag on the **open repo's** commit. The local tag fetched from pro points at a pro commit — pushing it would leak pro's commit history into the open repo:
   ```bash
   git tag -d vX.Y.Z                 # delete pro's tag fetched in step 1
   git tag vX.Y.Z <open-repo-head>   # re-create on open repo commit
   git push origin vX.Y.Z
   ```
3. Create the GitHub Release manually (no binary assets; notes = changelog + install links, copy format from the previous release):
   ```bash
   gh release view vX.Y.(Z-1) --json body --jq '.body'  # get template
   gh release create vX.Y.Z --title "vX.Y.Z" --latest --notes "..."
   ```

Version bump convention: only `release/app/package.json` gets the new version; root `package.json` stays `0.0.1` in the open repo.

## Example

```
/cherry-pick-pro
```
This will auto-detect the last release on the current branch and cherry-pick all newer commits from `pro/main`.
