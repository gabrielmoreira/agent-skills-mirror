# Worked Examples — End-to-End Web Scraping

Five complete, runnable examples, each exercising the pipeline from [SKILL.md](SKILL.md)
at a different tier. Shared helpers (`fetch`, `HostPoliteness`, `load_robots`,
`iter_sitemap`, `conditional_fetch`, `now_iso`, `record_id`) are defined in
[reference.md](reference.md) — the examples import them from a local `scrapelib.py`
containing those functions verbatim.

Every example assumes Phase A already passed: robots.txt checked and allowing, purpose
noted, PII plan not needed (all targets are public, non-personal content).

---

## Example 1 — Static blog post list → JSONL

**Shape:** classic tier-4 job. Public blog, post list in raw HTML, `?page=N` pagination.
**Fields:** title, url, published_at, summary.

```python
# blog_scrape.py
import json
import pathlib
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from scrapelib import HostPoliteness, fetch, load_robots, make_client, now_iso, record_id

BASE = "https://blog.example.com/articles"
OUT = pathlib.Path("data/example-blog/records/records.jsonl")
EXTRACTOR = ("example-blog", "1.0.0")


def parse_items(html: str, page_url: str, sha: str) -> list[dict]:
    tree = HTMLParser(html)
    records = []
    for card in tree.css("main article.post-summary"):
        a = card.css_first("h2 a")
        time_node = card.css_first("time[datetime]")
        summary = card.css_first("p.excerpt")
        url = urljoin(page_url, a.attributes.get("href", "")) if a else None
        if not url:
            continue  # a post card without a link is decoration, not data
        records.append({
            "id": record_id(url),
            "data": {
                "title": a.text(strip=True),
                "url": url,
                "published_at": time_node.attributes.get("datetime") if time_node else None,
                "summary": summary.text(strip=True) if summary else None,
            },
            "_prov": {
                "source_url": page_url,
                "final_url": page_url,
                "fetched_at": now_iso(),
                "http_status": 200,
                "content_sha256": sha,
                "fetch_tier": "http",
                "extractor": EXTRACTOR[0],
                "extractor_version": EXTRACTOR[1],
                "robots_checked": True,
                "run_id": "2026-07-15-a",
            },
        })
    return records


def main() -> None:
    import hashlib
    OUT.parent.mkdir(parents=True, exist_ok=True)
    politeness = HostPoliteness(delay=1.5)
    seen_ids: set[str] = set()
    with make_client() as client:
        rp = load_robots(client, BASE)
        empty_streak = 0
        with OUT.open("a", encoding="utf-8") as f:
            for page in range(1, 201):
                url = f"{BASE}?page={page}"
                if not rp.can_fetch(client.headers["User-Agent"], url):
                    print(f"robots disallows {url}; stopping")
                    break
                politeness.wait(url)
                resp = fetch(client, url)
                if resp.status_code == 404:
                    break
                sha = hashlib.sha256(resp.content).hexdigest()
                items = parse_items(resp.text, url, sha)
                if not items:
                    empty_streak += 1
                    if empty_streak >= 2:
                        break
                    continue
                empty_streak = 0
                new = [r for r in items if r["id"] not in seen_ids]
                seen_ids.update(r["id"] for r in new)
                for rec in new:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                print(f"page {page}: {len(new)} new / {len(items)} parsed")
    print(f"done: {len(seen_ids)} records → {OUT}")


if __name__ == "__main__":
    main()
```

Run and gate:

```powershell
python blog_scrape.py
# Quality gates: count vs expected, schema check, sample check
python -c "import json,sys; [json.loads(l) for l in open('data/example-blog/records/records.jsonl', encoding='utf-8')]" && echo JSONL_OK
python validate_records.py data/example-blog/records/records.jsonl   # see Example 3 for the validator
```

---

## Example 2 — Docs site with sitemap → offline searchable index

**Shape:** sitemap-driven full-coverage crawl into SQLite FTS5. Recurring-friendly via
`lastmod` + conditional GETs.

```python
# docs_index.py
import hashlib
import pathlib
import sqlite3

from selectolax.parser import HTMLParser

from scrapelib import (HostPoliteness, conditional_fetch, iter_sitemap, load_cache,
                       load_robots, make_client, now_iso)

SITEMAP = "https://docs.example.com/sitemap.xml"
DB = pathlib.Path("data/example-docs/state/index.sqlite")


def extract_doc(html: str) -> dict | None:
    tree = HTMLParser(html)
    main = tree.css_first("main, article, [role='main']")
    if main is None:
        return None
    for junk in main.css("nav, aside, script, style, .edit-link, .breadcrumbs"):
        junk.decompose()
    h1 = tree.css_first("h1")
    return {
        "title": h1.text(strip=True) if h1 else None,
        "body": " ".join(main.text(separator=" ").split()),
    }


def main() -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS docs USING fts5(url, title, body)")
    con.execute("""CREATE TABLE IF NOT EXISTS pages(
        url TEXT PRIMARY KEY, lastmod TEXT, content_sha256 TEXT, fetched_at TEXT)""")

    politeness = HostPoliteness(delay=1.0)   # large CDN-backed docs site
    cache = load_cache()
    stats = {"fetched": 0, "unchanged": 0, "skipped_lastmod": 0, "no_main": 0}

    with make_client() as client:
        rp = load_robots(client, SITEMAP)
        ua = client.headers["User-Agent"]
        for url, lastmod in iter_sitemap(client, SITEMAP, politeness):
            if not rp.can_fetch(ua, url):
                continue
            prev = con.execute("SELECT lastmod FROM pages WHERE url=?", (url,)).fetchone()
            if prev and lastmod and prev[0] == lastmod:
                stats["skipped_lastmod"] += 1
                continue                       # sitemap says unchanged since last run
            politeness.wait(url)
            body, changed = conditional_fetch(client, url, cache)
            if not changed and prev:
                stats["unchanged"] += 1
                continue
            if body is None:
                continue
            doc = extract_doc(body)
            if doc is None:
                stats["no_main"] += 1
                continue
            sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
            con.execute("DELETE FROM docs WHERE url=?", (url,))
            con.execute("INSERT INTO docs(url, title, body) VALUES (?,?,?)",
                        (url, doc["title"], doc["body"]))
            con.execute("INSERT OR REPLACE INTO pages VALUES (?,?,?,?)",
                        (url, lastmod, sha, now_iso()))
            con.commit()
            stats["fetched"] += 1
    print(stats)


if __name__ == "__main__":
    main()
```

Query the offline index:

```powershell
python -c "import sqlite3; con = sqlite3.connect(r'data/example-docs/state/index.sqlite'); [print(r) for r in con.execute(\"SELECT url, title FROM docs WHERE docs MATCH 'websocket NEAR reconnect' LIMIT 5\")]"
```

Re-running the script is the update mechanism: unchanged pages cost a 304 (or nothing at
all when `lastmod` matches), so weekly refreshes are cheap for both sides.

---

## Example 3 — Public product catalog table with pagination → validated CSV/JSONL

**Shape:** tier-4 table scrape with header-driven column mapping (robust to column
reordering), page-param pagination, schema validation, CSV export for spreadsheet handoff.

```python
# catalog_scrape.py
import csv
import hashlib
import json
import pathlib

from jsonschema import Draft202012Validator
from selectolax.parser import HTMLParser

from scrapelib import HostPoliteness, fetch, load_robots, make_client, now_iso, record_id

BASE = "https://catalog.example.org/parts"
OUTDIR = pathlib.Path("data/example-catalog/records")
SCHEMA = json.loads(pathlib.Path(__file__).with_name("record-schema.json").read_text("utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)

# Map on header TEXT, not column position — survives column reshuffles.
HEADER_MAP = {"part number": "part_no", "name": "name", "price (usd)": "price_usd",
              "in stock": "in_stock"}


def parse_table(html: str) -> list[dict]:
    tree = HTMLParser(html)
    table = tree.css_first("table#parts, table.catalog, main table")
    if table is None:
        return []
    headers = [th.text(strip=True).lower() for th in table.css("thead th")]
    cols = {i: HEADER_MAP[h] for i, h in enumerate(headers) if h in HEADER_MAP}
    rows = []
    for tr in table.css("tbody tr"):
        cells = tr.css("td")
        if len(cells) < len(headers):
            continue                                   # spanning/summary rows: skip
        raw = {name: cells[i].text(strip=True) for i, name in cols.items()}
        if not raw.get("part_no"):
            continue
        price_txt = raw.get("price_usd", "").replace("$", "").replace(",", "").strip()
        rows.append({
            "part_no": raw["part_no"],
            "name": raw.get("name") or None,
            "price_usd": float(price_txt) if price_txt else None,   # ValueError = drift → let it raise
            "in_stock": raw.get("in_stock", "").lower() in ("yes", "y", "true", "in stock"),
        })
    return rows


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    politeness = HostPoliteness(delay=2.0)              # small org site: extra gentle
    records, rejects = [], []
    with make_client() as client:
        rp = load_robots(client, BASE)
        for page in range(1, 100):
            url = f"{BASE}?page={page}"
            if not rp.can_fetch(client.headers["User-Agent"], url):
                break
            politeness.wait(url)
            resp = fetch(client, url)
            rows = parse_table(resp.text)
            if not rows:
                break
            sha = hashlib.sha256(resp.content).hexdigest()
            for row in rows:
                rec = {
                    "id": record_id(f"{BASE}#part={row['part_no']}"),
                    "data": row,
                    "_prov": {"source_url": url, "final_url": str(resp.url),
                              "fetched_at": now_iso(), "http_status": resp.status_code,
                              "content_sha256": sha, "fetch_tier": "http",
                              "extractor": "example-catalog", "extractor_version": "1.0.0",
                              "robots_checked": True, "run_id": "2026-07-15-a",
                              "page_number": page},
                }
                errors = sorted(VALIDATOR.iter_errors(rec), key=str)
                (records if not errors else rejects).append(
                    rec if not errors else {"record": rec, "errors": [e.message for e in errors]})

    # Dedupe on id (first-wins), then persist JSONL + CSV
    seen, unique = set(), []
    for r in records:
        if r["id"] not in seen:
            seen.add(r["id"])
            unique.append(r)
    with (OUTDIR / "records.jsonl").open("w", encoding="utf-8") as f:
        for r in unique:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (OUTDIR / "rejects.jsonl").open("w", encoding="utf-8") as f:
        for r in rejects:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (OUTDIR / "catalog.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["part_no", "name", "price_usd", "in_stock"])
        w.writeheader()
        w.writerows(r["data"] for r in unique)

    total = len(unique) + len(rejects)
    print(f"records={len(unique)} rejects={len(rejects)} "
          f"pass_rate={len(unique)/max(total,1):.1%} (gate: ≥98%)")


if __name__ == "__main__":
    main()
```

Gate notes: the pass-rate prints against the 98% gate; `price_usd` parse errors raise
rather than coerce (a currency-format change is drift and should stop the run, not produce
silently-wrong prices).

---

## Example 4 — JS-rendered public page via Playwright (simple)

**Shape:** tier-5. Public event listing rendered client-side; raw HTML is an empty shell
(verified in recon). Real Chrome, dedicated profile, no evasion. Also captures the JSON
endpoint the page calls, so the *next* run can drop to tier 4.

```python
# events_render.py
import hashlib
import json
import pathlib

from playwright.sync_api import sync_playwright

from scrapelib import now_iso, record_id

URL = "https://events.example.city/calendar"
PROFILE = r"~\ScrapeProfiles\public-default"
OUT = pathlib.Path("data/example-events/records/records.jsonl")
RAW = pathlib.Path("data/example-events/raw")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    json_endpoints: list[str] = []

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE, channel="chrome", headless=True)
        page = ctx.new_page()
        page.on("response", lambda r: json_endpoints.append(r.url)
                if "application/json" in (r.headers.get("content-type") or "")
                and r.request.method == "GET" else None)
        page.goto(URL, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_selector("[data-testid='event-card']", timeout=15_000)

        items = page.eval_on_selector_all(
            "[data-testid='event-card']",
            """els => els.map(e => ({
                 title: e.querySelector('h3')?.innerText?.trim() ?? null,
                 url: e.querySelector('a')?.href ?? null,
                 when: e.querySelector('time')?.getAttribute('datetime') ?? null,
                 venue: e.querySelector('[data-testid=\"venue\"]')?.innerText?.trim() ?? null,
               }))""")

        rendered = page.content()
        ctx.close()

    sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    (RAW / f"{sha[:16]}.html").write_text(rendered, encoding="utf-8")   # repair fixture

    with OUT.open("w", encoding="utf-8") as f:
        for it in items:
            if not it["url"]:
                continue
            f.write(json.dumps({
                "id": record_id(it["url"]),
                "data": it,
                "_prov": {"source_url": URL, "final_url": URL, "fetched_at": now_iso(),
                          "http_status": 200, "content_sha256": sha,
                          "fetch_tier": "browser", "extractor": "example-events",
                          "extractor_version": "1.0.0", "robots_checked": True,
                          "run_id": "2026-07-15-a"},
            }, ensure_ascii=False) + "\n")

    print(f"{len(items)} events → {OUT}")
    if json_endpoints:
        print("Tier-4 candidates observed (verify + prefer next run):")
        for u in sorted(set(json_endpoints))[:10]:
            print(" ", u)


if __name__ == "__main__":
    main()
```

If `wait_for_selector` times out and the page shows a challenge/CAPTCHA instead of events:
stop, screenshot for the report, escalate per reference.md §12. No retries, no workarounds.

---

## Example 5 — RSS/Atom feed aggregation → deduped JSONL

**Shape:** tier-3, the friendliest tier — feeds exist precisely to be polled. Multiple
feeds, conditional-GET support via feedparser's ETag handling, dedupe across feeds.

```python
# feeds_collect.py
import hashlib
import json
import pathlib
import time
from datetime import datetime, timezone

import feedparser   # pip install feedparser

from scrapelib import UA, now_iso, record_id

FEEDS = [
    "https://blog.example.com/rss.xml",
    "https://research.example.edu/atom.xml",
    "https://news.example.org/feed/",
]
STATE = pathlib.Path("data/feeds/state/feed_state.json")
OUT = pathlib.Path("data/feeds/records/records.jsonl")


def entry_time(entry) -> str | None:
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(STATE.read_text("utf-8")) if STATE.exists() else {}
    seen: set[str] = set()
    if OUT.exists():
        with OUT.open(encoding="utf-8") as f:
            seen = {json.loads(line)["id"] for line in f if line.strip()}

    new_count = 0
    with OUT.open("a", encoding="utf-8") as f:
        for feed_url in FEEDS:
            st = state.get(feed_url, {})
            parsed = feedparser.parse(feed_url, agent=UA,
                                      etag=st.get("etag"), modified=st.get("modified"))
            if parsed.get("status") == 304:
                print(f"{feed_url}: unchanged (304)")
                continue
            if parsed.bozo and not parsed.entries:
                print(f"{feed_url}: parse problem: {parsed.bozo_exception}")
                continue
            state[feed_url] = {"etag": parsed.get("etag"),
                               "modified": parsed.get("modified")}
            body_sha = hashlib.sha256(
                json.dumps([e.get("id", e.get("link", "")) for e in parsed.entries])
                .encode("utf-8")).hexdigest()
            for e in parsed.entries:
                link = e.get("link")
                if not link:
                    continue
                rid = record_id(e.get("id") or link)     # guid preferred over link
                if rid in seen:
                    continue
                seen.add(rid)
                new_count += 1
                f.write(json.dumps({
                    "id": rid,
                    "data": {
                        "title": e.get("title"),
                        "url": link,
                        "published_at": entry_time(e),
                        "summary": (e.get("summary") or "")[:2000] or None,
                        "feed": feed_url,
                    },
                    "_prov": {"source_url": feed_url, "final_url": feed_url,
                              "fetched_at": now_iso(),
                              "http_status": parsed.get("status", 200),
                              "content_sha256": body_sha, "fetch_tier": "feed",
                              "extractor": "feeds-collect", "extractor_version": "1.0.0",
                              "robots_checked": True, "run_id": "2026-07-15-a"},
                }, ensure_ascii=False) + "\n")
            time.sleep(1.0)                              # polite even to feeds

    STATE.write_text(json.dumps(state, indent=2), "utf-8")
    print(f"{new_count} new entries; {len(seen)} total")


if __name__ == "__main__":
    main()
```

Watch-mode cadence: schedule this hourly at most for news feeds, daily for blogs — the
304 path makes polling nearly free, but cadence should still match the source's real
publish rate (reference.md §10).
