# `analyzersClient`

Run Davis predictive/causal analyzers. Import:

```ts
import { analyzersClient } from "@dynatrace-sdk/client-davis-analyzers";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `queryAnalyzers` | `AnalyzerQueryResult` | `davis:analyzers:read` | List analyzer definitions; `add-fields` (`input`, `output`, `category`, `type`, …), `filter`, paginated (`page-key`, default 50 / max 200). |
| `getAnalyzer` | `AnalyzerDefinitionDetails` | `davis:analyzers:read` | Full meta-info for one analyzer by `analyzerName`. |
| `getAnalyzerDocumentation` | Markdown | `davis:analyzers:read` | Markdown docs for an analyzer (not all have docs). |
| `getJsonSchemaForInput` | JSON schema | `davis:analyzers:read` | JSON schema for an analyzer's input. |
| `getJsonSchemaForResult` | JSON schema | `davis:analyzers:read` | JSON schema for an analyzer's result. |
| `validateAnalyzerExecution` | `AnalyzerValidationResult` | `davis:analyzers:execute` | Validate input without executing. |
| `executeAnalyzer` | `AnalyzerExecuteResult` | `davis:analyzers:execute` (+ Grail read scopes as needed) | Start an analyzer execution; returns result or a `requestToken`. Options: `preview`, `timeout` (s). |
| `pollAnalyzerExecution` | `AnalyzerPollResult` | `davis:analyzers:execute` | Poll by `requestToken` until `executionStatus !== "RUNNING"`. |
| `cancelAnalyzerExecution` | `AnalyzerCancelResult` | `davis:analyzers:execute` | Cancel a started execution by `requestToken`. |

## Example — execute + poll

```ts
import { analyzersClient } from "@dynatrace-sdk/client-davis-analyzers";

const res = await analyzersClient.executeAnalyzer({
  analyzerName: "dt.statistics.GenericForecastAnalyzer",
  body: { timeSeriesData: { expression: "timeseries avg(dt.host.cpu.usage)" }, forecastHorizon: 10 },
});
let r = res;
while (r.result?.executionStatus === "RUNNING" && r.requestToken) {
  r = await analyzersClient.pollAnalyzerExecution({ analyzerName: "...", requestToken: r.requestToken });
}
```
