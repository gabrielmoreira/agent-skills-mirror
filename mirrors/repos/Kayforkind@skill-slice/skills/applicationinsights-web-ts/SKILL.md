---
name: applicationinsights-web-ts
description: Instrument browser/web apps with @microsoft/applicationinsights-web for Real User Monitoring (RUM), page views, clicks, AJAX/fetch dependencies, exceptions, custom events, and browser-side GenAI agent traces. Use when adding App Insights to React, Angular, Vite, Next.js, or React Native frontends. Not for Node.js server OpenTelemetry (azure-monitor-opentelemetry-ts).
version: 1.0.1
risk: unknown
source: https://github.com/microsoft/skills/tree/main/.github/plugins/azure-sdk-typescript/skills/applicationinsights-web-ts
source_repo: microsoft/skills
source_type: official
date_added: 2026-07-01
license: MIT
license_source: https://github.com/microsoft/skills/blob/main/LICENSE
---

# Application Insights JavaScript SDK (Web) for TypeScript

## When to Use

Use this skill when you need to instrument browser/web apps with the Application Insights JavaScript SDK (`@microsoft/applicationinsights-web`). Use for Real User Monitoring (RUM) — page views, clicks, AJAX/fetch dependencies, exceptions, custom events, and browser-side GenAI agent traces correlated to backend spans via W3C Trace Context.

**Trigger keywords:** Application Insights, RUM, browser telemetry, `@microsoft/applicationinsights-web`, trackPageView, trackEvent, trackException, web vitals, GenAI agent traces, click analytics, SPA route tracking, distributed tracing browser.

> **Distinct from `azure-monitor-opentelemetry-ts`**, which is for Node.js server apps. This skill is for **browser/web** code (and React Native).

## Prerequisites

1. **Verify package version before coding:**
   ```powershell
   npm view @microsoft/applicationinsights-web version
   ```

2. **Search `microsoft-docs` MCP for current API patterns:**
   - Query: `"Application Insights JavaScript SDK setup"`
   - Query: `"Application Insights JavaScript SDK configuration"`
   - Query: `"Application Insights JavaScript framework extensions React Angular"`

3. **Connection string** — The browser SDK requires a connection string at init time. **It ships in plaintext to clients** — Microsoft Entra ID auth is not supported for browser telemetry. Use a separate App Insights resource with local auth enabled for browser RUM if you need to isolate it from backend telemetry.

4. **Windows host (PowerShell) is primary.** All shell commands below are PowerShell-compatible.

## Procedure

### 1. Install Packages

```powershell
npm i --save @microsoft/applicationinsights-web
# Optional plugins (install only what you use):
npm i --save @microsoft/applicationinsights-clickanalytics-js
npm i --save @microsoft/applicationinsights-react-js @microsoft/applicationinsights-react-native @microsoft/applicationinsights-angularplugin-js
```

Typings ship with the package — no separate `@types/...` install needed.

| Package | Purpose |
| --- | --- |
| `@microsoft/applicationinsights-web` | Core RUM SDK (page views, AJAX, exceptions). |
| `@microsoft/applicationinsights-clickanalytics-js` | Auto-collect click telemetry. |
| `@microsoft/applicationinsights-react-js` | React plugin (router instrumentation, hooks, HOC, ErrorBoundary). |
| `@microsoft/applicationinsights-react-native` | React Native plugin (native crashes, sessions). |
| `@microsoft/applicationinsights-angularplugin-js` | Angular plugin (router events, ErrorHandler). |
| `@microsoft/applicationinsights-debugplugin-js` | Dev-only telemetry inspector. |
| `@microsoft/applicationinsights-perfmarkmeasure-js` | User Timing (`performance.mark/measure`) integration. |

### 2. Expose Connection String to Client

```powershell
# Vite / CRA / Next.js — expose to client via the public env prefix
$env:VITE_APPINSIGHTS_CONNECTION_STRING="InstrumentationKey=YOUR_KEY;IngestionEndpoint=https://...;LiveEndpoint=https://..."
$env:NEXT_PUBLIC_APPINSIGHTS_CONNECTION_STRING="InstrumentationKey=YOUR_KEY"
```

### 3. Initialize (npm path)

```typescript
import { ApplicationInsights } from "@microsoft/applicationinsights-web";

export const appInsights = new ApplicationInsights({
  config: {
    connectionString: import.meta.env.VITE_APPINSIGHTS_CONNECTION_STRING,
    enableAutoRouteTracking: true,        // SPA route changes -> page views
    enableCorsCorrelation: true,          // propagate Request-Id / traceparent to cross-origin AJAX
    enableRequestHeaderTracking: true,
    enableResponseHeaderTracking: true,
    distributedTracingMode: 2,            // DistributedTracingModes.AI_AND_W3C
    autoTrackPageVisitTime: true,
    disableFetchTracking: false,          // fetch() is auto-instrumented by default
    excludeRequestFromAutoTrackingPatterns: [/livemetrics\.azure\.com/i]
  }
});

appInsights.loadAppInsights();
appInsights.trackPageView();
```

**HARD RULE:** Call `loadAppInsights()` exactly once, as early as possible (before user interactions you want tracked). Then `trackPageView()` for the initial load — when `enableAutoRouteTracking` is on, subsequent route changes are automatic.

### 4. Alternative: SDK Loader Script (zero build pipeline)

Paste this as the **first** `<script>` in `<head>`:

```html
<script type="text/javascript" src="https://js.monitor.azure.com/scripts/b/ai.3.gbl.min.js" crossorigin="anonymous"></script>
<script type="text/javascript">
  var appInsights = window.appInsights || function (cfg) {
    /* See: https://learn.microsoft.com/azure/azure-monitor/app/javascript-sdk
       Use the latest snippet from the Microsoft Learn page above — it includes
       backup-CDN failover (cr), SDK-load-failure reporting, and the queue shim
       so calls before SDK ready are not lost. */
  }({ src: "https://js.monitor.azure.com/scripts/b/ai.3.gbl.min.js",
      crossOrigin: "anonymous",
      cfg: { connectionString: "YOUR_CONNECTION_STRING" } });
</script>
```

Loader-only API (queued until SDK loads): `trackEvent`, `trackPageView`, `trackException`, `trackTrace`, `trackDependencyData`, `trackMetric`, `trackPageViewPerformance`, `startTrackPage`, `stopTrackPage`, `startTrackEvent`, `stopTrackEvent`, `addTelemetryInitializer`, `setAuthenticatedUserContext`, `clearAuthenticatedUserContext`, `flush`.

### 5. Core Tracking APIs

```typescript
// Page views (SPAs that disable enableAutoRouteTracking)
appInsights.trackPageView({ name: "Checkout", uri: "/checkout", properties: { cartSize: 3 } });

// Custom events (user actions, business events)
appInsights.trackEvent({ name: "PurchaseCompleted" }, { orderId: "ord_123", amountUsd: 49.95 });

// Exceptions (caught errors)
try {
  await pay(order);
} catch (err) {
  appInsights.trackException({ exception: err as Error, severityLevel: 3, properties: { orderId: order.id } });
}

// Traces (logs, severity 0=Verbose, 1=Info, 2=Warning, 3=Error, 4=Critical)
appInsights.trackTrace({ message: "Cart hydrated from local storage", severityLevel: 1 });

// Custom metrics (numeric)
appInsights.trackMetric({ name: "checkout.duration_ms", average: 1234 });

// Dependencies (manually-tracked outbound calls — fetch/XHR are auto-tracked)
appInsights.trackDependencyData({
  id: crypto.randomUUID(),
  name: "GET /api/orders",
  duration: 87, success: true, responseCode: 200,
  data: "https://api.example.com/api/orders", target: "api.example.com", type: "Fetch"
});

// User identity (set ONCE per authenticated session — values are PII; do not pass emails)
appInsights.setAuthenticatedUserContext("user-id-123", "tenant-456", /*storeInCookie*/ true);
appInsights.clearAuthenticatedUserContext(); // on logout

// Force send before unload
appInsights.flush();
```

### 6. Telemetry Initializers (enrichment & filtering)

Run for every envelope before send. Return `false` to drop.

```typescript
import type { ITelemetryItem } from "@microsoft/applicationinsights-web";

appInsights.addTelemetryInitializer((item: ITelemetryItem) => {
  item.tags ??= {};
  item.tags["ai.cloud.role"] = "web-shop";
  item.tags["ai.cloud.roleInstance"] = window.location.hostname;
  item.data ??= {};
  item.data["app.version"] = import.meta.env.VITE_APP_VERSION;
  item.data["app.build"] = import.meta.env.VITE_BUILD_SHA;

  // Drop noisy health-check page views
  if (item.baseType === "PageviewData" && item.baseData?.uri?.endsWith("/healthz")) return false;

  // Scrub query-string secrets
  if (item.baseData?.uri) {
    item.baseData.uri = item.baseData.uri.replace(/([?&](token|sig|key)=)[^&]+/gi, "$1REDACTED");
  }
});
```

### 7. Click Analytics

```typescript
import { ClickAnalyticsPlugin } from "@microsoft/applicationinsights-clickanalytics-js";

const clickPlugin = new ClickAnalyticsPlugin();
const appInsights = new ApplicationInsights({
  config: {
    connectionString: import.meta.env.VITE_APPINSIGHTS_CONNECTION_STRING,
    extensions: [clickPlugin],
    extensionConfig: {
      [clickPlugin.identifier]: {
        autoCapture: true,
        dataTags: { useDefaultContentNameOrId: true, customDataPrefix: "data-ai-" },
        urlCollectHash: false,
        behaviorValidator: (b: string) => /^[a-z0-9_]+$/.test(b) ? b : ""
      }
    }
  }
});
appInsights.loadAppInsights();
```

Mark elements with `data-ai-*` attributes; clicks are emitted as Custom Events with parent-content metadata.

### 8. SPA Route Tracking

- **Built-in:** set `enableAutoRouteTracking: true`. Hooks `history.pushState/replaceState` and `popstate`.
- **React Router:** use `@microsoft/applicationinsights-react-js` `withAITracking` HOC. Use the React recipe in this file (step 11) and Microsoft Learn for Angular, Next.js, or Vite plugins.
- **Manual:** call `appInsights.trackPageView({ name, uri })` in your router's `useEffect` on route change. Disable `enableAutoRouteTracking` to avoid double counting.

### 9. Distributed Tracing (correlate to backend)

Set `distributedTracingMode: 2` (`DistributedTracingModes.AI_AND_W3C`). The SDK adds `traceparent` (and legacy `Request-Id`) to outbound `fetch`/`XHR`. Backends instrumented with **OpenTelemetry** (e.g. `@azure/monitor-opentelemetry`) auto-link to the browser's operation_Id.

For cross-origin calls, also set `enableCorsCorrelation: true` and add the calling origin to the **CORS exposed headers** on the API.

### 10. GenAI Agent Traces (OTel semantic conventions)

When the browser invokes an AI agent (function-calling, tool-use, model calls direct from the client), emit App Insights **Dependency** telemetry whose attributes follow the OpenTelemetry **GenAI semantic conventions** so they are queryable alongside backend agent spans.

**Set the opt-in env first** so backend instrumentations agree on the same schema version:

```powershell
$env:OTEL_SEMCONV_STABILITY_OPT_IN="gen_ai_latest_experimental"
```

Use the GenAI attribute tables and content-capture rules in this section when emitting traces. Full OTel names: https://opentelemetry.io/docs/specs/semconv/gen-ai/

#### Required attribute keys (use the OTel names verbatim)

| Span / op | Required attributes |
| --- | --- |
| `invoke_agent {agent.name}` | `gen_ai.operation.name=invoke_agent`, `gen_ai.provider.name`, `gen_ai.agent.name`, `gen_ai.agent.id` (when known) |
| `create_agent {agent.name}` | `gen_ai.operation.name=create_agent`, `gen_ai.provider.name`, `gen_ai.agent.name`, `gen_ai.request.model` |
| `chat {model}` | `gen_ai.operation.name=chat`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |
| `execute_tool {tool.name}` | `gen_ai.operation.name=execute_tool`, `gen_ai.tool.name`, `gen_ai.tool.type` (`function` \| `extension` \| `datastore`), `gen_ai.tool.call.id` |

`gen_ai.provider.name` well-known values: `openai`, `azure.ai.openai`, `azure.ai.inference`, `anthropic`, `aws.bedrock`, `gcp.gemini`, `gcp.vertex_ai`, `cohere`, `mistral_ai`, `groq`, `deepseek`, `perplexity`, `x_ai`, `ibm.watsonx.ai`.

> **HARD RULE — Sensitive content opt-in.** `gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result` are **Opt-In** by default. Gate them behind a runtime flag and avoid them in production unless you have approved data handling.

#### Pattern: invoke_agent + nested tool/model spans

```typescript
import { ApplicationInsights, SeverityLevel } from "@microsoft/applicationinsights-web";

type GenAiAttrs = Record<string, string | number | boolean | undefined>;

function startGenAiSpan(name: string, attrs: GenAiAttrs) {
  const id = crypto.randomUUID();
  const start = performance.now();
  const baseProps: GenAiAttrs = { "gen_ai.span.id": id, ...attrs };
  return {
    end(success: boolean, extra: GenAiAttrs = {}, error?: Error) {
      const duration = Math.round(performance.now() - start);
      const properties = { ...baseProps, ...extra };
      appInsights.trackDependencyData({
        id, name, duration, success,
        responseCode: error ? 500 : 200,
        type: "GenAI",
        target: String(attrs["gen_ai.provider.name"] ?? "genai"),
        properties: properties as Record<string, string>
      });
      if (error) {
        appInsights.trackException({
          exception: error,
          severityLevel: SeverityLevel.Error,
          properties: { ...properties, "error.type": error.name } as Record<string, string>
        });
      }
    }
  };
}

// Agent invocation
const agentSpan = startGenAiSpan("invoke_agent ResearchAssistant", {
  "gen_ai.operation.name": "invoke_agent",
  "gen_ai.provider.name": "azure.ai.openai",
  "gen_ai.agent.name": "ResearchAssistant",
  "gen_ai.agent.id": "asst_5j66UpCpwteGg4YSxUnt7lPY",
  "gen_ai.request.model": "gpt-4o-mini",
  "server.address": "myresource.openai.azure.com"
});

try {
  // Nested chat completion span
  const chat = startGenAiSpan("chat gpt-4o-mini", {
    "gen_ai.operation.name": "chat",
    "gen_ai.provider.name": "azure.ai.openai",
    "gen_ai.request.model": "gpt-4o-mini"
  });
  const res = await callAzureOpenAi(/* ... */);
  chat.end(true, {
    "gen_ai.response.model": res.model,
    "gen_ai.response.id": res.id,
    "gen_ai.response.finish_reasons": JSON.stringify(res.choices.map(c => c.finish_reason)),
    "gen_ai.usage.input_tokens": res.usage.prompt_tokens,
    "gen_ai.usage.output_tokens": res.usage.completion_tokens,
    "gen_ai.output.type": "text"
  });

  // Nested tool execution span
  const tool = startGenAiSpan("execute_tool getWeather", {
    "gen_ai.operation.name": "execute_tool",
    "gen_ai.tool.name": "getWeather",
    "gen_ai.tool.type": "function",
    "gen_ai.tool.call.id": "call_abc123"
  });
  const toolResult = await runGetWeather({ location: "SF" });
  tool.end(true);

  agentSpan.end(true, {
    "gen_ai.usage.input_tokens": res.usage.prompt_tokens,
    "gen_ai.usage.output_tokens": res.usage.completion_tokens
  });
} catch (err) {
  agentSpan.end(false, { "error.type": (err as Error).name }, err as Error);
}
```

The browser's `traceparent` is automatically attached to outbound `fetch` (when `distributedTracingMode: 2`), so downstream Azure OpenAI / agent backend spans hang under the same operation_Id in App Insights.

#### KQL: query GenAI traces in App Insights

```kusto
dependencies
| where type == "GenAI"
| extend op   = tostring(customDimensions["gen_ai.operation.name"]),
         agent = tostring(customDimensions["gen_ai.agent.name"]),
         model = tostring(customDimensions["gen_ai.request.model"]),
         tin   = toint(customDimensions["gen_ai.usage.input_tokens"]),
         tout  = toint(customDimensions["gen_ai.usage.output_tokens"])
| summarize calls=count(), p95_ms=percentile(duration, 95),
            avg_in=avg(tin), avg_out=avg(tout) by op, agent, model, bin(timestamp, 5m)
```

### 11. React (TypeScript)

React and React Native recipes follow in this file. For Angular/Next/Vite plugins, use the official packages listed in step 1 and Microsoft Learn.

```typescript
import { ApplicationInsights } from "@microsoft/applicationinsights-web";
import { ReactPlugin, withAITracking } from "@microsoft/applicationinsights-react-js";
import { createBrowserHistory } from "history";

const reactPlugin = new ReactPlugin();
const browserHistory = createBrowserHistory();

export const appInsights = new ApplicationInsights({
  config: {
    connectionString: import.meta.env.VITE_APPINSIGHTS_CONNECTION_STRING,
    extensions: [reactPlugin],
    extensionConfig: { [reactPlugin.identifier]: { history: browserHistory } }
  }
});
appInsights.loadAppInsights();

export const TrackedCheckout = withAITracking(reactPlugin, Checkout, "Checkout");
```

### 12. React Native

```typescript
import { ApplicationInsights } from "@microsoft/applicationinsights-web";
import { ReactNativePlugin } from "@microsoft/applicationinsights-react-native";

const rnPlugin = new ReactNativePlugin();
const appInsights = new ApplicationInsights({
  config: {
    connectionString: process.env.EXPO_PUBLIC_APPINSIGHTS_CONNECTION_STRING,
    extensions: [rnPlugin],
    disableFetchTracking: false
  }
});
appInsights.loadAppInsights();
```

### 13. Performance — Web Vitals

Auto-collected: page-load timings via `PerformanceTiming` / `PerformanceNavigationTiming`. To add Core Web Vitals:

```typescript
import { onCLS, onLCP, onINP, type Metric } from "web-vitals";

function send(m: Metric) {
  appInsights.trackMetric(
    { name: `web_vitals.${m.name.toLowerCase()}`, average: m.value },
    { rating: m.rating, navigationType: m.navigationType, id: m.id }
  );
}
onCLS(send); onLCP(send); onINP(send);
```

### 14. Cookies & Privacy

```typescript
new ApplicationInsights({ config: {
  connectionString,
  isCookieUseDisabled: true,         // hard-disable all cookies
  cookieCfg: { enabled: true, domain: ".example.com", path: "/", expiry: 365 }
}});
```

To honor consent dynamically:

```typescript
appInsights.getCookieMgr().setEnabled(userGaveConsent);
appInsights.config.disableTelemetry = !userGaveConsent;
```

### 15. Sampling

Server-side ingestion sampling (recommended) is configured on the App Insights resource. SDK-side sampling reduces network use:

```typescript
new ApplicationInsights({ config: { connectionString, samplingPercentage: 50 } });
```

Per-type sampling via telemetry initializer: drop with `return false` based on `item.baseType`.

### 16. Offline / Send-on-Unload

The SDK uses `sendBeacon` (default `onunloadDisableBeacon: false`) to flush on `pagehide` / `unload`. For SPAs, also call `appInsights.flush()` before destructive transitions (logout, hard reload).

## Pitfalls

1. **Do not initialize twice.** Re-importing the module under different bundles produces duplicate page views. Use a single shared module export.
2. **Initialize before first user input** to avoid losing early clicks/exceptions.
3. **Connection string is public** — never reuse the same App Insights resource for backend secrets.
4. **`enableAutoRouteTracking` + manual `trackPageView`** = duplicates. Pick one.
5. **CORS distributed tracing** requires the API to allow `Request-Id`, `Request-Context`, `traceparent`, `tracestate` request headers and expose `Request-Context` response header.
6. **GenAI sensitive content** (`gen_ai.input.messages` etc.) is Opt-In — never log without an explicit runtime flag and approved data handling.
7. **Agent token usage is on `chat` spans, not `invoke_agent`** — copy aggregated usage to the parent agent span only if you know it.
8. **React StrictMode** double-invokes effects in dev — guard `loadAppInsights()` with a module-level singleton.

## Verification

1. **Check SDK loaded in browser console:**
   ```javascript
   // Should return the ApplicationInsights instance, not undefined
   console.log(window.appInsights ?? appInsights);
   ```

2. **Verify telemetry is flowing** — open the App Insights portal > Transaction Search, or run KQL in Log Analytics:
   ```kusto
   pageViews
   | where timestamp > ago(10m)
   | summarize count() by name
   ```

3. **Verify GenAI traces:**
   ```kusto
   dependencies
   | where type == "GenAI"
   | where timestamp > ago(10m)
   | project timestamp, name, duration, customDimensions["gen_ai.operation.name"], customDimensions["gen_ai.agent.name"]
   ```

4. **Verify distributed tracing correlation** — check that backend dependency telemetry shares the same `operation_Id` as the browser page view:
   ```kusto
   pageViews
   | where timestamp > ago(10m)
   | join kind=inner (dependencies | where type == "Fetch") on operation_Id
   | project operation_Id, name, type
   ```

5. **Bundle size check** — the full web SDK is ~110 KB minified (~36 KB gzipped). For aggressive budgets, use the Loader Script path or tree-shake unused plugins.

## Key Types

```typescript
import {
  ApplicationInsights,
  SeverityLevel,
  DistributedTracingModes,
  type IConfiguration,
  type IConfig,
  type ITelemetryItem,
  type ITelemetryPlugin,
  type ICustomProperties,
  type IPageViewTelemetry,
  type IEventTelemetry,
  type IExceptionTelemetry,
  type ITraceTelemetry,
  type IMetricTelemetry,
  type IDependencyTelemetry
} from "@microsoft/applicationinsights-web";
```

## Best Practices

1. **One singleton instance** exported from a single module.
2. **Initialize early** in the app entrypoint, before router setup.
3. **Use telemetry initializers** to attach `app.version`, `tenantId`, and to scrub PII / query-string secrets.
4. **Set `distributedTracingMode: 2`** and ensure your APIs accept/expose W3C trace context headers.
5. **For GenAI**, follow OTel `gen_ai.*` attribute names verbatim — they are queryable across browser and backend telemetry uniformly.
6. **Gate sensitive content capture** (`gen_ai.input.messages` / `gen_ai.output.messages`) behind a build-time or runtime opt-in.
7. **Flush on logout / sensitive navigation** so in-flight telemetry isn't dropped.

## References

- Microsoft Learn (SDK setup, configuration, framework plugins): <https://learn.microsoft.com/azure/azure-monitor/app/javascript-sdk>
- ApplicationInsights-JS source: <https://github.com/microsoft/ApplicationInsights-JS>
- OTel GenAI semantic conventions: <https://opentelemetry.io/docs/specs/semconv/gen-ai/>
- GenAI attribute tables, React/RN recipes, and `IConfiguration` knobs used in this file (steps 3, 10–11, 14–15). This folder does not ship a references pack.

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
