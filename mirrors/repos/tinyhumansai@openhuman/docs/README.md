# docs/

Internal maintainer documentation. Public and contributor docs live in
`gitbooks/` (navigation in `gitbooks/SUMMARY.md`); agent and contributor rules
live in `AGENTS.md` (`CLAUDE.md` is a symlink to it); per-domain design notes
sit beside the code as `crates/openhuman-core/src/<domain>/README.md`.

## Contributor onboarding

- `CONTRIBUTING-BEGINNERS.md` — step-by-step first-PR guide for newcomers;
  linked from the root `README.md` and `CONTRIBUTING.md`.
- `SUPPORT.md` — where to ask for help; routes each kind of problem to a
  GitHub Discussions category.
- `community/discussions.md` — how maintainers organize and triage those
  Discussions categories.

## Process checklists

Both are referenced from `.github/PULL_REQUEST_TEMPLATE.md`.

- `TEST-COVERAGE-MATRIX.md` — feature-ID to test-path matrix. Feature IDs are
  validated against `scripts/feature-ids.json` by
  `scripts/check-coverage-matrix.mjs` in the `pr-quality` workflow; test paths
  are not validated, so keep them current by hand. Update rows in the same PR
  that changes a feature.
- `RELEASE-MANUAL-SMOKE.md` — manual smoke checklist run on every release cut;
  the only accepted substitute for a 🚫 matrix row.
- `QA-SIDEBAR-ICON-COLLAPSE.md` — one-off desktop QA checklist for the sidebar
  icon-collapse change (#5676).

## Engineering notes

Resource-footprint work for the embeddable core. Drivers live in
`scripts/profile/`; the scenario binary is
`crates/openhuman-core/src/bin/library_profile/main.rs` (`library-profile`,
behind the `rss-bench` feature).

- `library-benchmarking.md` — the benchmark environment: scenarios, driver
  scripts, and default/slim baselines.
- `library-minimal-recipe.md` — the `--no-default-features --features
  "skills,flows"` recipe for a headless library build, with measurements.
- `harness-comparison-2026-07-22.md` — footprint comparison of OpenHuman's core
  against other agent harnesses.

## Translated product READMEs

Translations of the root `README.md`, linked from its language bar:
`README.de.md`, `README.ja-JP.md`, `README.ko.md`, `README.ur-pk.md`,
`README.zh-CN.md`.

There is no `docs/plans/`; it was removed in `0017c58d86` and design notes now
live beside the code.
