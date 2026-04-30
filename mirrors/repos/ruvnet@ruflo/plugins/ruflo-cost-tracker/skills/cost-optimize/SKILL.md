---
name: cost-optimize
description: Analyze token usage patterns and recommend cost optimizations with estimated savings
argument-hint: ""
allowed-tools: mcp__claude-flow__agentdb_hierarchical-recall mcp__claude-flow__agentdb_pattern-search mcp__claude-flow__agentdb_pattern-store mcp__claude-flow__agentdb_semantic-route Bash
---

# Cost Optimize

Analyze recent token usage across agents and models, identify waste, and recommend specific optimizations with estimated dollar savings.

## When to use

When costs are higher than expected or you want to proactively reduce spending. Analyzes model selection efficiency, cache utilization, agent redundancy, and prompt efficiency.

## Steps

1. **Load usage data** -- call `mcp__claude-flow__agentdb_hierarchical-recall` to fetch recent token usage records from `cost-tracking` namespace (last 7 days)
2. **Analyze model fit** -- for each agent, assess whether the model tier matches task complexity:
   - Agents doing simple tasks (formatting, linting) on Sonnet/Opus -> suggest Haiku or Agent Booster
   - Agents doing complex tasks (architecture, security) on Haiku -> flag quality risk
3. **Check cache rates** -- compute cache hit rate per agent; if below 60%, recommend enabling or improving prompt caching (90% cost reduction on cache reads)
4. **Detect redundancy** -- look for multiple agents performing overlapping tasks, or agents being spawned for work that could be batched
5. **Estimate savings** -- for each recommendation, calculate: current cost, projected cost after optimization, dollar savings, percentage reduction
6. **Search patterns** -- call `mcp__claude-flow__agentdb_pattern-search` for previously successful optimizations
7. **Store recommendations** -- call `mcp__claude-flow__agentdb_pattern-store` to record optimization recommendations in `cost-patterns` namespace
8. **Report** -- display: ranked recommendations with savings estimate, total potential savings, implementation priority (quick wins first)

## CLI alternative

```bash
npx @claude-flow/cli@latest memory search --query "cost optimization strategies" --namespace cost-patterns
```
