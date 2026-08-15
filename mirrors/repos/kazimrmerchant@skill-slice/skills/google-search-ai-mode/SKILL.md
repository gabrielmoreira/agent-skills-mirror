---
name: google-search-ai-mode
description: "Drives Google Search AI Mode (google.com/ai) in the browser: Deep Search cited multi-page reports, Search Labs agentic tasks such as reservations, and Ultra information agents. Use when the user wants a Search-grounded cited report or those agentic/monitor tasks. Not for Gemini App Deep Research, NotebookLM over uploaded docs, or free-tier Deep Search outside US/English Pro/Ultra."
version: 1.0.1
---

# AI Mode in Google Search (google.com/ai)

The AI Mode tab runs full Gemini reasoning over live web retrieval. Its standout is **Deep Search**: browse hundreds of sites → a fully-cited, multi-page report in ~2–5 min, saved in AI Mode history.

**Before doing anything in this skill, read `google-ai-ultra/reference.md` first.** That reference file contains account-tier requirements, regional restrictions, and Labs opt-in details that gate every mode below.

## When to Use

Route here when the user wants:

- A **fast, Search-grounded, citation-heavy research report** (Deep Search).
- **Agentic Search tasks** such as restaurant reservations.
- **Background monitoring** via information agents ("keep me updated on…", "alert me when…").

This skill **complements** — not replaces — `gemini-app` Deep Research and `notebooklm`. Prefer `gemini-app` Deep Research for longer-form, non-search-grounded synthesis. Prefer `notebooklm` for source-grounded Q&A over user-uploaded documents.

### Hard requirements

- **Web & App Activity must be ON** in the Google Account. Without it, AI Mode and Deep Search will not function.
- **Deep Search** is restricted to **US region, English language, Google AI Pro/Ultra** subscribers. It is not available on free tiers.
- **Agentic capabilities** require opt-in via **Search Labs**.
- **Information agents** require **Google AI Ultra**.

## Prerequisites

1. A Google account with **AI Pro or Ultra** subscription (for Deep Search).
2. **Web & App Activity** enabled: Google Account → Data & privacy → Web & App Activity → ON.
3. Browser automation MCP tools available (`browser_navigate`, `browser_snapshot`, `browser_type`, `browser_click`, `browser_wait_for`, `browser_evaluate`, `browser_take_screenshot`).
4. Read `google-ai-ultra/reference.md` before first use — it documents tier gating, Labs opt-in steps, and regional checks.

## Modes

| Mode | Requirement | Use |
|---|---|---|
| **Deep Search** | Pro/Ultra, US, English | Select after a query → hundreds of sites → cited report |
| **Agentic capabilities** | Search Labs opt-in | Restaurant reservations and similar action-taking tasks |
| **Information agents** | Ultra | "keep me updated on…" / "alert me when…" → background monitor |

## Procedure

### Deep Search report (core path)

1. **Navigate to AI Mode.**
   ```
   browser_navigate → https://www.google.com/ai
   ```

2. **Snapshot the page** to find the AI Mode query box.
   ```
   browser_snapshot
   ```

3. **Type the complex research query** and submit.
   ```
   browser_type → <query text>, submit=true
   ```

4. **Snapshot the response area** to locate the **Deep Search** option near the response.
   ```
   browser_snapshot
   ```

5. **Click Deep Search.**
   ```
   browser_click → Deep Search option
   ```

6. **Wait for the report.** Deep Search runs 2–5 minutes server-side.
   ```
   browser_wait_for(time=120)
   ```

7. **Poll until complete.** Repeat snapshot + wait cycles (up to ~3×) until the report is fully rendered and the status leaves "Searching…".
   ```
   browser_snapshot
   browser_wait_for(time=60)
   ```
   Repeat up to 3 times.

8. **Extract the report text.** Target the report container identified in the snapshot.
   ```
   browser_evaluate → () => document.querySelector('[role="main"]')?.innerText
   ```
   Adjust the selector to match the actual report container from the snapshot.

9. **Extract citations.** Scope to the report region to reduce noise.
   ```
   browser_evaluate → () => [...document.querySelectorAll('a[href^="http"]')].map(a => ({ text: a.innerText, href: a.href }))
   ```
   Filter the result by domain, dropping nav/footer links.

10. **Optional: take a screenshot** for a visual record.
    ```
    browser_take_screenshot
    ```

### Agentic capabilities (reservations, etc.)

1. Ensure **Search Labs** opt-in is active for the account (see `google-ai-ultra/reference.md`).
2. `browser_navigate` → `https://www.google.com/ai`
3. `browser_snapshot` → find the query box.
4. `browser_type` a task-oriented query (e.g., "Book a table at [restaurant] for [time]"), `submit=true`.
5. `browser_snapshot` → look for agentic action prompts or reservation widgets.
6. Follow on-screen prompts via `browser_click` as needed.

### Information agents (Ultra only)

1. Confirm the account is **Ultra** tier.
2. `browser_navigate` → `https://www.google.com/ai`
3. `browser_type` a query that includes **"keep me updated on…"** or **"alert me when…"**, `submit=true`.
4. `browser_snapshot` → confirm the information agent was created and note its monitoring parameters.

## Pitfalls

- **No "Deep Search" option appears** → The account is not Pro/Ultra, or the region/language is not US/English. Report this to the user and fall back to `gemini-app` Deep Research.
- **"Web & App Activity is off"** → Direct the user to Google Account → Data & privacy → Web & App Activity → ON, then retry.
- **Report stuck after 5 minutes** → Deep Search completes server-side. Navigate to AI Mode **History** (`google.com/ai` → History) to find the finished report.
- **`browser_evaluate` returns null** → Selector drift. Always `browser_snapshot` first and target the report container's actual ref/role from the snapshot.
- **Citation array is huge or noisy** → Scope `querySelectorAll('a')` to the report node (not `document`) and filter by domain, dropping nav/footer links.
- **Agentic capabilities missing** → Search Labs opt-in may not be enabled. Check `google-ai-ultra/reference.md` for opt-in steps.
- **Information agents unavailable** → Requires Ultra tier; Pro and free tiers do not support this mode.

## Verification

Confirm success with these checks:

1. **Report content is substantive.** The extracted text is a multi-paragraph report with citation markers and a source list — not a single AI Overview blurb.
   ```
   browser_evaluate → () => document.querySelector('[role="main"]')?.innerText
   ```
   Verify the output length and structure.

2. **Citation array is non-trivial.** Expect dozens or more entries.
   ```
   browser_evaluate → () => [...document.querySelectorAll('a[href^="http"]')].map(a => ({ text: a.innerText, href: a.href }))
   ```
   Spot-check 2–3 `href` values resolve to real, live pages.

3. **Report is saved in history.** Navigate to AI Mode History and confirm the report appears for the query.
   ```
   browser_navigate → https://www.google.com/ai
   browser_snapshot → locate and click History
   browser_snapshot → confirm the Deep Search report is listed
   ```

## Related skills

- `gemini-app` — Deep Research for longer-form, non-search-grounded synthesis.
- `notebooklm` — Source-grounded Q&A over user-uploaded documents.
- `google-ai-ultra` — Read `google-ai-ultra/reference.md` for tier gating, Labs opt-in, and regional requirements that apply to this skill.
