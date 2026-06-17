# Grail Filter-Segments (`@dynatrace-sdk/client-filter-segment-management`)

> Env: ✅ Server runtime
> Status: current

Create and manage filter-segments that slice and contextualize Grail data.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `filterSegmentsClient` | `createFilterSegment`, `getFilterSegment`, `getFilterSegments`, `updateFilterSegment`, `partiallyUpdateFilterSegment`, `deleteFilterSegment` | Segment CRUD |
| `filterSegmentsClient` | `getLeanFilterSegments` | Minimal representations (faster) |
| `filterSegmentsClient` | `getFilterSegmentsEntityModel` | Data model structure |

Full method/type detail: [filterSegmentsClient.md](filterSegmentsClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Required scopes

- `storage:filter-segments:read` / `:write` / `:delete` / `:share` (sharing a public segment requires `:share`).

## Example

```ts
import { filterSegmentsClient } from "@dynatrace-sdk/client-filter-segment-management";

const data = await filterSegmentsClient.createFilterSegment({
  body: {
    name: "dev_environment",
    isPublic: false,
    includes: [{ filter: "...", dataObject: "logs" }],
  },
});
```

## Notes

- A filter-segment scopes/contextualizes Grail data via `includes` (per-`dataObject` filters) and optional `variables`.
- **Visibility:** `isPublic` `false` = private to owner; `true` = visible to everyone in the environment (requires `storage:filter-segments:share`).
- Use `getLeanFilterSegments` for faster, minimal responses when details aren't needed.
- Optimistic locking via version on updates.
- Filter syntax requires quoting special field names.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-filter-segment-management/
