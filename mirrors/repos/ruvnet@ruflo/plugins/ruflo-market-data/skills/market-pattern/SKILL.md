---
name: market-pattern
description: Detect and classify candlestick patterns from ingested OHLCV data
argument-hint: "<symbol> [--period 1D]"
allowed-tools: mcp__claude-flow__agentdb_hierarchical-recall mcp__claude-flow__agentdb_pattern-store mcp__claude-flow__agentdb_pattern-search mcp__claude-flow__ruvllm_hnsw_route Bash
---

# Market Pattern

Scan ingested OHLCV data for known candlestick patterns, classify them by type and reliability, and store for future reference.

## When to use

When you need to identify candlestick patterns (doji, hammer, engulfing, head-shoulders, etc.) in market data. Requires data to be ingested first via `market-ingest`.

## Steps

1. **Load candles** -- call `mcp__claude-flow__agentdb_hierarchical-recall` to retrieve normalized OHLCV data for the symbol and period from `market-data` namespace
2. **Scan for patterns** -- iterate through candle sequences looking for:
   - Single-candle: doji (open ~= close), hammer (long lower wick), inverted hammer
   - Two-candle: bullish/bearish engulfing
   - Three-candle: morning star, evening star, three white soldiers, three black crows
   - Multi-candle: head & shoulders, double top/bottom, cup & handle
3. **Classify** -- for each detection, assign: pattern name, type (reversal/continuation), direction (bullish/bearish), reliability score (0.0-1.0)
4. **Rank** -- sort by reliability score descending
5. **Store** -- call `mcp__claude-flow__agentdb_pattern-store` to persist each detected pattern in `market-patterns` namespace with the pattern vector
6. **Report** -- display: pattern name, date range, direction, reliability, suggested action

## CLI alternative

```bash
npx @claude-flow/cli@latest memory search --query "bullish reversal patterns" --namespace market-patterns
```
