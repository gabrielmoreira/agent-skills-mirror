---
name: browserwing
description: Browser automation platform with 78 built-in scripts and full CLI. Turn any website into structured data with one command. Use when the user needs to scrape websites, extract data, automate browsers, run built-in scripts (Hacker News, GitHub trending, Bilibili, Zhihu, stock data, etc.), navigate pages, fill forms, take screenshots, or control Chrome programmatically. Triggers include "scrape", "extract data", "browser automation", "web data", "trending", "hot topics", "stock data", "run script", "open website", "fill form", "screenshot", "headless browser".
---

# BrowserWing

Browser automation platform with 78 built-in scripts, CLI for AI agents, and full browser control API. Turn any website into structured JSON with one command.

## Install

```bash
npm install -g browserwing
```

Then start the server:

```bash
browserwing --port 8080
```

Chrome must be installed on the host machine.

### Verify Installation

```bash
browserwing doctor
```

## Quick Start — Run Built-in Scripts

BrowserWing ships with 78 ready-to-use scripts across 10 categories. No configuration needed.

```bash
# Get Hacker News top stories
browserwing run hackernews-top

# Get GitHub trending repos
browserwing run github-trending

# Get Bilibili hot videos
browserwing run bilibili-hot

# Search with parameters
browserwing run jd-search --keyword="mechanical keyboard"

# Output as table or CSV
browserwing run douban-movie-hot --format=table
browserwing run sinafinance-rank --format=csv > stocks.csv
```

### Discover Scripts

```bash
# List all scripts
browserwing ls

# List only built-in scripts
browserwing ls --builtin

# Search by keyword
browserwing ls --search=stock

# Filter by category
browserwing ls --category=finance

# JSON output for programmatic use
browserwing ls --format=json
```

### Built-in Script Categories

| Category | Examples |
|----------|---------|
| Tech | hackernews-top, github-trending, producthunt-hot, devto-top, stackoverflow-hot |
| Finance | sinafinance-rank, eastmoney-hot, xueqiu-hot, binance-gainers, yahoo-finance-quote |
| News | 36kr-hot, toutiao-hot, bbc-news, bloomberg-rss, reuters-search |
| Social | weibo-hot, zhihu-hot, xiaohongshu-hot, reddit-popular, twitter-trending |
| Entertainment | bilibili-hot, douban-movie-hot, douyin-hot, imdb-trending, youtube-trending |
| Shopping | jd-search, taobao-search, amazon-bestsellers, xianyu-hot, smzdm-hot |
| Academic | arxiv-new, google-scholar-search, baidu-scholar-search, cnki-search |
| Jobs | boss-recommend, linkedin-jobs |
| Reading | douban-book-hot, weread-ranking, substack-feed, lesswrong-curated |
| Government | gov-policy, gov-law |

## Direct Browser Control

Control Chrome directly from the CLI — navigate, click, type, extract, screenshot, and more.

### Workflow: Navigate → Snapshot → Interact → Extract

```bash
# 1. Navigate to a page
browserwing exec navigate https://example.com

# 2. Get page structure with element RefIDs
browserwing exec snapshot

# Output shows elements like:
#   @e1 - Search (textbox)
#   @e2 - Login (button)
#   @e3 - Sign Up (link)

# 3. Interact using RefIDs
browserwing exec type @e1 "search query"
browserwing exec press-key Enter
browserwing exec click @e2

# 4. Extract data
browserwing exec extract ".result-item" --fields=text,href --multiple

# 5. Take screenshot
browserwing exec screenshot --output=page.png

# 6. Execute JavaScript
browserwing exec eval 'document.title'
```

### All exec Actions

| Action | Usage | Description |
|--------|-------|-------------|
| navigate | `exec navigate <url>` | Open a URL |
| snapshot | `exec snapshot` | Get accessibility tree with @e refs |
| click | `exec click <@ref>` | Click element |
| type | `exec type <@ref> <text>` | Type into input |
| extract | `exec extract <selector> [--fields=text,href] [--multiple]` | Extract data |
| wait | `exec wait <@ref> [--state=visible] [--timeout=10]` | Wait for element |
| press-key | `exec press-key <Enter\|Tab\|Escape>` | Press key |
| screenshot | `exec screenshot [--output=file.png]` | Take screenshot |
| eval | `exec eval '<js>'` | Run JavaScript |
| fill-form | `exec fill-form --field=name:value [--submit]` | Fill form fields |
| tabs | `exec tabs <list\|new\|switch\|close>` | Manage tabs |
| select | `exec select <@ref> <value>` | Select dropdown |
| hover | `exec hover <@ref>` | Hover element |
| scroll | `exec scroll` | Scroll to bottom |
| back/forward | `exec back`, `exec forward` | Navigation history |
| page-info | `exec page-info` | Get URL and title |

## Admin Operations

Manage LLM configs, browser instances, cookies, scripts, and AI exploration — all from the CLI.

```bash
# LLM Configuration
browserwing config list
browserwing config add --name=gpt --provider=openai --api-key=sk-xxx --model=gpt-4o
browserwing config test gpt

# Browser Instances
browserwing browser list
browserwing browser start
browserwing browser stop

# Cookie Management
browserwing cookie list
browserwing cookie save
browserwing cookie import cookies.json

# Script Management
browserwing script get <id>
browserwing script create my-script.json
browserwing script delete <id>
browserwing script export --output=SKILL.md
browserwing script summary

# AI Exploration (auto-generate scripts)
browserwing explore start --url=https://example.com --task="find top products"
browserwing explore script <session-id>
browserwing explore save <session-id>

# System
browserwing health
browserwing doctor
browserwing mcp status
```

## Output Formats

All commands support `--format=json|table|csv`:

```bash
browserwing run zhihu-hot --format=json    # default, for piping
browserwing run zhihu-hot --format=table   # human-readable
browserwing run zhihu-hot --format=csv     # spreadsheet-friendly
```

## Agent Integration Pattern

Typical AI agent workflow:

```bash
# Step 1: Discover available scripts
browserwing ls --format=json

# Step 2: Find relevant script
browserwing ls --search=stock --format=json

# Step 3: Execute and get structured data
browserwing run sinafinance-rank

# Step 4: Pipe to other tools
browserwing run hackernews-top | jq '.[0:5]'
```

For direct browser control:

```bash
# Step 1: Open page
browserwing exec navigate https://example.com

# Step 2: Understand page structure
browserwing exec snapshot

# Step 3: Interact
browserwing exec click @e3
browserwing exec type @e5 "query"

# Step 4: Extract results
browserwing exec extract ".item" --fields=text,href --multiple --format=json
```

## CLI Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Cannot connect to server |
| 3 | Script not found |
| 4 | Script execution failed |
| 64 | Bad arguments |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BROWSERWING_URL` | Server URL (default: auto-detect from config.toml) |
| `BROWSERWING_JSON_ERRORS` | Set to `1` for JSON error output on stderr |

## Links

- GitHub: https://github.com/browserwing/browserwing
- npm: https://www.npmjs.com/package/browserwing
- Gitee: https://gitee.com/browserwing/browserwing
