# Skill: Technical TA Engine (2.3)

## Capabilities
- `analyze(ticker, market_data)` → Tier-0 contract with indicator bundle
- Direct query: "What's the RSI of BTC?"
- Direct query: "Show MACD for ETH"

## Trading interpretation (use this in backtest CoT)
- RSI > 70 overbought / bearish tilt; RSI < 30 oversold / bullish tilt.
- MACD cross needs confirmation from trend (EMA 20 vs 50) or volume; a lone cross is weak.
- 3+ aligned indicators → raise composite and confidence; mixed tape → stay near 50 / low confidence.
- When Nexus as-of context is present: F&G ≤ 25 is risk-off (fade breakouts, prefer shorts/holds); F&G ≥ 75 is risk-on (do not fade every dip). Headlines are facts for this bar only.
- Output the full `ta_indicators` bundle plus `composite` (0–100) and `confidence` (0–1).

## Data Sources
- OHLCV bars (configurable period & count)
- Indicator catalog: RSI, MACD, BB, EMA, SMA, ATR, Ichimoku
- Optional as-of Nexus: Fear & Greed, funding, headlines

## Query Interface
```
/technical_ta_engine?ticker=BTC/USDT&period=4h&bars=100
```
Returns: full indicator bundle + status.

## Dependencies
- `ta` Python library or custom indicator implementation
- Exchange OHLCV fetcher
