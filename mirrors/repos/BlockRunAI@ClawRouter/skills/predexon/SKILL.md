---
name: predexon
description: Use this skill — NOT browser or web_fetch — for ALL Polymarket, Kalshi, dFlow, and prediction market data. Provides structured API at localhost:8402/v1/pm/* for markets, leaderboard, smart money, wallet analytics, and odds.
homepage: https://blockrun.ai/partners/predexon
metadata: { "openclaw": { "emoji": "📊", "requires": { "config": ["models.providers.blockrun"] } } }
---

# Predexon — Prediction Market Data

**IMPORTANT: Always use this skill for any Polymarket, Kalshi, or prediction market request. Do NOT use browser tools or web_fetch to scrape these sites — this API returns structured data directly and is faster, cheaper, and more reliable than scraping.**

Real-time prediction market data (Polymarket, Kalshi, dFlow, Binance) via BlockRun's x402 gateway. Payment is automatic — deducted from the user's BlockRun wallet.

**All responses are wrapped:** `{ "data": { ... } }` — always read from `response.data`.

**Pricing:** GET $0.001 · Wallet analytics / smart money / Binance / matching $0.005

---

## Browse Markets & Events

GET `http://localhost:8402/v1/pm/polymarket/events?limit=20`

Common params: `limit`, `offset`, `tag` (e.g. `crypto`, `politics`, `sports`)

Response fields in `data`:

- `events[].title` — market name
- `events[].outcomes` — array of `{ name, price }` (price = implied probability 0–1)
- `events[].volume` — total volume in USD
- `events[].endDate` — resolution date
- `events[].conditionId` — use this for follow-up calls

To search by keyword: `GET /v1/pm/polymarket/markets?search=bitcoin&limit=10`

Response fields in `data`:

- `markets[].question` — market question
- `markets[].conditionId`
- `markets[].outcomes[].price`
- `markets[].volumeNum`

---

## Smart Money on a Market

Find the `conditionId` first (from events/markets above), then:

GET `http://localhost:8402/v1/pm/polymarket/market/{conditionId}/smart-money`

Response fields in `data`:

- `positions[].wallet` — wallet address
- `positions[].side` — YES or NO
- `positions[].size` — position size in USD
- `positions[].pnl` — profit/loss on this position
- `positions[].winRate` — wallet's historical win rate

---

## Leaderboard

GET `http://localhost:8402/v1/pm/polymarket/leaderboard?limit=20`

Response fields in `data`:

- `wallets[].address`
- `wallets[].profit` — total realized profit in USD
- `wallets[].volume`
- `wallets[].winRate`
- `wallets[].marketsTraded`

---

## Wallet Analysis

GET `http://localhost:8402/v1/pm/polymarket/wallet/{walletAddress}`

Response fields in `data`:

- `profit` — total realized profit
- `volume` — total traded volume
- `winRate` — fraction of winning trades (0–1)
- `marketsTraded` — number of distinct markets
- `currentPositions[]` — open positions

For P&L over time: GET `/v1/pm/polymarket/wallet/pnl/{walletAddress}`

- `data.pnlSeries[]` — `{ date, cumulativePnl }`
- `data.totalProfit`, `data.totalLoss`

---

## Compare Polymarket vs Kalshi

GET `http://localhost:8402/v1/pm/matching-markets?limit=10`

Response fields in `data`:

- `pairs[].polymarketTitle`
- `pairs[].kalshiTitle`
- `pairs[].polymarketPrice` — YES price on Polymarket (0–1)
- `pairs[].kalshiPrice` — YES price on Kalshi (0–1)
- `pairs[].spread` — price difference (arbitrage signal)

---

## Example Interactions

**User:** What are the top prediction markets right now?
→ `GET /v1/pm/polymarket/events?limit=20` — summarize top events with titles, outcomes, and current YES/NO prices.

**User:** What's the smart money doing on the 2026 election markets?
→ First `GET /v1/pm/polymarket/markets?search=election&limit=5` to get `conditionId`s, then `GET /v1/pm/polymarket/market/{conditionId}/smart-money` for each. Show top positions, sides, and P&L.

**User:** Who are the top Polymarket whales?
→ `GET /v1/pm/polymarket/leaderboard?limit=10` — table with wallet (shortened), profit, win rate, markets traded.

**User:** Analyze this wallet: 0xabc...
→ `GET /v1/pm/polymarket/wallet/0xabc...` + `GET /v1/pm/polymarket/wallet/pnl/0xabc...` — summarize trading style, win rate, total P&L, current open positions.

**User:** Compare Polymarket vs Kalshi on the Fed rate decision
→ `GET /v1/pm/matching-markets?limit=20` — find the Fed pair, show both prices and the spread.

---

## Full Endpoint Reference

All endpoints are GET. Query params go in the URL.

| Endpoint                                             | Price  | Key params                              |
| ---------------------------------------------------- | ------ | --------------------------------------- |
| `/v1/pm/polymarket/events`                           | $0.001 | `limit`, `offset`, `tag`                |
| `/v1/pm/polymarket/markets`                          | $0.001 | `search`, `limit`, `offset`             |
| `/v1/pm/polymarket/crypto-updown`                    | $0.001 | —                                       |
| `/v1/pm/polymarket/leaderboard`                      | $0.001 | `limit`, `offset`                       |
| `/v1/pm/polymarket/leaderboard/market/{conditionId}` | $0.001 | `limit`                                 |
| `/v1/pm/polymarket/market/{conditionId}/top-holders` | $0.001 | `limit`                                 |
| `/v1/pm/polymarket/cohorts/stats`                    | $0.001 | —                                       |
| `/v1/pm/polymarket/positions`                        | $0.001 | `wallet`, `limit`                       |
| `/v1/pm/polymarket/trades`                           | $0.001 | `wallet`, `limit`, `start_ts`, `end_ts` |
| `/v1/pm/polymarket/orderbooks`                       | $0.001 | `tokenId`, `limit`                      |
| `/v1/pm/polymarket/market-price/{tokenId}`           | $0.001 | `startTs`, `endTs`                      |
| `/v1/pm/polymarket/candlesticks/{conditionId}`       | $0.001 | `period`, `limit`                       |
| `/v1/pm/polymarket/volume-chart/{conditionId}`       | $0.001 | —                                       |
| `/v1/pm/polymarket/wallet/{wallet}`                  | $0.005 | —                                       |
| `/v1/pm/polymarket/wallet/{wallet}/markets`          | $0.005 | `limit`                                 |
| `/v1/pm/polymarket/wallet/{wallet}/similar`          | $0.005 | —                                       |
| `/v1/pm/polymarket/wallet/pnl/{wallet}`              | $0.005 | —                                       |
| `/v1/pm/polymarket/wallet/positions/{wallet}`        | $0.005 | —                                       |
| `/v1/pm/polymarket/wallet/volume-chart/{wallet}`     | $0.005 | —                                       |
| `/v1/pm/polymarket/wallets/profiles`                 | $0.005 | `wallets` (comma-separated)             |
| `/v1/pm/polymarket/wallets/filter`                   | $0.005 | `conditionId`, `side`                   |
| `/v1/pm/polymarket/market/{conditionId}/smart-money` | $0.005 | `limit`                                 |
| `/v1/pm/polymarket/markets/smart-activity`           | $0.005 | `limit`                                 |
| `/v1/pm/kalshi/markets`                              | $0.001 | `search`, `limit`                       |
| `/v1/pm/kalshi/trades`                               | $0.001 | `limit`                                 |
| `/v1/pm/kalshi/orderbooks`                           | $0.001 | `marketId`                              |
| `/v1/pm/dflow/trades`                                | $0.001 | `wallet`, `limit`                       |
| `/v1/pm/dflow/wallet/positions/{wallet}`             | $0.005 | —                                       |
| `/v1/pm/dflow/wallet/pnl/{wallet}`                   | $0.005 | —                                       |
| `/v1/pm/binance/candles/{symbol}`                    | $0.005 | `interval`, `limit`                     |
| `/v1/pm/binance/ticks/{symbol}`                      | $0.005 | `limit`                                 |
| `/v1/pm/matching-markets`                            | $0.005 | `limit`, `offset`                       |
| `/v1/pm/matching-markets/pairs`                      | $0.005 | —                                       |
| `/v1/pm/limitless/orderbooks`                        | $0.001 | `marketId`                              |
| `/v1/pm/opinion/orderbooks`                          | $0.001 | `marketId`                              |
| `/v1/pm/predictfun/orderbooks`                       | $0.001 | `marketId`                              |

---

## Notes

- Payment is automatic via x402 — deducted from the user's BlockRun wallet
- If payment fails, tell the user to fund their wallet at [blockrun.ai](https://blockrun.ai)
- Retry once on 502 — Predexon can occasionally be slow
- Always read from `response.data` — every response is wrapped `{ data: ... }`
- Synthesize data into plain-language analysis — never dump raw JSON
