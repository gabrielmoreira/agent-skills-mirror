# Roadmap

This roadmap is scoped to making AERS a high-quality, high-trust GitHub project rather than just a large link collection.

> **Execution plans (status as of 2026-07-22):** the `PLAN-2026-MM` files are sprint plans whose calendar labels drifted — all three were authored 2026-07-01…04 and largely executed immediately.
>
> - [`PLAN-2026-07.md`](PLAN-2026-07.md) — **closed**, 14/15 done (the external AERS-vs-Econometrics-Agent comparison remains open, tracked in [`SCOREBOARD.md`](SCOREBOARD.md) / [`INTEROP.md`](INTEROP.md) Recipe C).
> - [`PLAN-2026-08.md`](PLAN-2026-08.md) — headline deliverables **shipped** (Card–Krueger end-to-end replication, public benchmark scoreboard, bunching family, link-triage automation); see its status note.
> - [`PLAN-2026-09.md`](PLAN-2026-09.md) — **current / not started**: opening the evidence chain to external agents.

## Now

- Keep `catalog/skills.json` and `docs/SKILL_CATALOG.md` current.
- Require `make check` for all pull requests.
- Keep README links and docs category links green.
- Preserve the no-paid/proprietary-core scope rule for new listings.
- Keep `catalog/provenance.json`, `docs/LICENSE_AUDIT.md`, and `docs/SKILL_AUDIT.md` current.
- Use [`docs/search.html`](search.html) as the lightweight searchable catalog (now served on [GitHub Pages](https://brycewang-stanford.github.io/Auto-Empirical-Research-Skills/)).
- Keep GitHub Actions passing `scripts/validate-workflows.py` and review OpenSSF Scorecard findings.

## Next

- Enrich provenance metadata with exact vendored commits where upstream snapshots are known.
- Add scheduled external-link triage notes to releases when weekly checks fail.
- Convert the flagship eval prompts into executable scorecards where artifacts can be generated in CI without paid APIs.
- Keep [`ECOSYSTEM.md`](ECOSYSTEM.md) and [`../ecosystem/ecosystem.json`](../ecosystem/ecosystem.json) current as the agentic-research ecosystem evolves, and expand the [`INTEROP.md`](INTEROP.md) pipeline recipes (e.g. a benchmarked AERS-vs-Econometrics-Agent comparison).

## Later

- Package first-party AERS skills as installable bundles for agent runtimes that support plugins/marketplaces.
- Add per-skill eval prompts for flagship first-party skills.
- Maintain a public benchmark of empirical-research agent workflows: correctness, reproducibility, citation hygiene, and runtime safety.
- Close the rigor gaps surfaced by [`RIGOR_COVERAGE.md`](RIGOR_COVERAGE.md): method families with tagged skills but no eval scenario or benchmark task yet (synthetic control, panel FE, double/debiased ML, Bayesian, survival), plus the partials (an event-study benchmark task; a matching/PSM eval scenario).

## Completed Hardening Pass

- Generated machine-readable catalog and provenance metadata.
- Added license audit, skill hygiene audit, static search page, install guide, submission guide, flagship demos, release process, external-link workflow, and clean CI validation.
- Added machine-readable flagship eval prompts and generated reviewer docs.
- Added a generated methodological rigor coverage map ([`RIGOR_COVERAGE.md`](RIGOR_COVERAGE.md), built by `scripts/build-coverage-map.py` and freshness-checked in `make validate`) that joins the method taxonomy with eval scenarios and benchmark tasks and surfaces open gaps.
- Added an ecosystem positioning map ([`ECOSYSTEM.md`](ECOSYSTEM.md)), interoperability recipes ([`INTEROP.md`](INTEROP.md)), a machine-readable registry ([`../ecosystem/ecosystem.json`](../ecosystem/ecosystem.json)), and a sync-enforcing validator (`scripts/check-ecosystem.py`, wired into `make validate`).
