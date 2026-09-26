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
