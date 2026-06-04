---
mode: agent
description: Summarize agent metrics for a window (default last 24h). Invokes the observer agent; reports tokens, context-budget exceedances, approval-gate stats, anomalies, and growth watchlist.
---

# /ai-metrics

Run the [`observer`](../agents/pds-meta-observer.agent.md) agent over a metrics window.

## Behavior

1. Default window: trailing 24 hours.
2. If the user provides arguments, parse them as:
   - `--from <ISO>` and/or `--to <ISO>`
   - `--agent <name>` (repeatable)
   - `--trace <id>` (repeatable)
   - `--days <N>` (cap at 7)
3. Build an envelope with `task: "summarize metrics"`, the resolved `window`, and dispatch to the observer agent.
4. Print the returned `digest` as compact tables in this order:
   - **Window**: from / to / agents counted / events counted
   - **Totals**: tokens, files_read, bytes_read, tool_calls, approvals (requested/granted/denied), outcomes
   - **Per-agent**: rows of `agent | invocations | total_tokens | budget_exceedances | failure_count`
   - **Per-stage**: rows of `stage | invocations | p50_ms | p95_ms`
   - **Anomalies**: rows of `id | severity | count | first_seen | last_seen | remedy`
   - **Growth watchlist**: files flagged by plugin-compliance with `status: split-required` or `watch`
5. End with the `observer_verdict` and any `handoffs[]` the observer proposed. Do not auto-execute handoffs — the user decides.

## Hard rules

- Pure reporting; never modifies metrics, source, or rules.
- Refuses windows wider than 7 days unless `--force` is passed.
- Never prints raw `notes` fields verbatim — they may contain user content; truncate to 80 chars.
