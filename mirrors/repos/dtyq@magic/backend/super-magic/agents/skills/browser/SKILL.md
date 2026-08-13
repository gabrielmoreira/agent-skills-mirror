---
name: browser
description: Open and operate webpages in a real browser: navigate, read rendered content, inspect interactive elements, click, type, submit forms, press keys, select options, check boxes, hover, scroll, upload files, wait for page changes, manage pages, take and save screenshots, analyze visual layout, and inspect page errors and network activity.
---

# Browser

Use Browser tools through `run_sdk_snippet`. Pass only fields required by the task and let optional fields use their defaults. Use the common tools documented below directly. Before calling a capability documented only in a reference, read that reference and use its exact tool and parameter names; do not abbreviate or infer them.

## Default path

For most tasks, use this four-step path:

1. Open a new URL with `browser_open_page`.
2. Read with `browser_read_page`, or take one `browser_list_elements` when interaction is needed.
3. Find the exact ref, perform the action, and keep using the same `page_id`.
4. If the next step depends on a specific result, wait for that text, URL, ref, or download; otherwise verify once with a read or changes snapshot.

Do not list sessions before opening a normal sandbox page. Do not navigate to a URL that `browser_open_page` already opened.

```python
from sdk.tool import tool

page = tool.call("browser_open_page", {"url": "https://example.com"})
print(page.content)
if page.ok:
    page_id = page.data["page_id"]
    print(tool.call("browser_read_page", {"page_id": page_id}).content)
```

Use `browser_list_pages` only to reuse an existing page. Use `browser_list_sessions` only when choosing an authorized user Browser, resolving multiple sessions, or recovering from a disconnect.

## Find a control once

Take one interactive snapshot. Its ref records contain exactly these useful fields:

- `ref`
- `role`
- `accessible_name`
- `text`
- `attributes`
- `allowed_actions`

A ref record is an accessibility record, not a DOM element. It has no `tag_name` field. HTML details such as input `type` are inside `attributes`.

Use all returned refs when locating a target. Do not truncate `snapshot.content`, inspect only the first N refs, guess a ref, or repeatedly retry different elements. The normal path is to print the snapshot content, read its hierarchy, then use the exact ref in the next snippet.

```python
snapshot = tool.call("browser_list_elements", {"page_id": page_id})
print(snapshot.content)
```

After reading the printed tree, continue with its exact ref:

```python
field_ref = "<exact-ref-from-snapshot-content>"
filled = tool.call("browser_fill", {
    "page_id": page_id,
    "ref": field_ref,
    "value": "example query",
})
print(filled.content)
if filled.ok:
    print(tool.call("browser_press", {"page_id": page_id, "key": "Enter"}).content)
    print(tool.call("browser_read_page", {"page_id": page_id}).content)
```

Add `name` or `attributes` only when the first filter is ambiguous. Use the hierarchy in `snapshot.content` when repeated labels belong to different forms, dialogs, or page regions.

When a same-snippet pipeline must select from many refs, inspect `snapshot.data["snapshot"]["refs"]` in code and filter by `allowed_actions`, role, name, attributes, and hierarchy. This is a pipeline optimization, not the default reading path. Print `snapshot.content` when the code cannot prove one unique target.

After `browser_fill`, omit `ref` from `browser_press` when Enter should go to the current focus. Pass a fresh ref only when focus may have moved or a specific autocomplete/menu control must receive the key.

Do not add a generic wait after opening a page. After a submit, search, sign-in, or checkout action, read the current page once. If the required result is still pending, wait for the exact text, URL, ref, load state, or download that the next step needs.

## Common actions

These are the normal parameter forms. Apply the shared Code Mode result rules to each returned result.

```python
tool.call("browser_click", {"page_id": page_id, "ref": ref})
tool.call("browser_fill", {"page_id": page_id, "ref": ref, "value": "text"})
tool.call("browser_press", {"page_id": page_id, "key": "Enter"})
tool.call("browser_hover", {"page_id": page_id, "ref": ref})

# Page scroll: positive delta_y moves down; negative moves up.
tool.call("browser_scroll", {"page_id": page_id, "delta_y": 500})

# Bring one referenced element into view without additional wheel movement.
tool.call("browser_scroll", {"page_id": page_id, "ref": ref})

# Select by exact option value or unique visible label.
tool.call("browser_select", {"page_id": page_id, "ref": ref, "value": "Two"})

tool.call("browser_check", {"page_id": page_id, "ref": ref, "checked": True})
tool.call("browser_upload_file", {
    "page_id": page_id,
    "ref": ref,
    "file_paths": ["path/inside/workspace.txt"],
})
```

`browser_upload_file` accepts relative or absolute paths inside the current workspace. Paths outside the workspace are rejected.

Only use an action listed in that ref's `allowed_actions`. The model-readable snapshot also shows actions inline, for example:

```text
[textbox ref=e12 actions=click,fill,press,scroll] Search
[button ref=e13 actions=click,hover,scroll] Submit
```

## Wait and verify

Actions report that input was dispatched, not that the user's intended outcome occurred. Verify only what matters:

```python
waited = tool.call("browser_wait", {
    "page_id": page_id,
    "condition": "text",
    "value": "Completed",
    "timeout_ms": 10000,
})
print(waited.content)
```

Use:

- `condition="url"` with `value` for navigation to a known URL pattern.
- `condition="load_state"` with `state="domcontentloaded"` or `state="load"`.
- `condition="text"` with `value` for visible result text.
- `condition="ref"` with the exact ref in `value`.
- `condition="time"` with `duration_ms` only when no observable condition exists.

For a quick post-action check, use `browser_list_elements(scope="changes")`. After navigation, take a normal fresh snapshot instead; old refs no longer belong to the current document.

## Choosing how to look at a page

| You want | Use |
|----------|-----|
| Read an article, document, or post | `browser_read_page` |
| Find one control to click or fill | `browser_find` |
| `browser_read_page` returned nearly nothing | `browser_read_html` |
| Pull many values from a list or table | `browser_read_html`, then `browser_evaluate` |
| See every control at once | `browser_list_elements` |
| Understand layout, images, charts, maps, or canvas | `browser_visual_query` |

`browser_find` never picks for you. If it returns several matches, choose one by ref. Never write a selector you have not seen in `browser_read_html` output.

`browser_visual_query` captures and analyzes in one call and writes no file. Never take a screenshot and analyze it separately. Run at most one visual-model call at a time, and give a snippet at least 120 seconds when it follows other Browser work. Use `browser_find_visual` only when a control cannot be identified from text or structure. Use `browser_screenshot` only when the user asks to see or save an image.

Exact visual calls:

```python
shot = tool.call("browser_screenshot", {"page_id": page_id})
print(shot.content)

labeled = tool.call("browser_screenshot", {"page_id": page_id, "labels": True})
print(labeled.content)

saved = tool.call("browser_screenshot", {
    "page_id": page_id,
    "output_path": "screenshots/page.webp",
})
print(saved.content)
if saved.ok:
    print(saved.data["output_path"])

visual = tool.call("browser_visual_query", {
    "page_id": page_id,
    "query": "Describe the main visible regions and their spatial arrangement.",
})
print(visual.content)

match = tool.call("browser_find_visual", {
    "page_id": page_id,
    "target": "the primary search field",
})
print(match.content)
if match.ok:
    target_ref = match.data["ref"]
```

Use the validated `data["ref"]` from `browser_find_visual` for the next interaction.

Without `output_path`, screenshots are temporary UI snapshots displayed through the tool detail. They do not return `screenshot_data`, base64 bytes, or a reusable local path. Set `output_path` only when the user asks to save the screenshot or a later step needs a workspace file. The extension selects the format automatically: use `.webp` for the normal size-quality balance, `.jpg` or `.jpeg` when JPEG is required, and `.png` for lossless output. Omit `scale` and `quality` normally so the service uses the readable Tool Detail defaults. Set `scale` only when the user requests a specific output size; increasing it enlarges captured pixels but does not create new page detail. Set `quality` only when the user explicitly requests a different WebP/JPEG compression level; it is invalid for PNG. Read the saved workspace path from `result.data["output_path"]`.

If visual analysis is unavailable, continue with reads and snapshots when text or structure is sufficient. If the task requires appearance or spatial judgment, report the real visual error instead of claiming the image was understood.

## Refs, pages, and failures

- Read page IDs from `result.data["page_id"]`. Items in `browser_list_pages().data["pages"]` also use `page_id`.
- Reuse returned IDs exactly. Never construct `page_id`, `session_id`, refs, or visual labels.
- Refs remain stable within the same document only when the runtime can prove element identity. Navigation invalidates them.
- On `stale_ref`, `ref_not_found`, or `ambiguous_ref`, take one fresh interactive snapshot and locate the target again.
- Leave pages open unless the user asks to close them. Normal operations renew sandbox page lifetime.
- Use `browser_keep_alive` only when a known long-running step must preserve the same sandbox page.

## CAPTCHA and human verification

When a page shows a CAPTCHA, unusual-traffic warning, or human-verification step:

1. Stop automated interaction immediately. Do not bypass or script around it.
2. If the user said they can operate the visible or authorized Browser, keep the page open, state the exact manual action needed, and wait for confirmation.
3. Otherwise use a legitimate alternative only when the task allows one. Do not evade an explicit Browser-only test.
4. After manual verification, read the page or take a fresh snapshot. Do not reuse old refs.

Do not wait only for the final URL on sites that may insert verification. After the triggering action, read the current page first; if verification is present, stop immediately instead of retrying the wait.

## When a site blocks automation

If a page redirects away on its own, blanks out, or reports that developer tools are open, stop repeating the action. Read [references/blocked-pages.md](references/blocked-pages.md) and follow it. This is different from a CAPTCHA: a CAPTCHA asks a human to prove something and must not be bypassed.

## Boundaries

- Operate only pages authorized for the current Browser session.
- Do not expose endpoints, pairing or resume tokens, cookies, passwords, or browser history.
- Do not print raw protocol payloads, full DOM/accessibility dumps, or screenshot bytes.
- Use `browser_evaluate` to read focused application-specific data, never to interact with the page. Clicking, filling, and navigating must use ref-based tools so the runtime can report what changed.

## References

- Sessions, pages, navigation, waiting, lifecycle, and capabilities: [references/sessions.md](references/sessions.md)
- Element-list scopes and ref lifetime: [references/elements.md](references/elements.md)
- Screenshots, visual queries, and visual labels: [references/screenshots.md](references/screenshots.md)
- Console, network, JavaScript, and troubleshooting: [references/debugging.md](references/debugging.md)
- Authorized user Chrome sessions: [references/remote-chrome.md](references/remote-chrome.md)
- Automation-tool detection and blocked-page handling: [references/blocked-pages.md](references/blocked-pages.md)
