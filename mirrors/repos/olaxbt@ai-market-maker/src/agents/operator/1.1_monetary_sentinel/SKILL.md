# Skill: Monetary Sentinel (1.1)

## Capabilities
- `analyze(ticker, market_data, nexus_context)` → Tier-0 contract
- Direct query: "What's the current macro regime for BTC?"
- Direct query: "Is there a liquidity crisis signal?"

## Data Sources (as-of the bar date; never later prints)
- Fear & Greed — crypto mood (0–100)
- FRED — VIX, fed funds, 10y yield, trade-weighted USD, SPX, WTI
- DefiLlama lag-1 — stablecoin supply and all-chain TVL, 7d change
- OHLCV window return/vol — fallback liquidity proxy only

## How to read the overlay
- High VIX (≥32) or F&G ≤25 → Risk-Off even if TVL is up
- Rising fed funds / strong DXY → tighter dollar liquidity, lean Risk-Off
- Stablecoin or TVL 7d ≤ −8% → on-chain drain, Risk-Off
- F&G ≥75 with falling VIX and expanding stablecoins → Risk-On
- Quote the printed VIX / DXY / fed funds / 7d TVL change in reasoning; do not invent later data

## Query Interface
```
/monetary_sentinel?ticker=BTC/USDT
```
Returns: macro regime state + liquidity score + reasoning.

## Dependencies
- Historical overlay in backtest (`data/macro/*.csv` via `HistoricalNexusProvider`)
- Live Nexus `market_overview` when not in backtest
- Falls back to OHLCV stubs when those files/endpoints are missing
