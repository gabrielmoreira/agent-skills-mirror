---
name: end-to-end-web-scraping
description: "Runs an end-to-end pipeline for legal, ethical web data collection: legality gate, recon, extractor design, polite fetching, parsing, validation, deduplication, and persistence with full provenance. Use when the user wants to scrape, crawl, extract, or harvest a site; parse a site into structured data; get structured data from the web; run a sitemap crawl; do RSS collect work; perform HTML extract or table scrape tasks. Public, legally accessible data only — prefers official APIs, exports, RSS, and sitemaps before HTML scraping, and uses Playwright with a real, dedicated Chrome profile only for JS-rendered public pages. Never bypasses CAPTCHAs, logins, paywalls, or anti-bot systems; honors robots.txt, rate limits, and site ToS. Triggers: scrape, crawl, extract, harvest, parse site, structured data from web, sitemap crawl, RSS collect, HTML extract, table scrape."
version: 1.0.1
---

# End-to-End Web Scraping (Legal, Polite, Provenance-First)

Collect public web data through a disciplined pipeline: prove it's legal and welcome, find the cheapest viable source tier, write a deterministic extractor, fetch politely, validate against a schema, and persist records with provenance. The agent's expensive reasoning designs and repairs extractors; deterministic scripts do the volume.

## Hard Rules (non-negotiable, from user policy)

- NO CAPTCHA bypass, NO fingerprint spoofing, NO proxy rotation for evasion, NO stealth plugins.
- NO scraping behind login walls unless the user explicitly owns the account and consents.
- NO banks, no credential handling, no personal-data harvesting beyond what the task requires.
- Ask before any paid API or paid service is introduced.
- Honor robots.txt and site ToS for any automated collection at scale.
- Prefer dedicated browser profiles (never the user's daily profile) when a browser is needed.
- A CAPTCHA or block page is the site saying no; treat it as a terminal answer, not an obstacle.

## When to Use

**Use for:** public blog/news/docs content, open product catalogs, government and open-data portals, RSS/Atom feeds, sitemap-driven site copies, public tables and listings, research data collection feeding the user's research skills, and monitoring public pages for change.

**Do NOT use for (stop and tell the user why):**

- Login walls without explicit user permission and a user-owned account/session.
- Banking, payment, healthcare-portal, or any credentialed financial site.
- Anything requiring CAPTCHA solving, bot-detection evasion, or fingerprint manipulation.
- Bulk collection a site's ToS clearly prohibits (check before large crawls, not after).
- Harvesting personal data (emails, phone numbers, profiles) for outreach/enrichment.
- Re-publishing copyrighted content wholesale; extraction for analysis ≠ license to republish.

## Prerequisites

- **Python 3.10+** with `httpx`, `selectolax` (or `beautifulsoup4`), `jsonschema`, `playwright` installed.
- **Playwright Chromium/Chrome** browser installed: `playwright install chromium` (or use real Chrome channel).
- **curl.exe** available on Windows for recon (PowerShell primary host).
- **SQLite** for frontier state (standard library `sqlite3`).
- Load [record-schema.json](record-schema.json) before defining any project's output schema — instantiate, don't reinvent.
- For platform-specific requests (Reddit, YouTube, X), check the `multi-platform-agent-reach` skill FIRST — those have better tools than scraping.
- For Chrome profile/CDP conventions on this machine, see the `browser-connection` skill.

## Procedure

### Step 1 — Decision Tree: Cheapest Legitimate Tier First

Walk top to bottom; stop at the first tier that works. Never skip ahead to a browser.

```
0. LEGALITY GATE (always first — see Phase A below)
   Not clearly legal/permitted for this purpose? → STOP, explain to user.

1. Official API or documented data endpoint?
   → Use it. Free tier first; ASK USER before anything paid. Done.
   (Check multi-platform-agent-reach skill for platform CLIs already installed.)

2. Official export / dataset / bulk download (CSV dumps, open-data portal, archive)?
   → Download it. Done.

3. RSS / Atom feed or sitemap.xml?
   → Feeds for recency, sitemap for coverage. Cheap, stable, publisher-sanctioned.

4. Static HTML — is the target data in the raw HTTP response body?
   → Verify with one curl.exe/httpx fetch. If yes: httpx + selectolax/bs4. The workhorse tier.

5. JS-rendered — raw response is an empty shell but the page is public?
   → Playwright, real Chrome channel, dedicated scraping profile, normal automation only.
   → During recon, watch the network tab: if the page calls a clean JSON/XHR endpoint,
     drop back to tier 4 against that endpoint for all future runs.

6. Login wall / CAPTCHA / block page / ToS-prohibited / legally unclear?
   → STOP AND ASK THE USER. Present what was found, the options (official API, user's own
     authenticated session via browser-connection with consent, or abandoning), and the risk.
```

### Step 2 — Phase A: Scope & Legality Gate

1. Write down: target site(s), exact data fields wanted, purpose, expected volume, one-shot vs recurring.
2. Fetch `robots.txt`; parse User-agent groups, `Disallow`, `Crawl-delay`, `Sitemap` lines. Disallowed paths are off-limits for automated collection — no exceptions.
3. For >100-page jobs or recurring crawls: check the site's ToS page for scraping clauses.
4. PII check: does the data include personal information? If yes, minimize — collect only fields the task needs, plan redaction/retention (see [reference.md](reference.md) → Privacy section).
5. Output a one-paragraph scope note in the run log: what, why, tier chosen, robots status.

**PowerShell recon command for robots.txt:**
```powershell
curl.exe -sSI "https://example.com/robots.txt"
curl.exe -sS "https://example.com/robots.txt" | Out-File -Encoding utf8 robots.txt
```

### Step 3 — Phase B: Recon (touch the site ~3 times, not 300)

1. One `curl.exe -sSI` for headers: server, caching (`ETag`, `Last-Modified`), rate-limit headers.
2. One full fetch of a representative page; save it as a fixture. Diff raw HTML vs rendered DOM if JS-rendering is suspected (WebFetch or Playwright single pass).
3. Map: URL structure, pagination model (page param / cursor / next-link / infinite scroll), where fields live (JSON-LD? microdata? stable CSS anchors?), total expected item count.
4. Record everything in a `recon.md` note in the project folder — this is the extractor spec.

**PowerShell fixture save:**
```powershell
curl.exe -sS "https://example.com/page/1" | Out-File -Encoding utf8 fixtures\page-1.html
```

> **Load [reference.md](reference.md)** when implementing any phase — it has HTTP/parse/pagination/robots/Playwright/caching/storage/resume/errors/privacy/escalation details and PowerShell snippets.

### Step 4 — Phase C: Extractor Design

1. Prefer structured islands first: JSON-LD (`script[type="application/ld+json"]`), microdata, OpenGraph — they survive redesigns.
2. Else CSS/XPath against **stable anchors**: semantic tags, `data-*` attributes, ARIA roles, text anchors. Never hashed/utility class names (`css-1x2y3z`, Tailwind soup).
3. Define the output schema BEFORE writing the parser — instantiate [record-schema.json](record-schema.json) with project-specific `data` fields.
4. Write the extractor against the saved fixture; keep the fixture as a regression test.

> **Load [selectors-cookbook.md](selectors-cookbook.md)** when writing or repairing selectors for lists, tables, cards, nav, metadata, pagination, or JSON-LD.

### Step 5 — Phase D: Fetch Strategy

1. **Tier 4 (HTTP):** Python `httpx` client, retries with exponential backoff + jitter, honest UA.
2. **Tier 5 (Browser):** Playwright real Chrome (`channel="chrome"`), persistent context with a dedicated scraping profile dir — never the daily profile (see `browser-connection` skill for profile/CDP conventions on this machine).
3. Politeness defaults (see table below) apply regardless of tier. Concurrency is per-host.
4. Conditional GETs (`If-None-Match` / `If-Modified-Since`) on every recurring fetch.

### Step 6 — Phase E: Parse & Normalize

1. Parse with selectolax (fast) or BeautifulSoup (lenient) — tradeoffs in [reference.md](reference.md).
2. Normalize at parse time: absolute URLs (`urljoin`), ISO-8601 UTC dates, trimmed whitespace, decoded entities, canonical casing for enums.
3. Missing field → `null`, never a guess or empty-string placeholder.
4. Emit one JSON object per item with `data` + `_prov` per [record-schema.json](record-schema.json).

### Step 7 — Phase F: Validate & Dedupe

1. Validate every record against the JSON Schema (`jsonschema` lib). Failures go to a `rejects.jsonl` with the error — never silently dropped or coerced.
2. Dedupe on a stable natural key (canonical URL, or site ID) hashed into `id`.
3. Run quality gates (see Verification section) before declaring the dataset done.

### Step 8 — Phase G: Persist with Provenance

1. Layout: `raw/` (exact response bytes + meta sidecar), `records/records.jsonl`, `state/` (SQLite frontier for resume), `logs/`. Full layout in [reference.md](reference.md).
2. JSONL for pipelines, CSV for spreadsheet handoff, SQLite when querying/joining.
3. Every record carries `_prov`: source_url, fetched_at, http_status, content_sha256, extractor_version, fetch_tier, robots_checked. No provenance → not a record.

### Step 9 — Phase H: Monitor & Resume

1. Frontier state in SQLite so an interrupted crawl resumes exactly where it stopped.
2. Recurring jobs: conditional GETs + normalized content-hash change detection.
3. Drift alarm: selector returns 0 nodes or schema pass-rate drops → stop the run, re-run recon against a fresh fixture, repair the extractor, add the new fixture.

### Politeness Defaults

Apply these unless the site documents more generous limits. Robots `Crawl-delay` overrides downward (slower) always; never override upward.

| Setting | Default | Notes |
|---|---|---|
| Delay between requests (per host) | 1.5s + jitter(0–0.5s) | 3s+ for small/personal sites |
| Concurrency per host | 1 | max 2, only for large CDN-backed sites |
| Global concurrency (multi-host) | 4 | 8 absolute ceiling |
| User-Agent | identify as a bot with contact | e.g. `research-agent/1.0 (+mailto:user@example.com; personal research)` |
| `Retry-After` header | always honored, verbatim | on 429/503 |
| 429/5xx backoff | exponential ×2 from 2s, max 4 tries | then circuit-break the host for 15 min |
| Consecutive-error stop | 5 errors → halt run, report | never grind against a failing/blocking site |
| Crawl window | off-peak for big crawls when feasible | be a guest, not a load test |
| Caching | ETag/Last-Modified conditional GETs | never re-download unchanged pages |

Never rotate proxies, user agents, or fingerprints to distribute load past a block — a block means stop.

### Data Model — Record + Provenance

Canonical schema: [record-schema.json](record-schema.json). Shape:

```json
{
  "id": "sha256:1f3a…",
  "data": { "title": "…", "url": "…", "published_at": "2026-07-01T00:00:00Z" },
  "_prov": {
    "source_url": "https://example.com/post/1",
    "final_url": "https://example.com/post/1",
    "fetched_at": "2026-07-15T09:12:44Z",
    "http_status": 200,
    "content_sha256": "…",
    "fetch_tier": "http",
    "extractor": "example-blog",
    "extractor_version": "1.0.0",
    "robots_checked": true,
    "run_id": "2026-07-15-a"
  }
}
```

`id` = sha256 of the canonical natural key. `data` fields are project-specific and schema-validated. `_prov` is mandatory and identical in shape across all projects, which is what lets the research skills cite and audit any record later.

## Pitfalls

- **Silent bulk hammering** — launching a 5,000-page crawl with no delay because "it worked on 10 pages." Scale changes the ethics; politeness defaults are not optional at volume.
- **Ignoring robots.txt** because the library doesn't check it automatically. Check it in Phase A, in code, and log the result.
- **Browser-first laziness** — spinning up Playwright for a site whose data is in the raw HTML, an RSS feed, or a JSON endpoint. Walk the tree.
- **Scraping with the daily browser profile** — session/cookie contamination and consent ambiguity. Dedicated profile, always.
- **Storing secrets or PII carelessly** — cookies, tokens, or personal data landing in `records.jsonl` or committed fixtures. Scrub fixtures; keep auth state out of the dataset.
- **Guessing instead of nulling** — filling missing fields with plausible values. Null + flag.
- **Re-reading pages with the LLM at volume** — the model designs and repairs extractors; deterministic code runs them. If the model parses every page, the design is wrong.
- **Retrying parse failures like network failures** — a parse failure is drift; re-running it re-fails. Escalate to extractor repair instead of looping.
- **No fixtures** — an extractor without a saved raw-HTML regression fixture cannot be safely repaired later.

## Verification

### Quality Gates (dataset is not "done" until all pass)

- [ ] **Schema pass-rate ≥ 98%** of fetched items validate; rejects.jsonl reviewed, not ignored.
- [ ] **Required-field completeness ≥ 95%** per field, or the shortfall is explained in the run log.
- [ ] **Coverage check:** record count vs expected count from recon (sitemap size, stated total, pagination math). >5% gap → investigate before shipping.
- [ ] **Dedupe report:** duplicates found/removed count logged; zero duplicate `id`s remain.
- [ ] **Sample visual check:** open 3–5 random records next to their live source pages (or Playwright screenshots) and confirm field-by-field correctness — this catches the confidently-wrong-selector failure that validation cannot.
- [ ] **Provenance complete:** every record has all required `_prov` fields.
- [ ] **Politeness audit:** log shows delays honored, no 429s ground through, robots respected.

**PowerShell verification commands:**
```powershell
# Count records
(Get-Content records\records.jsonl | Measure-Object -Line).Lines

# Check for duplicate IDs
Get-Content records\records.jsonl | ConvertFrom-Json | Select-Object -ExpandProperty id | Group-Object | Where-Object { $_.Count -gt 1 }

# Verify all records have _prov
Get-Content records\records.jsonl | ConvertFrom-Json | Where-Object { -not $_._prov } | Measure-Object | Select-Object -ExpandProperty Count
# Expected: 0

# Check rejects count
(Get-Content records\rejects.jsonl | Measure-Object -Line).Lines
```

### Progress Checklist (copy into the run log)

```
[ ] A. Scope note written (fields, purpose, volume, one-shot/recurring)
[ ] A. robots.txt fetched, parsed, path allowed; Crawl-delay noted
[ ] A. ToS checked (required for scale/recurring); PII plan noted
[ ] B. Recon done: headers, fixture saved, pagination mapped, expected count estimated
[ ] C. Tier selected via decision tree (logged which and why)
[ ] C. Schema instantiated from record-schema.json
[ ] C. Extractor written + passing against fixture
[ ] D. Politeness config set (delay, concurrency, UA, backoff)
[ ] E. Normalization rules implemented (URLs, dates, whitespace, nulls)
[ ] F. Validation + dedupe wired; rejects.jsonl in place
[ ] G. Storage layout created; provenance on every record
[ ] F/G. Quality gates all pass
[ ] H. Resume state verified (kill + restart mid-crawl once, on big jobs)
[ ] H. Watch/monitor configured (recurring jobs only)
[ ] Handoff: records.jsonl + run log delivered to user / research skill
```

## Examples

> **Load [examples.md](examples.md)** when starting a job that resembles: blog list, sitemap docs crawl, paginated catalog, JS-rendered page, or RSS aggregation.

## Related Skills

- **multi-platform-agent-reach** — owns platform-specific access (installed CLIs, APIs); check it FIRST for Reddit/YouTube/X-shaped requests.
- **browser-connection** — owns Chrome profiles/CDP on this machine; leash policies apply when driving a browser.
- **playwright-test-automation** — deeper Playwright patterns for complex browser automation.
- **deep-research / research skills** — call this skill when a source needs structured harvesting beyond what WebFetch returns; hand back `records.jsonl` + the run log. `_prov.source_url` + `fetched_at` are the citation backbone.

## Deep-Dive Reference Files

| File | Read when |
|---|---|
| [reference.md](reference.md) | Implementing any phase — HTTP/parse/pagination/robots/Playwright/caching/storage/resume/errors/privacy/escalation details, PowerShell snippets |
| [examples.md](examples.md) | Starting a job that resembles: blog list, sitemap docs crawl, paginated catalog, JS-rendered page, RSS aggregation |
| [selectors-cookbook.md](selectors-cookbook.md) | Writing or repairing selectors for lists, tables, cards, nav, metadata, pagination, JSON-LD |
| [record-schema.json](record-schema.json) | Defining any project's output schema — instantiate, don't reinvent |
