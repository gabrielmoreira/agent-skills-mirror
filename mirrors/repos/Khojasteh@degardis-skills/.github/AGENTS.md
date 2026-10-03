# Release Instructions

For the agent preparing or publishing a GitHub release, or changing that release automation. Reconciling the reader-facing pages is release work, so this file owns when a release rewrites one and what a snapshot must agree with; [`docs/AGENTS.md`](../docs/AGENTS.md) owns what those pages say and how they say it.

The root `AGENTS.md` governs repository layout and commits. `degardis-authoring` governs skill content and versioning.

Do not commit or run the `Release skill bundles` workflow without explicit maintainer request and approval.

## Release preparation

1. Validate the whole collection: `degardis validate skills`.

2. Collect what changed since the last snapshot:

   ```console
   python .github/scripts/changes-since-release.py
   ```

   For each skill whose bundle content changed it prints the commits with their bodies, and a diffstat of the bundle files that changed. It also lists every retirement it detects. This is the input to everything.

3. Decide, per changed skill, whether this snapshot releases it or holds it back. Nothing is implicit: a changed skill that gets no dated section must be named in `--hold` at step 8, and the generator fails if one is neither released nor held.

4. Write each released skill's section. **The shipped source is the authority for every claim; the harvest only says where to look.** A commit body states what a session meant to do — the change may have landed differently, been narrowed, or been reversed by a later commit — so open the source a claim rests on and confirm the current source says it. Drop what the source does not support, however confidently a commit asserts it, and write what the source shows even where no commit mentioned it.

   Begin with one focused paragraph summarizing the bundle-level outcome, which release notes extract, then one bullet per user-noticeable subject. Merge everything several commits did to one subject into a single bullet, describe what the installed skill now does rather than what a session did, and carry no date, time, or agent name.

   A skill being published for the first time has no `CHANGELOG.md` yet — create it here, with that one dated section.

5. Take the version being released from `skill.yaml` and write it into the changelog section, the README version line, and the catalog row. Release preparation reads that number and never writes it — see [Versions](#versions). Reconcile that skill's README body from `Purpose` onward against the same source, to the conventions in [`docs/AGENTS.md`](../docs/AGENTS.md) — every behavioral claim, sample prompt, and steering option checked against the shipped source that delivers it, since the README is what a reader decides to install on. Update its short description too, and add the catalog row and download link if this is its first release.

6. Give every detected retirement its reason, per [`RETIRING.md`](RETIRING.md), and drop what the catalog still holds open for it — its row, its download link, and any sibling or guide link pointing at it. This is the counterpart of step 5's first-release row: the retiring commit leaves the README alone, so the row goes here or nowhere. The generator refuses to announce a retirement it cannot explain.

7. `python .github/scripts/check-docs.py`

8. Dry-run the notes:

   ```console
   python .github/scripts/generate-release-notes.py \
     --output .artifacts/test-notes.md \
     --tag skills-YYYY-MM-DD \
     --hold <skill-name>
   ```

   It must reject a changed skill that is neither released nor held, a version disagreement, a retirement with no reason, and an asset tag that is not this snapshot's.

9. Ask the maintainer to review and confirm each generated summary.

## Changelog form

`CHANGELOG.md` holds released history only, and a skill that has never been released has none at all — `changelog.py` rejects both a non-release section and a changelog with no release in it. The release that first publishes a skill creates its changelog; entries run newest first, with headings in the form

```markdown
## [X.Y.Z](https://github.com/Khojasteh/degardis-skills/releases/download/<tag>/<skill-name>.zip) - YYYY-MM-DD
```

Derive past versions and dates from the publishing snapshot tag, never from recollection. A changelog created for an already published skill includes every release through its first, whose only bullet is `Initial release.`

## Versions

A skill's version lives in `skill.yaml`, and release preparation only reads it. Raising it is the requester's call, made where the skill is authored, so nothing here sets, raises, or corrects that number — a snapshot publishes the version the source already declares. The changelog section, the README version line, and the catalog row all state it, and the generator refuses a section dated for this snapshot whose version differs from `skill.yaml`.

`check-docs.py` requires `skill.yaml` to equal the latest released version when the source has not changed since, and to be ahead of it when the source has. So a skill whose source moved on without a new version to publish it under is not releasable in this snapshot: hold it back, and ask the maintainer whether to authorize the version work before the next one.

## Distribution

Publish dated snapshots through `Release skill bundles` with a fresh `skills-YYYY-MM-DD` tag (`.N` for a second snapshot that day); it must reject an existing tag. The workflow installs published PyPI `degardis`, checks documentation, validates the collection, builds only the skills released in that snapshot, carries every other published bundle forward unchanged, sets the GitHub latest release, and refuses publication unless every skill with a released changelog section has exactly one `<skill-name>.zip`. README links rely on GitHub's repository-wide `releases/latest/download/` redirect.

Snapshot tags are distribution identifiers, not collection semantic versions; skills stay independently versioned in `skill.yaml`, README, and catalog.
