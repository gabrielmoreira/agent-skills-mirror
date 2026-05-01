---
type: skill
lifecycle: stable
inheritance: inheritable
name: ai-agent-design
description: Design autonomous AI agents that reason, plan, and execute tasks
tier: standard
applyTo: '**/*agent*,**/*design*'
currency: 2026-04-20
lastReviewed: 2026-04-30
---

# AI Agent Design Skill


> Patterns for designing AI agents—autonomous systems that use LLMs to reason, plan, and execute multi-step tasks.

## Agent vs Chatbot vs Workflow

| Aspect | Chatbot | Workflow | Agent |
|--------|---------|----------|-------|
| Autonomy | Low | None | High |
| Planning | None | Predefined | Dynamic |
| Tool Use | Limited | Fixed | Flexible |
| Memory | Session | None | Persistent |
| Error Recovery | Retry | Fail | Reason & adapt |

## Core Patterns

### ReAct (Reasoning + Acting)

```text
1. Thought: Reason about the task
2. Action: Choose and execute a tool
3. Observation: Process tool output
4. Repeat until complete
```

**Example:**

```text
Thought: Need Seattle weather to answer umbrella question
Action: weather_api(location="Seattle")
Observation: {"temp": 52, "condition": "rain", "precipitation": 80%}
Thought: Raining with 80% precipitation. Recommend umbrella.
```

### Plan-and-Execute

For complex multi-step tasks:

1. **Planner**: Create high-level plan
2. **Executor**: Execute each step
3. **Replanner**: Adjust based on results

Use when order matters and partial failures need recovery.

### Reflexion

Self-improvement through reflection:

1. Attempt task
2. Evaluate outcome
3. Generate reflection on failures
4. Store reflection in memory
5. Retry with reflection context

## Multi-Agent Patterns

### Supervisor

Central coordinator delegates to specialists:

```text
       Supervisor
      /    |    \
Research Writer Reviewer
```

### Hierarchical Teams

Nested supervisors for complex organizations:

```text
      Top Supervisor
       /         \
Research Lead  Writing Lead
   /    \         /    \
Web   Paper   Draft   Edit
```

### Debate/Adversarial

Multiple agents argue to reduce hallucination:

```text
Agent A (Pro) <--argue--> Agent B (Con)
              \    |    /
               Judge
```

## Tool Design

```json
{
  "name": "search_database",
  "description": "Search products. Use for availability/pricing queries.",
  "parameters": {
    "query": { "type": "string", "description": "Search terms" },
    "max_results": { "type": "integer", "default": 10 }
  }
}
```

**Principles:**

- Clear names (verb + noun)
- Rich descriptions with when/what
- Sensible defaults
- Structured error returns

### Tool Selection by Scale

| Tools | Strategy |
|-------|----------|
| < 10 | Direct selection |
| 10-50 | Categorize first |
| 50+ | Embed and retrieve |

## Memory Architecture

```text
Working Memory    → Current context (in prompt)
Short-Term Memory → Session state (key-value)
Long-Term Memory  → Facts, history (vector DB + graph)
```

### Memory Types

| Type | Storage | Use Case |
|------|---------|----------|
| Episodic | Vector DB | Past conversations |
| Semantic | Graph DB | Facts, relationships |
| Procedural | Code/prompts | How to do tasks |
| Working | Prompt | Current task |

### Memory Management

- **Summarization**: Compress old conversations
- **Forgetting**: Score by recency × importance × access
- **Consolidation**: Merge similar memories

## Error Recovery Ladder

1. **Retry**: Same action with backoff
2. **Rephrase**: Different query, same goal
3. **Alternative**: Different tool, same goal
4. **Partial**: Return partial results
5. **Escalate**: Ask human
6. **Abort**: Cannot complete, explain why

### Loop Detection

```python
def detect_loop(history, window=5, threshold=0.8):
    recent = history[-window:]
    previous = history[-window*2:-window]
    return similarity(recent, previous) > threshold
```

Recovery: reflection prompt, force tool change, replan, escalate.

## Human-in-the-Loop

Require approval for high-risk actions:

- Financial transactions
- Data deletion
- External communications
- Permission changes
- Irreversible operations

## Production Considerations

### Observability

Log: LLM calls, tool calls, state transitions, errors, recovery attempts.

### Cost Control

| Strategy | Implementation |
|----------|----------------|
| Token budgets | Max tokens per task |
| Step limits | Max N actions |
| Tiered models | GPT-4 plan, 3.5 execute |
| Caching | Cache tool/LLM results |
| Early termination | Stop when good enough |

### Safety Guardrails

- Input: Injection detection, PII filtering, rate limiting
- Action: Parameter sanitization, permission checks
- Output: Policy compliance, hallucination detection

## Framework Comparison

| Framework | Best For |
|-----------|----------|
| LangChain | Rapid prototyping |
| LangGraph | Complex multi-agent |
| AutoGen | Research, code gen |
| CrewAI | Business workflows |
| Semantic Kernel | Microsoft stack |

## Anti-Patterns

- **Over-autonomous**: No approval checkpoints
- **Unbounded loops**: No termination conditions
- **Tool explosion**: Too many tools confuse agent
- **Memory bloat**: No pruning strategy
- **Monolithic**: One agent does everything

## Checklist

- [ ] Clear agent persona and capabilities
- [ ] Minimal, well-described tool set
- [ ] Appropriate memory architecture
- [ ] Human-in-the-loop for high-risk
- [ ] Observability (logging, tracing)
- [ ] Safety guardrails
- [ ] Adversarial input testing
- [ ] Cost control and scaling plan

## When to Use

✅ **Good**: Open-ended research, multi-step workflows, tool orchestration
❌ **Poor**: Simple Q&A (use RAG), deterministic flows (use code), no human oversight
