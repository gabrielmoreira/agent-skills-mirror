# Claude Repository Guidance

Read `AGENTS.md` first. This file exists as a compatibility instruction source
for Claude-based agents working in this repository.

## Stewardship Defaults

- Treat community PRs and issues as maintainer evidence. Inspect code, tests,
  linked issues, comments, and CI before merging, harvesting, closing, or
  deferring work.
- Do not tag, publish, create a GitHub Release, or push release artifacts
  without Hunter's explicit approval.
- Keep CodeWhale branding while preserving first-class DeepSeek model/provider
  support and legacy migration care.
- Preserve contributor credit for harvested work with authorship,
  `Co-authored-by`, `Harvested from PR #N by @handle`, and changelog/release
  notes where applicable.

## Scratch Integration Branches

- For release queues, create disposable local branches from the real landing
  branch, for example `scratch/v0.8.59-pr-train-YYYYMMDD`.
- Use the scratch branch to merge or cherry-pick candidate PR heads in batches
  and learn which conflicts, tests, and overlaps are real.
- Do not ship the scratch branch itself. It may contain noisy merge commits,
  partial conflict resolutions, and unrelated PR interactions.
- After the scratch experiment, move only the safe result back to the release
  branch as narrow commits or direct merges. Keep each final commit explainable
  and testable.
- A PR that is clean against `main` is not necessarily clean against a release
  branch. Test mergeability against the branch that will actually receive the
  work.
- For already approved PRs, treat approval as a strong priority signal. Still
  inspect diffs, comments, check results, and release-branch conflicts before
  landing.

## v0.8.59 Release Work

- Base release triage on `codex/v0.8.59-release-ready` unless Hunter gives a
  newer branch.
- Work the queue in this order: release blockers, recently approved PRs, clean
  PRs with small scope, blocked PRs with obvious fixes, dirty PRs that can be
  harvested safely, then larger architecture issues.
- Prefer batching PR conflict discovery on scratch branches, then harvesting
  reviewed, credited, tested slices back into the release branch.
- Before claiming an issue is done, verify whether the release branch already
  contains equivalent work. If it does, prepare the GitHub note/closure path
  instead of reimplementing it.
- For the current v0.8.59 queue, start with
  `docs/V0_8_59_RELEASE_TRIAGE.md`, then refresh live GitHub state before
  taking action.
