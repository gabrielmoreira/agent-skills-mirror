---
name: observe-trace
description: Trace agent execution by collecting spans and building a trace tree for a task
argument-hint: "<task-id>"
allowed-tools: mcp__claude-flow__agentdb_hierarchical-recall mcp__claude-flow__agentdb_semantic-route mcp__claude-flow__agentdb_context-synthesize mcp__claude-flow__agentdb_pattern-search Bash
---

# Observe Trace

Collect distributed trace spans for a task and build a visual trace tree showing the execution flow, timing, and bottlenecks.

## When to use

When you need to understand how a task was executed across agents -- which spans ran, how long each took, where bottlenecks occurred, and how agents coordinated.

## Steps

1. **Collect spans** -- call `mcp__claude-flow__agentdb_hierarchical-recall` to retrieve all spans matching the `<task-id>` from the `observability` namespace
2. **Build trace tree** -- organize spans into a parent-child hierarchy using `parentSpanId` references, with the root span at the top
3. **Calculate timing** -- for each span, compute duration (endTime - startTime), and identify the critical path (longest chain of sequential spans)
4. **Identify bottlenecks** -- flag spans where duration exceeds the p95 for that operation type, or where gaps between spans suggest idle time
5. **Synthesize** -- call `mcp__claude-flow__agentdb_context-synthesize` to combine span metadata into a narrative summary of the execution flow
6. **Report** -- display the trace tree with: span name, agent, duration, status (OK/ERROR), and bottleneck flag; include total trace duration and critical path duration

## CLI alternative

```bash
npx @claude-flow/cli@latest memory search --query "trace spans for task TASK_ID" --namespace observability
```
