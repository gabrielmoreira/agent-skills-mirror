# Grail Resource Store (`@dynatrace-sdk/client-resource-store`)

> Env: ✅ Server runtime
> Status: current

Manage lookup data files in the Grail Resource Store, parsed with Dynatrace Pattern Language (DPL).

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `lookupDataClient` | `upload` | Upload lookup data with a DPL parse pattern |
| `lookupDataClient` | `uploadToTestPattern` | Preview parsing without persisting |
| `lookupDataClient` | `delete` | Remove a file (irreversible) |

Full method/type detail: [lookupDataClient.md](lookupDataClient.md) (per-method returns, scopes, examples) · [types.md](types.md).

## Required scopes

- `storage:files:write` (upload) / `storage:files:delete` (delete).

## Example

```ts
import { lookupDataClient } from "@dynatrace-sdk/client-resource-store";

const data = await lookupDataClient.upload({
  body: {
    content: "...",
    request: { filePath: "/lookups/mydata", lookupField: "id", parsePattern: "LD:id ',' LD:value" },
  },
});
```

## Notes

- File path rules (`filePath`): alphanumeric + `- _ . /`; must start with `/lookups`; end with `[a-zA-Z0-9]`; ≥ 2 `/`; ≤ 500 chars.
- A `lookupField` identifies a record; records are deduplicated by it on upload.
- Lookup files are parsed with **Dynatrace Pattern Language (DPL)** via `parsePattern` (e.g. `LD:id ',' LD:value`); each pattern match produces a record.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-resource-store/
