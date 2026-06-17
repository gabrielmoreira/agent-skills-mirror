# Davis AI Analyzers (`@dynatrace-sdk/client-davis-analyzers`)

> Env: ✅ Server runtime
> Status: current

Run Davis predictive and causal AI analyzers for custom ML analysis.

## Concepts

- **Async execution:** `executeAnalyzer` runs asynchronously. If a result isn't ready within the requested timeout it returns a `requestToken`; otherwise the final result is returned directly. Poll with `pollAnalyzerExecution` while `executionStatus === "RUNNING"`; cancel with `cancelAnalyzerExecution`. Results have a TTL.
- **Self-describing:** input/result JSON schemas and per-analyzer Markdown documentation are retrievable.
- **Naming:** "Davis AI" naming persists in APIs despite the "Dynatrace Intelligence" rebrand.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `analyzersClient` | `executeAnalyzer`, `pollAnalyzerExecution`, `cancelAnalyzerExecution` | Async execution lifecycle |
| `analyzersClient` | `getAnalyzer`, `queryAnalyzers`, `validateAnalyzerExecution` | Discovery & input validation |
| `analyzersClient` | `getAnalyzerDocumentation`, `getJsonSchemaForInput`, `getJsonSchemaForResult` | Docs & schemas |

Full method/type detail: [analyzersClient.md](analyzersClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Required scopes

- `davis:analyzers:read` (discovery/schemas), `davis:analyzers:execute` (validate/execute/poll/cancel). Some analyzers need extra scopes to read Grail data, e.g. `storage:buckets:read`, `storage:metrics:read`.

## Example

```ts
import { analyzersClient } from "@dynatrace-sdk/client-davis-analyzers";

const res = await analyzersClient.executeAnalyzer({ analyzerName: "...", body: { /* input */ } });
// poll with res.requestToken if not immediately SUCCEEDED
```

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-davis-analyzers/
