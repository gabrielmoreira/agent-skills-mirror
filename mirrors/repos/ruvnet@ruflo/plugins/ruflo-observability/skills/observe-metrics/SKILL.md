---
name: observe-metrics
description: Aggregate and display system metrics with anomaly detection for a time period
argument-hint: "[--period 1h]"
allowed-tools: mcp__claude-flow__agentdb_hierarchical-recall mcp__claude-flow__agentdb_pattern-search mcp__claude-flow__agentdb_pattern-store mcp__claude-flow__agentdb_semantic-route Bash
---

# Observe Metrics

Aggregate counters, gauges, and histograms from the observability namespace and flag anomalies.

## When to use

When you need a snapshot of system health -- task completion rates, error rates, active agent counts, memory usage, and token consumption. Useful for monitoring swarm performance and detecting degradation.

## Steps

1. **Retrieve metrics** -- call `mcp__claude-flow__agentdb_hierarchical-recall` to fetch metric records from the `observability` namespace for the specified period (default: 1 hour)
2. **Aggregate** -- compute:
   - Counters: sum totals (tasks_completed, errors, token_usage)
   - Gauges: current values (active_agents, memory_usage_bytes)
   - Histograms: p50, p95, p99 (task_duration_ms, span_duration_ms)
3. **Compute baselines** -- search for historical patterns via `mcp__claude-flow__agentdb_pattern-search` to establish baseline values for each metric
4. **Flag anomalies** -- mark metrics deviating >2 standard deviations from baseline with direction (above/below) and severity
5. **Store patterns** -- call `mcp__claude-flow__agentdb_pattern-store` to record current metric snapshot for future baseline comparison
6. **Report** -- display: metric name, current value, baseline, deviation, trend (up/down/stable), anomaly flag; overall health score (green/yellow/red)

## CLI alternative

```bash
npx @claude-flow/cli@latest memory search --query "system metrics for last hour" --namespace observability
```
