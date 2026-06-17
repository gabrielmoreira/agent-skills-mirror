# `lookupDataClient`

Manage Grail lookup data files. Import:

```ts
import { lookupDataClient } from "@dynatrace-sdk/client-resource-store";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `upload` | `ResourceUploadResponse` | `storage:files:write` | Upload/parse a lookup file. Body: `content` + `request` (`filePath`, `lookupField`, `parsePattern` required; optional `overwrite`, `displayName`, `description`, `skippedRecords`, `timezone`, `locale`, `autoFlatten`). |
| `uploadToTestPattern` | `ResourceTestPatternResponse` | `storage:files:write` | Test a DPL parse pattern against sample data without persisting — returns parsed records + types. |
| `delete` | — | `storage:files:delete` | Delete a lookup file by `filePath`. |

## Upload request fields

- `filePath` (required) — see path rules in [README](README.md#notes).
- `parsePattern` (required) — DPL pattern; each match = one record (e.g. `LD:id ',' LD:value`).
- `lookupField` (required) — record-identifying field (dedup key).
- `overwrite` (default `false`), `skippedRecords` (default `0`, skip header rows), `displayName`/`description` (≤ 500 chars), `timezone` (IANA TZDB), `locale` (ISO-639[_ISO-3166]), `autoFlatten` (default `true`).

## Example

```ts
import { lookupDataClient } from "@dynatrace-sdk/client-resource-store";

await lookupDataClient.upload({
  body: {
    content: "...",
    request: { filePath: "/lookups/mydata", lookupField: "id", parsePattern: "LD:id ',' LD:value" },
  },
});
```
