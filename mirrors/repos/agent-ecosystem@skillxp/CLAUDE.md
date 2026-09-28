# skillxp

Skill invocation runner: stage an Agent Skill on a real harness, invoke
it headlessly, and report what actually reached the model, with
transcript evidence. Builds on agentsummons (invocation) and
agentminutes (transcript parsing); renders no verdicts — graders consume
its observation bundles. `DEVELOPMENT.md` holds the release process.

## Commands

```bash
go test ./... -count=1
golangci-lint run             # lint + gofumpt (CI-enforced)
GOOS=windows go build ./...   # CI also tests on windows-latest

npm test --prefix wrappers/npm
python3 -m unittest discover -s wrappers/pypi/tests
```

## Drift

Harness skill lore (`profile/`) moves with harness releases without warning.
`profile.LastValidated` records the release each profile was last
re-confirmed on (the third axis next to agentsummons' flag surface and
agentminutes' transcript format). `skillxp doctor` is the free gate;
`skillxp drift probe` (maintainer-only, spends tokens, sandboxed) re-runs
the discovery, listing, and resume experiments and grades drift vs
inconclusive. Reconcile per `DEVELOPMENT.md`: fix the profile, bump the
table, note it in the changelog.

## Docs site (site/)

Hugo + Lotus Docs site for skillxp.dev, instantiated from
af-site-scaffold's template. Deploy with `site/build_and_sync` (rsync to
Dreamhost); llms.txt and per-page markdown are Hugo output formats,
regenerated on every build. The repo pre-commit hook runs
`site/check_prose_style` (Vale, DC style: em dashes and "not X, but Y"
constructions are errors). README.md is outside the hook's scope; lint it
with `vale --config site/.vale.ini README.md`.

Agent-friendliness is checked with afdocs, pinned in `site/package.json`
(`npm ci` in `site/` before the first run). Both runs go through
`site/agent-docs.test.ts`, a vitest case per check:
`npm run test:agent-docs:local` runs `site/check_agent_docs`, which serves
this working tree with `hugo server` on port 1718 and passes the URL in
`AGENT_DOCS_URL`, and is what `.github/workflows/agent-docs.yml` runs on
every pull request touching `site/**`; `npm run test:agent-docs` checks
skillxp.dev and is what `agent-docs-live.yml` runs on release or
dispatch. The local run skips `content-negotiation` and
`cache-header-hygiene`, which measure Dreamhost's Apache config that no
local server has; everything else comes from `agent-docs.config.yml`, so
there is no second config to keep in sync. Never move the port to 1719 or
1720: Node's fetch blocks the WHATWG bad-list ports and every check
reports "fetch failed". A warn does not fail the build, so read the
per-check lines; `npx afdocs check <url> --fixes` explains one in detail.

Two things in the site exist only to satisfy afdocs checks, so leave
them in place: `layouts/partials/absolute-links.html` rewrites
root-relative links to absolute ones in the markdown output
(`markdown-link-portability`), and `layouts/docs/baseof.html` renders
the sidebar nav after `</main>` with a skip link, so page content leads
the DOM (`content-start-position`).

## Releasing

Follow the checklist in `DEVELOPMENT.md`. Version bumps touch more than
the tag — easy to miss:

- `CHANGELOG.md`: promote Unreleased to the version heading before
  tagging; the release workflow extracts that section for the release
  notes and fails the release if it is missing.
- `site/data/landing.yaml`: the hero badge `text` carries the current
  release version (e.g. `v0.1.1`); bump it with each release and
  publish the site.

npm currently has no win32 platform packages (registry spam detection
blocks the names; see DEVELOPMENT.md for the restore steps when npm
support frees them).
