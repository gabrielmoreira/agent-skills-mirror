# Notes for coding agents

## Releasing

Every release gets a CHANGELOG.md entry written from the commit history; the Publish to npm workflow refuses a tag
without one and uses the entry as the GitHub release notes.

1. Raise the version everywhere it is kept (the `@open-artifact/*` packages, `plugins/dsh`, every plugin manifest and
   the marketplaces share one version).
2. Run `node scripts/changelog.mjs` to list the commits since the last `v*` tag (`node scripts/changelog.mjs <from> <to>`
   for another range).
3. Add a `## [x.y.z] - YYYY-MM-DD` section at the top of CHANGELOG.md: a one-line summary, then `### Added`,
   `### Changed`, `### Fixed` (and `### Removed` when something goes). Write what changed for people using Open Artifact,
   merging related commits; leave out release-bookkeeping commits and purely internal refactors. Add the version's
   compare link at the bottom (`[x.y.z]: https://github.com/JimLiu/open-artifact/compare/v<prev>...vx.y.z`).
4. Check it with `node scripts/changelog.mjs --check x.y.z`, commit, tag `vx.y.z` and push the tag.
