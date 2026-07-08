# Cost and Tokens Reference

Token consumption is the primary cost driver for GenAI applications. Every LLM call burns input tokens (the prompt and context window) and output tokens (the generated completion), and most providers bill the two at different rates. Dynatrace captures both counts on every span via the OTel GenAI semantic conventions, giving you a precise picture of consumption across models and providers.

**Important: there is no stored cost field.** `gen_ai.usage.cost` is null on every span — Dynatrace records token counts, not dollar amounts. Cost must be derived by multiplying token sums by the per-model price you supply. The cost queries in this file use `dql-template` blocks with `<placeholder>` values you replace with the rates from your provider's pricing page.

The per-model price is the one input you cannot assume on the user's behalf: list prices change often and vary by region, commitment, and contract. Before filling the `<input_price>`/`<output_price>` placeholders, ask the user for their per-1M-token input and output rates (or ask them to paste the rates from their provider's pricing page). Never silently insert prices from memory; stale rates produce confidently wrong cost numbers, which is worse than reporting tokens alone.

| Attribute | Notes |
|---|---|
| `gen_ai.usage.input_tokens` | Prompt tokens consumed per call |
| `gen_ai.usage.output_tokens` | Completion tokens generated per call |
| `gen_ai.request.model` | Model name as sent in the request |
| `gen_ai.provider.name` | Provider (e.g., `openai`, `Azure`, `amazon`, `ollama`) |
| `span.name` | Operation identifier (e.g., `openai.chat`, `bedrock.invoke_model`) |
| `start_time` | Use for time-series grouping — `timestamp` is null for GenAI spans |

---

## Token usage by model and provider

Total input and output token consumption broken down by model and provider, sorted by total tokens. Use this to identify which model-provider combinations dominate your token budget and to understand the input-to-output ratio for each.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.usage.input_tokens) or isNotNull(gen_ai.usage.output_tokens)
| summarize 
    input_tokens = sum(gen_ai.usage.input_tokens),
    output_tokens = sum(gen_ai.usage.output_tokens),
    cache_creation_tokens = sum(gen_ai.usage.cache_creation.input_tokens),
    cache_read_tokens = sum(gen_ai.usage.cache_read.input_tokens),
    total_tokens = sum(gen_ai.usage.input_tokens) + sum(gen_ai.usage.output_tokens),
    by: {gen_ai.provider.name, gen_ai.request.model}
| sort total_tokens desc
```

**How to read it:** Each row is a model-provider combination. `input_tokens` are the prompt tokens billed per call; `output_tokens` are the completion tokens generated. Most providers charge input and output tokens at different rates (output is usually more expensive), so tracking them separately is essential for cost attribution. A high `input_tokens` figure relative to `output_tokens` suggests large prompts or extensive system-context injection — a common source of cost overruns.

**Tip:** To compute an output-to-input ratio as a proxy for response verbosity, add the following stage after the `summarize` step. Embedding models (e.g., `text-embedding-3-large`) will show `output_tokens = 0` — that is expected.

```dql-snippet
| fieldsAdd verbosity_ratio = toDouble(output_tokens) / if(input_tokens > 0, toDouble(input_tokens), else: 1.0)
```

---

## Token usage spikes

Total token consumption over time in 5-minute buckets. Use this to detect sudden surges in token burn that may indicate runaway agents, prompt injection, or unexpected traffic increases.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.usage.input_tokens) or isNotNull(gen_ai.usage.output_tokens)
| summarize tokens = sum(gen_ai.usage.input_tokens) + sum(gen_ai.usage.output_tokens), by: {bin(start_time, 5m)}
```

**How to read it:** Each row is a 5-minute window. A sustained increase in `tokens` indicates growing load; a sharp isolated spike often points to a single large request or a batch job. Correlate spikes in token consumption with the error-rate and latency queries in `golden-signals.md` and `llm-signals.md` — simultaneous token and error spikes may indicate rate-limit-induced retries inflating prompt counts.

**Note on time bucketing:** `start_time` is used here because `timestamp` is null for GenAI spans. `bin(start_time, 5m)` produces correctly ordered 5-minute buckets. Change `5m` to `1h` for a longer-range trend view.

**Tip:** Add `gen_ai.request.model` to the `by:` clause to break the time series down by model. Add `gen_ai.provider.name` to see whether a spike is isolated to one provider.

---

## Most expensive prompts and models

Ranks model-provider-operation combinations by total token consumption — the best available proxy for cost when no stored price field exists. Because the OTel GenAI semantic conventions carry no per-prompt identifier by default, this query groups by `gen_ai.request.model`, `gen_ai.provider.name`, and `span.name` (the operation identifier, e.g., `openai.chat`, `bedrock.invoke_model`, `AzureChatOpenAI.chat`). This is the finest-grained grouping available without custom prompt tagging.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.usage.input_tokens) or isNotNull(gen_ai.usage.output_tokens)
| summarize input_tokens = sum(gen_ai.usage.input_tokens), output_tokens = sum(gen_ai.usage.output_tokens), total_tokens = sum(gen_ai.usage.input_tokens) + sum(gen_ai.usage.output_tokens), calls = count(), by: {gen_ai.request.model, gen_ai.provider.name, span.name}
| sort total_tokens desc
```

**How to read it:** Each row is a unique model + provider + operation combination. `total_tokens` is the combined prompt and completion token count — the primary cost driver. `calls` is the number of API calls in the window. A high `total_tokens` with a low `calls` count indicates large per-call context windows; a high `calls` count with moderate per-call tokens indicates high-frequency operations. Both are cost risks and warrant different remediation strategies.

**Tip:** To narrow to a specific operation type, add `| filter span.name == "openai.chat"` before the `summarize` step. To add per-model cost estimates inline, extend with the following stage — but note this applies a single price to all rows, so it is only accurate if you filter to one model first.

```dql-snippet
| fieldsAdd est_cost_usd = (input_tokens / 1000000.0) * <input_price> + (output_tokens / 1000000.0) * <output_price>
```

---

## Usage attribution (user and AI application)

Token spend grouped by *who* or *what* drove it, rather than by model. Use this for chargeback (cost per AI application or team), abuse detection (one user or tenant dominating consumption), and capacity planning. Attribution depends on the application propagating an identity attribute — there is no single guaranteed field, so discover what your spans carry before grouping.

**Discover candidate identity attributes:** inspect a sample of GenAI spans for fields that identify the application, service, user, or tenant.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.request.model)
| fields gen_ai.agent.name, service.name, dt.entity.service, gen_ai.conversation.id, gen_ai.usage.input_tokens, gen_ai.usage.output_tokens
| limit 20
```

**How to read it:** Look for a column that is consistently populated and meaningfully identifies the workload. `service.name` / `dt.entity.service` typically identify the AI application (matching the `GENAI_SERVICE` entity in [agent-signals.md → Agent topology](agent-signals.md#agent-topology-smartscape-entities)); `gen_ai.agent.name` identifies the agent. End-user identity is rarely standard — it is usually a custom attribute (e.g. `enduser.id`, `user.id`, or an application-specific key), so confirm which field, if any, your instrumentation sets.

**Attribute token spend by an identity field** (replace `<identity_field>` with the attribute you confirmed above, e.g. `service.name`):

```dql-template
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.usage.input_tokens) or isNotNull(gen_ai.usage.output_tokens)
| filter isNotNull(<identity_field>)
| summarize input_tokens = sum(gen_ai.usage.input_tokens), output_tokens = sum(gen_ai.usage.output_tokens), total_tokens = sum(gen_ai.usage.input_tokens) + sum(gen_ai.usage.output_tokens), calls = count(), by: {<identity_field>}
| sort total_tokens desc
```

**How to read it:** Each row is one application/user/tenant and its total token consumption. The top rows are your highest-spend consumers — the targets for cost optimization or, if a single end user dominates, the signal for abuse or a misbehaving client. Add `gen_ai.request.model` to the `by:` clause to see each consumer's model mix, then apply the cost template above (per model) to convert to estimated USD.

**Tip:** To attribute cost to a multi-turn session instead of an application, group by `gen_ai.conversation.id` — see [conversation-analytics.md → Cost and depth per conversation](conversation-analytics.md#cost-and-depth-per-conversation).

---

## Prompt caching economics

Several providers cache repeated prompt prefixes (system prompts, long shared context) and bill **cached input tokens at a steep discount** — often 10–25% of the normal input rate. When caching is active, the cached share of input tokens is the single largest lever on input cost. The cached-token count is reported on the span when the provider and instrumentation support it; the field name varies by provider, so the first task is to confirm whether you have this signal at all.

> **"Do I even have this enabled?"** Run the enablement check below. The OpenTelemetry fields are `gen_ai.usage.cache_read.input_tokens` (tokens served from cache — the cache hits) and `gen_ai.usage.cache_creation.input_tokens` (tokens written to cache); both are already counted within `gen_ai.usage.input_tokens`. Some instrumentations emit the raw provider attribute instead of the normalized OTel namespace (for example Anthropic-style flat `cache_read_input_tokens` / `cache_creation_input_tokens`), so the attribute name can vary by provider/SDK. If the check returns zero across the board, either the provider/SDK is not reporting cached tokens or you are not using prompt caching — verify the attribute name on your tenant before concluding.

**Enablement check:**

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.request.model)
| summarize 
    calls = count(), 
    calls_with_cache = countIf(isNotNull(gen_ai.usage.cache_read.input_tokens)), 
    cache_read_tokens = sum(gen_ai.usage.cache_read.input_tokens), 
    cache_creation_tokens = sum(gen_ai.usage.cache_creation.input_tokens),
    input_tokens = sum(gen_ai.usage.input_tokens)
```

**How to read it:** `calls_with_cache` is how many spans carry the cached-token attribute; `cache_read_tokens` is the total cached input tokens (cache hits). If `calls_with_cache` is `0`, prompt-caching telemetry is not present — report that rather than "no caching". If it is non-zero but `cache_read_tokens` is `0`, the field is recorded but no cache hits occurred (caching available but not effective). If both are non-zero, proceed to the cache-hit-rate query.

**Cache hit rate and savings by model:**

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.usage.cache_read.input_tokens)
| summarize 
    cache_read_tokens = sum(gen_ai.usage.cache_read.input_tokens), 
    cache_creation_tokens = sum(gen_ai.usage.cache_creation.input_tokens),
    input_tokens = sum(gen_ai.usage.input_tokens), 
    by: {gen_ai.request.model, gen_ai.provider.name}
| fieldsAdd cache_hit_rate_pct = if(input_tokens > 0, cache_read_tokens * 100.0 / input_tokens, else: 0.0)
| sort cache_hit_rate_pct desc
```

**How to read it:** `cache_hit_rate_pct` is the share of input tokens served from cache for each model. A high rate means most of your prompt prefix is being reused cheaply — good. A near-zero rate on a workload with large, repeated system prompts is a missed optimization: the prompt may not be stable enough (or ordered correctly) for the provider to cache it. Use the model's cached-token price (typically a fraction of the standard input rate — ask the user for it, as with all prices) to convert the cached tokens into realized savings.

**Tip:** Treat `cache_read_tokens` as a *subset* of `input_tokens`, not an addition — the standard input-token cost queries already include cached tokens at full price, so any cost estimate that ignores the cache discount overstates input spend on cache-heavy workloads.