# seed-registry/

**Source-of-truth for the [AmrDab/clawdcursor-guides](https://github.com/AmrDab/clawdcursor-guides)
GitHub registry.** The files here are not bundled into the clawdcursor
binary — they were used to seed the public GitHub repo, which the agent
fetches from at runtime (served at `clawdcursor.com/app-guides`).

These files in this `seed-registry/` directory are the **canonical
maintainer-side authoring copies**. The live versions on GitHub may
diverge as PRs land; if you're authoring a new guide, write it in the
guides repo directly via PR — don't sync through here.

See [docs/guide-marketplace.md](../docs/guide-marketplace.md) for the
full architecture.

## What's here

`guides/` — `AppGuide` JSONs for the apps the maintainers curate. The
schema matches `src/core/pipeline-types.ts AppGuide`. Every file passes
`clawdcursor guides lint <file>` (the same linter the client runs at
fetch time, and the same one the registry's CI runs on every PR).

| App | Lines | Workflows | Shortcuts | Tips |
|-----|-------|-----------|-----------|------|
| youtube | 80 | 19 | 36 | 13 |
| gmail | 50 | 8 | 12 | 6 |
| outlook | 50 | 8 | 12 | 6 |
| slack | 40 | 6 | 15 | 5 |
| figma | 90 | — | 116 | — |
| excel | 100 | 6 | 122 | — |
| discord | 30 | — | 27 | — |
| spotify | 25 | — | 23 | — |
| mspaint | 50 | 7 | 11 | — |
| olk | 30 | 4 | 7 | — |

## Bundled vs seed-registry

The clawdcursor binary ships only a **minimum core** in
`src/llm/knowledge/guides/`:
- `msedge.json` — universal browser knowledge (works for Edge,
  most patterns transfer to Chrome / Firefox)
- `notepad.json` — universal text-editor knowledge

Everything else lives here, gets pushed to the GitHub registry, and is
fetched by the agent on demand. Cached locally for 7 days; LRU-evicted
after 50 entries.

## Updating these files

1. Edit a guide here.
2. Run `clawdcursor guides lint seed-registry/guides/<app>.json` to validate.
3. Commit to clawdcursor's main repo.
4. Open a PR to the `clawdcursor-guides` GitHub repo with the updated
   file (out of band — these aren't auto-synced yet).
5. The next nightly index-aggregate run picks up the change.

## Adding a new guide

You can put the JSON anywhere and `clawdcursor guides submit <path>`
will lint it and print the PR instructions. To make it part of the
maintainer-curated seed, drop it here too and commit alongside.

## Trust level

Everything here is intended to be published with `trust: verified`. If
you want to seed `community` guides, put them in a parallel
`seed-registry/community/` directory — they don't ship to the verified
default fetch path.
