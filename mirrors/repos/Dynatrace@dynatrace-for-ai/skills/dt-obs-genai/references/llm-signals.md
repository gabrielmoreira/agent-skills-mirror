# LLM Signals Reference

GenAI spans captured with OpenTelemetry GenAI semantic conventions carry a set of LLM-specific attributes that go beyond the four golden signals. These LLM signals describe *which* model and provider served each request, *what type* of operation was invoked, *how many tokens* were consumed (input and output), *how long* the call took, and *whether* the call failed. Together they answer the questions most relevant to model selection, cost management, and performance tuning.

**Fields**

| Signal | Span attribute | Notes |
|---|---|---|
| Provider | `gen_ai.provider.name` | The model provider (e.g., `openai`, `amazon`, `ollama`, `VertexAI`) |
| Requested model | `gen_ai.request.model` | Model name sent in the request |
| Response model | `gen_ai.response.model` | Model name returned in the response; may differ from `gen_ai.request.model` due to provider aliasing or routing — swap it into any model-grouped query's `by:` clause to group by the actually-served model |
| Operation | `gen_ai.operation.name` | `chat` for LLM calls; also `execute_tool`, `invoke_agent`, `create_agent` |
| Input tokens | `gen_ai.usage.input_tokens` | Prompt tokens billed per call |
| Output tokens | `gen_ai.usage.output_tokens` | Completion tokens billed per call |
| Latency | `duration` | Grail duration value — divide by the `1ms` literal (`duration / 1ms`) for a numeric millisecond value |
| Failure | `span.status_code == "error"` | Do not use `request.is_failed` (always `0` for GenAI spans) |
| Time bucketing | `start_time` | Use `start_time` for time-series grouping — `timestamp` is null for these spans |

All queries in this file use `from: now()-24h`. Replace that window with any valid duration (e.g., `now()-1h`, `now()-7d`) to match your investigation scope.

---

## Slowest models

Ranks models by P95 latency. Use this to identify which models have the worst tail performance, and to catch outliers that may be hitting timeouts, rate limits, or serving large context windows.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.request.model)
| summarize requests = count(), p95_ms = percentile(duration, 95) / 1ms, by: {gen_ai.request.model}
| sort p95_ms desc
```

**How to read it:** Each row is one model. `p95_ms` is the 95th-percentile response time in milliseconds. `requests` shows call volume, which provides context for the latency figure — a high-P95 model with few requests may represent a rarely-used capability rather than a systemic problem. Models at the top of the list with high request volume are the primary candidates for investigation.

**Latency note:** Convert with the `1ms` duration literal (`/ 1ms`), not `/ 1000000.0` — dividing a duration by a plain number stays a nanosecond duration; only the literal yields a real millisecond number (use `/ 1s` for seconds).

**Tip:** Add `gen_ai.provider.name` to the `by:` clause to see whether a model's latency differs across providers that serve the same model family. Add `gen_ai.operation.name` to distinguish LLM call latency (`chat`) from tool-execution latency (`execute_tool`).

---

## Latency across providers

Compares P95 latency and request volume across providers. Use this to benchmark providers against one another and to detect provider-level degradations.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.request.model)
| summarize p95_ms = percentile(duration, 95) / 1ms, requests = count(), by: {gen_ai.provider.name}
| sort p95_ms desc
```

**How to read it:** Each row is one provider. `p95_ms` is the tail response time across all models served by that provider. `requests` is the total call volume. A provider with a much higher P95 than peers — especially at high volume — is worth investigating for regional routing issues, model-specific timeouts, or rate-limit-induced retries.

**Tip:** Filter to a single operation type by adding `| filter gen_ai.operation.name == "chat"` before the `summarize` step to isolate LLM call latency from agent-orchestration overhead. Correlate provider-level latency increases with the error-rate query in `golden-signals.md` — simultaneous latency and error spikes at the provider level often indicate rate limiting.

---

## Token usage by model

Total input and output token consumption broken down by model and provider. Use this to understand cost distribution, detect unexpectedly large context windows, and identify the highest-spend model-provider combinations.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.request.model)
| summarize input_tokens = sum(gen_ai.usage.input_tokens), output_tokens = sum(gen_ai.usage.output_tokens), by: {gen_ai.request.model, gen_ai.provider.name}
| sort output_tokens desc
```

**How to read it:** Each row is a model-provider combination. `input_tokens` is the total prompt tokens consumed; `output_tokens` is the total completion tokens generated. Most LLM providers charge separately for input and output tokens (and often at different rates), so tracking them independently is important for cost attribution. A high `input_tokens` figure relative to `output_tokens` indicates large prompts or extensive system-context injection — a common cause of cost overruns.

**Tip:** To see the ratio of output to input tokens (a proxy for response verbosity), add `| fieldsAdd ratio = toDouble(output_tokens) / if(input_tokens > 0, toDouble(input_tokens), else: 1.0)` after the `summarize` step. To convert token counts to an estimated cost, multiply by the provider's per-token rate and add a `fieldsAdd estimated_cost_usd` column.
