# WIKI Operations

> Operations reference for the LLM wiki system. See `wiki/WIKI.md` for schema.

## Ingest

Transforms a raw source into structured wiki knowledge.

```
raw/<source>.md  →  wiki/sources/<slug>.md  →  entity/concept pages  →  index
```

Procedure:

1. Human places source in `raw/` with frontmatter (`status: pending`)
2. LLM reads the source and discusses key takeaways with the operator
3. LLM writes `wiki/sources/<slug>.md` — a ≤100-line digest
4. LLM creates or revises entity/concept pages; wikilinks in both directions
5. LLM updates `wiki/index.md` with new/changed pages (grouped by type)
6. LLM appends entry to `wiki/log.md` → `## [YYYY-MM-DD] ingest | <source-slug>`
7. Mark raw source frontmatter `status: ingested`

Run: `node scripts/wiki/ingest.js --source raw/<file>.md`

## Query

Synthesises an answer from existing wiki pages.

1. LLM reads `wiki/index.md` to find all relevant pages
2. LLM reads those pages in full; synthesises answer with `[[citations]]`
3. Novel insights (≥2 sources, non-obvious conclusions) → file as `wiki/syntheses/<slug>.md`
4. Log the query: `## [YYYY-MM-DD] query | <topic>`

## Lint

Structural health check; run before committing any wiki changes.

1. Check for broken `[[wikilinks]]` (target must exist in `wiki/index.md`)
2. Check for orphan pages (no inbound wikilinks from any other page)
3. Check frontmatter completeness (all required fields present and non-empty)
4. Check `wiki/index.md` is in sync with actual `wiki/` file tree
5. Flag stale claims: `last_verified` >90 days → warn
6. Flag contradictions between pages on the same topic
7. Output a health report with actionable items (appended to `wiki/log.md`)

Run: `node scripts/wiki/lint.js`

## Cross-reference rules

- Every entity/concept page must link to ≥1 related page (via `related:` field)
- Source summaries must link to the entities/concepts they mention
- Syntheses must cite ≥2 source or concept pages
- **Bidirectional**: if A links to B, B should link back to A
- Orphan check runs automatically during `wiki/lint.js`

## Content trust scoring

| Score                | Meaning                        | Trigger to change                       |
| -------------------- | ------------------------------ | --------------------------------------- |
| `confidence: high`   | ≥3 independent sources agree   | Contradicting source → drop to `medium` |
| `confidence: medium` | 1–2 sources; no contradictions | Confirming 3rd source → raise to `high` |
| `confidence: low`    | Single source or inferred      | Never raise without additional source   |

Contradicting a `high` confidence claim requires filing a research ticket, not
just editing the page in place. Log the conflict first.

## Anneal (cross-reference pass)

`scripts/wiki/anneal.js` ensures bidirectional links are symmetric.

Run after ingest if new pages were created:

```bash
node scripts/wiki/anneal.js           # preview missing back-links
node scripts/wiki/anneal.js --fix     # write missing back-links in place
```

## Versioning policy

- Track changes via `updated:` frontmatter (not Git blame)
- Breaking changes to a page's core claim → bump `updated:`, add `sources_count:` delta
- Superseded content → set `status: deprecated` + `superseded_by: [[new-page]]`
- Never delete a deprecated page; keep it for audit trail
