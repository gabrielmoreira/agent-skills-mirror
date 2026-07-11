# PromptHub Repository Profile

## Baseline

- Upstream repository: `https://github.com/legeling/spec-init`
- Synchronized revision: `f83def11e7b3e1753cd6f32eacdf09b72b3b29ae`
- Revision date: 2026-06-30

## Lookup Order

1. Read repository `AGENTS.md`.
2. Read `spec/README.md`, `spec-init.topology.yml`, and the relevant files in
   `spec/rules/`.
3. Read the matching stable `spec/knowledge/*` documents and active change.
4. Then inspect implementation and tests.

## Path Adaptation

- Internal workflow, knowledge, changes, issues, releases, ADRs, archives, and
  rules live under `spec/`, not `docs/`.
- `docs/` remains the repository-facing user and contributor documentation
  surface.
- Non-trivial work uses
  `spec/changes/active/<change-key>/{proposal.md,specs/<domain>/spec.md,design.md,tasks.md,implementation.md}`.
- PromptHub keeps `spec/changes/archive/YYYY/MM/YYYY-MM-DD-<change-key>/` as
  the authoritative completed-change store. `spec/changes/completed/` is only a
  compatibility entry for upstream completed semantics.
- Do not create parallel `docs/workflow`, `docs/knowledge`, `docs/changes`, or
  `docs/rules` truth sources inside PromptHub.

## Phase Adaptation

- Keep the upstream phases: `specify`, `clarify`, `plan`, `tasks`, `analyze`,
  `implement`, and `converge`.
- Map convergence of a completed PromptHub change to `spec/changes/archive/`,
  not to a second physical completed store.
- A change may stay active only while implementation, verification, review,
  synchronization, or a recorded blocker remains.

## Issue And Submission Semantics

- GitHub remote snapshots and local delivery state remain separate.
- Before release use `Refs #<issue>`; use `Closes #<issue>` only after the
  containing version is published and the issue should close.
- Before any commit or push, read
  `spec/rules/submission-traceability-rules.md` and inspect
  `git status --short`.

## Design Conflict Gate

Stop for user confirmation if an upstream generic rule would replace
PromptHub's source of truth, rename existing historical records, change the
OpenSpec-style active change contract, or create a parallel document topology.
