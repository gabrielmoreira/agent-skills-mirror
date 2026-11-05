# Driver: browser-use

Your browser is a private headless Chrome that you drive with short `browser-use` Python snippets. Each session gets its own Chrome process and a fresh profile, so the other personas' logins and tabs never reach yours.

## Start and stop

```bash
<skill-dir>/scripts/chrome.sh start <session> <output-dir>
```

It prints an env prefix such as `BU_NAME=uxst-mobile-r1 BU_CDP_URL=http://127.0.0.1:61234 BH_TAB_MARKER=0`. Shell state does not carry between your commands, so put that exact prefix in front of every `browser-use` call:

```bash
<prefix> browser-use <<'PY'
goto_url("<App URL>"); wait_for_load()
capture_screenshot("<output-dir>/01-landing.png")
PY
```

The browser keeps its tab, page, and cookies between calls. Its tab is already open, so navigate with `goto_url`. When you're done: `<skill-dir>/scripts/chrome.sh stop <session> <output-dir>`.

## Actions

Helpers are pre-imported in every snippet. Chain several in one call when you don't need to look in between. For any keyboard input, start the snippet with `exec(open("<skill-dir>/scripts/keyboard.py").read())` and use its `fill`, `type_keys`, and `press`. The built-in `fill_input` and `press_key` open stray tabs in headless Chrome on macOS and hide your page.

| To | Do |
|----|----|
| See the screen | `capture_screenshot("<output-dir>/NN-slug.png")`, then open the PNG |
| Find what you can act on | `print(js(open("<skill-dir>/scripts/controls.js").read()))`: each visible control's name, CSS selector, click point `x`/`y`, and `inView` (false: scroll first) |
| Click or tap | `click_at_xy(x, y)`, then `wait_for_load()` if it navigates |
| Double-click | `click_at_xy(x, y); click_at_xy(x, y, clicks=2)`. That's the two clicks a real double-click sends |
| Type into a field | `fill("<selector>", "text")`: selects what's there, then types over it key by key |
| Paste into a field | click the field, then `type_text("text")`: the whole value lands at once |
| Press a key | `press("Enter")`, `press("Tab")` |
| Scroll | `scroll(x, y, dy=500)` scrolls down, `dy=-500` up |
| Pick from a dropdown | `js("const s = document.querySelector('<selector>'); s.value = '<value>'; s.dispatchEvent(new Event('change', {bubbles: true}))")` |
| Back, forward, reload | `js("history.back()")`, `js("history.forward()")`, `cdp("Page.reload")`; then `wait_for_load()` |
| Check where you are | `page_info()`: URL, title, scroll. When an alert or confirm is open, it returns `{"dialog": ...}` instead |
| Answer a dialog | `cdp("Page.handleJavaScriptDialog", accept=True)` (or `False`; add `promptText="..."` for a prompt) |
| Open a second tab | `first = current_tab()["targetId"]; new_tab("<url>"); cdp("Page.bringToFront")`. Return with `switch_tab(first); cdp("Page.bringToFront")`. Only the front tab counts as visible, like on a real screen |
| Wait | `wait(2)`, `wait_for_load()`, `wait_for_network_idle()` |
| Evidence after a failure | `<prefix> browser-use < <skill-dir>/scripts/failures.py`: failed requests (HTTP 400+) and JS errors since your last check. Run it right away; the buffer is short |

`controls.js` and `js(...)` read the DOM. Use them to find where to click, and the screenshot to decide what a person sees.

## Mobile

Right after `chrome.sh start`, before the first `goto_url`:

```bash
<prefix> browser-use < <skill-dir>/scripts/mobile-setup.py
```

It turns the tab into a 375×667 touch phone (iPhone SE) on slow 3G. The settings belong to the tab, so run it again after opening or switching to another tab. Check each screen with:

```bash
<prefix> browser-use <<'PY'
print(js(open("<skill-dir>/scripts/mobile-audit.js").read()))
PY
```

If the audit's `deviceWidth` isn't 375, the phone settings were lost; run `mobile-setup.py` again.

## Fresh session for a retest

`chrome.sh start <session>-retest <output-dir>` gives a second, empty profile with its own prefix, separate from your journey's.
