---
name: gemini-workspace
description: "Drives the Gemini side panel inside Gmail, Docs, Sheets, Slides, and Drive via browser automation: thread summaries, Help me write drafts, Sheets =AI(), Slides images, and questions about Drive files. Use when Gemini should act on live Workspace content rather than the standalone Gemini app. Trigger: Gemini Workspace, Gmail summarize, =AI() Sheets. Not for Google Vids, cinematic Veo/Flow, or accounts without the Ask Gemini icon."
version: 1.0.1
---

## Overview

The Gemini side panel operates on the user's **live Workspace files**. Open it with the Gemini spark/star icon (tooltip **Ask Gemini**) in the top-right of Gmail/Docs/Sheets/Slides/Drive. This skill covers driving that panel via browser automation (MCP tools). Use this skill — not the standalone `gemini-app` skill — when the task is *about* the user's own mail/docs/sheets/slides.

On Google AI Ultra, the Workspace side panel has the highest usage limits.

## When to Use

- User wants to **summarize a Gmail thread** or ask "what needs my response?"
- User wants **"Help me write"** to draft or refine content in Docs or Gmail
- User wants the **`=AI()` function** in Sheets for classification, extraction, or generation over cell ranges
- User wants to **generate images** or draft slide text in Slides
- User wants to **ask about a Drive file** (including PDFs/docs) without opening it
- User explicitly mentions "Gemini in Gmail/Docs/Sheets/Slides/Drive" or "Gemini side panel"

## Prerequisites

1. **Eligible Google AI or Workspace plan** — the Gemini side panel requires a qualifying subscription (e.g., Google AI Ultra, Gemini for Workspace). If the spark icon is absent, the account likely lacks an eligible plan.
2. **Browser automation MCP server** — the canonical automation loop is defined in `google-ai-ultra/reference.md`. **Read that reference file first** before executing any browser steps in this skill.
3. **English-first AI features** — Gemini Workspace features are English-first; the surrounding UI may be localized, which can change button labels.
4. **Windows host (PowerShell)** is the primary environment. All paths and commands assume Windows unless noted.

## Procedure

### Step 0 — Load the MCP automation playbook

Before driving the side panel, read `google-ai-ultra/reference.md` for the canonical MCP browser-automation loop (navigate → snapshot → click → type → wait → evaluate). All subsequent steps assume familiarity with that playbook.

### Step 1 — Navigate to the target Workspace app

| App | URL |
|---|---|
| Gmail | `https://mail.google.com` |
| Docs | `https://docs.google.com` |
| Sheets | `https://sheets.google.com` |
| Slides | `https://slides.google.com` |
| Drive | `https://drive.google.com` |

```
browser_navigate → <app URL>
```

### Step 2 — Open or select the target content

- **Gmail**: `browser_snapshot` → find a long thread (row shows a "(N)" message count); `browser_click` it.
- **Docs**: Open the target document.
- **Sheets**: Open the target spreadsheet; select the cell where `=AI()` will be used.
- **Slides**: Open the target presentation; select the slide.
- **Drive**: Navigate to the folder containing the target file.

### Step 3 — Open the Gemini side panel

1. `browser_snapshot` → locate the top-right **Ask Gemini** spark/star icon.
2. Confirm the icon tooltip reads **"Ask Gemini"** (not Calendar or Meet) before clicking.
3. `browser_click` the icon to open the side panel.

The panel lives in a right-hand region with `role="complementary"`.

### Step 4 — Issue the request

Choose the appropriate action per app:

#### Gmail — Summarize a thread
1. `browser_snapshot` → click the **Summarize this email** chip if present.
2. If the chip is absent, `browser_type` into the panel's prompt box: `Summarize this email thread`, then `submit=true`.
3. `browser_wait_for` text=`"Summary"`.

#### Gmail / Docs — "Help me write"
1. `browser_snapshot` → click the **Help me write** chip or type the request in the panel prompt box.
2. For Gmail replies: type `Draft a reply to this email` and submit.
3. `browser_wait_for` the generated text to appear in the panel.

#### Sheets — `=AI()` function
1. In the target cell, type: `=AI("prompt", range)`
   - Example: `=AI("Categorize this as Positive, Neutral, or Negative", A2:A100)`
2. Press Enter; the function populates the cell range.
3. To ask Gemini to analyze or build formulas, type the request in the side panel prompt box.

#### Slides — Generate images / draft text
1. `browser_snapshot` → click the **Generate image** chip or type `Generate an image of <description>` in the panel prompt box.
2. For slide text: type `Draft slide text about <topic>` and submit.
3. `browser_wait_for` the generated content.

#### Drive — Ask about a file
1. Select the target file in Drive.
2. Open the Gemini side panel.
3. Type `Summarize this file` or `What is this file about?` in the panel prompt box; submit.
4. `browser_wait_for` the response.

### Step 5 — Extract results

```
browser_evaluate → () => document.querySelector('[role="complementary"]')?.innerText
```

This returns the full text content of the Gemini side panel, avoiding truncation that can occur in `browser_snapshot`.

## Capability Map

| App | URL | Capabilities |
|---|---|---|
| **Gmail** | `mail.google.com` | Summarize a thread, "Help me write" a reply/draft, ask "what needs my response?" |
| **Docs** | `docs.google.com` | "Help me write"/refine/rewrite, summarize, generate content in place |
| **Sheets** | `sheets.google.com` | `=AI("prompt", range)` function for classification/extraction/generation over cells; ask to analyze/build formulas |
| **Slides** | `slides.google.com` | Generate images from a prompt; draft slide text |
| **Drive** | `drive.google.com` | Ask about a file without opening it; summarize PDFs/docs |

## Worked Example — Summarize a Gmail Thread (Full MCP Sequence)

1. `browser_navigate` → `https://mail.google.com`
2. `browser_snapshot` → find a long thread (row shows a "(N)" message count); `browser_click` it.
3. `browser_snapshot` → find the top-right **Ask Gemini** spark icon; `browser_click` it to open the side panel.
4. `browser_snapshot` → click the **Summarize this email** chip. If absent, `browser_type` into the panel's prompt box: `Summarize this email thread`, `submit=true`.
5. `browser_wait_for` text=`"Summary"`.
6. Extract: `browser_evaluate` → `() => document.querySelector('[role="complementary"]')?.innerText`.

## Pitfalls

- **No spark icon visible** → the account lacks an eligible plan. Switch to an account with Google AI Ultra or Gemini for Workspace, or report the missing feature.
- **No "Summarize" chip** → type the request manually in the panel prompt box instead of relying on chips.
- **Summary truncated in `browser_snapshot`** → always extract via `browser_evaluate` returning `innerText` of the `[role="complementary"]` panel. Snapshots can cut off long responses.
- **"Ask Gemini" greyed or unresponsive** → the thread may be too short or still loading. Run `browser_wait_for(time=3)` and retry, or pick a thread with 3+ messages.
- **Panel spins forever** → wait, then re-snapshot. If still stuck, reload the page and reopen the thread.
- **Wrong panel opened (Calendar/Meet)** → always confirm the icon tooltip is **"Ask Gemini"** in the snapshot *before* clicking. Google Workspace apps have multiple top-right icons.
- **`=AI()` not recognized in Sheets** → ensure the spreadsheet is on an eligible account and the function is available in your region. English-first features may not be enabled for all locales.
- **Localized UI labels** — button and chip labels may differ from English defaults. Use `browser_snapshot` to read actual labels rather than assuming exact text.

## Verification

Confirm the side panel operation succeeded with these checks:

1. **Panel shows a Summary/Response heading** — the panel displays a **Summary** heading (or equivalent response heading) with text referencing real content details (senders, decisions, file names).
2. **Non-empty extraction** — `browser_evaluate` returns a non-empty string (>50 chars) from the `[role="complementary"]` panel:
   ```
   browser_evaluate → () => document.querySelector('[role="complementary"]')?.innerText
   ```
   Expected: a string longer than 50 characters.
3. **Content-specific detail** — the summary or response names at least one specific detail from the source content (e.g., a sender name, a decision, a data point). This proves Gemini read the actual Workspace content rather than generating a generic response.

## Related Skills

- **`gemini-app`** — for tasks in the standalone Gemini app (not tied to live Workspace files).
- **`google-ai-ultra`** — parent skill containing the MCP automation playbook (`reference.md`) used by this skill. Always read `google-ai-ultra/reference.md` before executing browser automation steps here.
