---
name: cost-report
description: Generate a cost report showing token usage and USD costs by agent and model
argument-hint: "[--period today]"
allowed-tools: mcp__claude-flow__agentdb_hierarchical-recall mcp__claude-flow__agentdb_semantic-route mcp__claude-flow__agentdb_pattern-search Bash
---

# Cost Report

Generate a comprehensive cost report showing token usage, USD costs, and budget utilization for the specified period.

## When to use

When you need to understand current spending -- how much each agent costs, which models consume the most budget, and whether you're on track to stay within budget.

## Steps

1. **Retrieve usage** -- call `mcp__claude-flow__agentdb_hierarchical-recall` to fetch token usage records from the `cost-tracking` namespace for the specified period (default: today)
2. **Compute costs** -- for each record, calculate cost using model pricing:
   - Haiku: $0.25/M input, $1.25/M output
   - Sonnet: $3.00/M input, $15.00/M output
   - Opus: $15.00/M input, $75.00/M output
   - Include cache write/read costs where applicable
3. **Aggregate by model** -- sum costs per model, compute percentage share
4. **Aggregate by agent** -- sum costs per agent, include the model each agent used
5. **Check budget** -- recall budget configuration and compute utilization percentage, check alert thresholds (50%/75%/90%/100%)
6. **Report** -- display: total cost, budget remaining, model breakdown, agent breakdown, active alerts

## CLI alternative

```bash
npx @claude-flow/cli@latest memory search --query "cost report for today" --namespace cost-tracking
```
