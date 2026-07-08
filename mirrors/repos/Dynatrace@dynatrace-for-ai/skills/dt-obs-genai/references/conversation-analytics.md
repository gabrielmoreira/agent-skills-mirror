# Conversation Analytics Reference

The golden, LLM, cost, and agent signals are all measured per request (one span) or per turn (one `trace.id`). Real GenAI workloads are *conversational*: a user exchanges many turns with an agent, and the unit that matters for cost, quality, and abuse is the **conversation**, not the individual call. When the application propagates a conversation/session identifier, Dynatrace records it on every span as `gen_ai.conversation.id`, letting you roll spans up to the session level — cost per conversation, how deep conversations run, and which sessions are runaway-expensive or error-prone.

> **Field-presence caveat.** `gen_ai.conversation.id` is only populated when the application sets it (it is part of the OpenTelemetry GenAI conventions but not emitted by every framework). Run the presence check below first — if `with_conversation` is `0`, the app is not propagating a conversation id and the rest of this file does not apply. Verify the field name on your tenant before relying on these queries.

| Field | Notes |
|---|---|
| `gen_ai.conversation.id` | Conversation/session identifier shared by every span in a multi-turn session |
| `trace.id` | One request/response turn within a conversation (a `uid` — filter with `toUid()`) |
| `gen_ai.operation.name` | The type of GenAI operation performed within a conversation. A single conversation may span multiple operation types, e.g. `chat` (chat completion), `plan` (task decomposition), `execute_tool` (tool call), `retrieval` (vector store lookup), `search_memory` (memory query), `embeddings` (vector embeddings), `invoke_agent` (agent invocation), `invoke_workflow` (workflow invocation), `create_agent` (agent creation) |
| `start_time` | Use for time bucketing and first/last-seen — `timestamp` is null for GenAI spans |

---

## Presence check

Confirms whether conversation ids are being propagated before you query at the session level.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.request.model)
| summarize {spans = count(), with_conversation = countIf(isNotNull(gen_ai.conversation.id)), conversations = countDistinct(gen_ai.conversation.id)}
```

**How to read it:** `with_conversation` is the number of GenAI spans that carry a conversation id; `conversations` is the count of distinct sessions. If `with_conversation` is `0` while `spans` is non-zero, the application is instrumented for GenAI but is not setting `gen_ai.conversation.id` — report that the conversation dimension is unavailable rather than "no data".

---

## Cost and depth per conversation

Token spend, turn count, and error count for each conversation, ranked by total tokens. Use this to find the most expensive sessions, see how many turns and tool calls they took, and spot conversations that burned tokens while erroring.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.conversation.id)
| summarize
    {turns = countDistinct(trace.id),
    llm_calls = countIf(gen_ai.operation.name == "chat"),
    tool_calls = countIf(gen_ai.operation.name == "execute_tool"),
    input_tokens = sum(gen_ai.usage.input_tokens),
    output_tokens = sum(gen_ai.usage.output_tokens),
    total_tokens = sum(gen_ai.usage.input_tokens) + sum(gen_ai.usage.output_tokens),
    errors = countIf(span.status_code == "error")},
    by: {gen_ai.conversation.id}
| sort total_tokens desc
```

**How to read it:** Each row is one conversation. `turns` is the number of request/response turns (distinct traces); `llm_calls` and `tool_calls` break the session into model invocations versus tool executions. `total_tokens` is the session's full token spend — the best available proxy for its cost. A conversation with high `total_tokens` but few `turns` indicates large per-turn context windows (the context grows as history accumulates); a conversation with many `turns` and `tool_calls` is an agent doing extended multi-step work. A non-zero `errors` count on an expensive conversation is a strong candidate for investigation.

**Tip:** To attach an estimated cost, apply the per-model template from [cost-and-tokens.md](cost-and-tokens.md#most-expensive-prompts-and-models) — but note a conversation may span multiple models, so estimate per model first. To pivot from a costly conversation to its traces, take its `gen_ai.conversation.id` and add `| filter gen_ai.conversation.id == "<id>"` then project `trace.id` to list each turn for trace-level drill-down.

---

## Conversation depth and duration

How long conversations run, by turn count and wall-clock span. Use this to understand typical session shape and to surface abnormally long sessions that may indicate a stuck agent or a user fighting with a bad response.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.conversation.id)
| summarize {turns = countDistinct(trace.id), first_seen = min(start_time), last_seen = max(start_time)}, by: {gen_ai.conversation.id}
| fieldsAdd duration_min = (last_seen - first_seen) / 1m
| sort turns desc
```

**How to read it:** Each row is one conversation. `turns` is its depth in request/response turns; `duration_min` is the elapsed minutes from the first to the last span in the session. Most conversations cluster at a low turn count — rows far out in the tail (very high `turns`, or a long `duration_min` with few turns) are worth inspecting: extreme depth often coincides with an agent loop (see [agent-signals.md → Agent loops and runaway detection](agent-signals.md#agent-loops-and-runaway-detection)), and a long duration with few turns can indicate slow individual turns.

**Tip:** Add `tool_calls = countIf(gen_ai.operation.name == "execute_tool")` to the `summarize` to see whether depth comes from tool use or from repeated LLM turns. To get the distribution rather than the tail, follow with `| summarize p50 = percentile(turns, 50), p95 = percentile(turns, 95), max_turns = max(turns)`.

---

## Conversation traffic and error rate over time

New conversations started per time bucket and the share that contained an error. Use this as a session-level health signal alongside the per-span traffic in `golden-signals.md`.

```dql
fetch spans, from: now()-24h
| filter isNotNull(gen_ai.conversation.id)
| summarize {errored = countIf(span.status_code == "error") > 0}, by: {gen_ai.conversation.id, hour = bin(start_time, 1h)}
| summarize {conversations = count(), errored_conversations = countIf(errored)}, by: {hour}
| fieldsAdd error_conv_rate_pct = if(conversations > 0, errored_conversations * 100.0 / conversations, else: 0.0)
| sort hour asc
```

**How to read it:** Each row is one hour. `conversations` is the number of distinct sessions active in that hour; `errored_conversations` is how many contained at least one errored span. `error_conv_rate_pct` reframes errors at the session level — a single failed span buried in a long, otherwise-successful conversation counts the conversation once, which better reflects user-perceived reliability than a raw per-span error rate. A rising session-level error rate is a strong signal even when the per-span rate looks flat.

**Tip:** Change `1h` to `1d` for a longer trend, or add `gen_ai.request.model` to both `by:` clauses to see whether session-level errors concentrate on one model.
