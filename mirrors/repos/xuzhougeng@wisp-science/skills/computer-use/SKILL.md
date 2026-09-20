---
name: computer-use
description: "Use Cua Driver through MCP to inspect and operate the user's native desktop apps on Windows, macOS, or Linux. Trigger when a task requires a desktop application, native file dialog, OS window, signed-in browser UI, screenshot-grounded interaction, or a result that must be verified in the application. Keep browser page work in browser-use when the page bridge is sufficient."
fold_cue: "instead_of=blind_pixel_clicking use=list_windows_then=get_window_state — keep an exact window target and refresh state after navigation or UI changes"
---

# Computer Use — operate native desktop apps with Cua Driver

Wisp uses the installed Cua Driver as an MCP server. Cua Driver owns the
platform-specific desktop integration; this Skill owns the agent workflow and
the safety boundary. It can operate native apps, native file dialogs, and
browser windows that are visible to the host desktop.

## Before the first action

Use this Skill only when the Cua Driver tools are advertised in the current
conversation. If they are absent, do not invent tool names or fall back to
blind shell input. Tell the user to install Cua Driver, add a stdio MCP
connection with:

```text
command: cua-driver
args: mcp
```

Then ask them to reconnect the MCP service. The driver must run in the
interactive user session. An SSH or service-session process cannot see the
user's desktop. On macOS, Accessibility and Screen Recording permission must
be granted to the Cua Driver app identity. On Windows and Linux, report any
interactive-session or display-server refusal as a capability boundary.

If the available Cua Driver tool exposes a health, doctor, or permission
status call, use it first. Otherwise call `list_apps` or `list_windows` as a
read-only connection check. A process starting successfully is not evidence
that the desktop is controllable.

## Tool selection

Use the exact tool schemas advertised by the connected Cua Driver server. The
common names are:

- `list_apps` and `launch_app` for application discovery and startup;
- `list_windows` for exact process/window identity;
- `get_window_state` for the accessibility tree plus a window screenshot;
- `get_desktop_state` for the primary desktop screenshot and desktop identity;
- `click`, `type_text`, `press_key`, `hotkey`, `scroll`, and `drag` for input;
- window or session cleanup tools when the driver advertises them.

Do not guess a selector, process ID, window ID, element index, or coordinate.
Read the current state first. For input, prefer a window target with an exact
`pid` and `window_id`; use the returned accessibility `element_index` when the
control exposes a semantic action. Use window-local pixel coordinates only
when the element is not actionable semantically. Use a desktop target only
for deliberate foreground screen actions.

## Observe → act → verify

For every meaningful action:

1. Discover the app and select one exact window. If several candidates match,
   stop and resolve the ambiguity instead of choosing by title alone.
2. Call `get_window_state` and keep the resulting window identity and fresh
   element references together. Treat element indexes as stale after a page
   navigation, dialog transition, window recreation, or material UI change.
3. Perform one bounded action. Prefer background delivery when the target and
   platform support it. Request foreground delivery only for that action when
   the application requires focus and interrupting the user's desktop is
   acceptable.
4. Read the same target again and verify the application state or external
   artifact. A successful input dispatch is not proof that the application
   handled it.
5. If the result is stale, ambiguous, refused, or unverifiable, follow the
   returned refusal code and re-observe. Do not retry the same blind action.

For a native save or export, verify the actual path and file existence with a
filesystem tool after the application reports completion. For a visual canvas,
verify the screenshot and, where possible, an application-owned state or
exported artifact. For a browser page, use `browser-use` page tools when they
provide the needed operation; use Cua Driver for browser chrome, native
dialogs, or a page surface that the browser bridge cannot access.

## Safety boundaries

- Ask for confirmation before sending, posting, purchasing, deleting,
  submitting, or otherwise committing an irreversible external action.
- Never type passwords, API keys, payment data, or one-time codes. Have the
  user enter them in the visible application and continue after confirmation.
- Do not use desktop control to solve CAPTCHA or bypass human verification.
- Do not treat `effect: confirmed` as a universal success signal; inspect its
  evidence and verify the application-owned result.
- Keep one foreground input sequence serialized. Do not drive two windows with
  concurrent keyboard or pointer actions.
- If a target disappears, permissions change, or the driver returns a
  structured refusal, report the concrete reason and stop or re-observe as the
  refusal instructs.

## First smoke task

For a new installation, use a reversible task such as opening Calculator,
entering `6 × 7`, and reading back `42`. For this project’s acceptance task,
open Inkscape, make one small edit, export through the native dialog, and
verify the resulting SVG exists at the requested path. Record the platform,
driver version, delivery mode, and whether verification was semantic, visual,
or filesystem-based.
