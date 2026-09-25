# ADR Format

Architecture Decision Records live in `docs/adr/`, numbered sequentially (`0001-slug.md` …). Create the directory the first time an ADR is actually written; find the next number by scanning for the highest existing one.

## Template

```md
# {Decision, stated as a fact}

{A short paragraph: the situation, what was decided, and the reason.}
```

A paragraph is a complete ADR. The record exists so a future reader learns the decision was deliberate and why — length adds nothing to that.

Add extra sections only when they earn their bytes:

- `status:` frontmatter (`proposed` / `accepted` / `deprecated` / `superseded-by: 0007`) — when decisions get revisited
- **Alternatives** — when the losing options will predictably be re-proposed later
- **Consequences** — when a downstream effect is non-obvious enough to trip someone

## The three-part test (all must hold before offering one)

1. **Reversal is expensive.** Cheap-to-undo choices don't need records; you'd just undo them.
2. **A future reader would be puzzled.** If the code makes the choice self-evident, the record is redundant.
3. **A genuine trade-off was made.** "We did the only sensible thing" records nothing.

## What typically passes the test

- Structural commitments: repo layout, event-sourcing vs CRUD, monolith vs services.
- How contexts communicate (events vs synchronous calls; who owns which data, referenced by ID only).
- Lock-in technology picks — the database, queue, auth provider; not every library, only the quarter-to-replace ones.
- Deliberate departures from the path a reasonable engineer would assume — these prevent well-meaning "fixes" of intentional choices.
- Invisible constraints: compliance limits, partner SLAs, hardware realities that the code can't show.
- Non-obvious rejections — the alternative someone will suggest again in six months, and why it lost.
