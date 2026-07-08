# GenAI Golden Signals Reference

The four golden signals — traffic, errors, latency, and saturation — apply directly to GenAI applications instrumented with OpenTelemetry GenAI semantic conventions. Each GenAI call is captured as a span with `gen_ai.request.model` identifying the model, `gen_ai.provider.name` identifying the provider, `gen_ai.operation.name` identifying the operation type (`chat`, `execute_tool`, `invoke_agent`, `create_agent`), and token-usage fields (`gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`) on each span. Failures are identified by `span.status_code == "error"`. Latency is stored in the `duration` field — a Grail duration value (nanoseconds internally); divide by the `1ms` duration literal (`duration / 1ms`) to get a numeric millisecond value. Saturation for GenAI has no single CPU/memory proxy; it is provider-side and multi-dimensional. Providers enforce several rate limits simultaneously — most commonly tokens per minute (TPM) and requests per minute (RPM) — and a single request is throttled (HTTP 429) the moment any one dimension is exceeded, even if the others have headroom. TPM counts input and output tokens combined with equal weight, so the canonical token-saturation measure is total (input + output) tokens per minute, not output alone — input tokens (large context windows, retrieved documents, system prompts, tool schemas) frequently dominate. RPM is tracked by the request-throughput (Traffic) signal below.

---

## Traffic

Request throughput over time, broken down by one-minute buckets. Use this to detect traffic spikes, drops, or unexpected silence that may indicate an upstream or routing problem.

```dql
fetch spans, from: now()-1h
| filter isNotNull(gen_ai.request.model)
| summarize requests = count(), by: {bin(start_time, 1m)}
```

**How to read it:** Each row is one minute. `requests` is the number of GenAI span invocations in that bucket. A sustained drop to zero means no spans are being ingested — check instrumentation or the agent pipeline. A sudden spike may indicate a load test or runaway retry loop.

**Tip:** Replace `from: now()-1h` with `from: now()-7d` to see weekly patterns. Add `by: {bin(start_time, 1m), gen_ai.request.model}` to break out traffic per model.

**Saturation note:** This per-minute request count *is* the requests-per-minute (RPM) dimension of provider rate limiting. An agent that issues many small tool calls can exhaust RPM long before it approaches the token (TPM) limit, so read this signal alongside Token Throughput below — either dimension can trigger a 429.

---

## Errors

Error rate per model, ranked by the models with the highest share of failed spans. `span.status_code == "error"` is the correct failure predicate for GenAI spans — do not use `request.is_failed`, which is always `0` for this span type.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.request.model)
| summarize total = count(), errors = countIf(span.status_code == "error"), by: {gen_ai.request.model}
| fieldsAdd error_rate_pct = if(total > 0, errors * 100.0 / total, else: 0.0)
| sort error_rate_pct desc
```

**How to read it:** `error_rate_pct` is the percentage of spans that ended with an error status for each model. Values above ~1 % warrant investigation. Sort by `errors` (absolute count) rather than rate when overall volume differs greatly between models. Add `gen_ai.provider.name` to the `by:` clause to isolate errors to a specific provider.

---

## Latency

P50 and P95 response time per model in milliseconds.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.request.model)
| summarize p50_ms = percentile(duration, 50) / 1ms, p95_ms = percentile(duration, 95) / 1ms, by: {gen_ai.request.model}
| sort p95_ms desc
```

**How to read it:** `p50_ms` is the median round-trip time for a model call; `p95_ms` is the 95th-percentile tail latency. A large gap between P50 and P95 (e.g., P50 = 2 s, P95 = 30 s) indicates high variance — often caused by context-length outliers, cold-start timeouts, or rate-limit retries. Models that consistently sit at the top of the P95 sort are candidates for timeout tuning or load-shedding.

**Unit note:** Convert with the `1ms` duration literal (`/ 1ms`), not `/ 1000000.0` — dividing a duration by a plain number stays a nanosecond duration; only the literal yields a real millisecond number.

---

## Token Throughput (TPM)

Token throughput as a proxy for GenAI backend load. Unlike traditional services, GenAI has no single CPU or memory metric that reflects saturation; the token-per-minute (TPM) rate against the provider's limit is the closest equivalent. Provider TPM counts **input + output tokens combined**, so `total_tpm` — not output alone — is the value that approaches the rate limit. The query keeps the input/output split visible because input tokens (large context windows, retrieved documents, system prompts, tool schemas) usually dominate and are the first to saturate.

```dql
fetch spans, from: now()-1h
| filter isNotNull(gen_ai.usage.input_tokens) or isNotNull(gen_ai.usage.output_tokens)
| summarize
    total_tpm = sum(coalesce(gen_ai.usage.input_tokens, 0)) + sum(coalesce(gen_ai.usage.output_tokens, 0)),
    input_tpm = sum(coalesce(gen_ai.usage.input_tokens, 0)),
    output_tpm = sum(coalesce(gen_ai.usage.output_tokens, 0)),
    by: {bin(start_time, 1m)}
```

**How to read it:** `total_tpm` is the combined input + output token volume per minute — the figure to compare against the provider's TPM limit. `input_tpm` and `output_tpm` show where the volume comes from; a high `input_tpm` share points at oversized prompts or context rather than long generations. Correlate `total_tpm` spikes with P95 latency increases in the Latency query — if throughput and latency rise together, the backend is approaching saturation. To isolate a specific provider or model, add `gen_ai.provider.name` or `gen_ai.request.model` to the `by:` clause; rate limits are enforced per provider/model tier, so saturation must be read at that granularity, not just in aggregate.

**Saturation note:** GenAI saturation manifests as provider-side rate limiting (HTTP 429), not local CPU saturation, and the limit is multi-dimensional — TPM, RPM, and their daily counterparts are enforced simultaneously, so a 429 can come from RPM (see the Traffic signal) even with token headroom. A `rate_limit_exceeded` 429 is transient and should be retried with backoff; an `insufficient_quota` 429 means a billing cap was hit and will not clear on retry. Monitor `errors` (from the Errors query above) alongside `total_tpm` and request throughput: a rising error rate that coincides with a throughput spike is a strong signal of rate-limit-induced saturation.
