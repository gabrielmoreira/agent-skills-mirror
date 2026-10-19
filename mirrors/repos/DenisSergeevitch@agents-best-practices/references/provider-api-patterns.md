# Provider API Patterns

## Provider-neutral view

Most provider APIs can support the same architecture:

```text
instructions + context + tool schemas
  -> model output
  -> final response or tool call
  -> application executes tool
  -> application returns tool result
  -> repeat
```

Provider differences are mostly in message shape, state handling, hosted tools, streaming events, and reasoning/tool item formats.

## OpenAI Responses-style APIs

Use Responses-style APIs for new OpenAI-native agent work when available. They provide typed output items, hosted tools, remote MCP support, stateful chaining options, and richer agent-like primitives.

Implementation pattern:

```python
response = client.responses.create(
    model=model,
    instructions=instructions,
    input=input_items,
    tools=visible_tools,
    store=True,
)

for item in response.output:
    if item.type == "function_call":
        result = execute_tool(item.name, item.arguments)
        next_response = client.responses.create(
            model=model,
            previous_response_id=response.id,
            input=[{
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": result,
            }],
        )
```

Use the harness for private/business tools, permission checks, durable state, and audit logs even when hosted tools are available.

## Realtime voice adapters

Choose the interaction architecture using [realtime voice agents](realtime-voice-agents.md). The following OpenAI protocol distinctions were checked October 13, 2026; current model evidence and documentation caveats live in [source links](source-links.md#realtime-voice-agents).

### OpenAI Realtime API

- Speech-to-speech sessions support `server_vad`, `semantic_vad`, or manual turn control. `create_response` and `interrupt_response` control different behaviors; configure the effective response owner rather than treating every speech event as a command to create a response.
- Treat `response.done` and its `response.status` (`completed`, `cancelled`, `failed`, or `incomplete`) as generation termination. This event does not establish playback completion. The conversation guide's `response.cancelled` wording differs from the current server-event schema; use the schema for the selected API version.
- On WebSocket interruption, stop local playback and send `conversation.item.truncate` with the item ID and the played `audio_end_ms`. WebRTC/SIP manage output-buffer truncation on the server. Neither path provides a precisely aligned shortened transcript or evidence of physical audibility on every client.

### OpenAI GPT-Live

GPT-Live is a separate full-duplex API with a delegated execution backend, not a renamed Realtime session. Its client and managed Responses delegation modes have different context ownership.

| Boundary | Adapter contract |
|---|---|
| Client delegation | `session.delegation.created` provides `delegation.id`, target, and `offset_ms`, not task text. Build the request from collected transcripts and current application state. |
| Transcript stream | Input/output transcript deltas have approximate `start_ms`/`end_ms`; they have no item ID or completed-turn event. Preserve fragments and times, and correlate overlapping speakers independently. |
| Context updates | `session.instructions.append`, `session.thinking.append`, and `session.commentary.append` take plain-string content of at most 500 tokens and a required `delegation_id`: a known client delegation ID or `null` for general context. |
| Update receipts | Match append acknowledgments through `client_event_id`. They describe estimated context injection, not speech/playback completion or proof that the model used the entire update. |
| Quiet versus spoken facts | Thinking context is not spoken immediately but can influence later speech; commentary is paraphrased aloud. Neither is a private channel for secrets or backend reasoning. |
| Backend configuration | Managed delegation exposes a subset of Responses settings. Check reasoning/tool support against the chosen backend model; changing delegation mode requires a new Live session. |
| Output control | Primary Live WebSocket audio deltas have no timing fields or output-audio-done event; reflected sideband deltas have `start_ms`/`end_ms`, which are not playback receipts. Sideband controls do not mute output; pre-playback checks require a client player or media relay that buffers and releases audio. |

Keep the Live delegation ID distinct from Responses response/tool-call IDs and application operation IDs. Use the [voice profile](realtime-voice-agents.md) for cancellation, revision fencing, permissions, playback evidence, and recovery rather than inferring those guarantees from a provider event.

## Chat Completions-style and OpenAI-compatible APIs

Use Chat Completions-style APIs when you need compatibility with OpenAI-compatible providers or when your harness already owns message history manually.

Implementation pattern:

```python
messages = [
    {"role": "system", "content": instructions},
    {"role": "user", "content": task},
]

while True:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=visible_tools,
    )
    msg = response.choices[0].message
    messages.append(msg)

    if not msg.tool_calls:
        return msg.content

    for call in msg.tool_calls:
        result = execute_tool(call.function.name, call.function.arguments)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": result,
        })
```

In this pattern, the harness owns:

- conversation state;
- message trimming;
- compaction;
- previous tool results;
- tool-call ID matching;
- approval pauses;
- retries;
- finalization.

## Anthropic API pattern

With Anthropic APIs, use structured tool-use and tool-result blocks. The model emits a tool-use request; the application executes the operation and returns the corresponding result in the next request.

Provider-neutral shape:

```text
request: messages + tools
response: assistant content with tool-use blocks
application: validate and execute tool-use blocks
next request: user/tool-result content blocks
repeat until final answer
```

Keep the same harness rules: validate arguments locally, check permissions, return structured results, preserve budgets, and trace every step.

## API adapter layer

Use an adapter so the rest of the harness is provider-neutral.

Adapter responsibilities:

```text
normalize input messages/items
normalize tool schemas
normalize model output into ToolCall or FinalAnswer events
normalize tool results back to provider format
handle streaming event conversion
handle provider-specific state chaining
capture token/cost/latency metadata
```

Internal event types should be stable even when provider APIs differ.

## Hosted tools versus client tools

Hosted tools run in provider infrastructure. Client tools run in your application or sandbox.

Hosted tools are useful for:

- web search;
- file search;
- code execution;
- image generation;
- general computer/browser use;
- remote connector calls supported by the provider.

Client tools are preferred for:

- private business APIs;
- tenant-specific permissions;
- regulated data;
- financial actions;
- communication sends;
- state-changing operations;
- custom audit requirements.

Do not outsource business authorization to a hosted tool unless the product explicitly supports and logs the required approval policy.

## Strict schemas

Use strict function schemas where available:

```text
required fields explicit
unknown fields rejected
enums for actions
minimum/maximum constraints
validated IDs
structured outputs
```

Then validate again in the harness before execution.

## Streaming

Streaming can reduce latency but adds complexity.

Rules:

- buffer enough data to validate complete tool calls;
- execute only when a tool call is complete;
- keep result ordering deterministic;
- handle aborts by sending synthetic tool results if required;
- do not stream partial sensitive data to users before output guardrails run.

## State strategies

Options:

```text
stateless: every request sends full selected context
previous-response chaining: provider stores prior state references
conversation object: provider stores conversation items
application event store: harness stores full operational history
```

Even when provider state is used, maintain an application event store for audit, replay, approvals, and evals.

## Native generation-state adapters

Some models interleave discrete text with continuous latent computation inside one generation. Learned hidden-state adapters, changed model weights, and specialized decoding are model/training/serving mechanisms; they are distinct from [harness refinement](self-refining-recursive-harnesses.md#taxonomy), programmable context, and [per-request routing](agentic-loop.md#per-request-model-routing). Keep this an optional post-MVP backend integration after a measured ordinary executor. A prompt or a nominally compatible chat endpoint does not establish these capabilities.

This section owns the harness-facing continuation contract, not a model-training recipe. Establish the backend's actual capabilities before admitting it:

| Boundary | Adapter requirement |
|---|---|
| Generation modes | Verify supported text/latent transitions, entry/exit rules, per-span and total generation limits, tool yielding, and cancellation. Count computation even when no text is emitted; mode transitions do not authorize actions. |
| Semantic state | Identify whether continuation requires complete native state or recorded nontext inputs. Carry compatible state across tool-result ingestion without reconstructing earlier latent positions from text or diagnostic labels. |
| State identity | Scope handles to tenant/session/branch and bind them to the model, learned adapter, tokenizer, generation rules, runtime/state format, and relevant position/mask settings. Reuse the [routing compatibility checks](agentic-loop.md#per-request-model-routing); a matching public model name is insufficient. |
| Continuation outcome | Distinguish accepted native resume, missing/expired state, incompatible state, and an explicitly restarted generation. Require a tested native restore/replay path for equivalence claims; otherwise stop or use a permitted restart with its lost context declared. |
| Tool handoff | Convert complete text-mode tool requests into the existing typed call/result protocol. Latent vectors, mode markers, and readable projections are not executable calls or approvals; reuse [tool validation and permission enforcement](tools-and-permissions.md). |

**Semantic state is not merely a prompt-cache optimization.** Ordinary prefix caching may be discarded when the exact inputs can be reconstructed. A text log omits continuous positions in a hybrid trajectory; losing their native state can change the continuation even if every visible message is retained. Full-history KV continuation may preserve computation under fixed model/adapter parameters, complete state, and consistent causal/positional settings. That does not establish crash durability, bounded memory growth, cross-model portability, or equivalence after eviction, quantization, or summarization.

Keep native inference state separate from the [application's durable records](always-on-agents.md#records-and-atomic-publication). A continuation handle is not an audit trail or a durable task checkpoint. Preserve operational events and tool-effect receipts outside it; loss of model state must not replay an unknown external effect. Use the existing [retry and reconciliation rules](agentic-loop.md#retry-policy) rather than a second retry policy here.

Readable pseudo-text or nearest-token projections are derived diagnostics. Geometric alignment, lexical relevance, and fluent labels do not prove a complete or faithful causal explanation, confidentiality, or correct task execution. Do not substitute them for native state, source evidence, or authorization. Follow [operational tracing](security-observability.md#observability) without making private hidden reasoning a required log or user-facing artifact; evaluate diagnostic usefulness and computation cost in [hybrid serving evals](evals.md#native-generation-state-and-hybrid-serving-evals).

## OpenAI-compatible provider caveats

OpenAI-compatible APIs vary in:

- tool-call schema fidelity;
- support for parallel tool calls;
- strict schema behavior;
- streaming event shapes;
- reasoning item visibility;
- multimodal support;
- context windows;
- storage defaults;
- hosted tools;
- safety behavior.

Do not assume full OpenAI parity. Test the exact provider and model.

## Prompt caching and retention

Provider APIs differ in prompt-cache controls, but the harness rules are provider-neutral:

```text
stable content first
volatile content late
deterministic tool/schema ordering
append-only history until compaction
cache usage fields logged on every call
prompt/tool bundle versions tracked
```

OpenAI APIs expose prompt caching automatically on supported requests and report cached-token usage in response metadata. Some OpenAI APIs also support retention controls for longer-lived cached prefixes.

Anthropic APIs expose prompt caching through provider-specific cache controls and usage fields. Use provider documentation for current marker syntax, TTL behavior, and breakpoint limits.

OpenAI-compatible APIs vary. Confirm whether the provider actually implements prompt caching, how it reports cache hits, and whether routing keys or backend cache settings are available.

See [prompt-caching-and-cost.md](prompt-caching-and-cost.md) for the detailed provider-neutral design pattern.

## Source links

- OpenAI Responses migration: https://developers.openai.com/api/docs/guides/migrate-to-responses
- OpenAI function calling: https://developers.openai.com/api/docs/guides/function-calling
- OpenAI tools: https://developers.openai.com/api/docs/guides/tools
- OpenAI Agents SDK: https://developers.openai.com/api/docs/guides/agents
- OpenAI guardrails and human review: https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
- OpenAI prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching
- OpenAI Prompt Caching 201: https://developers.openai.com/cookbook/examples/prompt_caching_201
- Anthropic building effective agents: https://www.anthropic.com/research/building-effective-agents
- Anthropic writing effective tools for agents: https://www.anthropic.com/engineering/writing-tools-for-agents
