# Quickstart: Session Budget Enforcement Guardrails

**Branch**: `109-session-budget-guardrails` | **Date**: 2026-08-14

## What This Does

Prevents runaway API costs by enforcing per-session spending caps and tool-call
depth limits. After this feature, a casual phone question can never silently burn
$11+ in API costs.

## Quick Setup (30 seconds)

Add to your `openclaw.json` under `agents.defaults`:

```json
{
  "agents": {
    "defaults": {
      "budget": {
        "sessionBudgetUsd": 5.0,
        "maxToolCallsPerTurn": 20
      },
      "interfaceDefaults": {
        "openai": { "model": "anthropic/claude-haiku-4-5" },
        "n2n": { "model": "anthropic/claude-haiku-4-5" }
      }
    }
  }
}
```

Restart the gateway. Done.

## What Happens When a Budget Is Hit

When the session cost cap is reached:

```
⚠️ Session budget reached ($5.02 / $5.00 cap)

Summary:
  • 34 API calls, 890K input tokens, 12K output tokens
  • Top cost: exec (18 calls, $2.10), github-mcp (4 calls, $1.40)
  • Session duration: 47 minutes

To continue, say "override budget" (adds $2.00 to ceiling).
To start fresh, begin a new session.
```

When the tool-call limit is reached:

```
⚠️ Tool call limit reached (20/20 this turn)

Here's what I found so far:
  [intermediate findings summary]

Should I continue investigating? (say "yes" to allow 20 more calls)
```

## Environment Variable Override

For quick adjustments without touching config:

```bash
export NETCLAW_SESSION_BUDGET_USD=2.0  # Override session cap
```

## Verification

After setup, check that the Prometheus metric exists:

```bash
curl -s http://localhost:9090/api/v1/query \
  --data-urlencode 'query=netclaw_session_budget_trips_total' | jq .
```

The counter should appear (value 0 until a cap is hit).

## Defaults (if you configure nothing)

| Setting | Default | Effect |
|---------|---------|--------|
| `sessionBudgetUsd` | 5.0 | Sessions halt at $5 |
| `maxToolCallsPerTurn` | 20 | Agent pauses after 20 tool calls |
| `contextWarningTokens` | 100000 | Warning at 100K context tokens |
| `contextAutoSummarize` | false | No auto-summarization |
| `interfaceDefaults.openai.model` | (inherits primary) | Falls back to agent default |

## Alerting (Optional)

Add to your Prometheus alerting rules:

```yaml
- alert: NetclawSessionBudgetTripped
  expr: increase(netclaw_session_budget_trips_total[1h]) > 3
  for: 0m
  labels:
    severity: warning
  annotations:
    summary: "Multiple session budget halts in the last hour"
    description: "{{ $value }} sessions hit their cost cap. Check if budget is too low or if something is triggering expensive agentic chains."
```
