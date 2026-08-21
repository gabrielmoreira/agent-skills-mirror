---
name: multi-agent-architect
description: "Wires LangGraph StateGraph systems with typed shared state, supervisor routing, and DeepAgents-style critique loops. Trigger on planner/researcher/coder/validator graphs or Redis-scoped session history. Not for single-chain RAG, or selecting Mem0 vs Graphiti as the memory product."
version: 1.0.1
risk: safe
source: community
metadata:
  category: ai-engineering
  source_repo: pravin-python/antigravity-awesome-skills
  source_type: community
  date_added: "2025-05-07"
  author: community
  tags: [langgraph, langchain, multi-agent, orchestration, deepagents, rag, tool-calling]
  tools: [claude, cursor, gemini]
  license: "MIT"
  license_source: "https://github.com/pravin-python/antigravity-awesome-skills/blob/main/LICENSE"
---

# Multi-Agent Architect

## Overview

This skill turns the agent into a Senior AI Multi-Agent Architect specialized in LangGraph, LangChain, and DeepAgents. It provides structured workflows for creating and updating production-grade multi-agent systems — including supervisor agents, planners, researchers, coders, and memory-backed autonomous pipelines.

**Trigger keywords:** multi-agent, LangGraph, supervisor agent, agent orchestration, DeepAgents, agent workflow, planner agent, conditional routing, agent state graph.

## When to Use

- Creating a new agent or multi-agent workflow from scratch
- Working with LangGraph state graphs, nodes, edges, or conditional routing
- Questions about agent communication, memory systems, or tool-calling pipelines
- Debugging or optimizing an existing LangChain/LangGraph agent system
- Architecting supervisor, planner, research, coding, or validation agent roles
- Integrating DeepAgents with hierarchical planning and delegation

## Prerequisites

- Python 3.10+ installed and available on PATH
- `langgraph`, `langchain-openai`, `langchain-community` installed — verify with:
  ```powershell
  pip show langgraph langchain-openai langchain-community
  ```
- Redis instance reachable if using Redis-backed memory (set `REDIS_URL` env var)
- `OPENAI_API_KEY` set as an environment variable — never hardcode in source
- FastAPI + Uvicorn only if exposing the graph as a REST API

## Procedure

### 1. Clarify the Goal

Before writing any code, determine:

- **Business objective** the agent system must achieve
- **Agent roles** needed (supervisor, planner, researcher, coder, validator)
- **Tools** each agent requires
- **Memory strategy** (Redis, Vector DB, LangChain Memory)
- **Communication protocol** connecting agents (shared state, message passing)

If the goal, tool permissions, or routing logic are ambiguous, **stop and ask for clarification** before generating a full architecture.

### 2. Define the State Schema

All agents share a typed state object passed through the graph:

```python
from typing import TypedDict

class AgentState(TypedDict):
    user_goal: str
    tasks: list[str]
    completed_tasks: list[str]
    next_agent: str
    context: dict
    step_count: int          # guards against infinite loops
    error: str | None
```

### 3. Define Agent Nodes

Each agent is an **async function** that reads from state and returns updated state:

```python
import logging
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

async def research_node(state: AgentState) -> AgentState:
    logger.info("research_node: starting")
    llm = ChatOpenAI(model="gpt-4o")
    result = await llm.bind_tools(research_tools).ainvoke(state["user_goal"])
    state["context"]["research"] = result.content
    state["next_agent"] = "coder"
    return state
```

### 4. Build the LangGraph

Wire nodes together with edges and conditional routing:

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("research",   research_node)
    graph.add_node("coder",      coding_node)
    graph.add_node("validator",  validation_node)
    graph.add_node("tools",      ToolNode(all_tools))

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_next,
        {"research": "research", "coder": "coder", "end": END}
    )

    graph.add_edge("research",  "supervisor")
    graph.add_edge("coder",     "validator")
    graph.add_edge("validator", "supervisor")

    return graph.compile()

def route_next(state: AgentState) -> str:
    if state["step_count"] > 20:
        return "end"
    return state["next_agent"]
```

### 5. Add Memory

```python
import os
from langchain_community.chat_message_histories import RedisChatMessageHistory

def get_memory(session_id: str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=os.getenv("REDIS_URL"),
        ttl=3600
    )
```

### 6. Run the Graph

```python
async def run(user_goal: str, session_id: str):
    graph = build_graph()
    initial_state = AgentState(
        user_goal=user_goal,
        tasks=[],
        completed_tasks=[],
        next_agent="supervisor",
        context={},
        step_count=0,
        error=None,
    )
    return await graph.ainvoke(initial_state)
```

### 7. Expose via FastAPI (optional)

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RunRequest(BaseModel):
    goal: str
    session_id: str

@app.post("/run")
async def run_agent(req: RunRequest):
    result = await run(req.goal, req.session_id)
    return {"result": result}
```

### 8. Generate Standard Folder Structure

Always generate code in this layout:

```
multi_agent_system/
├── agents/          # One file per agent role
├── tools/           # Tool definitions and wrappers
├── memory/          # Redis, VectorDB, LangChain memory helpers
├── prompts/         # Prompt templates (one per agent)
├── workflows/       # High-level orchestration logic
├── graphs/          # LangGraph state + compiled graph definitions
├── api/             # FastAPI routes (optional)
├── configs/         # Config loader — no secrets in code
├── tests/           # Unit + integration tests per agent
└── main.py
```

### 9. Updating an Existing Agent

When the user wants to update or debug an existing agent, structure the response as:

| Section | Content |
|---|---|
| **Existing Issue** | Describe the current problem |
| **Root Cause** | Identify why it's happening in the architecture |
| **Proposed Update** | Outline the changes at architecture level |
| **Updated Code** | Generate only the changed modules |
| **Migration Notes** | What breaks, what's backward-compatible |
| **Performance Impact** | Latency / token / memory delta |

## Examples

### Example 1: Research + Coding Multi-Agent Workflow

```python
# agents/research_agent.py
async def research_node(state: AgentState) -> AgentState:
    llm = ChatOpenAI(model="gpt-4o").bind_tools([web_search, rag_search])
    response = await llm.ainvoke(
        f"Research the following and return structured findings:\n{state['user_goal']}"
    )
    state["context"]["research"] = response.content
    state["next_agent"] = "coder"
    return state

# agents/coding_agent.py
async def coding_node(state: AgentState) -> AgentState:
    llm = ChatOpenAI(model="gpt-4o").bind_tools([python_repl, github_tool])
    response = await llm.ainvoke(
        f"Given this research:\n{state['context']['research']}\n\nWrite production Python code."
    )
    state["context"]["code"] = response.content
    state["next_agent"] = "validator"
    return state
```

### Example 2: Supervisor with Dynamic Delegation

```python
# agents/supervisor_agent.py
DELEGATION_PROMPT = """
You are a supervisor. Given the current state, decide the next agent.
Available agents: research, coder, validator, end.
Respond with ONLY the agent name.

Goal: {goal}
Completed: {completed}
Context keys available: {context}
"""

async def supervisor_node(state: AgentState) -> AgentState:
    state["step_count"] += 1
    llm = ChatOpenAI(model="gpt-4o")
    decision = await llm.ainvoke(
        DELEGATION_PROMPT.format(
            goal=state["user_goal"],
            completed=state["completed_tasks"],
            context=list(state["context"].keys()),
        )
    )
    next_agent = decision.content.strip().lower()
    # Validate against allowlist before setting
    allowed = {"research", "coder", "validator", "end"}
    state["next_agent"] = next_agent if next_agent in allowed else "end"
    return state
```

### Example 3: DeepAgents Reflection Loop

```python
async def reflection_node(state: AgentState) -> AgentState:
    llm = ChatOpenAI(model="gpt-4o")
    critique = await llm.ainvoke(
        f"Evaluate this output critically:\n{state['context'].get('code', '')}\n"
        "List any bugs, gaps, or improvements. Be concise."
    )
    state["context"]["critique"] = critique.content
    state["next_agent"] = "coder" if "bug" in critique.content.lower() else "end"
    return state
```

## Pitfalls

- **Agent loops indefinitely between supervisor and sub-agents** — Add `step_count: int` to state; return `"end"` in `route_next()` when `step_count > N` (default 20).
- **Supervisor routes to a non-existent agent name** — Validate the LLM's routing output against a hardcoded allowlist before setting `next_agent`.
- **Memory leaks across user sessions** — Scope Redis keys to `session_id` and always set a TTL (`ttl=3600`).
- **Tool results are ignored by the next agent** — Always write tool output into `state["context"]` and confirm the next node reads it.
- **Agents share too many tools and hallucinate wrong tool calls** — Use `.bind_tools([only_relevant_tools])` per agent instead of a global tool list.
- **Graph fails silently on API rate limits** — Wrap LLM calls in retry logic with exponential backoff using `tenacity`.
- **Hardcoded secrets in generated code** — All secrets must use `os.getenv()`:
  ```python
  OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")   # ✅ correct
  OPENAI_API_KEY = "sk-..."                        # ❌ never do this
  ```
- **Unvalidated user input injected into prompts** — Treat all user input as untrusted; sanitize before injection.
- **Python REPL tool runs outside sandbox** — Document that `python_repl` tool nodes must only run in a sandboxed, isolated environment.
- **No rate-limit handling in production** — Add rate-limit handling and exponential backoff on all LLM and external API calls.

## Verification

1. **Confirm package versions are installed and compatible:**
   ```powershell
   pip show langgraph langchain-openai langchain-community
   ```
   Expected: each package prints its version with no "not found" error.

2. **Verify no hardcoded secrets exist in generated code:**
   ```powershell
   Select-String -Path .\multi_agent_system\**\*.py -Pattern "sk-[a-zA-Z0-9]" -SimpleMatch
   ```
   Expected: no matches. All keys must come from `os.getenv()`.

3. **Run the graph end-to-end with a test goal:**
   ```python
   import asyncio
   result = asyncio.run(run("Build a hello-world FastAPI endpoint", "test-session-001"))
   assert result["step_count"] <= 20, "Step count exceeded guard — possible infinite loop"
   assert result["error"] is None, f"Graph returned error: {result['error']}"
   ```

4. **Verify Redis memory scoping (if Redis is used):**
   ```powershell
   redis-cli KEYS "test-session-001:*"
   ```
   Expected: keys are scoped to the session ID and have a TTL set.

5. **Verify supervisor routing allowlist enforcement:**
   ```python
   # Inject an invalid next_agent and confirm route_next returns "end"
   test_state = AgentState(user_goal="x", tasks=[], completed_tasks=[],
                           next_agent="nonexistent", context={}, step_count=25, error=None)
   assert route_next(test_state) == "end"
   ```

6. **Verify FastAPI endpoint (if API layer is generated):**
   ```powershell
   uvicorn main:app --reload --port 8000
   curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d '{"goal":"test","session_id":"smoke"}'
   ```
   Expected: HTTP 200 with a JSON result body.

## Best Practices

- ✅ One agent = one responsibility — never combine planning + coding + testing in one node
- ✅ Use `TypedDict` for all state schemas — enables type checking and graph validation
- ✅ Bind only the tools each agent needs — reduces hallucinated tool calls
- ✅ Always add a `step_count` guard to prevent infinite routing loops
- ✅ Use `async`/`await` throughout — LangGraph supports async natively
- ✅ Store all secrets in environment variables loaded via `os.getenv()`
- ✅ Set TTLs on all Redis keys scoped to `session_id`
- ✅ Log at every node entry and tool call for observability
- ✅ Validate supervisor routing output against an allowlist of agent names
- ❌ Don't hardcode API keys, model names, or Redis URLs
- ❌ Don't share tool lists across agents that don't need them
- ❌ Don't skip error handling — tool failures and empty LLM responses are common
- ❌ Don't trust unvalidated LLM routing decisions — always check against an allowlist

## Limitations

- This skill does not replace environment-specific testing, load testing, or security review before production deployment.
- Generated LangGraph code targets the current stable API — always verify method signatures against your installed version (`pip show langgraph`).
- Stop and ask for clarification if the agent's goal, tool permissions, or routing logic is ambiguous before generating a full architecture.
- DeepAgents integration patterns assume the library is installed and configured in the target environment.

## Related Skills

- `langchain-rag` — When you need retrieval-augmented generation pipelines specifically
- `fastapi-backend` — When deploying agent systems as production REST APIs
- `python-async` — When deepening async/await patterns used throughout agent nodes
