---
name: foundry-observability
description: |
  Trace, monitor, and evaluate Microsoft Foundry hosted agents end-to-end. Covers OpenTelemetry GenAI traces in Application Insights via KQL, eval-trace correlation, azd ai agent monitor, dataset curation from production traces, built-in evaluators (quality + safety/RAI), batch evals, trending and regression detection.
  Triggers: "trace agent", "Foundry tracing", "App Insights agent", "KQL trace", "gen_ai.operation.name", "gen_ai.evaluation.result", "azd ai agent monitor", "evaluate agent", "batch evaluation", "agent eval", "Foundry evaluation", "RAI eval", "safety eval", "evaluator", "regression detection", "eval trending", "trace to dataset", "AIF_RESPONSE_ID".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Foundry Observability — Tracing + Evaluations + RAI

End-to-end guide for understanding what a Foundry hosted agent did, why it failed, and whether it is getting better or worse over time. Foundry agents emit OpenTelemetry GenAI semantic conventions to Application Insights automatically (via the `APPLICATIONINSIGHTS_CONNECTION_STRING` injected by the platform). Both **traces** (request flow) and **evaluation results** (quality + safety scores) land in App Insights, queryable via KQL. This skill is **language-agnostic** — KQL is universal; defer SDK-specific eval signatures to the Microsoft Docs MCP.

## Before You Build — Discovery (MANDATORY)

Foundry tracing and evaluation APIs change frequently. **Always confirm current shapes before writing code.**

1. **Microsoft Docs MCP** (`microsoft-docs`) — query in this order:
   - `"Foundry agent tracing OpenTelemetry GenAI"` — current OTel attribute set the platform emits
   - `"App Insights gen_ai customDimensions"` — table layout and attribute storage
   - `"Foundry evaluator built-in"` — current built-in evaluator names and parameters
   - `"Azure AI evaluation safety RAI"` — RAI evaluator availability per region
   - `"azd ai agent monitor"` — CLI flags and output shape
2. **Azure MCP for live App Insights queries:**
   - `monitor_resource_log_query` — run any KQL in this skill against the live App Insights resource. Always pass `subscription` explicitly.
3. **Azure MCP for evaluations:** the `foundry` tool exposes `evaluation_*` methods:
   - `evaluation_dataset_create`, `evaluation_dataset_get`, `evaluation_dataset_versions_get`
   - `evaluation_agent_batch_eval_create`, `evaluation_get` (groups + runs)
   - `evaluation_comparison_create`, `evaluation_comparison_get`
4. **Verify SDK versions** when generating code: `pip show azure-ai-projects azure-ai-evaluation` (or equivalent for `.NET`/JS). Built-in evaluator names move between previews — never assume from training data.

## Mental Model

```
            ┌─────────────────────────────────────────────────┐
            │   Foundry Hosted Agent (Responses/Invocations)  │
            │   OTel auto-emitted by protocol library         │
            └────────────────────────┬────────────────────────┘
                                     │ APPLICATIONINSIGHTS_CONNECTION_STRING
                                     ▼
              ┌──────────────────────────────────────────┐
              │           Application Insights           │
              │  requests · dependencies · customEvents  │
              │           traces · exceptions            │
              └──────────────┬───────────────────────────┘
                             │  KQL via monitor_resource_log_query
              ┌──────────────┴────────────────┐
              ▼                               ▼
   Trace analysis (debug)          Eval correlation (quality)
```

**Eval flywheel:**

```
Production traces ─► Curated dataset ─► Batch eval ─► Compare versions
        ▲                                                    │
        └────── Promote / regress ◄──────────────────────────┘
```

**Key terms:**

- **trace** — a complete request flow, identified by `operation_Id`
- **span** — one operation inside a trace (e.g., `chat`, `execute_tool`, `invoke_agent`); identified by `id`, parent via `operation_ParentId`
- **conversation_id** — Foundry-level session ID (`gen_ai.conversation.id`); spans many traces
- **response_id** — single agent reply ID (`gen_ai.response.id`); the join key between spans and eval results
- **agent_name** / **agent_id** — Foundry-visible name vs. internal ID; agent_id often encodes version (`name:version`)
- **evaluator** — code (built-in or custom) that scores a response on one dimension
- **evaluation result** — single (evaluator, response) score with `value`, `label`, `explanation`
- **dataset / dataset version** — input cases for batch eval; versioned for reproducibility
- **baseline / comparison** — pinned reference run; treatment compared against it for regression detection

## App Insights Table Mapping

| Table          | What lives here                                                                                                                                    |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `requests`     | Incoming HTTP to the agent endpoint. Carries `gen_ai.agent.name` (Foundry name) and `azure.ai.agentserver.*`. **Preferred entry point** for filtering by agent name. |
| `dependencies` | GenAI spans: `chat` (LLM inference), `execute_tool` (tool calls), `invoke_agent`, `create_agent`. Holds token counts, model, response IDs.        |
| `customEvents` | **Evaluation results** — rows where `name == "gen_ai.evaluation.result"`. Scores, labels, explanations.                                            |
| `traces`       | Log events including GenAI input/output messages. Also carries `azure.ai.agentserver.*` on hosted agents.                                          |
| `exceptions`   | Errors with stack traces. Join via `operation_Id` to `requests`/`dependencies` for context.                                                        |

## Key OTel GenAI Attributes

On `dependencies` `customDimensions`:

| Attribute                          | Meaning                                | Example                                   |
| ---------------------------------- | -------------------------------------- | ----------------------------------------- |
| `gen_ai.operation.name`            | Span operation type                    | `chat`, `invoke_agent`, `execute_tool`    |
| `gen_ai.conversation.id`           | Foundry session ID                     | `conv_5j66UpCpwteGg4YS...`                |
| `gen_ai.response.id`               | Single response ID (eval join key)     | `chatcmpl-123`, `caresp_...`, `resp_...`  |
| `gen_ai.agent.name`                | Code-level class name on `dependencies` | `BingSearchAgent`                        |
| `gen_ai.agent.id`                  | Agent ID; may encode `name:version`    | `support-bot:3`                           |
| `gen_ai.request.model`             | Requested model                        | `gpt-4o`                                  |
| `gen_ai.response.model`            | Actual model used                      | `gpt-4o-2024-05-13`                       |
| `gen_ai.usage.input_tokens`        | Prompt token count                     | `450`                                     |
| `gen_ai.usage.output_tokens`       | Completion token count                 | `120`                                     |
| `gen_ai.response.finish_reasons`   | Stop reason(s)                         | `["stop"]`, `["tool_calls"]`              |
| `error.type`                       | Error class                            | `timeout`, `rate_limited`, `content_filter` |
| `gen_ai.input.messages`            | Full input messages (on `invoke_agent`) | JSON array                              |
| `gen_ai.output.messages`           | Full output messages (on `invoke_agent`) | JSON array                              |

On `customEvents` where `name == "gen_ai.evaluation.result"`:

| Attribute                         | Meaning                                  |
| --------------------------------- | ---------------------------------------- |
| `gen_ai.evaluation.name`          | Evaluator name (`Relevance`, `HateUnfairness`, ...) |
| `gen_ai.evaluation.score.value`   | Numeric score (e.g., `4.0`)              |
| `gen_ai.evaluation.score.label`   | Human label (`pass`, `fail`, `relevant`) |
| `gen_ai.evaluation.explanation`   | Free-form rationale                      |
| `gen_ai.response.id`              | Correlates this eval to the scored span  |
| `gen_ai.conversation.id`          | Conversation the response belongs to     |

## Span Correlation

| Field                | Purpose                                                  |
| -------------------- | -------------------------------------------------------- |
| `operation_Id`       | Trace ID — joins `requests` ↔ `dependencies` ↔ `traces` ↔ `exceptions` |
| `id`                 | Span ID                                                  |
| `operation_ParentId` | Parent span ID — build span trees                        |

> **Critical:** Eval results **do NOT** link via `id` / `operation_ParentId`. They correlate to spans via `gen_ai.response.id` (preferred) or `gen_ai.conversation.id`. This is the single most-missed gotcha when joining tables.

## KQL Templates

All snippets assume `customDimensions` is already a `dynamic` column — **do not** wrap it in `parse_json()`.

### 1. Recent agent activity (last 7d, by Foundry agent name)

```kql
requests
| where timestamp > ago(7d)
| extend
    foundryAgentName = coalesce(
        tostring(customDimensions["gen_ai.agent.name"]),
        tostring(customDimensions["azure.ai.agentserver.agent_name"])),
    conversationId = coalesce(
        tostring(customDimensions["gen_ai.conversation.id"]),
        tostring(customDimensions["azure.ai.agentserver.conversation_id"]),
        operation_Id),
    responseId = tostring(customDimensions["azure.ai.agentserver.response_id"])
| where foundryAgentName == "<foundry-agent-name>"
| project timestamp, success, duration, resultCode,
          conversationId, responseId, operation_Id
| order by timestamp desc
| take 100
```

### 2. Trace tree for one conversation (operation_Id pivot)

```kql
let convId = "<conversation-id>";
let opIds = requests
| where customDimensions["gen_ai.conversation.id"] == convId
   or customDimensions["azure.ai.agentserver.conversation_id"] == convId
| distinct operation_Id;
dependencies
| where operation_Id in (opIds)
| extend operation = tostring(customDimensions["gen_ai.operation.name"]),
         model = tostring(customDimensions["gen_ai.request.model"]),
         tool = tostring(customDimensions["gen_ai.tool.name"])
| project timestamp, duration, success, operation, name, tool, model,
          id, operation_ParentId, operation_Id
| order by timestamp asc
```

### 3. Tool call latency breakdown

```kql
dependencies
| where timestamp > ago(24h)
| where customDimensions["gen_ai.operation.name"] == "execute_tool"
| extend toolName = tostring(customDimensions["gen_ai.tool.name"]),
         toolType = tostring(customDimensions["gen_ai.tool.type"])
| summarize calls = count(),
            failures = countif(success == false),
            p50 = percentile(duration, 50),
            p95 = percentile(duration, 95),
            p99 = percentile(duration, 99),
            avgMs = avg(duration)
        by toolName, toolType
| order by p95 desc
```

### 4. Failed runs with error type (joined to exceptions)

```kql
let failures = dependencies
| where timestamp > ago(24h)
| where success == false or toint(resultCode) >= 400
| extend operation = tostring(customDimensions["gen_ai.operation.name"]),
         errorType = tostring(customDimensions["error.type"])
| project timestamp, name, duration, resultCode, errorType, operation, operation_Id;
failures
| join kind=leftouter (
    exceptions
    | where timestamp > ago(24h)
    | project operation_Id, exType = type, exMessage = outerMessage
) on operation_Id
| order by timestamp desc
| take 100
```

### 5. Eval results joined to responses (via gen_ai.response.id)

```kql
let evals = customEvents
| where timestamp > ago(7d)
| where name == "gen_ai.evaluation.result"
| extend responseId = tostring(customDimensions["gen_ai.response.id"]),
         evalName = tostring(customDimensions["gen_ai.evaluation.name"]),
         score = todouble(customDimensions["gen_ai.evaluation.score.value"]),
         label = tostring(customDimensions["gen_ai.evaluation.score.label"]);
let spans = dependencies
| where timestamp > ago(7d)
| where isnotempty(customDimensions["gen_ai.response.id"])
| extend responseId = tostring(customDimensions["gen_ai.response.id"]),
         model = tostring(customDimensions["gen_ai.request.model"]);
evals
| join kind=inner spans on responseId
| project timestamp, responseId, evalName, score, label, model, duration
| order by score asc
```

### 6. Token usage by agent version (sum input + output)

```kql
dependencies
| where timestamp > ago(7d)
| where customDimensions["gen_ai.operation.name"] in ("chat", "invoke_agent")
| extend agentId = tostring(customDimensions["gen_ai.agent.id"]),
         agentVersion = iff(agentId contains ":",
                            tostring(split(agentId, ":")[1]), ""),
         inTokens = toint(customDimensions["gen_ai.usage.input_tokens"]),
         outTokens = toint(customDimensions["gen_ai.usage.output_tokens"])
| summarize calls = count(),
            totalIn = sum(inTokens),
            totalOut = sum(outTokens),
            avgIn = avg(inTokens),
            avgOut = avg(outTokens)
        by agentId, agentVersion
| order by totalIn desc
```

## azd ai agent monitor

`azd ai agent monitor` is the fastest way to tail recent activity for a deployed Foundry agent.

```bash
azd ai agent monitor --tail 20             # last 20 spans
azd ai agent monitor --follow              # stream new spans
azd ai agent monitor --conversation <id>   # filter to one conversation
```

Under the hood it queries App Insights against the `dependencies` and `requests` tables for the deployed agent's resource. Use it for ad-hoc tailing; use the KQL snippets above (via `monitor_resource_log_query`) for deep investigation, joins, and historical analysis.

## Evaluation — Built-in Evaluators

Foundry's evaluation SDK ships with two families of built-in evaluators. Names and exact signatures evolve — confirm current set with `microsoft-docs` (`"azure-ai-evaluation built-in evaluators"`) before generating SDK code.

### Quality evaluators

| Evaluator              | What it scores                                          |
| ---------------------- | ------------------------------------------------------- |
| `Relevance`            | Does the response address the user's query?            |
| `Coherence`            | Is the response logically structured?                  |
| `Fluency`              | Is the language natural and grammatical?               |
| `Groundedness`         | Is the response supported by the provided context?     |
| `IntentResolution`     | Did the agent correctly understand the user's intent?  |
| `ResponseCompleteness` | Did the agent answer the full question?                |
| `ToolCallAccuracy`     | Were the right tools called with the right arguments?  |

### Safety / RAI evaluators

| Evaluator            | What it flags                                                  |
| -------------------- | -------------------------------------------------------------- |
| `HateUnfairness`     | Hate speech, discriminatory or biased content                  |
| `Violence`           | Violent content                                                |
| `SexualContent`      | Sexual content                                                 |
| `SelfHarm`           | Self-harm content                                              |
| `IndirectAttack`     | Cross-domain prompt injection / jailbreak attempts             |
| `ProtectedMaterial`  | Copyrighted text, song lyrics, etc.                            |
| `CodeVulnerability`  | Security flaws in generated code                               |

### Composite evaluators

- `QualityEvaluator` — runs the quality set together
- `SafetyEvaluator` — runs the RAI set together

> **Both score and label matter for RAI.** Numeric severity score AND human-readable label (`safe`, `low`, `medium`, `high`) should be alerted on. Defer signature details (constructor params, async/sync, threshold conventions) to the docs MCP — they differ across SDK versions.

## Evaluation Workflow

1. **Curate dataset** — manually author JSONL or harvest from production traces (see [Trace → Dataset Pipeline](#trace--dataset-pipeline)).
2. **Run batch eval** against an agent version — Azure MCP `evaluation_agent_batch_eval_create`, or via the Foundry SDK (`project.evaluations.create` / language equivalent). Pin the dataset version (`v3`) and capture the returned `evaluationId` + `evalRunId`.
3. **Inspect results** — Foundry portal, OR KQL on `customEvents` for per-response scores (template #5 above).
4. **Compare versions** — `evaluation_comparison_create` with `baselineRunId` + `treatmentRunIds`. **`displayName` is required** in the `insightRequest` despite the schema marking it optional.
5. **Decide** — promote, hold, or rollback. Record the decision in lineage (see below).

> Use `evaluation_get` to list groups (`isRequestForRuns: false`) or runs within a group (`isRequestForRuns: true`, `evalId: <group>`). The parameter is `evalId`, **not** `evaluationId`, even though creation used `evaluationId`.

## Trace → Dataset Pipeline

Production traces are the highest-signal source of test cases. Workflow:

1. **Harvest** — pick a KQL filter that captures interesting cases:
   - **Errors** — `dependencies | where success == false`
   - **Slow** — `dependencies | where duration > <threshold_ms>`
   - **Low eval scores** — `customEvents` with score below threshold, joined to `dependencies` (template #5)
   - **Combined** — multi-criteria OR
2. **Filter for quality** — drop trivially short conversations, dedupe by `conversationId`, optionally `| sample 50` for stratified subsets.
3. **Extract** — pull `gen_ai.input.messages` (query) and `gen_ai.output.messages` (response) from `invoke_agent` spans for the harvested `conversationId`s.
4. **Transform to JSONL** — one line per case:
   ```json
   {"query": "...", "response": "...", "ground_truth": "...",
    "metadata": {"source": "trace", "conversationId": "...", "harvestRule": "error"}}
   ```
5. **Human review (MANDATORY)** — never auto-commit harvested traces. Show candidates as a table; user approves/edits/rejects.
6. **Persist locally** — `.foundry/datasets/<agent-name>-<source>-v<N>.jsonl`.
7. **Sync to Foundry** (optional) — upload blob, then `evaluation_dataset_create` with `connectionName` of an `AzureStorageAccount` project connection.

**Local cache layout:**

```
.foundry/
├── datasets/
│   ├── <agent>-traces-v1.jsonl
│   ├── <agent>-traces-v2.jsonl
│   └── manifest.json
├── results/        # eval run outputs (cached for offline diffing)
└── evaluators/     # custom evaluator definitions, if any
```

## Dataset Versioning + Lineage

**Naming:** `<agent-name>-<source>-v<N>` where source ∈ {`traces`, `synthetic`, `manual`, `combined`}. Increment `N` for every change; never mutate a published version.

**Tags** in `manifest.json` (mutable lifecycle labels):

| Tag                  | When                                                  |
| -------------------- | ----------------------------------------------------- |
| `baseline`           | Reference for regression comparisons                  |
| `prod`               | Currently used for production evaluation              |
| `canary`             | Staged rollout                                        |
| `regression-<date>`  | Caught a regression                                   |
| `deprecated`         | Replaced by newer version                             |

**`manifest.json`** holds the full lineage chain — dataset version → eval run(s) → agent version → comparison(s) → deployment decision:

```json
{"datasets": [{
  "name": "support-bot-prod-traces", "version": "v3", "tag": "prod",
  "evalRuns": [
    {"evalId": "eval-001", "runId": "run-abc", "agentVersion": "3"},
    {"evalId": "eval-001", "runId": "run-def", "agentVersion": "4"}
  ],
  "comparisons": [{"baselineRunId": "run-abc", "treatmentRunIds": ["run-def"],
                   "result": "v4 +25% coherence"}],
  "deployments": [{"agentVersion": "4", "reason": "v4 improved coherence"}]
}]}
```

**Trending:** plot per-evaluator score across runs in the same eval group (same evaluator set + thresholds). If the evaluator set changes, start a new group.

**Regression detection:** `evaluation_comparison_create` returns per-evaluator `treatmentEffect` (`Improved` / `Changed` / `Degraded` / `Inconclusive` / `TooFewSamples`) plus delta. Common thresholds: `> +2%` PASS, `±2%` NEUTRAL, `> -2%` REGRESSION. Inconclusive verdicts mean increase sample size (≥30 cases).

## Critical Gotchas — Do Not Confuse

- **Eval results live in `customEvents`, NOT `dependencies`.** Easiest miss in the entire stack. Filter `name == "gen_ai.evaluation.result"`.
- **Eval correlates via `gen_ai.response.id` / `gen_ai.conversation.id`, NOT `id` / `operation_ParentId`.** The OTel parent-span linkage does not connect evals to spans.
- **`requests` is the preferred entry point for agent-name filtering** for hosted agents. `gen_ai.agent.name` on `requests` = Foundry name; on `dependencies` = code class name. Always start from `requests`, then carry `operation_Id` forward.
- **Hosted agents auto-emit OTel** via the protocol library. Don't add a second OTel exporter — you'll get duplicate spans.
- **`APPLICATIONINSIGHTS_CONNECTION_STRING` is platform-injected** for hosted agents. Do not redeclare it in `agent.yaml` env — let the platform manage it.
- **RAI evaluators emit BOTH score and label.** Alert on label transitions (`safe → low → medium`) AND numeric thresholds — labels can swing categorically without large numeric movement.
- **`displayName` is required** in `evaluation_comparison_create` `insightRequest` despite schema marking it optional. Comparison API rejects without it.
- **`evaluation_get` uses `evalId`** even though creation used `evaluationId`.
- **Don't `parse_json(customDimensions)`** in KQL — it's already `dynamic`. Index directly: `customDimensions["gen_ai.response.id"]`.
- **Do not weaken evaluators or remove dataset rows to recover scores.** A score drop on a harder dataset is healthy signal, not a regression.

## Common Errors / Debugging Recipes

**"Agent didn't call the expected tool"**

1. Pull the trace (template #2) and inspect `gen_ai.response.finish_reasons` on the `chat` span — `["tool_calls"]` means the model decided to call a tool; `["stop"]` means it answered directly.
2. Check `traces` table for `gen_ai.choice` events to see what tool the model picked, if any.
3. Inspect `gen_ai.input.messages` on the `invoke_agent` span for the system prompt + tool definitions — common cause is unclear tool descriptions.

**"Eval scores low for safety"**

1. Filter `customEvents` to `gen_ai.evaluation.name in ("HateUnfairness", "Violence", "SelfHarm", ...)` and `score >= <medium-threshold>`.
2. For each flagged response, pull `gen_ai.output.messages` from the matching `invoke_agent` span (join via `gen_ai.response.id`).
3. Build a targeted dataset of the failing slice; run `SafetyEvaluator` on it after a prompt fix to confirm the regression is closed.

**"Latency spike in tool call"**

1. Run template #1 to confirm the spike on `requests` (end-to-end), then template #2 to see the full span tree for one slow conversation.
2. Run template #3 to identify which `tool.name` carries the p95.
3. Check the slow `execute_tool` span's `duration` vs. its parent `chat` span's `duration` — if `execute_tool` dominates, the problem is in the tool implementation, not the model.

**"Where did this dataset row come from?"**

1. Read `metadata.conversationId` from the JSONL row.
2. Run template #2 with that `convId` to recover the original production trace.
3. Cross-reference `manifest.json` — `harvestRule`, `timeRange`, `reviewedBy` tell you why it was selected and who curated it.

## Reference Links

- **OTel GenAI semconv:** <https://opentelemetry.io/docs/specs/semconv/gen-ai/>
  - Spans: <https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/>
  - Agent spans: <https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/>
  - Events: <https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/>
- **Foundry tracing & monitoring:** Microsoft Learn → search `"trace agents Azure AI Foundry"`
- **azure-ai-evaluation SDK:** Microsoft Learn → search `"azure-ai-evaluation built-in evaluators"`
- **RAI evaluators (regional availability):** Microsoft Learn → search `"Azure AI safety evaluators region"`
- **azd ai agent CLI:** Microsoft Learn → search `"azd ai agent monitor"`
- **App Insights KQL reference:** <https://learn.microsoft.com/azure/data-explorer/kusto/query/>
