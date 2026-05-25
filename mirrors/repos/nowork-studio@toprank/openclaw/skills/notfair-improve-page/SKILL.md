---
name: notfair-improve-page
description: Improve one URL inside a registered site by producing a focused diagnosis, proposal, and verification artifact.
metadata: { "openclaw": { "emoji": "🧱", "homepage": "https://github.com/nowork-studio/notfair", "requires": { "bins": ["python3"] } } }
---

# NotFair Improve Page

1. Read `{baseDir}/../../shared/adapter-rules.md`.
2. Read `{baseDir}/../../shared/artifact-contract.md`.
3. Read `{baseDir}/../../shared/policy.md`.
4. Load the site work folder, then focus on the target URL and choose the canonical page-level skills that best fit the issue.
5. Read and follow the canonical NotFair skill at `{baseDir}/../../../seo/seo-page/SKILL.md`.
6. Convert the page diagnosis into a structured proposal using `python3 {baseDir}/../../bin/improve_page.py <site> --url <url> --issue-summary "..." --proposal-summary "..."`.
7. If you also have file-level edits to suggest, include `--patch-path` and `--patch-summary` so a `patch-set.json` artifact is written.
8. Verify that the run wrote `proposal.json` and `verification.json`, plus `patch-set.json` when relevant.
9. If the next action requires editing a site repo, CMS, publishing content, or opening a PR, stop and ask for approval before doing it.

## Wrapper job

Use this when the operator wants a single page improved.

Typical combinations:
- `seo-page` for diagnosis,
- `meta-tags-optimizer` for title/meta candidates,
- `schema-markup-generator` for structured data proposals,
- `content-writer` for a content brief or rewrite draft.

Write at least `proposal.json` and `verification.json`. If you generate patches or file-level changes, also write `patch-set.json`.
