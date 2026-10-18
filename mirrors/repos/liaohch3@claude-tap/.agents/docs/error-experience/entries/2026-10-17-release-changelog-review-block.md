# Release changelog review blocks automatic publishing

Date: 2026-10-17

## Failure and evidence

[Auto Release run 39040400288](https://github.com/liaohch3/claude-tap/actions/runs/39040400288)
passed the release PR checks, then failed with `All comments must be resolved`.
No release tag was created. Release PR #442 had six unresolved review threads
covering duplicated release notes, internal evidence commits, and missing Chinese notes.

## Root cause

The generator appended commit subjects to already curated Unreleased notes.
This duplicated product fixes and exposed internal validation work in the public
changelog. The workflow attempted an administrator merge even while review
requirements remained unmet. Passing checks did not imply permission to merge.

## Correction and prevention

- Promote curated Unreleased content once, preserving older release sections.
- Validate both language documents before writing either file.
- Keep internal commit subjects out of public release notes.
- Wait for checks, then enable auto-merge when review requirements remain unmet.
  Exiting without enabling auto-merge leaves approval unable to resume a push-only workflow.
- Pin merge requests to the checked head commit and resolve findings only after
  inspecting the regenerated release PR.
- Exercise the generator through its real CLI and execute the workflow merge
  guard for blocked and clean states in regression tests.
