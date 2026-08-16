---
name: token-tracker
description: "Track token consumption, enforce session budgets, and display cost for every NetClaw interaction."
version: 2.0.0
license: Apache-2.0
author: netclaw
tags: [budget, cost-control, guardrails]
---

# Skill: Token Tracker + Budget Enforcement

## Purpose

Track and display token consumption and cost for every NetClaw interaction.
**Enforce per-session spending caps and tool-call depth limits** to prevent
runaway API costs. Serialize MCP server responses in GCF format to reduce
token usage by 40-60% on tabular network data.

## What This Prevents

Without this skill, a single casual phone question can trigger unbounded
agentic tool chains that silently burn $10+ in API costs. This skill ensures:

- Sessions halt at a configurable cost ceiling (default: $5)
- Tool-call chains pause after N calls per question (default: 20)
- The operator sees what was accomplished and can choose to continue
- Budget status is visible in every response footer

## Tools Used

This skill uses the `netclaw_tokens` shared library (`src/netclaw_tokens/`):

| Module | Function | Purpose |
|--------|----------|---------|
| counter.py | count_tokens() | Count tokens via Anthropic API (fallback: len/4 estimate) |
| counter.py | count_message_tokens() | Count tokens for full message arrays |
| cost_calculator.py | calculate_cost() | Calculate USD cost with model-aware pricing |
| cost_calculator.py | get_pricing() | Look up model pricing (with env var override) |
| budget_policy.py | BudgetPolicy | Per-session budget configuration |
| budget_policy.py | resolve_session_config() | Load policy from config + interface detection |
| session_ledger.py | SessionLedger | Cumulative tracking + enforcement |
| footer.py | format_footer() | Format mandatory token/cost footer |
| gcf_serializer.py | serialize_response() | Serialize data to GCF with JSON fallback |
| gcf_wrapper.py | wrap_json_response() | Convert JSON responses to GCF |

## Workflow Steps

### On session start

1. **Resolve budget policy**: Call `resolve_session_config(config, session_key)` to get the
   `BudgetPolicy` for this session — accounts for interface type (mobile/desktop/discord),
   per-agent overrides, and environment variable overrides.
2. **Initialize ledger**: Create `SessionLedger(budget=policy)` — enforcement is now active.

### On each user message

3. **Reset turn counter**: Call `session_ledger.new_turn()` — resets tool-call counter for
   this turn.

### Before each tool invocation

4. **Check budget**: Call `session_ledger.check_budget()` → returns `(should_halt, reason)`.
   - If `should_halt` is True: **STOP.** Return `session_ledger.get_halt_message()` to the
     user. Do NOT execute the tool. Do NOT make another API call.
   - If False: proceed.
5. **Record tool call**: Call `session_ledger.record_tool_call()` to increment the per-turn
   counter.

### On each model API response

6. **Count tokens**: Use `count_tokens()` or read the API response usage block.
7. **Calculate cost**: Use `calculate_cost()` with the active model.
8. **Record in ledger**: Call `session_ledger.record()` with tool name, token count, cost,
   and GCF savings.
9. **Format footer**: Use `format_footer()` — now includes budget status.

### On operator "continue" / "override budget"

10. **Override**: Call `session_ledger.override_budget()`.
    - If halt was `tool_limit`: resets the tool-call counter (free, no dollar increase).
    - If halt was `cost_cap`: extends budget by `override_increment_usd` AND resets tools.

## Budget Enforcement Rules

1. **Cost cap is a hard stop.** When `total_cost >= session_budget_usd`, no further API
   calls or tool invocations are permitted until the operator explicitly continues.
2. **Tool-call limit is a soft pause.** When `tool_calls_this_turn >= max_tool_calls_per_turn`,
   the agent pauses, presents findings so far, and asks permission to continue.
3. **Continuation is always explicit.** The agent must NEVER silently resume after a halt.
4. **Mid-stream completion.** If a halt triggers during a multi-tool chain, the current
   response completes (no half-streamed output), then the halt message is appended.
5. **Safe defaults.** If no budget configuration exists in `openclaw.json`, enforcement
   activates with: $5 session cap, 20 tool calls per turn, override allowed (+$2 increments).

## Configuration

### Automatic (zero-config)

Works out of the box with safe defaults. No configuration required.

### Via openclaw.json

```json
{
  "agents": {
    "defaults": {
      "budget": {
        "sessionBudgetUsd": 5.0,
        "maxToolCallsPerTurn": 20,
        "contextWarningTokens": 100000,
        "allowOverride": true,
        "overrideIncrementUsd": 2.0
      },
      "interfaceDefaults": {
        "openai": { "model": "anthropic/claude-haiku-4-5", "thinkingLevel": "medium" },
        "n2n": { "model": "anthropic/claude-haiku-4-5", "thinkingLevel": "medium" },
        "discord": { "model": "anthropic/claude-haiku-4-5", "thinkingLevel": "low" }
      }
    }
  }
}
```

### Via environment variable (quick override)

```bash
export NETCLAW_SESSION_BUDGET_USD=2.0  # Overrides config, takes effect next session
```

## Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | API key for Anthropic token counting (already used by NetClaw) |
| `NETCLAW_TOKEN_PRICING_OVERRIDE` | No | JSON string to override default model pricing |
| `NETCLAW_SESSION_BUDGET_USD` | No | Override session cost cap (default: 5.0) |

## Model Pricing (defaults)

| Model | Input (per 1M) | Output (per 1M) |
|-------|-----------------|------------------|
| Claude Opus 4.6 | $5.00 | $25.00 |
| Claude Sonnet 4.6 | $3.00 | $15.00 |
| Claude Haiku 4.5 | $1.00 | $5.00 |

Prompt caching discount: 90% off cached input tokens.

## Example Usage

```python
from netclaw_tokens import (
    count_tokens, calculate_cost, format_footer,
    SessionLedger, BudgetPolicy, resolve_session_config,
)
from netclaw_tokens.gcf_serializer import serialize_response

# ── Session start ──────────────────────────────────────────────
config = load_openclaw_config()  # Your config loader
session_key = "agent:main:openai:abc-123"  # From gateway

policy = resolve_session_config(config, session_key)
# → BudgetPolicy(session_budget_usd=5.0, model="anthropic/claude-haiku-4-5", ...)

ledger = SessionLedger(budget=policy)

# ── Each user message ──────────────────────────────────────────
ledger.new_turn()

# ── Before each tool call ──────────────────────────────────────
should_halt, reason = ledger.check_budget()
if should_halt:
    return ledger.get_halt_message()  # Return to user, stop processing

ledger.record_tool_call()

# ── After model response ──────────────────────────────────────
tc = count_tokens("show BGP peers on router R1")
cost = calculate_cost(tc.input_tokens, 382, model=policy.model or "claude-sonnet-4-6")
ledger.record("pyats_show_bgp", tc, cost)

# ── Footer (every response) ──────────────────────────────────
footer = format_footer(tc, cost, session_summary=ledger.get_summary())
# Output: Tokens: 8/382/390 | Cost: $0.01 | Session: $0.84/$5.00 (17%) | Tools: 6/20
```

## Session Commands

- **"show session token usage"** — Returns full session summary with per-tool breakdown
- **"show token breakdown by tool"** — Returns ranked per-tool token consumption table
- **"show budget status"** — Returns current budget ceiling, remaining, and tool-call count
- **"override budget"** / **"continue"** — Extends budget or allows more tool calls after halt
- **"compare token usage with and without GCF"** — Shows GCF savings analysis

## Prometheus Metrics (emitted by the exporter)

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `netclaw_session_budget_trips_total` | Counter | agent, reason, interface | Budget halt events |
| `netclaw_model_cost_usd_total` | Counter | agent, model, provider | Cumulative API cost |
| `netclaw_model_calls_total` | Counter | agent, model | API call count |
| `netclaw_session_tool_calls_total` | Counter | agent, interface | Tool invocations |

## GAIT Integration

Token summaries (including budget status and any halt events) are automatically
included in GAIT session logs via `SessionLedger.get_gait_summary()`, providing
an immutable audit trail of token consumption and budget enforcement per session.

## Future: Context Auto-Summarize

When `contextAutoSummarize: true` is configured and context exceeds the warning
threshold, old tool results will be automatically summarized into a compact form
before being re-sent as context. This keeps long sessions viable without constant
"start a new session" friction. (Documented hook — implementation tracked separately.)

## Future: Daily Aggregate Safety Net

Per-session caps protect against single-session runaways. A process-level daily
aggregate cap (`dailyBudgetUsd`) is the next logical layer for protecting against
many concurrent sessions or rapid session cycling. Not in scope for this version
but the SessionLedger architecture supports it (add a shared process-level counter).
