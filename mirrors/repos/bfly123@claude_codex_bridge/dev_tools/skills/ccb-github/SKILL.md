---
name: ccb-github
description: Maintain this CCB project's GitHub-facing release and npm publication surface. Use when preparing, publishing, auditing, or fixing CCB releases; updating README.md, README_zh.md, CHANGELOG.md, VERSION, package.json, GitHub release notes/assets, repository description/topics, npm registry state, or GitHub Actions release/test status.
---

# CCB GitHub Release Maintainer

## Core Rule

Treat GitHub as the user-facing product page. A release is not done until local version files, npm package metadata, both READMEs, changelog, GitHub Release, release assets, npm registry state, and Actions status all agree.

GitHub's repository homepage renders README from the default branch, not from the latest release tag. If release documentation is prepared on a feature or hotfix branch, merge that branch to the default branch before calling the homepage updated.

Use repository `SeemSeam/claude_codex_bridge` unless the user explicitly gives a different repo.

For CCB releases, npm publishing is part of the release surface by default. If `package.json`, npm wrapper scripts, README npm install snippets, or `.github/workflows/npm-publish.yml` are missing or stale during release preparation, create or repair them before the release commit and before creating or pushing the release tag. Do not create a tag first and add npm publish support in a later branch commit.

## Execution Contract

When the user asks for a final release or homepage result, do the git/GitHub work instead of only describing it:

1. Make the file edits, including npm package/workflow/docs auto-completion for release work.
2. Run the local checks.
3. Commit the changes.
4. Push the working branch.
5. Merge to the default branch when README/GitHub homepage state must change.
6. Push the default branch.
7. Create/push the release tag only after the intended release commit contains all required release and npm files, when package contents changed and the user asked for a release.
8. Create or update the GitHub Release page.
9. Wait for required GitHub Actions, release assets, and npm Trusted Publishing for npm-enabled releases.
10. Run the published checker and npm registry verification, then report the result.

Keep the checker read-only. Git writes, GitHub Release writes, workflow reruns, and tag operations are explicit agent actions done in the sequence above, not hidden inside the checker.

## Quick Audit

From the CCB repo root, run the bundled checker before and after release work:

```bash
CHECKER="dev_tools/skills/ccb-github/scripts/check_release_state.py"

python "$CHECKER" --phase prepare --repo SeemSeam/claude_codex_bridge
python "$CHECKER" --phase published --repo SeemSeam/claude_codex_bridge --wait-seconds 1800
```

The checker is read-only. It catches mechanical drift, but still manually inspect the top of `README.md` and `README_zh.md` because stale "What's New" prose can be semantically wrong even when version numbers are correct.

Use `--phase dev` for ordinary CCB development or maintainer tooling changes that are not intended to create a package release. Use `--wait-seconds 0` for lightweight commit/push work where the user did not ask to wait for GitHub Actions:

```bash
python "$CHECKER" --phase dev --repo SeemSeam/claude_codex_bridge --wait-seconds 0
```

`--phase dev` checks that the worktree is clean, the branch is pushed, and the change set is classified as development-only vs package/release-impacting. When `--wait-seconds` is greater than 0, it also waits for required GitHub workflows.

`--phase published` checks both release state and homepage state: GitHub latest release, release assets, `SHA256SUMS`, release workflows, branch validation workflows, and README/README_zh as rendered from the repository default branch. Use `--wait-seconds 1800` immediately after tagging so the checker waits for `Release Artifacts` and uploaded assets instead of reporting transient failures. The checker does not replace npm registry verification; for CCB releases, also verify `npm view @seemseam/ccb version dist-tags --json`.

## Decision Tree

- Before tagging: run `--phase prepare`; fix every FAIL before creating a tag. Also inspect the npm publication surface and auto-complete missing `package.json`, npm wrapper scripts, README npm install snippets, and `.github/workflows/npm-publish.yml` before tagging.
- After pushing a tag or creating a release: run `--phase published --wait-seconds 1800`; fix every FAIL before reporting success.
- After an interruption during release/tag work: run both phases, then follow the recovery runbook below from the first failing state. After an interruption during ordinary development, run only `--phase dev`.
- During README-only maintenance: still run `--phase prepare` so version badges, release notes, install URLs, and memory wording stay aligned.
- During normal development: run `--phase dev --wait-seconds 0` after commit/push; use a positive wait only when the user asks for CI verification or the change is risky enough to need it.
- When the user asks for the final published result, include commit, push, merge-to-main when needed, GitHub Actions verification, Release assets verification, npm registry verification, and homepage README verification.

## Development Version Management

Use this for CCB development changes, including `dev_tools`, tests, docs, CI, and maintainer workflows.

1. Classify the change:
   - `dev_tools/`, tests, docs, and CI-only checks usually do not require a package release.
   - `lib/`, `ccb`, `bin/`, installer scripts, release build scripts, `VERSION`, `package.json`, `.github/workflows/npm-publish.yml`, README release notes, or `CHANGELOG.md` may affect users and must be considered for release.
2. Run targeted tests first, then the smallest broad check that matches the risk.
3. Commit the development change.
4. Push the branch.
5. Run:
   ```bash
   python dev_tools/skills/ccb-github/scripts/check_release_state.py --phase dev --repo SeemSeam/claude_codex_bridge --wait-seconds 0
   ```
6. If `--phase dev` reports runtime/package changes and the user wants a published package, switch to the Release Preparation Checklist and Publish Sequence, including npm auto-completion.
7. If the change is development-only, do not create a tag or GitHub Release.

`--phase dev` is intentionally strict about local and push state: uncommitted changes or unpushed commits mean the development result is not final yet. Red or in-progress workflows block completion only when this skill is explicitly waiting for CI.

## Test Scope Policy

Default to the smallest verification set that gives meaningful signal for the files changed. Do not run full-suite tests for small edits unless the user asks, the change crosses shared runtime boundaries, or targeted checks reveal risk.

- README, image, and docs-only edits: run `git diff --check`; optionally run `check_release_state.py --phase dev --wait-seconds 0` after commit/push.
- Skill edits or skill migration: run `quick_validate.py <skill-dir>` when available and compare source/active copies with `diff -ru`, excluding caches; do not run pytest for skill-only edits.
- Installer or shell edits: run `bash -n install.sh` or the relevant shell syntax check, plus focused installer tests that cover the changed behavior.
- `lib/`, `ccbd`, provider runtime, startup, tmux, or shared behavior edits: run targeted pytest for the touched module and adjacent contract tests; broaden only when the change affects cross-module behavior.
- Release assets, version files, package build scripts, or explicit release/tag work: use the Release-Only Local Verification below.
- npm package or Trusted Publishing workflow edits: run `node --check` on changed npm wrapper scripts, `npm pack --dry-run`, and a local tarball install smoke when the package wrapper changed.
- GitHub homepage updates: merge to the default branch only when the user explicitly asks for homepage visibility, then verify default-branch README and CI as needed.

## Release Preparation Checklist

Update these files together:

- `VERSION`
- `ccb.py` `VERSION = "..."` (or legacy Python-in-`ccb` layouts)
- `package.json` `"version": "..."`
- npm wrapper scripts under `bin/` when package behavior changes or the package is being introduced.
- `.github/workflows/npm-publish.yml`
- `CHANGELOG.md`
- `README.md`
- `README_zh.md`

README requirements:

- Top version badge must match the new version.
- "What's New" / "最新亮点" must describe the current release, not an older milestone; compare it against the newest `CHANGELOG.md` section and ensure it covers the most important user-facing bullets.
- "Config Control" / "配置控制" must stay aligned with current `.ccb/ccb.config` behavior.
- Keep the shared memory wording concise: `.ccb/ccb_memory.md` is the project-wide shared memory document.
- Do not reintroduce root `CCB.md` support or mention it as a current feature.
- Install commands must point at the actual public GitHub repo.
- Release Notes / 新版本记录 must include the new version near the top.
- npm install snippets should point at `npm install -g @seemseam/ccb` when npm is the recommended install path.

npm auto-completion requirements:

- Treat npm publishing as enabled for every CCB package release. If `package.json` is absent, add the root npm wrapper package instead of skipping npm.
- If npm wrapper scripts are absent, add or repair CLI bins for `ccb`, `ask`, `autonew`, and `ctx-transfer` so the npm package installs the intended GitHub Release payload.
- If `.github/workflows/npm-publish.yml` is absent, add the Trusted Publishing workflow before tagging.
- If README install sections do not mention npm and npm is the intended install path, update both English and Chinese READMEs in the release commit.
- Before tagging, verify the intended tag commit contains npm release files with:
  ```bash
  git show HEAD:package.json >/dev/null
  git show HEAD:.github/workflows/npm-publish.yml >/dev/null
  ```
  Missing files mean the release preparation is incomplete; fix and recommit before creating the tag.

npm requirements:

- `package.json` version must match `VERSION`, `ccb` `VERSION`, and the release tag without the leading `v`.
- `package.json` must publish `@seemseam/ccb` as a public package with CLI bins for `ccb`, `ask`, `autonew`, and `ctx-transfer`.
- `.github/workflows/npm-publish.yml` must exist and use npm Trusted Publishing/OIDC: GitHub-hosted runner, Node 24, `permissions: id-token: write`, no `NODE_AUTH_TOKEN`, and `npm publish --access public`.
- If npm Trusted Publisher is not configured for owner `SeemSeam`, repository `claude_codex_bridge`, workflow filename `npm-publish.yml`, blank environment, and allowed action `npm publish`, stop and report the registry-side blocker.

GitHub repo homepage requirements:

- `gh repo view SeemSeam/claude_codex_bridge --json description,homepageUrl,repositoryTopics,latestRelease`
- Description and topics should match the current public positioning.
- If README install URLs or badge links point to an old owner, fix them before tagging.

## Release-Only Local Verification

Use this full local gate only for release/tag/package work, or when runtime/package changes are broad enough that targeted tests are not sufficient. Run at least:

```bash
pytest -q
python -m compileall -q lib ccb
git diff --check
npm pack --dry-run
python scripts/build_linux_release.py --allow-dirty --output-dir dist-release-local
```

For startup, tmux, ccbd, provider auth, or release asset changes, add the relevant targeted tests or smoke commands before publishing.

## Homepage Maintenance Without A New Tag

Use this when the latest release exists but GitHub's repository homepage is stale:

1. Update `README.md`, `README_zh.md`, GitHub metadata, or `dev_tools` release checks.
2. Run:
   ```bash
   python dev_tools/skills/ccb-github/scripts/check_release_state.py --phase prepare --repo SeemSeam/claude_codex_bridge
   ```
3. Commit and push the maintenance branch.
4. Merge the maintenance branch into the default branch so GitHub homepage README changes are visible:
   ```bash
   git checkout main
   git pull --ff-only origin main
   git merge --no-ff <maintenance-branch>
   git push origin main
   ```
5. Wait for default-branch `Tests`, `CCBD Real Platform Smoke`, and `Cross-Platform Compatibility Test`.
6. Run:
   ```bash
   python dev_tools/skills/ccb-github/scripts/check_release_state.py --phase published --repo SeemSeam/claude_codex_bridge --wait-seconds 1800
   ```

Do not create a new release tag for README-only homepage maintenance unless runtime/package contents changed and the user explicitly wants a new release.

## Publish Sequence

Use this order:

1. Complete release changes, including version files, changelog, README/README_zh, npm package metadata/wrapper scripts, and npm publish workflow. If npm files are missing, add them now instead of deferring.
2. Run local release verification.
3. Commit release changes.
4. Push the branch.
5. Merge the release branch into the default branch when the repository homepage must reflect the release docs:
   ```bash
   git checkout main
   git pull --ff-only origin main
   git merge --no-ff <release-branch>
   git push origin main
   ```
6. Before tagging, verify the intended release commit contains `package.json` and `.github/workflows/npm-publish.yml`; if not, stop and return to step 1.
7. Create and push tag `vX.Y.Z` from the intended release commit.
8. Create the GitHub Release page for `vX.Y.Z`.
9. Let `Release Artifacts` upload assets.
10. Let `Npm Publish` publish `@seemseam/ccb@X.Y.Z` through npm Trusted Publishing.
11. Confirm `Release Artifacts` is green for the tag or a valid `workflow_dispatch` recovery on the release tag commit, confirm `Npm Publish` is green for the release tag commit, and confirm branch validation workflows for the release commit are green or consciously accepted as warnings:
   - `Tests`
   - `CCBD Real Platform Smoke`
   - `Cross-Platform Compatibility Test`
12. Confirm release assets exist:
   - `ccb-linux-x86_64.tar.gz`
   - `ccb-macos-universal.tar.gz`
   - `SHA256SUMS`
13. Confirm npm registry state:
   ```bash
   npm view @seemseam/ccb version dist-tags --json
   ```
14. Confirm the GitHub homepage README is updated by reading default-branch README through GitHub:
   ```bash
   gh api 'repos/SeemSeam/claude_codex_bridge/contents/README.md?ref=main' --jq .content | base64 -d | rg 'version-|vX.Y.Z'
   ```

The current workflow expects the Release page to exist before uploading assets. If `Release Artifacts` fails with `release not found`, create the Release and rerun the workflow. When using manual `workflow_dispatch`, select the release tag/ref or otherwise ensure the run's `headSha` matches the release tag commit; the checker does not accept unrelated manual runs.

The published checker must pass after this sequence. It verifies local push state, tag presence, GitHub latest release, release assets, `SHA256SUMS`, default-branch README, and whether the default branch contains the release tag.
The npm registry check must also pass after this sequence; `latest` must resolve to the same version as the GitHub Release.

## Recovery Runbook

Use the checker output first; each FAIL includes a suggested fix. Common cases:

- Release page missing: create it with `gh release create vX.Y.Z --repo SeemSeam/claude_codex_bridge --title vX.Y.Z --notes-file <notes-file>`, then rerun `Release Artifacts`.
- Release Artifacts recovered through `workflow_dispatch`: run it on the release tag/ref or otherwise ensure the run `headSha` matches the tag commit; unrelated manual runs are not accepted.
- Release assets missing: rerun the `Release Artifacts` workflow for the tag, then verify `ccb-linux-x86_64.tar.gz`, `ccb-macos-universal.tar.gz`, and `SHA256SUMS`.
- npm files missing before tag: add or repair `package.json`, npm wrapper scripts, README npm snippets, and `.github/workflows/npm-publish.yml` in the release commit, rerun local verification, then tag.
- npm workflow missing after tag: the existing tag cannot contain files committed later. Do not claim it will auto-publish from that old tag. Stop and ask for an explicit maintainer decision: move/recreate the tag, publish manually from a reviewed commit, or bump to a new patch version with npm files included before tagging.
- npm Trusted Publisher mismatch: configure npm package `@seemseam/ccb` with owner `SeemSeam`, repository `claude_codex_bridge`, workflow filename `npm-publish.yml`, blank environment, and allowed action `npm publish`; then rerun `Npm Publish` for the release tag.
- npm version already exists: do not overwrite; bump all version surfaces and publish a new patch version.
- npm publish 404/401: confirm package ownership, scope permission, npm Trusted Publisher configuration, and that the workflow ran from a tag containing the committed `package.json`.
- Tag missing locally or remotely: stop and confirm the intended release commit before creating or pushing the tag.
- Tag SHA mismatch: do not force-push automatically; inspect the tag and ask for explicit maintainer approval before rewriting release history.
- GitHub CLI unauthenticated: run `gh auth login`, then rerun the published check.
- Workflow red: open the failed run, fix the root cause, rerun the workflow, and keep the release incomplete until it is green.
- README install URL mismatch: update both English and Chinese install snippets to the active public repo.
- GitHub homepage still shows an old version: merge/push the release documentation changes to the default branch; updating a tag or non-default branch is not enough.
- Empty changelog or README release entry: add concrete user-facing bullets, not placeholder headings.

## Post-Release Verification

Run:

```bash
gh release view vX.Y.Z --repo SeemSeam/claude_codex_bridge --json tagName,url,assets
gh run list --repo SeemSeam/claude_codex_bridge --limit 10
npm view @seemseam/ccb version dist-tags --json
python dev_tools/skills/ccb-github/scripts/check_release_state.py --phase published --repo SeemSeam/claude_codex_bridge --wait-seconds 1800
git status --short --branch
```

Report only the useful facts: version, commit/tag, release URL, key fixes, test status, artifact status, and whether the worktree is clean.

## Stop Conditions

Do not call the release complete if any of these are true:

- README or README_zh still shows an old current version or stale current-release highlights.
- `VERSION`, `ccb`, changelog, badges, or release notes disagree.
- `package.json` version differs from `VERSION`, `ccb` `VERSION`, or the release tag.
- The intended tag commit for a package release lacks `package.json` or `.github/workflows/npm-publish.yml`.
- The release tag is missing, points to the wrong commit, or differs between local and origin.
- The default branch does not contain the release tag when the GitHub homepage should represent that release.
- The working branch has unpushed release commits.
- GitHub latest release does not point to the new tag after publish.
- Required release assets are missing.
- `SHA256SUMS` does not contain checksum entries for every required tarball asset.
- npm `latest` does not resolve to `@seemseam/ccb@X.Y.Z` after an npm-enabled release.
- `Npm Publish` failed, is missing for a tag that should publish npm, or ran against a different commit than the release tag.
- Tests or Release Artifacts failed.
- GitHub homepage README on `main` still shows an old current version.
- The worktree has uncommitted release edits.
