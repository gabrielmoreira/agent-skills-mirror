---
name: trader-backtest
description: Run a historical backtest using npx neural-trader with Rust/NAPI engine (8-19x faster) and walk-forward validation
allowed-tools: Bash Read mcp__claude-flow__memory_store mcp__claude-flow__memory_retrieve mcp__claude-flow__memory_search mcp__claude-flow__neural_train mcp__claude-flow__agentdb_pattern-store
argument-hint: "<strategy-name> --symbol <TICKER> [--period 2020-2024]"
---
Run a historical backtest using the `neural-trader` Rust/NAPI engine.

Steps:
1. Ensure neural-trader is available:
   `npm ls neural-trader 2>/dev/null || npm install neural-trader`
2. Check for saved strategy config:
   `mcp__claude-flow__memory_retrieve({ key: "strategy-STRATEGY_NAME", namespace: "trading-strategies" })`
   If not found, list available: `mcp__claude-flow__memory_search({ query: "strategy", namespace: "trading-strategies", limit: 10 })`
3. Run backtest via neural-trader CLI:
   ```bash
   npx neural-trader --backtest --strategy <name> --symbol <TICKER> --period <range> --walk-forward
   ```
   For multi-indicator strategies:
   ```bash
   npx neural-trader --backtest --strategy multi-indicator --position-sizing kelly --symbol SPY --period 2020-2024
   ```
4. Capture performance metrics from output: total return, annualized return, Sharpe ratio, Sortino ratio, max drawdown, win rate, profit factor, number of trades
5. Store backtest results:
   `mcp__claude-flow__memory_store({ key: "backtest-STRATEGY-TIMESTAMP", value: "RESULTS_JSON", namespace: "trading-backtests" })`
6. If Sharpe > 1.5, store as successful pattern:
   `mcp__claude-flow__agentdb_pattern-store({ pattern: "profitable-STRATEGY_TYPE", data: "PARAMS_AND_RESULTS" })`
7. Train SONA on the outcome:
   `mcp__claude-flow__neural_train({ patternType: "trading-strategy", epochs: 10 })`
