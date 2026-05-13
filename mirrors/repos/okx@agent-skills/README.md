# agent-skills

A collection of AI agent skills for OKX exchange operations. Each skill is a self-contained Markdown file with YAML frontmatter that tells an AI agent when to activate and how to execute tasks via the [`okx`](https://www.npmjs.com/package/@okx_ai/okx-trade-cli) CLI.

## Skills

| Skill | Description | Auth Required |
|-------|-------------|:-------------:|
| [`okx-cex-auth`](skills/okx-cex-auth/SKILL.md) | OAuth login / API-key setup, plus install/update/remove of the `okx-auth` helper binary. Activated on first run or whenever a command returns 401 / session expired. | Setup |
| [`okx-cex-market`](skills/okx-cex-market/SKILL.md) | Public market data: prices, tickers, order books, candles, funding rates, open interest, instruments, stock tokens, metals/forex, and 70+ technical indicators (RSI, MACD, EMA, Bollinger, KDJ, SuperTrend, AHR999, BTC rainbow…). | No |
| [`okx-cex-trade`](skills/okx-cex-trade/SKILL.md) | Order management: spot, perpetual swap, dated futures, options, event contracts. TP/SL, trailing stop, iceberg, TWAP, conditional/OCO algo orders. | Yes |
| [`okx-cex-portfolio`](skills/okx-cex-portfolio/SKILL.md) | Account operations: balances, positions, P&L, trading fees, account config, fund transfers, position-mode switching. | Yes |
| [`okx-cex-bot`](skills/okx-cex-bot/SKILL.md) | Grid bots (spot / USDT-margined / coin-margined contract) and DCA Martingale bots (Spot DCA / Contract DCA). Create, amend, stop, monitor, AI-recommended parameters. | Yes |
| [`okx-cex-earn`](skills/okx-cex-earn/SKILL.md) | Simple Earn (flexible / fixed-term / lending), Flash Earn, On-chain Earn (staking / DeFi), Dual Investment (DCD / 双币赢), AutoEarn (自动赚币). | Yes |
| [`okx-cex-smartmoney`](skills/okx-cex-smartmoney/SKILL.md) | Smart-money analytics: leaderboard traders, position tracking, trade records, consensus signals, signal history. | Yes |
| [`okx-sentiment-tracker`](skills/okx-sentiment-tracker/SKILL.md) | Crypto news, coin-level sentiment analysis, trending coins, social buzz, market mood. | Yes |
| [`okx-cex-skill-mp`](skills/okx-cex-skill-mp/SKILL.md) | OKX Skills Marketplace: search, browse, install, update, remove skill packs. | Yes |

## Requirements

- [`okx` CLI](https://www.npmjs.com/package/@okx_ai/okx-trade-cli) installed:
  ```bash
  npm install -g @okx_ai/okx-trade-cli
  ```
- For authenticated skills, configure credentials by either:
  - **OAuth** — run the `okx-cex-auth` skill (recommended for end users)
  - **API key** — write `~/.okx/config.toml` directly:
    ```bash
    okx config init
    ```

## Skill Format

Each skill is a Markdown file with a YAML frontmatter header:

```yaml
---
name: skill-name
description: "Trigger description for the AI agent routing system."
license: MIT
metadata:
  author: okx
  version: "1.3.3"
  homepage: "https://www.okx.com"
  agent:
    requires:
      bins: ["okx"]
    install:
      - id: npm
        kind: node
        package: "@okx_ai/okx-trade-cli@1.3.3"
        bins: ["okx"]
        label: "Install okx CLI (npm)"
---
```

The `description` field drives agent routing — it enumerates natural-language phrases and scenarios that should trigger the skill. Skills with a `references/` subdirectory use `{baseDir}` as a runtime-resolved path pointing to the skill's own directory.

> **Description length limit**: Codex CLI enforces a **1024-character maximum** on this field. Target ≤ 900 characters to leave headroom for future trigger additions.

Skills may share helpers via the top-level [`skills/_shared/`](skills/_shared/) directory (e.g. `preflight.md` for credential / profile checks).

## Usage

Skills are loaded by AI coding agents — Claude Code, Cursor, Windsurf, Codex CLI, and any Skills-Plugin-compatible client — to provide contextual instructions for CLI-based OKX operations. The agent reads the skill document at activation time and follows the command examples and operation flows described within.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add or improve skills, and [REVIEWING.md](REVIEWING.md) for review criteria.

## Security

Report security issues per [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
