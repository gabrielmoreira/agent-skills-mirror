# Reference — End-to-End Web Scraping

Deep implementation reference for every pipeline phase in [SKILL.md](SKILL.md).
All code targets Windows + PowerShell + Python 3.11+ unless noted. No evasion techniques
appear anywhere in this file by design; a block is an answer, not a challenge.

---

## 1. HTTP client patterns

### 1.1 httpx client with retries, backoff, and Retry-After

```python
import random
import time

import httpx

UA = "research-agent/1.0 (+mailto:user@example.com; personal research; contact for opt-out)"

DEFAULT_HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def make_client(timeout: float = 20.0) -> httpx.Client:
    return httpx.Client(
        headers=DEFAULT_HEADERS,
        timeout=httpx.Timeout(timeout, connect=10.0),
        follow_redirects=True,
        limits=httpx.Limits(max_connections=4, max_keepalive_connections=2),
    )


def fetch(client: httpx.Client, url: str, max_tries: int = 4) -> httpx.Response:
    """GET with exponential backoff + jitter. Honors Retry-After. Raises on final failure."""
    delay = 2.0
    for attempt in range(1, max_tries + 1):
        try:
            resp = client.get(url)
        except (httpx.TransportError, httpx.TimeoutException):
            if attempt == max_tries:
                raise
            time.sleep(delay + random.uniform(0, 0.5))
            delay *= 2
            continue

        if resp.status_code in RETRYABLE_STATUS:
            if attempt == max_tries:
                resp.raise_for_status()
            retry_after = resp.headers.get("Retry-After")
            wait = delay
            if retry_after:
                try:
                    wait = max(float(retry_after), delay)
                except ValueError:
                    pass  # HTTP-date form; exponential delay is a safe floor
            time.sleep(wait + random.uniform(0, 0.5))
            delay *= 2
            continue

        return resp  # includes 3xx-followed and 4xx non-retryable; caller decides

    raise RuntimeError("unreachable")
```

Rules baked in:
- **429/503 are obeyed, not fought.** `Retry-After` wins over the local schedule.
- 401/403/404 are returned to the caller — they are routing decisions (skip, stop,
  escalate; see §11), never retried blindly.
- Connection pool capped at 4 — the politeness ceiling lives in the client, not in hope.

### 1.2 Per-host rate limiter + circuit breaker

```python
import time
from collections import defaultdict
from urllib.parse import urlsplit


class HostPoliteness:
    def __init__(self, delay: float = 1.5, jitter: float = 0.5, trip_after: int = 5):
        self.delay, self.jitter, self.trip_after = delay, jitter, trip_after
        self.last_hit: dict[str, float] = defaultdict(float)
        self.errors: dict[str, int] = defaultdict(int)
        self.tripped_until: dict[str, float] = defaultdict(float)

    def wait(self, url: str) -> None:
        import random
        host = urlsplit(url).netloc
        if time.monotonic() < self.tripped_until[host]:
            raise RuntimeError(f"circuit open for {host}; halt run and report")
        gap = self.delay + random.uniform(0, self.jitter)
        sleep_for = self.last_hit[host] + gap - time.monotonic()
        if sleep_for > 0:
            time.sleep(sleep_for)
        self.last_hit[host] = time.monotonic()

    def record(self, url: str, ok: bool) -> None:
        host = urlsplit(url).netloc
        if ok:
            self.errors[host] = 0
        else:
            self.errors[host] += 1
            if self.errors[host] >= self.trip_after:
                self.tripped_until[host] = time.monotonic() + 900  # 15 min
```

Five consecutive failures on a host trips the breaker for 15 minutes and the run halts with
a report. Grinding against a failing or blocking site is both rude and useless.

### 1.3 curl.exe patterns (Windows)

In **Windows PowerShell 5.1**, `curl` is an alias for `Invoke-WebRequest` — always invoke
`curl.exe` explicitly. In PowerShell 7+ the alias is gone but `curl.exe` still never hurts.

```powershell
# Headers only — cheap recon (server, caching, redirects)
curl.exe -sSI "https://example.com/"

# Full fetch with honest bot UA, follow redirects, save body
curl.exe -sS -L `
  -A "research-agent/1.0 (+mailto:user@example.com; personal research)" `
  -H "Accept: text/html" `
  -o page.html `
  --max-time 30 `
  "https://example.com/articles"

# Conditional GET with a stored ETag (exits with 304 body-less when unchanged)
curl.exe -sS -H "If-None-Match: `"abc123`"" -o page.html -w "%{http_code}" "https://example.com/"

# Rate/redirect diagnostics
curl.exe -sS -o NUL -w "status=%{http_code} time=%{time_total}s redirects=%{num_redirects} final=%{url_effective}`n" "https://example.com/"
```

Use curl.exe for recon and one-off fetches; use httpx once a loop exists (connection reuse,
typed responses, easier retry logic).

---

## 2. HTML parsing — library tradeoffs

| | selectolax | BeautifulSoup4 | lxml |
|---|---|---|---|
| Engine | Lexbor (C) | pluggable (html.parser / lxml) | libxml2 (C) |
| Speed | fastest (~10–50× bs4) | slowest | fast |
| Malformed-HTML tolerance | good | best (most lenient) | good with `html` parser |
| Selectors | CSS only | CSS + find API | CSS + **XPath** |
| Text extraction | `node.text(deep=True)` | `.get_text(" ", strip=True)` | `.text_content()` |
| Best for | volume parsing, crawls | messy one-off pages, exploration | XPath needs, XML/sitemaps |

Defaults: **selectolax** for anything run in a loop; **BeautifulSoup(html, "lxml")** when
exploring an unfamiliar messy page interactively; **lxml** when a pattern genuinely needs
XPath (`following-sibling`, text anchors) or when parsing XML (sitemaps, feeds).

```python
# selectolax essentials
from selectolax.parser import HTMLParser

tree = HTMLParser(html)
for card in tree.css("main article.post"):
    title_node = card.css_first("h2 a")
    yield {
        "title": title_node.text(strip=True) if title_node else None,
        "url": title_node.attributes.get("href") if title_node else None,
    }
```

```python
# lxml XPath — text-anchor pattern bs4/selectolax can't do
from lxml import html as lhtml

doc = lhtml.fromstring(page_bytes)
# value cell that follows a label cell
vals = doc.xpath('//th[normalize-space()="ISBN"]/following-sibling::td[1]/text()')
```

Always parse from **bytes** (let the parser sniff `<meta charset>`) or decode via
`resp.text` (httpx honors the Content-Type charset). Never `bytes.decode("utf-8")` blind.

---

## 3. Structured islands: JSON-LD, microdata, OpenGraph

Check these BEFORE writing CSS selectors — they are publisher-maintained and survive redesigns.

```python
import json
from selectolax.parser import HTMLParser


def extract_jsonld(html: str) -> list[dict]:
    """All JSON-LD entities, with @graph flattened. Malformed blocks skipped, not fatal."""
    out: list[dict] = []
    for node in HTMLParser(html).css('script[type="application/ld+json"]'):
        try:
            data = json.loads(node.text())
        except (json.JSONDecodeError, TypeError):
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict):
                out.extend(g for g in item.get("@graph", [item]) if isinstance(g, dict))
    return out


def first_of_type(entities: list[dict], *types: str) -> dict | None:
    for e in entities:
        t = e.get("@type", "")
        tset = set(t) if isinstance(t, list) else {t}
        if tset & set(types):
            return e
    return None

# Usage: article = first_of_type(extract_jsonld(html), "Article", "NewsArticle", "BlogPosting")
# Common types worth checking: Product (offers.price), Article, Event, Recipe,
# BreadcrumbList, Organization, JobPosting.
```

```python
def extract_meta(html: str) -> dict:
    """OpenGraph + Twitter + standard meta in one pass. Fallback layer under JSON-LD."""
    tree = HTMLParser(html)
    meta: dict[str, str] = {}
    for m in tree.css("meta"):
        a = m.attributes
        key = a.get("property") or a.get("name")
        if key and a.get("content"):
            meta[key] = a["content"]
    title = tree.css_first("title")
    return {
        "title": meta.get("og:title") or (title.text(strip=True) if title else None),
        "description": meta.get("og:description") or meta.get("description"),
        "canonical_url": meta.get("og:url"),
        "image": meta.get("og:image"),
        "published": meta.get("article:published_time"),
        "site_name": meta.get("og:site_name"),
    }
```

Microdata (`itemscope`/`itemprop`) is rarer; when present, `extruct` (pip) parses all three
formats at once — worth the dependency only if a target actually uses microdata.

Precedence when the same field exists in multiple places:
**JSON-LD > microdata > OpenGraph > visible DOM.** Record which layer supplied each field
if the project needs auditability.

---

## 4. Pagination patterns

Identify the model during recon (Phase B); each has a distinct loop shape.

### 4.1 Page parameter (`?page=2`, `/page/2/`)
```python
def paginate_pages(client, base: str, politeness, max_pages: int = 500):
    empty_streak = 0
    for page in range(1, max_pages + 1):
        politeness.wait(base)
        resp = fetch(client, f"{base}?page={page}")
        items = parse_items(resp.text)
        if not items:
            empty_streak += 1
            if empty_streak >= 2:   # two empty pages = end (some sites gap)
                break
            continue
        empty_streak = 0
        yield from items
```
End conditions to detect (in priority order): explicit total/last-page number in the DOM,
empty result page, repeated content (page N == page N-1 → some sites clamp instead of 404).

### 4.2 rel=next / next-link
```python
from urllib.parse import urljoin

def paginate_next_link(client, start: str, politeness, limit: int = 1000):
    url, seen = start, set()
    while url and url not in seen and len(seen) < limit:
        seen.add(url)
        politeness.wait(url)
        resp = fetch(client, url)
        yield from parse_items(resp.text)
        tree = HTMLParser(resp.text)
        nxt = (tree.css_first('link[rel="next"]')
               or tree.css_first('a[rel="next"]')
               or tree.css_first('nav.pagination a.next, .pagination a[aria-label*="Next" i]'))
        url = urljoin(url, nxt.attributes.get("href")) if nxt and nxt.attributes.get("href") else None
```
The `seen` set guards against next-link loops (real sites have them).

### 4.3 Cursor / token APIs (found during recon in the network tab)
```python
def paginate_cursor(client, endpoint: str, politeness):
    cursor = None
    while True:
        politeness.wait(endpoint)
        params = {"limit": 50} | ({"cursor": cursor} if cursor else {})
        data = fetch(client, httpx.URL(endpoint, params=params)).json()
        yield from data["items"]
        cursor = data.get("next_cursor")
        if not cursor:
            break
```
When a JS site's own frontend calls a public JSON endpoint, calling that endpoint the same
way the page does is normal use of a public interface — keep the honest UA, keep the rate
limits, and do not attach auth you weren't given.

### 4.4 Infinite scroll (browser tier only)
See §6.3. First choice is still to find the XHR endpoint feeding the scroll and use §4.3.

---

## 5. robots.txt and sitemaps

### 5.1 robots.txt — fetch honestly, parse with stdlib

```python
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser


def load_robots(client: httpx.Client, any_site_url: str) -> RobotFileParser:
    parts = urlsplit(any_site_url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    rp = RobotFileParser()
    resp = client.get(robots_url)          # our UA, not urllib's default
    if resp.status_code >= 400:
        rp.parse([])                        # absent robots = no restrictions stated
    else:
        rp.parse(resp.text.splitlines())
    rp.set_url(robots_url)
    return rp


rp = load_robots(client, "https://example.com/whatever")
assert rp.can_fetch(UA, "https://example.com/articles/1")   # gate EVERY frontier URL
crawl_delay = rp.crawl_delay(UA) or rp.crawl_delay("*")     # overrides politeness downward
sitemaps = rp.site_maps() or []
```

Wire `can_fetch` into the frontier so disallowed URLs are skipped **in code**, and log each
skip. A human decision at Phase A plus a code gate at Phase D is the standard.

### 5.2 Sitemap parsing (index-aware, lastmod-aware)

```python
import gzip
import xml.etree.ElementTree as ET

SM = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def iter_sitemap(client, url: str, politeness, _depth: int = 0):
    """Yield (loc, lastmod) from a sitemap or sitemap index, recursively."""
    if _depth > 3:
        return
    politeness.wait(url)
    resp = fetch(client, url)
    body = resp.content
    if url.endswith(".gz") or body[:2] == b"\x1f\x8b":
        body = gzip.decompress(body)
    root = ET.fromstring(body)
    if root.tag == f"{SM}sitemapindex":
        for sm in root.findall(f"{SM}sitemap/{SM}loc"):
            yield from iter_sitemap(client, sm.text.strip(), politeness, _depth + 1)
    else:
        for u in root.findall(f"{SM}url"):
            loc = u.findtext(f"{SM}loc", "").strip()
            lastmod = u.findtext(f"{SM}lastmod")
            if loc:
                yield loc, lastmod
```

`lastmod` + your stored `fetched_at` = free incremental crawling: skip URLs whose lastmod
predates the last successful fetch. Trust it loosely (some sites set it wrong) — pair with
conditional GETs (§7) as the ground truth.

---

## 6. Playwright extraction for JS-rendered sites

Normal browser automation only: real Chrome, real rendering, honest identity. No stealth
plugins, no fingerprint patching, no CAPTCHA hand-offs. If the site challenges the browser,
that's a stop-and-escalate (§11).

### 6.1 Launch discipline (this machine)

- **Dedicated scraping profile:** `launch_persistent_context` with a scraping-only
  `user_data_dir` (e.g. `~\ScrapeProfiles\public-default`). Never the daily
  Chrome profile; the browser-connection skill owns profile/CDP conventions here — consult
  it before attaching to any existing browser (CDP 9222 hub is for user-consented,
  user-owned session work only, not bulk scraping).
- **Real Chrome channel** (`channel="chrome"`) — preferred over bundled Chromium per user policy.
- Headed for development/debugging; headless is fine for public pages once stable.

```python
from playwright.sync_api import sync_playwright

PROFILE = r"~\ScrapeProfiles\public-default"

def render_and_extract(url: str) -> list[dict]:
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE, channel="chrome", headless=True,
        )
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_selector("main [data-testid='result-card'], main article", timeout=15_000)
        items = page.eval_on_selector_all(
            "main article",
            """els => els.map(e => ({
                 title: e.querySelector('h2')?.innerText?.trim() ?? null,
                 url:   e.querySelector('a')?.href ?? null,
               }))""",
        )
        html = page.content()          # archive the rendered DOM as the fixture
        ctx.close()
    return items
```

### 6.2 Find the feed, then leave the browser

While the page loads, capture its own API calls; if a clean JSON endpoint appears, all
future runs use §4.3 over HTTP instead of rendering:

```python
captured = []
page.on("response", lambda r: captured.append((r.url, r.status))
        if "application/json" in (r.headers.get("content-type") or "") else None)
page.goto(url, wait_until="networkidle")
# inspect `captured`; promote the real data endpoint into the recon notes
```

### 6.3 Infinite scroll (public listing pages)

```python
prev_count = -1
for _ in range(30):                                  # hard cap, always
    page.mouse.wheel(0, 4_000)
    page.wait_for_timeout(900)                        # give the XHR time to land
    count = page.locator("[data-testid='result-card']").count()
    if count == prev_count:
        break                                         # no growth = exhausted
    prev_count = count
```

Politeness applies to browsers too: one context, sequential pages, same per-host delays.
A browser is a heavier guest than httpx, not an exemption.

---

## 7. Rate limiting, caching, ETag / If-Modified-Since

Conditional GETs make recurring crawls nearly free for the site and fast for you.

```python
import json
import pathlib

CACHE = pathlib.Path("state/http_cache.json")


def load_cache() -> dict:
    return json.loads(CACHE.read_text("utf-8")) if CACHE.exists() else {}


def conditional_fetch(client, url: str, cache: dict) -> tuple[str | None, bool]:
    """Returns (body, changed). body None + changed False on 304 with no stored body."""
    entry = cache.get(url, {})
    headers = {}
    if entry.get("etag"):
        headers["If-None-Match"] = entry["etag"]
    if entry.get("last_modified"):
        headers["If-Modified-Since"] = entry["last_modified"]
    resp = client.get(url, headers=headers)
    if resp.status_code == 304:
        return entry.get("body"), False
    resp.raise_for_status()
    cache[url] = {
        "etag": resp.headers.get("ETag"),
        "last_modified": resp.headers.get("Last-Modified"),
        "body": resp.text,
    }
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache), "utf-8")
    return resp.text, True
```

For large bodies, store the body in `raw/` (see §8) and keep only validators + the content
hash in the cache file. Respect `Cache-Control: max-age` when present: within the window,
don't even send the conditional request.

---

## 8. Storage layouts

```
data/<project>/
├── recon.md                      # Phase B notes: structure, pagination, selectors, counts
├── raw/                          # exact response bytes — the audit trail & repair fixtures
│   └── 2026-07-15/
│       ├── 1f3a9c0d2b7e4a51.html          # first 16 hex of content sha256
│       └── 1f3a9c0d2b7e4a51.meta.json     # url, fetched_at, status, headers subset
├── records/
│   ├── records.jsonl             # validated records (record-schema.json shape)
│   └── rejects.jsonl             # failed validation, with the error attached
├── state/
│   ├── frontier.sqlite           # crawl state: resume, dedupe, change detection
│   └── http_cache.json           # ETag / Last-Modified validators
└── logs/
    └── run-2026-07-15-a.log      # scope note, politeness audit, gate results
```

Principles:
- **Raw is append-only and never rewritten** — it's what lets you re-parse after an
  extractor fix without re-hitting the site, and it's the provenance ground truth.
- Content-hash filenames dedupe identical bodies for free.
- JSONL over JSON-array: appendable, streamable, crash-safe (a truncated last line is
  detectable and droppable).
- SQLite when records need querying/joining; export JSONL → SQLite rather than making
  SQLite the write path of the crawl loop.
- Write files as UTF-8 explicitly (`open(p, "w", encoding="utf-8")`) — Windows default
  cp1252 will corrupt non-ASCII content silently.

Frontier schema:

```sql
CREATE TABLE IF NOT EXISTS frontier (
  url            TEXT PRIMARY KEY,
  status         TEXT NOT NULL DEFAULT 'pending',  -- pending|done|failed|skipped_robots
  http_status    INTEGER,
  content_sha256 TEXT,
  fetched_at     TEXT,           -- ISO-8601 UTC
  tries          INTEGER NOT NULL DEFAULT 0,
  error          TEXT
);
CREATE INDEX IF NOT EXISTS ix_frontier_status ON frontier(status);
```

---

## 9. Idempotency and resume

A crawl must survive being killed at any instant and re-run without duplicating work or
records.

```python
import hashlib
import json
import sqlite3
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_id(natural_key: str) -> str:
    return "sha256:" + hashlib.sha256(natural_key.encode("utf-8")).hexdigest()


def crawl(con: sqlite3.Connection, client, politeness, out_path):
    while True:
        row = con.execute(
            "SELECT url FROM frontier WHERE status='pending' AND tries<3 LIMIT 1"
        ).fetchone()
        if row is None:
            break
        url = row[0]
        con.execute("UPDATE frontier SET tries=tries+1 WHERE url=?", (url,))
        con.commit()
        try:
            politeness.wait(url)
            resp = fetch(client, url)
            body = resp.text
            sha = hashlib.sha256(resp.content).hexdigest()
            for rec in extract_records(body, url, sha):
                append_jsonl(out_path, rec)               # id = record_id(canonical url)
            con.execute(
                "UPDATE frontier SET status='done', http_status=?, content_sha256=?, fetched_at=? WHERE url=?",
                (resp.status_code, sha, now_iso(), url),
            )
            politeness.record(url, ok=True)
        except Exception as exc:
            con.execute("UPDATE frontier SET status='failed', error=? WHERE url=?", (str(exc)[:500], url))
            politeness.record(url, ok=False)
        con.commit()
```

- **Idempotent records:** `id` derives from the natural key, so re-parsing the same page
  produces the same id; the loader dedupes on id (last-write-wins or first-wins — pick one
  and log it).
- **Resume token = the frontier itself.** Restart the script; it picks up `pending` rows.
- For cursor APIs, persist the last cursor in `state/` after each page, not at the end.
- Post-run: `SELECT status, COUNT(*) FROM frontier GROUP BY status` goes in the run log.

---

## 10. Change detection / watch mode

For recurring jobs ("tell me when this page changes"):

1. **Conditional GET first** (§7) — 304 means unchanged, done, nearly free for both sides.
2. On 200, compare a **normalized content hash**, because raw HTML churns (timestamps,
   CSRF tokens, ad slots, session ids) without meaningful change:

```python
import hashlib
from selectolax.parser import HTMLParser

VOLATILE = "script, style, noscript, iframe, [data-timestamp], .ad, #cookie-banner, time"

def normalized_hash(html: str, scope: str = "main, article, #content") -> str:
    tree = HTMLParser(html)
    root = tree.css_first(scope) or tree.body or tree.root
    for sel in VOLATILE.split(", "):
        for n in root.css(sel):
            n.decompose()
    text = " ".join(root.text(separator=" ").split())   # collapse whitespace
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

3. Hash changed → re-extract, diff the **records** (field-level), report what changed.
4. Cadence: match the source's real change rate (news: hours; docs: daily; catalog prices:
   daily). Sub-hourly polling of a site that changes weekly is impolite by definition.
5. Two consecutive extraction failures in watch mode = drift alarm → stop polling, repair
   the extractor against a fresh fixture, then resume.

---

## 11. Error taxonomy and handling

| Class | Signals | Action |
|---|---|---|
| Transient network | DNS fail, conn reset, timeout | Retry ×3 exp backoff + jitter; then mark `failed` |
| Rate limited | 429, 503 + Retry-After | Honor header, backoff, slow the whole run (halve concurrency / double delay) |
| Server error | 500/502/504 | Retry ×3; persistent → circuit-break host, report |
| Gone | 404 / 410 | Mark done-empty, drop from future frontiers; no retry |
| Auth required | 401, login redirect | **Stop & escalate to user** (§12). Never probe credentials |
| Forbidden / blocked | 403, block page, challenge/CAPTCHA markers | **Stop & escalate.** Do not rotate anything; do not retry harder |
| Robots-disallowed | `can_fetch` False | Skip + log `skipped_robots`; never fetch |
| Empty render | 200 but no target nodes | Once: climb HTTP→browser tier. Still empty → drift, repair extractor |
| Parse fail / drift | selector 0-hits, shape mismatch | NOT a retry. Save body to raw/, repair extractor vs fixture, re-parse from raw |
| Schema reject | validation error | Record → rejects.jsonl with error; investigate if rate >2% |

Detecting challenge/block pages (to classify, not to bypass): tiny body on a normally large
page, title/body containing "Access denied", "Verify you are human", "Just a moment",
CAPTCHA iframe present, or an interstitial status pattern (403/503 with an HTML challenge
body). Classification result: **stop and escalate**, with the evidence.

---

## 12. When to STOP and escalate to the user

Halt the run and present findings + options (never work around silently):

1. **Login wall** appears on target content → options: official API; the user's own
   authenticated session via browser-connection **with their explicit consent**; or drop scope.
2. **CAPTCHA or bot challenge** → the site declines automation. Options: official API,
   contacting the site, manual collection, or abandoning. Bypassing is off the table.
3. **robots.txt disallows** the needed paths → show the lines; automated collection of
   those paths is out; ask whether reduced scope (allowed paths, RSS, API) still helps.
4. **ToS prohibits** the collection (found in Phase A) → quote the clause, present risk.
5. **Paid API** is the right answer (rate limits, completeness, ToS) → per user policy,
   ask before spending anything.
6. **Legal uncertainty** — PII at scale, copyright-heavy content, jurisdiction questions →
   surface the concern plainly; the user decides, informed.
7. **Unexpected load impact** — errors/latency spiking on a small site mid-crawl → stop,
   report, propose gentler settings or off-peak resumption.

---

## 13. Privacy: PII minimization, redaction, retention

- **Minimize at extraction:** the parser only emits fields in the schema. If the task
  doesn't need author emails, the selector for them never gets written.
- **Redact before storage** when incidental PII rides along in free text:

```python
import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b")

def redact(text: str) -> str:
    return PHONE.sub("[PHONE]", EMAIL.sub("[EMAIL]", text))
```

- Mark redaction in provenance (`_prov.pii_scrubbed: true`) so downstream users know.
- **Public ≠ free-for-all:** GDPR-style rules apply to personal data even when publicly
  posted. Names attached to public professional content (bylines) used for citation are
  normal; compiling profiles of individuals is not what this skill is for.
- **Retention:** raw HTML archives holding personal data get a deletion date in `recon.md`;
  fixtures kept long-term get scrubbed. Never commit cookies, tokens, or auth state to the
  data directory — browser profile state lives outside `data/` entirely.

---

## 14. Windows / PowerShell operational snippets

```powershell
# Project scaffold
$proj = "~\scrapes\example-blog"
New-Item -ItemType Directory -Force -Path "$proj\raw", "$proj\records", "$proj\state", "$proj\logs" | Out-Null

# Python env (per scrape workspace, not global)
py -3.11 -m venv "$proj\.venv"
& "$proj\.venv\Scripts\Activate.ps1"
pip install httpx selectolax beautifulsoup4 lxml jsonschema playwright feedparser
python -m playwright install chrome   # real Chrome channel binaries check

# robots.txt quick look
curl.exe -sS "https://example.com/robots.txt" |
  Select-String -Pattern "^(User-agent|Disallow|Allow|Crawl-delay|Sitemap)"

# JSONL sanity checks
Get-Content "$proj\records\records.jsonl" | Measure-Object -Line          # record count
Get-Content "$proj\records\records.jsonl" -TotalCount 3                    # eyeball head
Get-Content "$proj\records\records.jsonl" | ForEach-Object {
  ($_ | ConvertFrom-Json)._prov.fetch_tier } | Group-Object | Select Name, Count

# UTF-8 pitfalls: PS 5.1 `>` redirection writes UTF-16LE. Either write files from Python
# (encoding="utf-8") or be explicit:
$body | Out-File -FilePath "$proj\raw\page.html" -Encoding utf8

# Resume state at a glance
python -c "import sqlite3; con=sqlite3.connect(r'$proj\state\frontier.sqlite'); print(con.execute('SELECT status, COUNT(*) FROM frontier GROUP BY status').fetchall())"

# Long-running crawl in the background with a transcript
Start-Process -NoNewWindow py -ArgumentList "crawl.py" -RedirectStandardOutput "$proj\logs\run.out.log" -RedirectStandardError "$proj\logs\run.err.log"
```

Path hygiene: prefer no-space paths for tool state (matches this machine's existing
convention); always pass `encoding="utf-8"` in Python file I/O; use raw strings (`r"C:\…"`)
for Windows paths in Python.

---

## 15. Cross-references

- [SKILL.md](SKILL.md) — pipeline phases, politeness defaults, quality gates.
- [examples.md](examples.md) — five worked, runnable examples using these patterns.
- [selectors-cookbook.md](selectors-cookbook.md) — selector recipes per page shape.
- [record-schema.json](record-schema.json) — the record + provenance contract.
- Sibling skills: `browser-connection` (Chrome profiles/CDP on this machine),
  `playwright-test-automation` (deeper Playwright), `multi-platform-agent-reach`
  (platform APIs/CLIs — check first for platform-shaped requests), `leash`
  (security-first browser control policies).
