# `filterSegmentsClient`

Manage Grail filter-segments. Import:

```ts
import { filterSegmentsClient } from "@dynatrace-sdk/client-filter-segment-management";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createFilterSegment` | `DetailedFilterSegment` | `storage:filter-segments:write` (+ `:share` if `isPublic`) | Create a segment (`name`, optional `description`, `variables`, `includes`, `isPublic`). |
| `getFilterSegment` | `DetailedFilterSegment` | `storage:filter-segments:read` | Get one segment by `filterSegmentUid`. |
| `getFilterSegments` | `FilterSegments` | `storage:filter-segments:read` | Get all segments (full). Prefer lean if details not needed. |
| `getLeanFilterSegments` | `LeanFilterSegments` | `storage:filter-segments:read` | Get all segments in minimal form (faster). |
| `getFilterSegmentsEntityModel` | `FilterSegmentNamespaceDto` | `storage:filter-segments:read` | Get the filter-segment entity model. |
| `updateFilterSegment` | — | `storage:filter-segments:write` (+ `:share` for public) | Full update of a segment. |
| `partiallyUpdateFilterSegment` | — | `storage:filter-segments:write` (+ `:share` to set `isPublic` true) | Update a subset of `name`/`description`/`isPublic`/`variables`/`includes`; given `variables`/`includes` are overridden; requires `optimistic-locking-version`. |
| `deleteFilterSegment` | — | `storage:filter-segments:delete` | Remove a segment for all users. |

## Example

```ts
import { filterSegmentsClient } from "@dynatrace-sdk/client-filter-segment-management";

const seg = await filterSegmentsClient.createFilterSegment({
  body: {
    name: "dev_environment",
    isPublic: false,
    variables: { type: "query", value: "fetch logs | limit 1" },
    includes: [{ filter: "...", dataObject: "logs" }],
  },
});
```
