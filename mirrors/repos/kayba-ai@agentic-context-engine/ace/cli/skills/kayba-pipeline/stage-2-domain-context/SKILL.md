---
name: kayba-stage-2-domain-context
description: Gather domain context about the repository and agent — system prompt, tool definitions, domain docs, and behavior patterns from traces. Trigger when the user says "run stage 2", "gather context", "domain context", or when invoked by the kayba-pipeline orchestrator.
---

# Stage 2: Domain Context Gathering

Understand the agent's world — what it does, what tools it has, and what "success" looks like.

## Inputs

- **`TRACES_FOLDER`** — path to directory containing trace JSON files

## Process

### 0. Detect trace format

Before reading traces, identify the framework that produced them. Read 1 trace file and check:

| Signal | Framework |
|--------|-----------|
| `info.agent_info.implementation`, `info.environment_info`, `simulation.messages[]` with `role`/`tool_calls`/`turn_idx` | **tau2-bench** |
| `runs[].steps[]` with `type: "tool"`, `lc_kwargs` | **LangChain / LangSmith** |
| `events[]` with `event_type`, `span_id`, `parent_id` | **LlamaIndex** |
| `choices[].message.tool_calls[]` at top level | **Raw OpenAI API logs** |
| `trace.spans[]` with `attributes`, `trace_id` | **OpenTelemetry / Arize / Langfuse** |

Record the detected format in the output under **Trace Format**. All subsequent trace-reading steps use the field paths appropriate for that format.

If the format is unrecognized, note the top-level keys and structure, then proceed best-effort with field names found in the data.

### 1. Detect architecture

Read 2-3 traces and determine if this is a single-agent or multi-agent system:

- **Single agent**: one `agent_info` entry, one conversation thread, tool calls from one identity
- **Multi-agent / router**: look for multiple `agent_info` entries, routing tool calls (e.g., `transfer_to_*`, `delegate_to_*`), sub-conversation arrays, or distinct system prompts per agent identity

If multi-agent: document each agent separately (name, role, tools, handoff triggers) and note the routing logic. The remaining steps apply per-agent.

### 2. Find the system prompt

Use a fallback chain — stop at the first hit:

1. **Config files** — grep for keys: `system_prompt`, `system_message`, `instructions`, `AGENT_INSTRUCTION`, `SYSTEM_PROMPT` in YAML/JSON/TOML/Python/JS files
2. **Source code** — search for prompt template strings, f-strings, or `.format()` calls that build the system message (look in agent implementation files)
3. **Trace extraction** — read 3 trace files from `{TRACES_FOLDER}`:
   - Check `info.environment_info.policy` (tau2-bench format)
   - Check first message with `role: "system"` in the messages array
   - Check `raw_data` fields for system-level content
4. **Not found** — if none of the above yields a system prompt, explicitly record `SYSTEM_PROMPT_STATUS: NOT_FOUND` in the output and flag this for the orchestrator. Do not fabricate or guess.

When found, record both the prompt content and its **source location** (file path + line, or trace field path).

### 3. Extract tool definitions

Two-pass approach: source code first (ground truth), then traces (usage evidence).

**Pass 1 — Source code discovery:**
- Search for tool/function definition patterns: `@tool`, `@is_tool`, `def tool_`, function schema arrays, OpenAPI specs, `tools=[]` arguments
- For each tool, extract from source:
  - Name
  - Input parameters with types and defaults
  - Return type / output schema (document the structure, not just "returns a dict")
  - Side effects: READ (no state change), WRITE (mutates state), GENERIC (neither)
  - Validation rules the tool does NOT enforce (critical — grep for comments like "API does not check", "agent must enforce")

**Pass 2 — Trace usage evidence:**
- Read ALL traces (if <= 20) or a stratified sample (see step 4 for sampling)
- Extract every unique `tool_calls[].name` from assistant messages
- Extract every `role: "tool"` response to document actual output shapes
- For each tool, record one example input/output pair from traces

**Reconcile the two passes:**
- Tools in source but NOT in traces = "available but unused" — flag these; they may be relevant for edge cases the agent should handle
- Tools in traces but NOT in source = possible dynamic tools or external APIs — investigate

Output the full tool inventory as a table with columns: Name, Category, Input Schema, Output Schema, Observed in Traces (Y/N), Unvalidated Rules.

### 4. Find domain documentation

- READMEs, product docs, wiki links
- Policy files (e.g., `data/*/policy.md`, domain-specific docs)
- Inline code comments explaining business logic
- Test files that describe expected behavior
- Anything that explains what the agent does and what "success" means for its users

### 5. Catalogue agent behavior patterns

**Trace selection — stratified sampling** (do not just grab "5-10 random traces"):

1. Count total traces in `{TRACES_FOLDER}`. If <= 20, read ALL of them.
2. If > 20, select a stratified sample:
   - Sort by `termination_reason` — include at least 2 per unique reason
   - Sort by conversation length (message count) — include shortest, longest, and 2 median
   - Sort by tool call count — include lowest and highest
   - If task outcomes are available (pass/fail), include at least 3 of each
   - Target: ~15 traces total, or 30% of the corpus, whichever is larger

For each selected trace, document:
- **Function call frequency** — which tools are called most, in what order
- **Tool call sequences** — common tool chains (e.g., get_user -> get_reservation -> cancel)
- **Success patterns** — what does a thread that accomplishes its goal look like?
- **Failure patterns** — what does a thread that fails or gets stuck look like?
- **Error patterns** — what error strings appear in tool outputs? Group by root cause
- **Policy violation patterns** — where does the agent break its own rules? (e.g., multiple tool calls per turn, acting without confirmation)
- **User feedback signals** — reverts, ratings, explicit corrections, escalations, stop tokens, transfer tokens

### 6. Write findings

Write all findings to `eval/stage2_domain_context.md`:

```markdown
# Domain Context

## Trace Format
- Framework: [detected framework name]
- Key field paths: [e.g., simulation.messages[], info.environment_info.policy]

## Architecture
- Type: [single-agent | multi-agent]
- [If multi-agent: agent roster with roles and handoff triggers]

## Agent Purpose
[1-2 sentence summary of what this agent does]

## System Prompt
- **Source**: [file path + line, or trace field path, or NOT_FOUND]
- **Status**: [verbatim | reconstructed | not_found]

[The system prompt content, or "NOT_FOUND — downstream stages should account for missing system prompt"]

## Tools
| Tool | Category | Input Schema | Output Schema | In Traces? | Unvalidated Rules |
|------|----------|-------------|---------------|------------|-------------------|
| tool_name | READ/WRITE/GENERIC | `{param: type}` | `{field: type}` | Y/N | "API does not check X" |

### Tools available but never called in traces
- [tool_name — why it matters]

## Domain Rules
[Key business rules, constraints, policies the agent must follow]

## Behavior Patterns

### Success patterns
- [pattern 1]

### Failure patterns
- [pattern 1]

### Policy violation patterns
- [violation with frequency: N/M turns]

### Error patterns
| Error | Frequency | Root cause |
|-------|-----------|------------|
| error string | N traces | cause |

### User feedback signals
- [signal 1]
```

## Outputs

- `eval/stage2_domain_context.md`
