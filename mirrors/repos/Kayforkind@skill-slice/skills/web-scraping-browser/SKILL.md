---
name: web-scraping-browser
description: "Scrapes JS-rendered pages with Hermes browser_* + CDP: navigate, snapshot, interact, extract JSON from the live DOM after static fetch fails. Use when a SPA, login wall, infinite scroll, or click-to-reveal hides data from HTTP fetch. Not for Playwright E2E suites (browser-automation), owned-Chrome research/screenshots (chrome-browser-automation), or CAPTCHA/anti-bot bypass."
version: 1.0.1
alwaysApply: false
---

# Web Scraping with the Browser (Hermes `browser_*` + CDP)

Static fetching gets you the HTML the server sends. The browser gets you the DOM the user sees. This skill is the playbook for the second one.

## When to Use

Reach for `browser_navigate` instead of a static fetch when any of these hold:

| Signal | Why static fails |
|---|---|
| SPA (React/Vue/Next CSR) | Server returns an empty `<div id="root">`; data arrives via XHR after JS runs |
| Login / auth-gated content | Cookies + session state live in the real browser profile |
| Infinite scroll / lazy load | Content doesn't exist in the DOM until scrolled into view |
| Click-to-reveal (tabs, accordions, "Load more") | Content is behind an interaction, not a URL |
| Anti-bot that fingerprints the client | Real Chrome with a real profile passes; `requests`-style fetches get 403/challenge pages |
| Canvas / dynamically-built tables | Data only materializes in the live DOM (or needs a screenshot + vision) |

**Escalation path — always cheapest first:**

1. Static fetch / `web_extract` on the URL.
2. Result empty, or body is just `<script>` tags and an app shell? → `browser_navigate(url)` + `browser_snapshot`.
3. Snapshot shows the content? Extract via `browser_console` (§Procedure, step 3).
4. Content requires being signed in? → CDP-attached signed-in session (§Procedure, step 5).
5. Content is visual-only (canvas, chart image)? → screenshot + `vision_analyze` (§Procedure, step 8).

Do **not** start at step 4. The signed-in browser is the escalation of last resort, not the default.

## Prerequisites

- **Hermes browser tools** (`browser_navigate`, `browser_snapshot`, `browser_console`, `browser_click`, `browser_type`, `browser_press`, `browser_scroll`, `browser_get_images`, `browser_dialog`, `browser_cdp`) must be available in the current session.
- **For signed-in scraping:** the browser-hub Chrome must be running — the persistent instance with real user profiles at `~\Chrome\UserData`, exposed on CDP `http://127.0.0.1:9222`. Verify it is up before attempting auth-gated work.
- **For Playwright-over-CDP:** the on-demand `playwright` MCP must be enabled (enable script + reload if needed).
- **Windows host is primary.** Commands and paths assume PowerShell on Windows. Path `~\Chrome\UserData` is the hub's Chrome user-data directory — do not repoint or duplicate it.

## Procedure

### Step 1 — Core loop: navigate → snapshot → locate → act → re-snapshot → extract

Every browser scrape follows the same five-beat loop:

```
navigate → snapshot → locate (@ref or selector) → act (click/type/press/scroll) → re-snapshot → extract
```

**Concrete sequence — scrape a product listing behind a search form:**

```
browser_navigate("https://shop.example.com")
→ returns compact snapshot:
    textbox "Search products" @e3
    button "Search" @e4
    link "Sign in" @e7

browser_type(@e3, "mechanical keyboard")
browser_press("Enter")

browser_snapshot(full: false)
→ heading "Results for 'mechanical keyboard'"
    link "Keychron K8 Pro — $89" @e12
    link "NuPhy Air75 — $109" @e13
    button "Next page" @e29
```

Rules of the loop:

- **Every action invalidates refs.** `@e12` is only valid against the snapshot that produced it. After any `click`/`type`/`navigate`/`scroll`, re-snapshot before using refs again.
- `browser_snapshot(full: false)` (compact) for orientation and finding interactive elements; `browser_snapshot(full: true)` when you need to read page *content* from the accessibility tree.
- Prefer `browser_press("Enter")` in a focused search box over hunting for a submit button — one fewer ref to resolve.
- For bulk data extraction, don't parse the snapshot — the snapshot is for *navigation*. Extract with `browser_console` (Step 3), which returns clean JSON.

### Step 2 — Verify the page loaded and rendered

Never assume load-complete after `browser_navigate` returns. Poll a condition before extracting:

**Poll for an element (the workhorse):**

```
browser_console("!!document.querySelector('.results-grid .card')")
→ false … re-issue after a beat … → true → proceed to extract
```

**Poll for a data sentinel** (element exists but is a skeleton/spinner):

```
browser_console(`
  (() => {
    const el = document.querySelector('.price');
    return el && !el.closest('[class*="skeleton"]') && /\d/.test(el.innerText);
  })()
`)
```

**Network/loader idle via CDP:**

```
browser_cdp("Runtime.evaluate", {
  expression: "document.readyState === 'complete' && !document.querySelector('[class*=\"spinner\"],[class*=\"loading\"]')",
  returnByValue: true
})
```

Cap every polling loop at ~10 attempts. If the sentinel never turns true: wrong selector, content is inside an iframe (Step 6), or the page errored — snapshot and look before retrying harder.

**Dialogs:** JS `alert`/`confirm`/`prompt` dialogs block everything until handled. If a snapshot or action stalls and the page has a pending dialog, resolve it:

```
browser_dialog(action: "accept")                       // or "dismiss"
browser_dialog(action: "accept", prompt_text: "yes")   // for prompt()
// equivalent raw CDP: browser_cdp("Page.handleJavaScriptDialog", { accept: true })
```

### Step 3 — Extract data via the page (`browser_console`)

`browser_console(expression)` evaluates JS in the page and returns the serialized result. This is your primary extraction tool — it reads the *live* DOM, including everything JS built after load.

**Golden rule: return plain JSON-serializable values.** No DOM nodes, no functions, no circular refs. Always `.map()` down to strings/numbers/plain objects.

**Pull a table:**

```
browser_console(`
  JSON.stringify([...document.querySelectorAll('table.results tbody tr')].map(tr => {
    const c = tr.querySelectorAll('td');
    return {
      name:  c[0]?.innerText.trim(),
      price: c[1]?.innerText.trim(),
      link:  tr.querySelector('a')?.href ?? null
    };
  }))
`)
```

**Pull an article (SPA where web_extract saw nothing):**

```
browser_console(`
  JSON.stringify({
    title: document.querySelector('h1')?.innerText,
    byline: document.querySelector('[class*="author"], [rel="author"]')?.innerText ?? null,
    published: document.querySelector('time')?.getAttribute('datetime') ?? null,
    body: [...document.querySelectorAll('article p')].map(p => p.innerText).join('\\n\\n')
  })
`)
```

**Pull all links matching a pattern:**

```
browser_console(`
  JSON.stringify([...document.querySelectorAll('a[href*="/product/"]')]
    .map(a => ({ text: a.innerText.trim(), href: a.href }))
    .filter(x => x.text))
`)
```

**Images:** `browser_get_images()` returns `{url, alt}` for every `<img>` — use it before writing a custom console expression for images. Fall back to console only for `background-image`, `<picture>/srcset`, or lazy-load attributes:

```
browser_console(`
  JSON.stringify([...document.querySelectorAll('img[data-src], img[srcset]')]
    .map(i => i.dataset.src || i.currentSrc || i.src))
`)
```

Wrap complex returns in `JSON.stringify(...)` yourself — it guarantees serialization and survives odd objects (e.g., elements with custom `toJSON`). Escape newlines inside template strings you embed (`'\\n\\n'` as above).

**Extraction sanity check:** if the console expression returns `[]`, the selector is wrong OR the content hasn't rendered yet (Step 4). Debug with a counting probe first: `browser_console("document.querySelectorAll('table').length")`.

### Step 4 — Infinite scroll & lazy load

Two patterns, escalating:

**Pattern A — snapshot-count loop (simple feeds):**

```
browser_navigate("https://feed.example.com")
loop (max ~15 iterations):
  count = browser_console("document.querySelectorAll('[data-testid=\"post\"]').length")
  browser_scroll("down")
  browser_scroll("down")
  newCount = browser_console("document.querySelectorAll('[data-testid=\"post\"]').length")
  if newCount == count for 2 consecutive iterations → stop (feed exhausted or rate-limited)
extract everything in one console call
```

**Pattern B — scrollHeight plateau via CDP (precise, works when `browser_scroll` steps are too small):**

```
browser_cdp("Runtime.evaluate", {
  expression: "window.scrollTo(0, document.body.scrollHeight); document.body.scrollHeight",
  returnByValue: true
})
→ { result: { value: 14200 } }

// poll: repeat the same call; when value stops growing across 2–3 polls, you've hit bottom
browser_cdp("Runtime.evaluate", {
  expression: "window.scrollTo(0, document.body.scrollHeight); document.body.scrollHeight",
  returnByValue: true
})
→ { result: { value: 14200 } }   // plateau → done
```

Between scrolls, give lazy content a beat by polling a *sentinel* rather than sleeping (Step 2). If the site uses a "Load more" **button** instead of true infinite scroll, treat it as pagination (Step 7): snapshot → click `@ref` of the button → re-snapshot → repeat until the button disappears.

**Always extract after the loop, not per-iteration** — one `browser_console` over the fully-loaded DOM is cheaper and dedupes itself. Exception: virtualized lists (DOM recycles rows as you scroll — count stops matching what you saw). For those, extract per-iteration and dedupe by a stable key (href, id) in your accumulator.

### Step 5 — Auth & signed-in scraping

Signed-in scraping runs against the **browser-hub Chrome** — the persistent instance with real user profiles at `~\Chrome\UserData`, exposed on CDP `http://127.0.0.1:9222`.

**HARD RULES — non-negotiable:**

- **Attach, never launch.** `connectOverCDP("http://127.0.0.1:9222")`, then `browser.contexts()[0]`, then `context.newPage()`. Never `chromium.launch()`, never `browser.newContext()` — a fresh context has no cookies and defeats the entire point.
- **Never create or add a Chrome profile.** If Chrome shows an "Add profile" / "create profile" prompt, decline and stop — you attached wrong or the hub isn't running. Do not click through it.
- **Google SSO chooser:** when a site's "Sign in with Google" opens the account chooser, pick the identity per browser-hub rules for the task (flow vs grok identity) — never guess, never add an account.
- **Never point a self-launched Chrome at `~\Chrome\UserData`.** The hub owns that directory. Pointing your own launch at it causes profile-lock corruption. Attach over CDP instead.

**Playwright-over-CDP (via the on-demand `playwright` MCP — enable script + reload if needed):**

```python
browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
ctx = browser.contexts[0]          # THE existing signed-in context — do not create a new one
page = ctx.new_page()
page.goto("https://app.example.com/dashboard")
data = page.evaluate("() => [...document.querySelectorAll('.row')].map(r => r.innerText)")
page.close()                       # close your page; never close the browser/context
```

**Same thing with Hermes tools only** (browser tools already ride the hub session): just `browser_navigate("https://app.example.com/dashboard")` — if the profile is signed in, you're in. Verify auth state before scraping:

```
browser_console("document.cookie.length > 0 && !location.pathname.includes('/login')")
```

**Cookie reuse** — export session cookies to replay requests statically (much faster for bulk API scraping once you have the session):

```
browser_cdp("Network.getAllCookies", {})
→ { cookies: [ { name: "session_id", value: "...", domain: ".example.com", ... }, ... ] }
```

Filter to the target domain, build a `Cookie:` header, and hit the site's JSON API directly with static fetches. This hybrid (browser for auth, static for volume) is the fastest pattern for large authenticated scrapes. Treat exported cookies as credentials: keep them out of committed files and logs.

### Step 6 — Hard cases: Shadow DOM, iframes, captchas

**Shadow DOM** — `querySelectorAll` doesn't pierce shadow roots; walk them explicitly:

```
browser_console(`
  JSON.stringify((function collect(root, out = []) {
    root.querySelectorAll('*').forEach(el => {
      if (el.shadowRoot) collect(el.shadowRoot, out);
      if (el.matches('.item-title')) out.push(el.innerText.trim());
    });
    return out;
  })(document))
`)
```

Snapshots usually *do* surface shadow content (the accessibility tree pierces it), so refs from snapshots often still work for clicking — it's console extraction that needs the walker.

**Iframes** — same-origin iframes are reachable via `document.querySelector('iframe').contentDocument`. Cross-origin iframes are not; take the `frame_id` from the snapshot and target the frame directly:

```
browser_cdp("Runtime.evaluate",
  { expression: "JSON.stringify([...document.querySelectorAll('.row')].map(r => r.innerText))", returnByValue: true },
  frame_id: "<frame_id from snapshot>")
```

If you need the frame's own targets: `browser_cdp("Target.getTargets", {})` and match by URL, then pass `target_id`.

**Captchas / challenge pages** — do not attempt to solve or bypass captchas programmatically. Legitimate options: (a) escalate to the signed-in browser-hub session, where an established profile + cookies usually means the challenge never fires; (b) navigate in the visible browser and let the human user clear it once, then continue in the same session; (c) stop and report if the site's ToS prohibits automated access. Respect robots/ToS — a challenge is the site saying no.

### Step 7 — Pagination buttons

```
loop:
  browser_snapshot(full: false)          // fresh refs every iteration — mandatory
  extract this page via browser_console  // paginated DOMs replace content, so extract per-page
  find button "Next" @eNN in THIS snapshot
  if absent or disabled → done
  browser_click(@eNN)
  poll sentinel for new page content (Step 2 — e.g. first-row text changed)
```

### Step 8 — Device/viewport emulation (mobile-only content)

```
browser_cdp("Emulation.setDeviceMetricsOverride",
  { width: 390, height: 844, deviceScaleFactor: 3, mobile: true })
```

### Step 9 — Save with provenance

Every scrape ends with a **provenance-stamped artifact**. Extracted-but-unverified data is a liability.

Save JSON with source metadata, not bare arrays:

```json
{
  "source_url": "https://shop.example.com/search?q=mechanical+keyboard",
  "scraped_at": "2026-07-15T14:32:00Z",
  "method": "browser_console querySelectorAll('.card')",
  "record_count": 48,
  "records": [ ... ]
}
```

Report honestly: if 3 of 48 records have null prices, say so in the artifact and the summary — don't silently drop them.

## Pitfalls

1. **Stale refs.** `@e12` belongs to one snapshot. Any navigate/click/type/scroll → re-snapshot before the next ref-based call. Symptom: "ref not found" or clicking the wrong element.
2. **Scrolling without re-snapshotting.** New content after scroll is invisible to your old snapshot. Scroll → snapshot → then act.
3. **Launching Chrome for authenticated work.** Signed-in scraping = attach to `http://127.0.0.1:9222` + `contexts()[0]` + `newPage()`. `launch()` / `newContext()` = fresh, logged-out, fingerprint-suspicious browser.
4. **Touching Chrome's default User Data dir with your own launch.** The hub owns `~\Chrome\UserData`. Never point a self-launched Chrome at it (profile-lock corruption); attach over CDP instead.
5. **Clicking "Add profile" / "create profile" in Chrome.** Never. That prompt means you're in the wrong place — stop and re-attach.
6. **Non-serializable console returns.** Returning DOM nodes/NodeLists/functions from `browser_console` yields `{}` or garbage. Always map to plain data and `JSON.stringify` it; escape embedded newlines (`'\\n'`).
7. **Extracting before render.** `[]` from a correct-looking selector usually means "too early", not "no data". Poll a sentinel (Step 2); never assume load-complete after navigate returns.
8. **Parsing the snapshot as your dataset.** Snapshots are lossy, truncated, formatted for navigation. Bulk data comes from `browser_console` → JSON. Snapshot = eyes; console = hands.

## Verification

Every scrape must pass at least the first two of these three checks:

1. **Count check:** does `record_count` match what the page claims ("48 results")? Read the claim off the page:
   ```
   browser_console("document.querySelector('.results-count')?.innerText")
   ```
   Compare the returned text to your `record_count`. Mismatch = selector drift or missing pages.

2. **Sample cross-check:** take 2–3 random records and confirm they appear in a fresh `browser_snapshot(full: true)` — this catches selector drift where you scraped the wrong nodes (e.g., sponsored placements instead of results).

3. **Visual confirmation:** screenshot the page and `vision_analyze` it against a sample of your data ("does this screenshot show a product 'NuPhy Air75' at $109?"). This is the only check that catches *rendering* mismatches — CSS-hidden elements, overlapped content — that DOM extraction happily scrapes anyway.

**Quick verification commands:**

| Check | Command | Expected |
|---|---|---|
| Auth state | `browser_console("document.cookie.length > 0 && !location.pathname.includes('/login')")` | `true` |
| Element exists | `browser_console("!!document.querySelector('.results-grid .card')")` | `true` |
| Row count | `browser_console("document.querySelectorAll('table.results tbody tr').length")` | Matches page claim |
| Render complete | `browser_cdp("Runtime.evaluate", { expression: "document.readyState === 'complete'", returnByValue: true })` | `{ result: { value: true } }` |
| Hub reachable | `browser_cdp("Target.getTargets", {})` | Returns target list (confirms CDP `127.0.0.1:9222` is live) |

## Quick reference

| Task | Call |
|---|---|
| Load page + get refs | `browser_navigate(url)` |
| See page / refresh refs | `browser_snapshot(full: false)`; `full: true` for content |
| Interact | `browser_click(@ref)` / `browser_type(@ref, text)` / `browser_press("Enter")` |
| Scroll | `browser_scroll("down")`, or CDP `window.scrollTo` for scroll-to-bottom |
| Extract data | `browser_console("JSON.stringify([...document.querySelectorAll(sel)].map(...))")` |
| All images | `browser_get_images()` |
| Handle dialog | `browser_dialog(action: "accept" \| "dismiss")` |
| Cookies out | `browser_cdp("Network.getAllCookies", {})` |
| Cross-origin iframe | `browser_cdp("Runtime.evaluate", {...}, frame_id: <from snapshot>)` |
| Mobile viewport | `browser_cdp("Emulation.setDeviceMetricsOverride", {...})` |
| Signed-in session | attach `127.0.0.1:9222` → `contexts()[0]` → `newPage()` — never launch, never new context, never "Add profile" |
