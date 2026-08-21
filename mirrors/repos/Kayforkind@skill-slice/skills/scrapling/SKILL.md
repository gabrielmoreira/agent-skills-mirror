---
name: scrapling
description: "Fetches and extracts pages with Scrapling HTTP Fetcher, DynamicFetcher for JS-rendered HTML, and Spider crawling via CLI or Python. Use when static or JS pages must be extracted after a generic web extract fails, or when crawling URLs the user is allowed to collect. Not for CAPTCHA solving, credential stuffing, or ignoring robots and site terms; never treat stealth fetchers as a license for unauthorized access."
version: 1.0.1
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Web Scraping, Browser, Cloudflare, Stealth, Crawling, Spider]
    related_skills: [duckduckgo-search, domain-intel]
    homepage: https://github.com/D4Vinci/Scrapling
prerequisites:
  commands: [scrapling, python]
---

# Scrapling

[Scrapling](https://github.com/D4Vinci/Scrapling) is a web scraping framework with anti-bot bypass, stealth browser automation, and a spider framework. It provides three fetching strategies (HTTP, dynamic JS, stealth/Cloudflare) and a full CLI.

**This skill is for educational and research purposes only.** Users must comply with local/international data scraping laws and respect website Terms of Service.

## When to Use

- Scraping static HTML pages (faster than browser tools)
- Scraping JS-rendered pages that need a real browser
- Bypassing Cloudflare Turnstile or bot detection
- Crawling multiple pages with a spider
- When the built-in `web_extract` tool does not return the data you need

## Prerequisites

- **Python 3.10+** — verify with `python --version`
- **pip** — verify with `pip --version`
- On Windows (PowerShell), use `python -m pip` if `pip` is not on PATH

### Installation

Full install (HTTP + browser + stealth):

```powershell
pip install "scrapling[all]"
scrapling install
```

Minimal install (HTTP only, no browser):

```powershell
pip install scrapling
```

Browser automation only:

```powershell
pip install "scrapling[fetchers]"
scrapling install
```

> **HARD RULE:** You MUST run `scrapling install` after pip install. Without it, `DynamicFetcher` and `StealthyFetcher` will fail with a browser-not-found error.

## Procedure

### Quick Reference

| Approach | Class | Use When |
|----------|-------|----------|
| HTTP | `Fetcher` / `FetcherSession` | Static pages, APIs, fast bulk requests |
| Dynamic | `DynamicFetcher` / `DynamicSession` | JS-rendered content, SPAs |
| Stealth | `StealthyFetcher` / `StealthySession` | Cloudflare, anti-bot protected sites |
| Spider | `Spider` | Multi-page crawling with link following |

---

### 1. CLI Usage

#### Extract Static Page

```powershell
scrapling extract get 'https://example.com' output.md
```

With CSS selector and browser impersonation:

```powershell
scrapling extract get 'https://example.com' output.md --css-selector '.content' --impersonate 'chrome'
```

#### Extract JS-Rendered Page

```powershell
scrapling extract fetch 'https://example.com' output.md --css-selector '.dynamic-content' --disable-resources --network-idle
```

#### Extract Cloudflare-Protected Page

```powershell
scrapling extract stealthy-fetch 'https://protected-site.com' output.html --solve-cloudflare --block-webrtc --hide-canvas
```

#### POST Request

```powershell
scrapling extract post 'https://example.com/api' output.json --json '{"query": "search term"}'
```

#### Output Formats

The output format is determined by the file extension:

| Extension | Format |
|-----------|--------|
| `.html` | Raw HTML |
| `.md` | Converted to Markdown |
| `.txt` | Plain text |
| `.json` / `.jsonl` | JSON |

---

### 2. Python: HTTP Scraping

#### Single Request

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
for q in quotes:
    print(q)
```

#### Session (Persistent Cookies)

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://example.com/', stealthy_headers=True)
    links = page.css('a::attr(href)').getall()
    for link in links[:5]:
        sub = session.get(link)
        print(sub.css('h1::text').get())
```

#### POST / PUT / DELETE

```python
page = Fetcher.post('https://api.example.com/data', json={"key": "value"})
page = Fetcher.put('https://api.example.com/item/1', data={"name": "updated"})
page = Fetcher.delete('https://api.example.com/item/1')
```

#### With Proxy

```python
page = Fetcher.get('https://example.com', proxy='http://user:pass@proxy:8080')
```

---

### 3. Python: Dynamic Pages (JS-Rendered)

For pages that require JavaScript execution (SPAs, lazy-loaded content):

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://example.com', headless=True)
data = page.css('.js-loaded-content::text').getall()
```

#### Wait for Specific Element

```python
page = DynamicFetcher.fetch(
    'https://example.com',
    wait_selector=('.results', 'visible'),
    network_idle=True,
)
```

#### Disable Resources for Speed

Blocks fonts, images, media, stylesheets (~25% faster):

```python
from scrapling.fetchers import DynamicSession

with DynamicSession(headless=True, disable_resources=True, network_idle=True) as session:
    page = session.fetch('https://example.com')
    items = page.css('.item::text').getall()
```

#### Custom Page Automation

```python
from playwright.sync_api import Page
from scrapling.fetchers import DynamicFetcher

def scroll_and_click(page: Page):
    page.mouse.wheel(0, 3000)
    page.wait_for_timeout(1000)
    page.click('button.load-more')
    page.wait_for_selector('.extra-results')

page = DynamicFetcher.fetch('https://example.com', page_action=scroll_and_click)
results = page.css('.extra-results .item::text').getall()
```

---

### 4. Python: Stealth Mode (Anti-Bot Bypass)

For Cloudflare-protected or heavily fingerprinted sites:

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True,
    block_webrtc=True,
    hide_canvas=True,
)
content = page.css('.protected-content::text').getall()
```

#### Stealth Session

```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page1 = session.fetch('https://protected-site.com/page1')
    page2 = session.fetch('https://protected-site.com/page2')
```

---

### 5. Element Selection

All fetchers return a `Selector` object with these methods:

#### CSS Selectors

```python
page.css('h1::text').get()              # First h1 text
page.css('a::attr(href)').getall()      # All link hrefs
page.css('.quote .text::text').getall() # Nested selection
```

#### XPath

```python
page.xpath('//div[@class="content"]/text()').getall()
page.xpath('//a/@href').getall()
```

#### Find Methods

```python
page.find_all('div', class_='quote')       # By tag + attribute
page.find_by_text('Read more', tag='a')    # By text content
page.find_by_regex(r'\$\d+\.\d{2}')        # By regex pattern
```

#### Similar Elements

Find elements with similar structure (useful for product listings):

```python
first_product = page.css('.product')[0]
all_similar = first_product.find_similar()
```

#### Navigation

```python
el = page.css('.target')[0]
el.parent                # Parent element
el.children              # Child elements
el.next_sibling          # Next sibling
el.prev_sibling          # Previous sibling
```

---

### 6. Python: Spider Framework

For multi-page crawling with link following:

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10
    download_delay = 1

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
                "tags": quote.css('.tag::text').getall(),
            }

        next_page = response.css('.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

result = QuotesSpider().start()
print(f"Scraped {len(result.items)} quotes")
result.items.to_json("quotes.json")
```

#### Multi-Session Spider

Route requests to different fetcher types:

```python
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class SmartSpider(Spider):
    name = "smart"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)
```

#### Pause/Resume Crawling

```python
spider = QuotesSpider(crawldir="./crawl_checkpoint")
spider.start()  # Ctrl+C to pause, re-run to resume from checkpoint
```

## Pitfalls

- **Browser install required (HARD RULE):** Run `scrapling install` after pip install — without it, `DynamicFetcher` and `StealthyFetcher` will fail with a browser-not-found error.
- **Timeout units differ (HARD RULE):** `DynamicFetcher` / `StealthyFetcher` timeout is in **milliseconds** (default 30000). `Fetcher` timeout is in **seconds**. Mixing these up causes premature timeouts or hangs.
- **Cloudflare bypass latency:** `solve_cloudflare=True` adds 5–15 seconds to fetch time — only enable when needed.
- **Resource usage:** `StealthyFetcher` runs a real browser — limit concurrent usage to avoid memory exhaustion.
- **Legal compliance (HARD RULE):** Always check `robots.txt` and website Terms of Service before scraping. This library is for educational and research purposes only.
- **Python version (HARD RULE):** Requires Python 3.10+. Older versions will fail at import.
- **Windows PowerShell quoting:** Use single quotes for JSON payloads in CLI commands. If single quotes cause issues in PowerShell, escape with backticks or use `--json` with a here-string.
- **Proxy format:** Proxy string must include scheme: `http://user:pass@proxy:8080`. Omitting the scheme causes silent failures.

## Verification

### Verify Installation

```powershell
python -c "import scrapling; print(scrapling.__version__)"
```

Expected: a version string (e.g., `0.3.x` or similar).

### Verify Browser Binaries

```powershell
scrapling install
```

Re-running is safe; it will report if browsers are already installed.

### Verify CLI Extract

```powershell
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
```

Then check the output file exists:

```powershell
Test-Path quotes.md
```

Expected: `True`. Open `quotes.md` to confirm scraped content is present.

### Verify Python Fetcher

```powershell
python -c "from scrapling.fetchers import Fetcher; p = Fetcher.get('https://quotes.toscrape.com/'); print(len(p.css('.quote .text::text').getall()))"
```

Expected: `10` (ten quotes on the first page).

### Verify DynamicFetcher

```powershell
python -c "from scrapling.fetchers import DynamicFetcher; p = DynamicFetcher.fetch('https://quotes.toscrape.com/'); print(len(p.css('.quote')))"
```

Expected: `10`. If this fails with a browser error, re-run `scrapling install`.

## Related Skills

- **duckduckgo-search** — search engine scraping without anti-bot issues
- **domain-intel** — domain reconnaissance and DNS lookup before scraping
