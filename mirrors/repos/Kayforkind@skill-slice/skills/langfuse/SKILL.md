---
name: langfuse
description: "Integrates Langfuse traces, spans, generations, prompt versions, datasets, and LLM-as-judge scores with LangChain, LlamaIndex, OpenAI, and Vercel AI SDK. Use when adding LLM observability, cost tracking, or prompt A/B. Not for generic APM (Datadog/OpenTelemetry) or training-run dashboards (weights-and-biases). Self-hosted Docker/ClickHouse provisioning is out of scope."
version: 1.0.1
risk: unknown
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
---

# Langfuse

Langfuse is an open-source LLM observability platform covering tracing, prompt management, evaluation, datasets, and cost/quality monitoring. This skill guides integration with LangChain, LlamaIndex, OpenAI, and raw Python/JS SDKs.

**Role**: LLM Observability Architect — think in traces, spans, generations, scores, and datasets. Use data to drive prompt improvements and catch regressions.

## When to Use

Trigger this skill when the user mentions or implies any of:
- `langfuse`
- LLM observability / monitoring LLM apps
- LLM tracing / debugging LLM calls
- Prompt management / prompt versioning / A/B testing prompts
- LLM evaluation / scoring / LLM-as-judge
- Datasets for LLM eval
- Cost tracking for LLM calls
- Integrating observability with LangChain, LlamaIndex, OpenAI, Anthropic, or Vercel AI SDK

Do not use this skill for non-LLM application monitoring or generic APM (Datadog, OpenTelemetry backend traces) unless the user explicitly wants Langfuse for LLM-specific spans.

## Prerequisites

1. **Language runtime**: Python 3.9+ or TypeScript/JavaScript (Node 18+).
2. **Langfuse access**: Cloud account at `https://cloud.langfuse.com` OR a self-hosted instance URL.
   - Self-hosted requires infrastructure (Docker/Postgres/ClickHouse). Out of scope for this skill beyond providing the `host` URL.
3. **API keys**: `public_key` (`pk-...`) and `secret_key` (`sk-...`) from Project Settings. Use env vars — never hardcode.
4. **LLM provider keys**: e.g. `OPENAI_API_KEY`. Use `YOUR_KEY` placeholders in shared code.
5. **SDK install**:
   - Python: `pip install langfuse openai langchain langchain-openai`
   - JS/TS: `npm install langfuse openai @langchain/openai`
6. **Concepts**: Understand traces (top-level), spans (nested work), generations (LLM calls), and scores.

## Procedure

### 1. Configure environment (Windows PowerShell primary)

```powershell
# PowerShell — set for current session
$env:LANGFUSE_PUBLIC_KEY = "pk-lf-YOUR_KEY"
$env:LANGFUSE_SECRET_KEY = "sk-lf-YOUR_KEY"
$env:LANGFUSE_HOST = "https://cloud.langfuse.com"  # or self-hosted URL
$env:OPENAI_API_KEY = "YOUR_KEY"
```

On Windows, persist with `setx` (requires new shell to take effect):
```powershell
setx LANGFUSE_PUBLIC_KEY "pk-lf-YOUR_KEY"
setx LANGFUSE_SECRET_KEY "sk-lf-YOUR_KEY"
setx LANGFUSE_HOST "https://cloud.langfuse.com"
```

The Python/JS SDKs auto-read `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` — explicit constructor args override env vars.

### 2. Basic tracing (Python SDK)

```python
from langfuse import Langfuse
import openai

langfuse = Langfuse()  # reads env vars

trace = langfuse.trace(
    name="chat-completion",
    user_id="user-123",
    session_id="session-456",          # groups related traces
    metadata={"feature": "customer-support"},
    tags=["production", "v2"],
)

generation = trace.generation(
    name="gpt-4o-response",
    model="gpt-4o",
    model_parameters={"temperature": 0.7},
    input={"messages": [{"role": "user", "content": "Hello"}]},
    metadata={"attempt": 1},
)

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)

generation.end(
    output=response.choices[0].message.content,
    usage={
        "input": response.usage.prompt_tokens,
        "output": response.usage.completion_tokens,
    },
)

trace.score(name="user-feedback", value=1, comment="User clicked helpful")

langfuse.flush()  # IMPORTANT in serverless/short-lived processes
```

### 3. OpenAI drop-in integration (auto-tracing)

```python
from langfuse.openai import openai  # drop-in replacement

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    name="greeting",            # trace name
    session_id="session-123",
    user_id="user-456",
    tags=["test"],
    metadata={"feature": "chat"},
)

# Streaming supported
stream = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
    name="story-generation",
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")

# Async supported
from langfuse.openai import AsyncOpenAI
async_client = AsyncOpenAI()
# await async_client.chat.completions.create(..., name="async-greeting")
```

### 4. LangChain integration (callback handler)

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    public_key="pk-lf-YOUR_KEY",
    secret_key="sk-lf-YOUR_KEY",
    host="https://cloud.langfuse.com",
    session_id="session-123",
    user_id="user-456",
)

llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}"),
])
chain = prompt | llm

# Per-invocation
response = chain.invoke(
    {"input": "Hello"},
    config={"callbacks": [langfuse_handler]},
)

# Or global default
import langchain
langchain.callbacks.manager.set_handler(langfuse_handler)
response = chain.invoke({"input": "Hello"})
```

Works with agents, retrievers, and tools — pass the handler via `config={"callbacks": [langfuse_handler]}`.

### 5. Decorator pattern (clean instrumentation)

```python
from langfuse.decorators import observe, langfuse_context
import openai

@observe()  # creates a trace
def chat_handler(user_id: str, message: str) -> str:
    context = get_context(message)
    return generate_response(message, context)

@observe()  # nested -> span under parent trace
def get_context(message: str) -> str:
    docs = retriever.get_relevant_documents(message)
    return "\n".join([d.page_content for d in docs])

@observe(as_type="generation")  # LLM generation span
def generate_response(message: str, context: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": message},
        ],
    )
    return response.choices[0].message.content

@observe()
def main_flow(user_input: str):
    langfuse_context.update_current_trace(
        user_id="user-123",
        session_id="session-456",
        tags=["production"],
    )
    result = process(user_input)
    langfuse_context.score_current_trace(name="success", value=1 if result else 0)
    return result

# Async supported: @observe() on async def works.
```

### 6. Prompt management (versioning)

```python
from langfuse import Langfuse
import openai

langfuse = Langfuse()

# Fetch a prompt created in the UI or via API
prompt = langfuse.get_prompt("customer-support-v2")
compiled = prompt.compile(customer_name="John", issue="billing question")

response = openai.chat.completions.create(
    model=prompt.config.get("model", "gpt-4o"),
    messages=compiled,
    temperature=prompt.config.get("temperature", 0.7),
)

# Link a generation to the specific prompt version
trace = langfuse.trace(name="support-chat")
generation = trace.generation(name="response", model="gpt-4o", prompt=prompt)

# Create/update a prompt via API
langfuse.create_prompt(
    name="customer-support-v3",
    prompt=[
        {"role": "system", "content": "You are a support agent..."},
        {"role": "user", "content": "{{user_message}}"},
    ],
    config={"model": "gpt-4o", "temperature": 0.7},
    labels=["production"],  # or ["staging", "development"]
)

# Fetch latest with a specific label
prompt = langfuse.get_prompt("customer-support-v3", label="production")
```

### 7. Evaluation and scoring

```python
from langfuse import Langfuse
import openai

langfuse = Langfuse()
trace = langfuse.trace(name="qa-flow")

# Manual scores
trace.score(name="relevance", value=0.85, comment="Addressed the question")
trace.score(name="correctness", value=1, data_type="BOOLEAN")

# LLM-as-judge
def evaluate_response(question: str, response: str) -> float:
    eval_prompt = f"""Rate the response quality from 0 to 1.
Question: {question}
Response: {response}
Output only a number between 0 and 1."""
    result = openai.chat.completions.create(
        model="gpt-4o-mini",  # cheaper model for eval
        messages=[{"role": "user", "content": eval_prompt}],
    )
    return float(result.choices[0].message.content.strip())

score = evaluate_response(question, response)
trace.score(name="quality-llm-judge", value=score)

# Dataset creation
langfuse.create_dataset(name="support-qa-v1")
langfuse.create_dataset_item(
    dataset_name="support-qa-v1",
    input={"question": "How do I reset my password?"},
    expected_output="Go to settings > security > reset password",
)

# Run eval over dataset
dataset = langfuse.get_dataset("support-qa-v1")
for item in dataset.items:
    response = generate_response(item.input["question"])
    trace = langfuse.trace(name="eval-run")
    trace.generation(name="response", input=item.input, output=response)
    similarity = calculate_similarity(response, item.expected_output)
    trace.score(name="similarity", value=similarity)
    item.link(trace, "eval-run-1")
```

### 8. Flush and shutdown

- Call `langfuse.flush()` before process exit in serverless / short-lived functions.
- For long-running services, the SDK flushes asynchronously on a schedule; still call `langfuse.flush()` on graceful shutdown.

## Pitfalls

- **Missing `flush()` in serverless**: Traces/scores are batched and sent asynchronously. If the process exits before flush, data is lost. Always `langfuse.flush()` before return in Lambda/Cloud Functions/short scripts.
- **Hardcoded keys**: Never commit `pk-`/`sk-` keys. Use env vars (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`).
- **Wrong host for self-hosted**: Must point `host` (or `LANGFUSE_HOST`) at the self-hosted base URL, not `cloud.langfuse.com`. Mismatched host silently sends nowhere or 401s.
- **OpenAI drop-in import shadowing**: `from langfuse.openai import openai` must replace the standard `import openai` everywhere in the module, or calls won't be traced. Mixing the two in the same file is a common bug.
- **Decorator context not set**: `langfuse_context.update_current_trace()` must be called inside an `@observe()`-decorated function; calling it outside a trace raises.
- **Score data type mismatch**: `data_type="BOOLEAN"` expects 0/1; numeric scores expect floats. Mismatched types can break dashboard aggregations.
- **Prompt `compile` missing variables**: Forgetting a `{{var}}` leaves it unresolved silently in some SDK versions — validate compiled output.
- **High-volume ingestion**: Self-hosted Langfuse needs adequate ClickHouse/Postgres resources; high-volume without optimization causes ingestion lag.
- **Real-time dashboard latency**: Scores and traces may take seconds to appear; do not treat the UI as instant.
- **Never delete production prompts/datasets**: Treat labeled `production` prompts and datasets as immutable history. Version forward (`-v3`, `-v4`) instead of overwriting.
- **Windows path/env quirks**: `setx` does not affect the current shell — open a new terminal. PowerShell uses `$env:VAR` for reads, `setx` for persistence.

## Verification

1. **SDK installed and importable**:
   ```powershell
   python -c "import langfuse; print(langfuse.version.__version__)"
   ```
   Expected: a version string (e.g. `2.x.x`).

2. **Env vars present (PowerShell)**:
   ```powershell
   echo $env:LANGFUSE_PUBLIC_KEY
   echo $env:LANGFUSE_SECRET_KEY
   echo $env:LANGFUSE_HOST
   ```
   Expected: non-empty values matching your project.

3. **End-to-end smoke test**:
   ```python
   from langfuse import Langfuse
   langfuse = Langfuse()
   trace = langfuse.trace(name="smoke-test", user_id="verify-user")
   trace.generation(name="noop-gen", model="gpt-4o", input={"messages": []}).end(output="ok")
   trace.score(name="smoke", value=1)
   langfuse.flush()
   print("flushed")
   ```
   Expected: prints `flushed`; within ~30s a trace named `smoke-test` appears in the Langfuse UI Traces tab.

4. **OpenAI drop-in traced**:
   ```python
   from langfuse.openai import openai
   r = openai.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":"ping"}], name="verify-dropin")
   print(r.choices[0].message.content)
   ```
   Expected: a response AND a `verify-dropin` trace in the UI.

5. **LangChain callback traced**: After invoking a chain with `config={"callbacks": [langfuse_handler]}`, confirm a trace with nested spans/generations appears in the UI.

6. **Prompt fetch verified**:
   ```python
   from langfuse import Langfuse
   lf = Langfuse()
   p = lf.get_prompt("customer-support-v2", label="production")
   print(p.name, p.version, p.config)
   ```
   Expected: prints the prompt name, version number, and config dict.

## Related Skills

Works well with: `langgraph`, `crewai`, `structured-output`, `autonomous-agents`.

- **Observable LangGraph Agent** (langfuse + langgraph): Build agent → add Langfuse callback → trace LLM calls and tool uses → score outputs → monitor and iterate.
- **Monitored RAG Pipeline** (langfuse + structured-output): Build RAG → trace retrieval and generation → score relevance/accuracy → track cost/latency → optimize.
- **Evaluated Agent System** (langfuse + langgraph + structured-output): Build agent with structured outputs → create eval dataset → run evals with traces → compare prompt versions → deploy best performers.

## Limitations

- Use this skill only when the task clearly matches Langfuse observability scope.
- Self-hosted infrastructure setup (Docker/Postgres/ClickHouse provisioning) is out of scope; provide the `host` URL only.
- Do not treat output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
