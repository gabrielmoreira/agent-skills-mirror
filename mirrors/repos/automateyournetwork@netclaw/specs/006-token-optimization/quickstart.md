# Quickstart: Token Optimization (Count + TOON)

**Feature**: 006-token-optimization
**Date**: 2026-03-26

## Prerequisites

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable set
- Existing NetClaw installation

## Installation

```bash
# Install new dependencies
pip install anthropic toon-format

# The shared library is at src/netclaw_tokens/
# Ensure src/ is on your PYTHONPATH or install as editable package
```

## Quick Verification

```python
# 1. Test token counting
from netclaw_tokens.counter import count_tokens
result = count_tokens("Hello, how many tokens is this?")
print(f"Tokens: {result.input_tokens}, Estimated: {result.estimated}")

# 2. Test TOON serialization
from netclaw_tokens.toon_serializer import serialize_response
data = [{"hostname": "R1", "interface": "Gi0/0", "status": "up"},
        {"hostname": "R1", "interface": "Gi0/1", "status": "down"}]
response = serialize_response(data)
print(f"TOON output:\n{response.toon_data}")
print(f"Savings: {response.savings_pct:.1f}%")

# 3. Test cost calculation
from netclaw_tokens.cost_calculator import calculate_cost
cost = calculate_cost(input_tokens=1245, output_tokens=382, model="claude-opus-4-6")
print(f"Cost: ${cost.total_cost:.4f}")

# 4. Test footer formatting
from netclaw_tokens.footer import format_footer
footer = format_footer(result, cost, toon_savings=response.savings_tokens)
print(footer)
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | API key for token counting (already used by NetClaw) |
| `NETCLAW_TOKEN_PRICING_OVERRIDE` | No | JSON string to override default model pricing |

## What Changed

- All MCP server responses now use TOON format (JSON fallback on error)
- Every interaction displays a token/cost footer
- Session-level token tracking available via "show session token usage"
- HEARTBEAT.md check-ins include token summaries
- SOUL.md mandates token transparency as core behavior
