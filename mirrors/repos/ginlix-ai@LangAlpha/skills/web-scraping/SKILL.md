---
name: web-scraping
description: "Web scraping with Scrapling: MCP tool wrappers for quick fetching, plus direct Python API for advanced scraping with selectors, sessions, and spiders"
license: MIT
---

# Web Scraping with Scrapling

## Overview

Two ways to scrape in the sandbox:

1. **MCP tool wrappers** (recommended for simple fetches) — call `get()`, `fetch()`, `stealthy_fetch()` directly. Synchronous, returns dicts.
2. **Direct Python API** (for advanced use) — import Scrapling classes for selectors, sessions, spiders. Async, returns Page objects.

## MCP Tool Wrappers (via Python)

Auto-registered as top-level functions in the sandbox. No imports needed. **Synchronous** — no `await`.

Quick fetches can run inline via `ExecuteCode`. For spiders, multi-URL crawls, or anything you'll iterate on, write the scraper to `work/<task_name>/scraper.py` and run it via `Bash` — edit-and-rerun beats resubmitting code.

### Basic Usage

```python
# Fast HTTP fetch → markdown
result = get(url="https://example.com", extraction_type="markdown")
print(result["status"])      # 200
print(result["url"])         # "https://example.com"
print(result["content"][0])  # markdown string (first element of list)

# Browser fetch for JS-rendered pages
result = fetch(url="https://spa-site.com", extraction_type="markdown", network_idle=True)

# Anti-bot bypass (Cloudflare, etc.)
result = stealthy_fetch(url="https://protected-site.com", extraction_type="markdown", solve_cloudflare=True)
```

### Response Format

All MCP tools return a **dict** (not a Page object):

```python
{
    "status": 200,
    "url": "https://example.com",
    "content": ["<markdown or html text>", ""]  # list, use [0] for content
}
```

- No `.css()`, `.xpath()`, `.find_all()` methods — use BeautifulSoup to parse if needed
- No `.body`, `.headers`, `.cookies` — only `status`, `url`, `content`
- `content` is always a **list**; the actual text is `content[0]`

### CSS Selector with MCP Tools

The `css_selector` param returns **raw HTML** of matched elements, not parsed text:

```python
# Returns HTML of matched elements — must parse manually
result = get(url="https://example.com", css_selector="h1", extraction_type="HTML")
html_fragment = result["content"][0]

# Parse with BeautifulSoup if you need text/attributes
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_fragment, "html.parser")
titles = [h1.get_text() for h1 in soup.find_all("h1")]
```

### Available Tools

| Function | Use case | Key params |
|----------|----------|------------|
| `get(url, ...)` | Static pages, APIs | `impersonate`, `stealthy_headers`, `timeout` (seconds) |
| `fetch(url, ...)` | JS-rendered SPAs | `headless`, `network_idle`, `wait_selector`, `disable_resources`, `timeout` (ms) |
| `stealthy_fetch(url, ...)` | Anti-bot sites | All `fetch` params + `solve_cloudflare`, `hide_canvas` |
| `bulk_get(urls, ...)` | Parallel HTTP | `urls: list[str]`, same params as `get` |
| `bulk_fetch(urls, ...)` | Parallel browser | `urls: list[str]`, same params as `fetch` |
| `bulk_stealthy_fetch(urls, ...)` | Parallel stealth | `urls: list[str]`, same params as `stealthy_fetch` |

### Common Parameters

| Param | Default | Notes |
|-------|---------|-------|
| `extraction_type` | `"markdown"` | `"markdown"`, `"HTML"`, or `"text"` |
| `css_selector` | `None` | Returns raw HTML of matched elements |
| `main_content_only` | `True` | Extract `<body>` only |
| `proxy` | `None` | Proxy URL |

---

## Direct Python API (Advanced)

For selectors, sessions, spiders, or when you need the full Page object. **Requires imports. Async.**

### Fetcher (Fast HTTP — Tier 1)

```python
from scrapling.fetchers import AsyncFetcher

page = await AsyncFetcher.get("https://example.com", stealthy_headers=True)
print(page.status)       # 200
print(page.body)         # Raw bytes
print(page.headers)      # Response headers

# CSS selectors (Scrapy-style pseudo-elements)
titles = page.css("h1::text").getall()
links = page.css("a::attr(href)").getall()

# XPath
items = page.xpath("//div[@class='item']/text()").getall()

# BeautifulSoup-style
divs = page.find_all("div", class_="content")
```

### DynamicFetcher (Browser — Tier 2)

```python
from scrapling.fetchers import DynamicFetcher

page = await DynamicFetcher.async_fetch(
    "https://spa-website.com",
    headless=True,
    network_idle=True,
    disable_resources=True,
    timeout=30000,
    wait_selector=".data-table",
)
rows = page.css("table.data-table tr")
for row in rows:
    cells = row.css("td::text").getall()
```

### StealthyFetcher (Anti-Bot — Tier 3)

```python
from scrapling.fetchers import StealthyFetcher

page = await StealthyFetcher.async_fetch(
    "https://protected-site.com",
    headless=True,
    solve_cloudflare=True,
    network_idle=True,
)
```

### Sessions (Persistent Connections)

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate="chrome") as session:
    login_page = session.post("https://site.com/login", data={...})
    dashboard = session.get("https://site.com/dashboard")
    data = dashboard.css(".user-data::text").getall()
```

### Spider (Multi-Page Crawl)

```python
from scrapling.spiders import Spider, Request, Response

class PriceScraper(Spider):
    name = "prices"
    start_urls = ["https://example.com/products"]
    concurrent_requests = 5

    async def parse(self, response: Response):
        for product in response.css(".product"):
            yield {
                "name": product.css(".name::text").get(),
                "price": product.css(".price::text").get(),
            }
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield Request(next_page)

spider = PriceScraper()
result = spider.start()
result.items.to_json("results/prices.json")
```

## Converting HTML to Markdown

```python
import html2text

converter = html2text.HTML2Text()
converter.body_width = 0  # No line wrapping
markdown = converter.handle(html_string)
```

## When to Use Which

| Need | Use |
|------|-----|
| Quick page content as markdown | MCP `get()` or `fetch()` |
| Extract specific elements (CSS/XPath) | Direct Python API with selectors |
| Login + scrape authenticated pages | Direct Python API with sessions |
| Crawl many pages with pagination | Direct Python API with Spider |
| Bypass Cloudflare | MCP `stealthy_fetch()` or direct `StealthyFetcher` |
| Save results to file | Direct Python API (spider `.to_json()`) |
