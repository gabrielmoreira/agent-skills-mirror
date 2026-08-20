---
name: browser-use
description: "Use this skill to drive Wisp Browser Runtime sessions (shared daily Chrome or workspace Chrome) — open pages, read them, click, fill and submit forms, navigate, switch tabs, or scrape content that needs the user's existing cookies and login state. Triggers when the user asks to do something in their browser, log into a site and act inside it, fill out a web form, click through a flow, or extract data from a page that requires being signed in. Tools: browser_setup (check/connect the extension), web_open_tab (open a URL), web_scan (read visible content + actionable elements with ready-made selectors), web_execute_js (click/type/navigate, or a JSON command for tabs/CDP), web_screenshot (see what the tab is showing — layout, charts, canvas, QR codes). Not for the built-in read-only web fetch — this is for interacting with a live browser."
fold_cue: "instead_of=guessing-selectors use=web_scan first — it returns a unique CSS selector and rect for every actionable element; never invent selectors"
---

# Browser Use — act inside the user's real Chrome

Wisp talks to the **Browser Runtime**. Shared mode uses the user's daily
Chrome via the unpacked extension — every action runs in their real
profile: existing cookies, logins, extensions, and normal fingerprint all
apply. Workspace mode can launch a separate Chrome profile. If both are
connected, pass `session: "shared"` or `session: "workspace"`. If
Settings → Browser has **Open browser automatically** enabled (the
default) and no extension is connected, Wisp may start the installed
Chrome/Chromium/Edge so the extension can reconnect. That is still the
user's profile, not Playwright or Selenium.

For figures/code extraction use `web_scan` with `mode: "article"` then
`web_save_assets`. For ChatGPT web one-shot use `web_agent_send`,
`web_agent_wait`, `web_agent_read` on an already-logged-in tab.

Every `web_scan` and `web_execute_js` call needs the user's approval by
design. Do not treat that as a bug to route around.

## Before anything: confirm the bridge is live

Call `browser_setup`. If `status` is not `connected` (or `live_retrieval`
is false), relay its `steps` (load the unpacked extension from
`extension_path`, verbatim) and **stop**. Do not answer live, latest,
current, or URL-specific questions from prior knowledge. Tell the user
this turn contains no live web retrieval and wait until the popup shows
*Connected to Wisp*. Only continue from memory if they explicitly ask
for a knowledge-only answer. Never invent the path.

One exception: the user says the extension is already installed. Chrome
suspends its service worker when idle and reconnects on a one-minute
alarm, so `disconnected` can just be a sleeping worker. Try `web_open_tab`
or `web_scan` once — a successful call proves the bridge is live — and
relay the install steps only if that call fails too.

## The loop

1. **`web_open_tab`** `{url}` — open the page (works even with no tab
   open yet). Waits until the document is complete, then returns the new
   tab id plus `ready`. If `ready` is false, the load timed out — call
   `web_scan` before acting.
2. **`web_scan`** — read the page (after waiting for document complete).
   Returns `page.text`, `page.title`, `page.ready_state`, and
   `page.elements[]`, where each element carries a **unique `selector`**,
   its visible `text`/`aria_label`, and a `rect` `[x,y,w,h]`. Use these
   selectors directly — do not guess. If `ready` is false, scan again;
   do not click a partial page. Use `tabs_only:true` first when you are
   unsure which tab to target; pass `switch_tab_id:<id>` to pin one.
3. **`web_execute_js`** — act, then re-scan to confirm the effect. The
   extension waits for complete before running the script, and again if
   the script navigates.

## Recipes (`web_execute_js` `script`)

| Goal | script |
|---|---|
| Click | `document.querySelector('<selector>').click()` |
| Type into a field | `const e=document.querySelector('<sel>'); e.value='text'; e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true}))` |
| Submit a form | click the submit control by its selector, then re-scan |
| Navigate current tab | `location.href='https://example.com'` |
| Read a value | `document.querySelector('<sel>').textContent` |

`script` may instead be a **JSON command**:

| Goal | JSON command |
|---|---|
| Switch to & focus a tab (so the user sees it) | `{"cmd":"tabs","method":"switch","tabId":<id>}` |
| List tabs | `{"cmd":"tabs"}` (or just `web_scan tabs_only`) |
| Close tabs you opened | `{"cmd":"tabs","method":"close","tabIds":[<id>,...]}` — returns `closed` + `remaining` |
| Trusted click when `.click()` is ignored | `{"cmd":"cdp","method":"Input.dispatchMouseEvent","params":{"type":"mousePressed","x":<x>,"y":<y>,"button":"left","clickCount":1}}` then the same with `"type":"mouseReleased"` — use the element's `rect` centre from `web_scan` |

Prefer plain JS. Reach for `cmd:cdp` only when a page blocks synthetic
events or you truly need trusted input.

## Seeing the page — `web_screenshot`

`web_scan` gives text and elements; **`web_screenshot`** gives sight. Use it
when structure isn't enough: rendered layout, a chart or diagram, a
canvas/WebGL page, a QR code, a PDF or image viewer, or a page that looks
broken. It captures the **visible viewport** of the tab — to see below the
fold, scroll first (`web_execute_js` `scrollTo(0, 1200)`) and capture again.
Pass `question` to say what to read out of it, e.g.
`{"question":"is the login QR code visible and not expired?"}`.

It goes through the configured vision model, so `web_scan` stays the cheaper
default — screenshot when you need eyes, not for every step.

## Tab hygiene — track what you open, offer to close it

Browsing tasks (searching papers, opening a dozen results) leave the user
with a pile of tabs to close by hand. So:

1. Every `web_open_tab` returns `tab.id`. **Keep a running list of the ids
   you opened in this task**, in your own message text — e.g. after a batch
   write `opened tabs: 1234, 1235, 1236`. `{"cmd":"tabs"}` cannot tell you
   which tabs are yours, only what exists.
2. When the task is done, before your final answer, **ask the user**:
   name the count and offer to close them, e.g. *"我为这次检索开了 6 个标签
   页，需要我关掉吗？"* Do not close anything without a yes.
3. On a yes, close them in one call:
   `{"cmd":"tabs","method":"close","tabIds":[1234,1235,1236]}`. Report
   `closed`; ids already gone are skipped silently.

Close **only ids you opened yourself**. Tabs the user had open, or ones
they opened during the task, are theirs — never include them, and never
close a tab mid-task that later steps still need.

## Stop conditions (do not automate through these)

- **Human verification / CAPTCHA:** if `web_scan` returns
  `human_intervention.required=true`, stop, ask the user to complete the
  challenge in the visible tab, and wait for their confirmation before
  scanning again.
- **Credentials:** never type passwords, card numbers, or one-time codes
  yourself. If a step needs a password, have the user sign in directly in
  the browser and continue once they confirm.
- **Irreversible / outward actions** (send, pay, post, delete): confirm
  with the user before clicking the control.
- **Downloads:** for multiple-file downloads, first surface the browser
  settings from `browser_setup` (`download_automation`) and wait for the
  user to confirm; until then trigger at most one download.
- **Blocked sites:** if `web_open_tab` or a navigational `web_execute_js`
  fails with `blocked by user URL filter`, do not retry that site. Read
  `browser_setup.url_filters.block` for the current list. Prefer entries in
  `url_filters.prefer` for literature search and similar retrieval; other
  sites are still allowed.
