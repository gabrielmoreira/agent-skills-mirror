---
name: universal-web-adaptation
description: Use this skill when asked to work with an unfamiliar public website and the goal is to make progress generically before writing site-specific rules. It teaches Copilot how to probe controls, classify UI patterns, try multiple search and navigation strategies, follow popups, and only create a site profile when the generic approach is no longer sufficient.
license: Proprietary session artifact for local Copilot use
---

# Universal web adaptation skill

Use this skill when the user wants a **general solution across many websites**, not a one-by-one manual integration first.

This skill is especially suitable for:

- unfamiliar public websites
- search-oriented workflows
- result-page collection and lightweight summaries
- deciding whether a site needs a dedicated profile or can stay generic

For the `99idea` Playwright project, this skill should work together with:

- `src\run-demo.js`
- `src\planner.js`
- `src\llm-planner.js`
- `src\site-profiles.js`
- `scenarios\site-profiles.json`

## Core principle

Always try this order:

1. **Capability discovery** — check if opencli already supports the site (`opencli list`)
2. **Auth cascade** — classify: PUBLIC → COOKIE/SESSION → HEADER → LOGIN-GATED
3. **Generic adaptation** — probe UI controls and try heuristic strategies
4. **Temporary scenario tuning** — adjust runtime before assuming selectors are wrong
5. **Popup / opener / alternate-submit handling**
6. **Site profile only if generic adaptation still fails**

The goal is to minimize per-site handwork.

### Execution path decision (inspired by opencli)

Before touching the DOM, first determine which execution layer to use:

```text
if opencli has an adapter for this site:
    use opencli (zero LLM cost, deterministic)
elif the site has a public API:
    use fetch (structured data, no rendering)
elif the site renders server-side (SSR):
    use web_fetch or Playwright (metadata extraction)
else:
    use Browser Agent with login-state or mark blocked
```

This avoids wasting time on SPA shells that will never yield results via scraping.

## What “generic adaptation” means

When facing a new site, do not immediately create a profile. First try to discover:

- likely search inputs
- likely opener buttons or icons
- likely submit controls
- whether Enter works
- whether a click opens a popup or new tab
- whether the site verifies best by URL, title, or visible text

## Standard workflow

### 1. Probe the page

Collect candidates for:

- inputs
- buttons
- anchors
- role=button
- role=search

Prefer candidates whose metadata includes:

- `search`
- `query`
- `find`
- `搜索`
- `查找`

For each candidate, record:

- visibility
- enabled/editable status
- approximate position
- container context
- whether duplicates exist in header/footer/overlay regions

### 2. Classify the site UI

Put the site into one of these buckets:

- **direct-search**: visible input plus obvious submit
- **opener-search**: search exists but must be opened first
- **popup-search**: submit opens a new tab or popup
- **duplicate-controls**: multiple matching controls require container qualification
- **hidden-disabled**: search exists but is not immediately usable
- **SPA-shell**: page returns JS-only content, no usable DOM without full rendering
- **login-gated**
- **anti-bot / rate-limited**

### Auth cascade classification (from opencli)

Also classify the site's auth requirements:

- **PUBLIC**: no auth needed, fetch/web_fetch works
- **COOKIE**: requires browser session cookies (opencli Browser Bridge)
- **HEADER**: requires custom auth headers (API key, Bearer token)
- **LOGIN-GATED**: requires interactive login, not suitable for default regression

### 3. Try generic action strategies

Try these in order:

1. fill visible search input + press Enter
2. fill visible search input + click nearest likely submit
3. if search is hidden, click likely opener then retry 1 and 2
4. if click or Enter opens a popup, switch to the popup and continue there
5. verify success by:
   - URL change
   - expected URL parameter
   - title change
   - visible result container text

Prefer URL verification whenever available.

### 4. Use temporary runtime tuning before giving up

If the page is heavy or slow:

- use `waitUntil: "domcontentloaded"`
- use `postNavigationLoadState: "domcontentloaded"`
- add a settle delay

Do not assume selectors are wrong if the real problem is heavy page load behavior.

### 5. Decide whether to keep it generic or create a profile

Stay generic if:

- the search flow works with robust heuristic selectors
- the same logic is likely reusable across many sites

Create a dedicated profile only if:

- the site needs exact selectors to avoid ambiguity
- the site has duplicate controls in multiple containers
- the site needs a stable popup-specific submit selector
- the site has a unique opener pattern worth remembering

## Failure classification rules

### Strict mode violation

Meaning:

- your selector is too broad
- multiple header/footer/overlay controls match

Response:

- add container-qualified selectors
- prefer the visible and nearest control to the active search region

### Timeout waiting for visible/editable

Meaning:

- the control is hidden
- disabled
- off-screen
- not opened yet

Response:

- find and click the opener
- retry with a container-specific visible control

### Enter does nothing

Meaning:

- the page requires a dedicated submit control
- or the form uses JS-driven submission

Response:

- inspect nearest clickable sibling/container controls
- test the likely submit node

### Search opens a new tab/popup

Meaning:

- current-page URL checks will fail

Response:

- switch the active page to the popup
- continue verification and screenshot on the popup page

### Login / anti-bot / rate-limit

Meaning:

- the site is not a good candidate for stable default regression

Response:

- mark blocked or special
- do not force it into the generic stable matrix

## Output expectations

When using this skill, the agent should produce:

1. **execution path recommendation**: opencli / fetch / browser — and why
2. **auth cascade classification**: PUBLIC / COOKIE / HEADER / LOGIN-GATED
3. the site UI classification
4. the generic strategy attempted
5. whether generic adaptation succeeded
6. whether a site profile is actually needed
7. the final stable selectors or blocker reason

Also include explicit evidence lines when possible:

- URL before/after
- title before/after
- the selector used for input and submit
- whether popup-following was required

## Proven lessons from this environment

- **CNN** needed container-qualified selectors to avoid duplicate `q` inputs.
- **Bilibili** needed popup-following behavior because search opens `search.bilibili.com` in a new tab.
- **BBC** exposes a hidden and disabled search input, so generic probing alone is not enough yet.
- **Tencent News** shows a visible search button but no directly usable input in the default state.
- **GitHub** works, but is a low-frequency special case because of rate limits.

## When to combine with other skills

- Use `external-site-profile-learning` when generic adaptation fails and a durable site profile is needed.
- Use `content-search-summarization` when the goal is to search a content platform and summarize the top results.

## Practical rule of thumb

If a new site can be made to work by:

- picking the right visible input
- picking the right nearby submit
- following a popup
- using URL verification

then keep it in the **generic** path first.

If success depends on an exact remembered selector or a unique UI ritual, then promote it into a **site profile**.
