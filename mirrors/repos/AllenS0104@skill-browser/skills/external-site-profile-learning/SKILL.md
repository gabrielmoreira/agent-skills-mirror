---
name: external-site-profile-learning
description: Use this skill when investigating, adding, validating, or debugging external website profiles for the 99idea Playwright browser demo. It teaches how to probe selectors, classify failure modes, add config-driven profiles, and validate both heuristic and Gemini flows.
license: Proprietary session artifact for local Copilot use
---

# External site profile learning skill

Use this skill when working on the target Playwright browser project (for example, the `99idea` demo project).

This project is a Playwright-based browser demo that supports config-driven external site profiles through:

- `scenarios\site-profiles.json`
- `src\site-profiles.js`
- `src\planner.js`
- `src\llm-planner.js`
- `src\run-demo.js`

## What this skill is for

Use this skill when the task involves any of the following:

- adding a new external site profile
- debugging why an external site passes heuristics but fails with Gemini
- turning a random website experiment into a stable config-driven profile
- identifying whether a site is suitable for the default regression matrix
- distinguishing selector problems from login, anti-bot, or hidden-UI problems

## Core rules

1. Prefer **URL** or **title** verification for external sites whenever possible.
2. Prefer **stable, unique selectors** over generic selectors like `button` or `[name="q"]`.
3. If a site profile exists, the final plan should use the profile's **exact** `searchInputSelector` and `submitSelector`.
4. Keep GitHub out of the default regression matrix. It works, but repeated probing can trigger rate limits.
5. **Classify the site's execution tier before writing a browser profile:**
   - If opencli already supports the site, prefer an opencli-based workflow over a selector-based profile
   - If the site has a public API, prefer fetch over browser automation
   - Only write a browser profile when no higher-tier execution path exists
6. Treat these as different failure classes:
   - selector ambiguity
   - hidden or disabled controls
   - opener-required search UI
   - SPA shell (no usable DOM without full JS rendering)
   - login gates
   - anti-bot / rate-limit behavior
   - heavy pages that stall on `load`

### Dual-engine awareness (inspired by opencli)

When stabilizing a site, consider whether the profile should be:

- **Data-only (YAML-like)**: selector + verification config in JSON — for traditional DOM-based sites
- **Runtime-aware**: includes execution path recommendation (opencli / fetch / browser) — for modern platforms

A good profile should record not just *how to interact with the UI*, but also *what the best execution path is*.

## Standard workflow

### 1. Probe the site

Open the homepage in Playwright and inspect:

- search inputs
- submit buttons
- search opener buttons or icons
- whether inputs are visible, enabled, and editable
- whether there are duplicate controls in headers, footers, drawers, or overlays

Record:

- selector candidates
- whether search is immediately usable
- whether search is hidden/disabled until another action happens
- whether the site supports a deterministic URL check after search

### 2. Classify the site

Use this decision process:

- If a visible input and a stable submit control exist, the site is a good normal profile candidate.
- If the site requires an opener interaction but still fits the current action model, prefer a more specific selector strategy or a special-case scenario.
- If the site requires behavior beyond the current action model, mark it blocked or incomplete rather than forcing a brittle profile.
- If the site is gated by login or aggressively rate-limited, do not add it to the default regression matrix.

### 3. Add the profile

When the site is a good fit, add a data-only profile to `scenarios\site-profiles.json` with:

- `name`
- `hostnames`
- `searchInputSelector`
- `submitSelector`
- `verificationMode`
- `expectedUrlTemplate` when URL verification is available
- `executionTier` — recommended execution path: `opencli`, `fetch`, or `browser`
- `opencliCommand` — if opencli supports it, the exact command template
- `authLevel` — `PUBLIC`, `COOKIE`, `HEADER`, or `LOGIN-GATED`

Keep the behavior in code and the site data in JSON.

Recommended profile-writing rules:

- use exact selectors, not broad selectors that only happen to work once
- qualify selectors with a container when header and footer controls are duplicated
- prefer `verificationMode: "url"` when the site has a deterministic query string
- prefer `verificationMode: "title"` when the search result page has a stable title change
- do not force opener-only or login-gated flows into a normal default profile

### 4. Validate both planning modes

Validate in this order:

1. Heuristic run
2. Gemini / LLM run

Use commands like:

```powershell
npm run validate:external:core
npm run validate:external:popup
npm run validate:external:heavy
npm run validate:external
npm run validate:external:llm:core
npm run validate:external:llm:popup
npm run validate:external:llm:heavy
npm run validate:external:llm
node src\run-demo.js --allow-external --url "https://example.com/" --goal "Search Example for AI and verify that the URL includes q=AI."
node src\run-demo.js --scenario <temp-scenario.json> --planner llm
```

Before Gemini validation, ensure:

- `GEMINI_API_KEY` is available
- `BROWSER_USE_LLM_PROVIDER=gemini`

If the site hangs on full load, use a temporary scenario with:

- `waitUntil: "domcontentloaded"`
- `postNavigationLoadState: "domcontentloaded"`

### 5. Record the failure mode if it does not fit

Use these interpretations:

- **strict mode violation / multiple matches**  
  The selector is too broad. Add a stronger container-qualified selector.

- **timeout waiting for visible or editable**  
  The control is hidden, disabled, off-screen, or not opened yet.

- **type succeeds but Enter does not navigate**  
  The site likely needs a specific submit control instead of Enter.

- **works only with a special opener path**  
  Consider a special scenario instead of a default profile.

- **rate limit / anti-bot / login gate**  
  Do not force it into the stable regression matrix.

## Known good profiles

These are already proven patterns in this project:

### Wikipedia

- input: `#searchInput`
- submit: `#search-form button[type="submit"]`
- verification: title

### Python.org

- input: `#id-search-field`
- submit: `#submit`
- verification: URL contains `q={searchTerm}`

### arXiv

- input: `form.mini-search input[name="query"]`
- submit: `form.mini-search button`
- verification: URL contains `query={searchTerm}`

### YouTube

- input: `input[name="search_query"]`
- submit: `button.ytSearchboxComponentSearchButton`
- verification: URL contains `search_query={searchTerm}`

### CNN

- input: `#pageFooter input[name="q"]`
- submit: `#pageFooter button.search-bar__submit`
- verification: URL contains `q={searchTerm}`
- runtime hint: prefer `domcontentloaded` because the homepage may stall on full `load`

### Bilibili

- input: `#nav-searchform input.nav-search-input`
- submit: `#nav-searchform .nav-search-btn`
- verification: URL contains `keyword={searchTerm}`
- runtime hint: the search flow opens a popup / new tab, so popup following must remain enabled in the runner

## Special case

### GitHub

GitHub works through the search palette, but repeated probing can trigger secondary rate limits.

Recommended pattern:

1. click `button[aria-label="Search or jump to…"]`
2. type into `#query-builder-test`
3. press `Enter`
4. verify URL contains `q={searchTerm}`

Do not treat GitHub as a normal default regression target.

## Blocked or incomplete sites

### BBC

- current state: blocked
- reason: the discovered input is hidden and disabled until additional UI state changes occur

### Tencent News

- current state: blocked
- reason: the homepage shows a search button but no directly usable search input in the default state

### Zhihu

- current state: blocked
- reason: homepage flow goes through sign-in, so anonymous search is not a clean default regression target

## Implementation notes for future agents

- When a profile exists, normalize LLM-generated `type` and `click` steps back to the exact profile selectors.
- If a site has duplicate header/footer search controls, prefer container-qualified selectors.
- If an external site is flaky under full page load, fix the runtime first before assuming the selectors are wrong.
- Keep default validation conservative. A smaller stable matrix is better than a noisy one.
- Use grouped validation runs to isolate profile regressions by class: `core`, `popup`, and `heavy`.
- For each validation report, include concrete evidence (URL/title signal, selector used, and whether popup switching occurred).
