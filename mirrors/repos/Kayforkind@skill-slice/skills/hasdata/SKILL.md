---
name: hasdata
description: "Calls HasData (api.hasdata.com, x-api-key) for Google/Bing SERP JSON, vertical scrapers (Amazon, Zillow, Maps), POST /scrape/web on arbitrary public URLs, and async Scraper Jobs with poll plus webhook. Use when the request is HasData, public SERP, or bulk public crawl. Not for authenticated first-party product APIs, CAPTCHA bypass, or Playwright/CDP sessions that never hit HasData."
version: 1.0.1
risk: safe
source: official
source_type: official
source_repo: HasData/hasdata-cli
license: MIT
license_source: "https://github.com/HasData/hasdata-cli/blob/main/LICENSE"
date_added: "2026-06-04"
---

# HasData

Cloud platform for extracting public web data. One API key, three execution modes. All endpoints sit under `https://api.hasdata.com` and authenticate with the `x-api-key` header.

## When to Use

Use this skill when:

- The user needs web scraping of arbitrary URLs.
- The user needs search engine results (Google, Bing, Trends).
- The user needs structured data extraction (ecommerce, real estate, travel, jobs, local business, YouTube).
- The user needs bulk/async crawling with webhook fan-out.
- The user explicitly asks about HasData or `api.hasdata.com`.

## Prerequisites

- A valid HasData API key. Store it in the environment variable `HASDATA_API_KEY`. Never hardcode, never log.
- On Windows (PowerShell), set it for the current session:

  ```powershell
  $env:HASDATA_API_KEY = "YOUR_KEY"
  ```

  Or persist it for future sessions:

  ```powershell
  [Environment]::SetEnvironmentVariable("HASDATA_API_KEY", "YOUR_KEY", "User")
  ```

- HTTP client with a configurable timeout of **at least 300 seconds** (see Pitfalls).
- Network egress to `https://api.hasdata.com`.

## Three Execution Modes

| Mode | Latency | When | Endpoint |
|---|---|---|---|
| **Web Scraping API** | seconds | Arbitrary URL — JS rendering, CSS/AI extraction, screenshots | `POST /scrape/web` |
| **Scraper APIs** (sync) | seconds | Pre-parsed JSON for known platforms (Google, Amazon, Zillow, …) | `GET /scrape/<vertical>/<resource>` |
| **Scraper Jobs** (async) | minutes–hours | Bulk extraction, recursive crawling, webhook fan-out | `POST /scrapers/<slug>/jobs` |

**Decision rule.** Default to a **Scraper API** when one exists for the target platform (pre-parsed JSON, no selector maintenance). Use **Web Scraping** for arbitrary URLs not covered by an API. Reach for a **Scraper Job** only when no API equivalent exists — `crawler`, `contacts`, `sec-edgar`, `amazon-bestsellers`, `amazon-product-reviews` — *or* when async fan-out + webhooks save engineering time over a paginated client loop.

## Always-True Response Shape

```json
{
  "requestMetadata": { "id": "…", "status": "ok", "url": "…" },
  "...": "endpoint-specific"
}
```

**HARD RULE:** Treat data as valid only if `requestMetadata.status === "ok"`. HTTP 200 alone is **not** a success signal.

## Procedure

### 1. Quick smoke test (Google SERP)

```powershell
curl -G 'https://api.hasdata.com/scrape/google/serp' `
  --data-urlencode 'q=coffee' `
  -H 'x-api-key: YOUR_KEY'
```

Expected: JSON with `requestMetadata.status` equal to `"ok"`.

### 2. Choose the execution mode

- **Scraper API** — if the platform has a dedicated endpoint (Google, Amazon, Zillow, Airbnb, Indeed, YouTube, etc.). Load the matching reference file (see Reference Loading Guide below) for parameters.
- **Web Scraping API** — for arbitrary URLs. Load `references/web-scraping.md`.
- **Scraper Job** — for bulk/async. Load `references/scraper-jobs.md`.

### 3. Web Scraping API (`POST /scrape/web`)

Load `references/web-scraping.md` before constructing the request.

```powershell
curl -X POST 'https://api.hasdata.com/scrape/web' `
  -H 'x-api-key: YOUR_KEY' `
  -H 'Content-Type: application/json' `
  -d '{\"url\":\"https://example.com\",\"jsRendering\":false,\"outputFormat\":\"markdown\"}'
```

Key parameters (full list in reference):

- `url` — target URL (required).
- `jsRendering` — **default to `false`**. Enable only if the page requires a headless browser.
- `outputFormat` — `markdown`, `html`, `text`, or `screenshot`.
- `extract` — CSS selectors or AI extraction prompt.
- `headers` — pass custom headers including `Cookie` (there is **no** top-level `cookies` parameter).

### 4. Scraper APIs (sync, `GET /scrape/<vertical>/<resource>`)

Load the relevant reference file for the vertical:

```powershell
curl -G 'https://api.hasdata.com/scrape/google/serp' `
  --data-urlencode 'q=coffee' `
  --data-urlencode 'num=10' `
  -H 'x-api-key: YOUR_KEY'
```

Check `requestMetadata.status === "ok"` before consuming results. Inspect rich-snippet fields (`knowledgeGraph`, `localResults`, `inlineShoppingResults`, `relatedQuestions`) before considering direct page access.

### 5. Scraper Jobs (async, `POST /scrapers/<slug>/jobs`)

Load `references/scraper-jobs.md` before constructing the request.

```powershell
curl -X POST 'https://api.hasdata.com/scrapers/crawler/jobs' `
  -H 'x-api-key: YOUR_KEY' `
  -H 'Content-Type: application/json' `
  -d '{\"url\":\"https://example.com\",\"outputFormat\":[\"markdown\"],\"includePaths\":\"/docs/.+\"}'
```

**HARD RULES for async jobs:**

1. The submit response handle is `body.id` (an **integer**), **not** `jobId`. Persist it immediately.
2. Poll `GET /scrapers/jobs/<id>` every 10–30 s with backoff.
3. Treat webhooks as **best-effort** (3 retries). Always pair with polling.
4. On `finished`, the status carries `data: {csv, json, xlsx}` short-lived URLs — **download immediately**.

### 6. High-leverage patterns

- **SERP-first enrichment.** Use Google SERP to surface public snippets for company/professional lookup before attempting direct scraping. Treat personal email/phone lookup as allowed only with a legitimate purpose and user authorization.
- **AI Mode + verify.** `/scrape/google/ai-mode` for the answer + references → `/scrape/web` (markdown) on each reference URL → cited RAG context, no vector DB.
- **Maps → leads.** `/scrape/google-maps/search` returns business websites and phones. Apply opt-out, rate, and privacy-law constraints before any outreach use.
- **Crawler → corpus.** `crawler` Scraper Job with `outputFormat: ["markdown"]` + `includePaths: "/docs/.+"` produces an LLM-ready corpus in one submission.
- **Pre-extracted via SERP rich snippets.** `knowledgeGraph`, `localResults`, `inlineShoppingResults`, `relatedQuestions` carry pre-parsed public facts. Always check them before considering direct page access.

## Reference Loading Guide

Load these files **on demand** — when the user's request maps to a specific vertical or pattern:

| Reference file | Load when… |
|---|---|
| `references/web-scraping.md` | Using `POST /scrape/web` — parameters, JS scenarios, AI extraction, cookie auth. |
| `references/search.md` | Google SERP / Light / AI Mode / News / Shopping / Bing / Trends + pagination. |
| `references/ecommerce.md` | Amazon (product, search, seller, seller-products) and Shopify. |
| `references/real-estate.md` | Zillow, Redfin (bracketed filters). |
| `references/travel.md` | Airbnb, Booking, Google Flights (occupancy rules, token pagination, IATA codes). |
| `references/local-business.md` | Maps (search/place/reviews/photos/posts), Yelp, YellowPages. |
| `references/jobs.md` | Indeed and Glassdoor. |
| `references/youtube.md` | YouTube search / video / channel / transcript. |
| `references/scraper-jobs.md` | Async submit/poll/results, Crawler, Contacts, SEC EDGAR, webhook receiver. |
| `references/code-recipes.md` | Ready-to-paste Python and TypeScript clients with retry, backoff, bounded concurrency, and the full job lifecycle. |

## Wiring from Code

- **Auth:** `x-api-key` header on every request. Read from `HASDATA_API_KEY` env. Never hardcode, never log.
- **Timeouts:** Set client timeout **≥ 300 s**. HasData's own deadline is 300 s; shorter clients produce phantom failures while still being billed on completion.
- **Retries:** `429` and `5xx` only — exponential backoff with jitter. **Never retry `4xx`** (auth, validation).
- **Concurrency:** Cap at your plan limit. The free tier is **1**; anything higher just generates `429`s.
- **Async jobs:** Handle is `body.id` (integer), not `jobId`. Poll `GET /scrapers/jobs/<id>` every 10–30 s. Webhooks are best-effort; always pair with polling. Download result URLs immediately on `finished`.

See `references/code-recipes.md` for complete Python and TypeScript client implementations.

## Pitfalls

- **300 s server deadline.** Match your client timeout to at least 300 s. Shorter timeouts cause phantom failures while still being billed.
- **`requestMetadata.status === "ok"` is the only success signal.** HTTP 200 alone is not enough — always check the metadata status field.
- **Disable `jsRendering` first.** Enable only if the page needs it — most static pages parse fine without a headless browser. Rendering costs more and is slower.
- **No `cookies` parameter.** Cookies go through `headers["Cookie"]`, not a top-level field.
- **`includePaths` regex is case-sensitive.** `/blog/.+` will not match `/Blog/...`.
- **Scraper Job `data` is double-wrapped.** Each row is `body.data[i].data`; the outer wrapper carries `id`, `jobId`, `dataId`, `createdAt`, `updatedAt`.
- **Async job handle is `body.id` (integer), not `jobId`.** Persist it immediately after submit.
- **Webhooks are best-effort with 3 retries.** Always have a polling fallback.
- **Concurrency cap.** Free tier is 1 concurrent request. Exceeding your plan limit generates `429`s.
- **Never retry `4xx`.** `401` = invalid key, `403` = quota exhausted, `429` = concurrency cap. Only `429` and `5xx` are retryable.
- **Result URLs are short-lived.** Download `csv`/`json`/`xlsx` URLs immediately on job `finished`.

## Verification

1. **API key validity** — run the smoke test and confirm `requestMetadata.status === "ok"`:

   ```powershell
   curl -G 'https://api.hasdata.com/scrape/google/serp' `
     --data-urlencode 'q=test' `
     -H "x-api-key: $env:HASDATA_API_KEY"
   ```

   Expected output contains: `"status": "ok"`.

2. **Error code mapping** — verify you handle each correctly:

   | HTTP | Meaning | Retry? |
   |---|---|---|
   | `401` | Invalid key | No |
   | `403` | Quota exhausted | No |
   | `429` | Concurrency cap | Yes (backoff) |
   | `500` | Server error | Yes (backoff) |

3. **Async job lifecycle** — after `POST /scrapers/<slug>/jobs`, verify:
   - Response contains `id` (integer) — not `jobId`.
   - `GET /scrapers/jobs/<id>` eventually returns status `finished`.
   - `data.csv`, `data.json`, or `data.xlsx` URLs are present and downloadable.

4. **Client timeout** — confirm your HTTP client timeout is set to **≥ 300 s**.

## Resources

- Sitemap: <https://docs.hasdata.com/llms.txt>
- API status codes: <https://docs.hasdata.com/api-codes>
- Credits & concurrency: <https://docs.hasdata.com/credits-and-concurrency>
- Dashboard: <https://app.hasdata.com>

## Limitations

- Requires access to HasData services and valid credentials.
- Data quality and available fields depend on the target website and extraction method used.
- JavaScript-heavy websites may require rendering, which can affect performance and cost.
- Use only for public data or content the user is authorized to access; respect site terms, robots/access controls, privacy law, and rate limits.
- Rate limits, quotas, and account restrictions may apply depending on the endpoint and subscription plan.
