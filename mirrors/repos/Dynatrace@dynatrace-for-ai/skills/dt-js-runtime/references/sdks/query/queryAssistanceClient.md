# `queryAssistanceClient`

Dev-time DQL assistance — autocomplete, parse, verify. None execute the query. Import:

```ts
import { queryAssistanceClient } from "@dynatrace-sdk/client-query";
```

| Method | Returns | Purpose |
|---|---|---|
| `queryAutocomplete` | `AutocompleteResponse` | Structured list of suggestions for the query at a given cursor position. Body is an `AutocompleteRequest` (`query`, position). |
| `queryParse` | `DQLNode` | Structured tree of the canonical form of the query. Body is a `ParseRequest`. |
| `queryVerify` | `VerifyResponse` | Verify a query for validity without executing it. Body is a `VerifyRequest`. |

Permissions are per Grail bucket/table — see [README](README.md#required-scopes).

## Example

```ts
import { queryAssistanceClient } from "@dynatrace-sdk/client-query";

const data = await queryAssistanceClient.queryParse({
  body: { query: "fetch events | filter event.type == \"davis\" | limit 10" },
});
```

Token types (returned by parse) can be `USER` (written by the user), `CANONICAL` (normalized form), or `INFO` (explanatory, e.g. `condition:` prefix), among the `TokenType` enum (see [types.md](types.md)).
