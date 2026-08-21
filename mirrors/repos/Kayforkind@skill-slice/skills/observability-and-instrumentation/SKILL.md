---
name: observability-and-instrumentation
description: "Instruments production features with structured event logs, RED/USE metrics, OpenTelemetry traces, and page-vs-ticket alerts written beside the code. Use when adding logging, metrics, tracing, or alerting, or when incidents lacked evidence. Not for debugging a live outage (debugging-and-error-recovery), Lighthouse CI budgets, or Spark/Android profilers."
version: 1.0.1
---

# Observability and Instrumentation

## Overview

Code you can't observe is code you can't operate. Observability is the ability to answer "what is the system doing and why?" from the outside, using the telemetry the code emits. Instrumentation is not a post-launch add-on — it's written alongside the feature, the same way tests are. If a feature ships without telemetry, the first user-reported bug becomes archaeology instead of a query.

## When to Use

- Building any feature that will run in production
- Adding a new service, endpoint, background job, or external integration
- A production incident took too long to diagnose ("we couldn't tell what happened")
- Setting up or reviewing alerting rules
- Reviewing a PR that adds I/O, retries, queues, or cross-service calls

**NOT for:**
- Diagnosing a failure happening right now — use the `debugging-and-error-recovery` skill (observability is what makes that skill fast next time)
- Profiling and optimizing measured slowness — use the `performance-optimization` skill
- Launch-day monitoring checklists and rollback triggers — see the `shipping-and-launch` skill; this skill covers the instrumentation that feeds them

## Prerequisites

- A structured logging library available in the project (e.g., `pino`, `winston`, `serilog`, `structlog`). If only `console.log` exists, install a structured logger first.
- An OpenTelemetry SDK compatible with the project's runtime (e.g., `@opentelemetry/sdk-node`, `opentelemetry-java`, `opentelemetry-python`). Auto-instrumentation packages for HTTP, gRPC, and common DB clients should be installed.
- A metrics backend or library (e.g., `prom-client` for Prometheus, OpenTelemetry metrics API, or vendor SDK). The RED/USE and cardinality rules apply regardless of backend.
- A tracing backend or collector endpoint configured (e.g., Jaeger, Tempo, OTLP collector).
- An alerting destination configured (e.g., PagerDuty, Slack, Opsgenie) with at least two severities: page and ticket.
- For Windows hosts (PowerShell primary): ensure environment variables for service names, OTLP endpoints, and resource attributes are set in the active shell session before starting the instrumented process.

## Procedure

### 1. Define "working" before instrumenting

Telemetry without a question is noise. Before adding any instrumentation, write down 2–4 questions an on-call engineer will ask about this feature:

```
FEATURE: checkout payment retry
QUESTIONS ON-CALL WILL ASK:
1. What fraction of payments succeed on first attempt vs after retry?
2. When a payment fails permanently, why? (provider error? timeout? validation?)
3. Is the payment provider slower than usual?
→ Every signal below must help answer one of these.
```

If you can't name the questions, you're not ready to instrument — you'll log everything and learn nothing.

### 2. Pick the right signal for each question

| Signal | Answers | Cost profile | Example |
|---|---|---|---|
| **Structured log** | "What happened in this specific case?" | Per-event; grows with traffic | `payment_failed` with provider error code |
| **Metric** | "How often / how fast, in aggregate?" | Fixed per series; cheap to query | p99 latency of provider calls |
| **Trace** | "Where did time go across services?" | Per-request; usually sampled | One slow checkout, broken down by hop |

Rule of thumb: metrics tell you **that** something is wrong, traces tell you **where**, logs tell you **why**.

### 3. Structured logging

Log events, not prose. Every log line is a JSON object with a stable event name and machine-readable fields:

```typescript
// BAD: string interpolation — unqueryable, inconsistent
logger.info(`Payment ${id} failed for user ${userId} after ${n} retries`);

// GOOD: stable event name + structured fields
logger.warn({
  event: 'payment_failed',
  paymentId: id,
  provider: 'stripe',
  errorCode: err.code,
  attempt: n,
}, 'payment failed');
```

**Log levels — use them consistently:**

| Level | Meaning | On-call action |
|---|---|---|
| `error` | Invariant broken; someone may need to act | Investigate |
| `warn` | Degraded but handled (retry succeeded, fallback used) | Watch for trends |
| `info` | Significant business event (order placed, job finished) | None |
| `debug` | Diagnostic detail | Off in production by default |

**Correlation IDs are mandatory.** Generate (or accept) a request ID at the system boundary and attach it to every log line, span, and outbound call. Without it, you cannot reconstruct a single request from interleaved logs:

```typescript
// Express: child logger per request, ID propagated downstream
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] ?? crypto.randomUUID();
  req.log = logger.child({ requestId: req.id });
  res.setHeader('x-request-id', req.id);
  next();
});
```

**Never log secrets, tokens, passwords, or full PII.** This is a hard rule — telemetry pipelines are a classic data-leak path. Allowlist fields; don't log whole request bodies.

### 4. Metrics

For request-driven services, instrument **RED** on every endpoint and every external dependency: **R**ate (requests/sec), **E**rrors (failure rate), **D**uration (latency histogram, not average). For resources (queues, pools, hosts), use **USE**: **U**tilization, **S**aturation, **E**rrors.

The vendor-neutral path is the OpenTelemetry metrics API (same SDK and context as tracing in step 5). The example below uses Prometheus' `prom-client` — one common backend choice, not the only one; the RED/USE and cardinality rules are identical either way.

```typescript
import { Histogram } from 'prom-client';

const httpDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'route', 'status_class'],  // '2xx', not '200'
  buckets: [0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
});
```

**Cardinality is the failure mode.** Every unique label combination is a separate time series. Labels must come from small, fixed sets (route template, status class, provider name). Never use user IDs, raw URLs, error messages, or other unbounded values as labels — that belongs in logs and traces.

```
OK as label:    route="/api/tasks/:id"   status_class="5xx"   provider="stripe"
NEVER a label:  user_id, email, request_id, full URL, error message text
```

Track averages never, percentiles always: an average hides the 1% of users having a terrible time. Use histograms and read p50/p95/p99.

### 5. Distributed tracing

Use OpenTelemetry — it's the vendor-neutral standard, and auto-instrumentation covers HTTP, gRPC, and common DB clients with near-zero code:

```typescript
// tracing.ts — must be imported before anything else
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';

const sdk = new NodeSDK({
  serviceName: 'checkout-service',
  instrumentations: [getNodeAutoInstrumentations()],
});
sdk.start();
```

Add manual spans only around meaningful internal units of work (e.g., `applyDiscounts`, `chargeProvider`) and attach the attributes on-call will filter by. Propagate context across every async boundary — HTTP headers, queue message metadata — or the trace dies at the gap. Sample head-based at a low rate by default; keep 100% of errors if your backend supports tail sampling.

**Windows (PowerShell) startup note:** Set the OTLP exporter endpoint and service name as environment variables before launching the process:

```powershell
$env:OTEL_EXPORTER_OTLP_ENDPOINT = "http://localhost:4317"
$env:OTEL_SERVICE_NAME = "checkout-service"
node --require ./tracing.ts dist/index.js
```

### 6. Alerting

Alert on **symptoms users feel**, not on causes:

```
SYMPTOM (page-worthy):           CAUSE (dashboard, not a page):
error rate > 1% for 5 min        CPU at 85%
p99 latency > 2s                 one pod restarted
queue age > 10 min                disk at 70%
```

Cause-based alerts fire when nothing is wrong and miss failures you didn't predict. Symptom-based alerts fire exactly when users are hurt, regardless of the cause.

Rules for every alert you create:

1. **It must be actionable.** If the response is "ignore it, it self-heals", delete the alert.
2. **It links to a runbook** — even three lines: what it means, first query to run, escalation path.
3. **It has a threshold and duration** justified by the SLO or by historical data, not by a guess.
4. Use two severities only: **page** (user-facing, act now) and **ticket** (degradation, act this week). A third tier becomes noise that trains people to ignore everything.

### 7. Verify the telemetry itself

Instrumentation is code; it can be wrong. Before calling the work done, trigger the paths and look at the actual output:

1. Force an error in staging → find it in the logs by `requestId`, confirm fields are structured (not `[object Object]`)
2. Send test traffic → confirm metric series appear with the expected labels and sane values
3. Follow one request across services in the tracing UI → no broken spans
4. Fire each new alert once (lower the threshold temporarily) → confirm it reaches the right channel and the runbook link works

### 8. Sign off against the checklist

Before marking instrumentation complete, run the Verification checklist in this file as the pre-launch instrumentation gate.

## Pitfalls

| Rationalization | Reality |
|---|---|
| "I'll add logging after it works" | "After" becomes "after the first incident", which is the most expensive moment to discover you're blind. Instrument as you build. |
| "More logs = more observability" | Unstructured noise makes incidents slower, not faster. Three queryable events beat three hundred prose lines. |
| "console.log is fine for now" | Unstructured output can't be filtered, correlated, or alerted on. The structured logger costs five extra minutes once. |
| "We can just look at the dashboards when something breaks" | Dashboards built without defined questions show you everything except the answer. Start from on-call questions. |
| "Alert on everything important, we'll tune later" | A noisy pager trains people to ignore it. The tuning never happens; the missed real page does. |
| "User ID as a metric label makes debugging easier" | It also makes your metrics backend fall over. High-cardinality lookups belong in logs and traces. |
| "Tracing is overkill for our two services" | Two services already means cross-service latency questions logs can't answer. Auto-instrumentation makes the cost trivial. |

**Red flags to reject in review:**

- A feature PR with retries, queues, or external calls and zero new telemetry
- Log lines built by string interpolation instead of structured fields
- No correlation/request ID — each log line is an orphan
- Metrics labeled with user IDs, raw URLs, or error message text (cardinality bomb)
- Latency tracked as an average with no percentiles
- Alerts that fire daily and get acknowledged without action
- Alerts on causes (CPU, memory) paging humans while user-facing error rate is unmonitored
- Secrets, tokens, or full request bodies appearing in logs
- "It works on my machine" as the only evidence a production feature is healthy

## Verification

After instrumenting a feature, confirm each item:

- [ ] The on-call questions for this feature are written down, and each signal maps to one
- [ ] All log output is structured (JSON), with stable event names and a correlation ID on every line
- [ ] No secrets, tokens, or unredacted PII in any log line (spot-check actual output)
- [ ] RED metrics exist for every new endpoint and every external dependency, with bounded label sets
- [ ] Latency is a histogram; p95/p99 are queryable
- [ ] A single request can be followed end-to-end in the tracing UI without broken spans
- [ ] Every new alert is symptom-based, has a runbook link, and was test-fired once
- [ ] An induced failure in staging was located via telemetry alone, without reading the source

**Checkable commands:**

```bash
# Confirm structured JSON logs with requestId present
grep -o '"requestId":"[^"]*"' staging.log | head -5

# Confirm Prometheus metric series exist with expected labels
curl -s http://localhost:9464/metrics | grep http_request_duration_seconds_count

# Confirm trace spans exported (adjust endpoint/port to your collector)
curl -s http://localhost:4317/health
```

```powershell
# Windows (PowerShell): confirm structured JSON logs with requestId present
Select-String -Path .\staging.log -Pattern '"requestId":"[^"]*"' | Select-Object -First 5

# Windows (PowerShell): confirm metric series
Invoke-RestMethod -Uri http://localhost:9464/metrics | Select-String "http_request_duration_seconds_count"
```

The at-a-glance pre-launch gate is the Verification checklist above.

## Related skills

- `debugging-and-error-recovery` — use when a failure is happening right now; this skill makes that one faster next time
- `performance-optimization` — use when profiling measured slowness; this skill provides the metrics that reveal it
- `shipping-and-launch` — use for launch-day monitoring checklists and rollback triggers; this skill covers the instrumentation that feeds them
- `security-and-hardening` — source of the hard rule: never log secrets, tokens, passwords, or full PII
