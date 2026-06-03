---
name: daytona-flow-validator
description: Daytona UI flow validation loop. Use when validating real app behavior, checking a Daytona flow, proving a bug is fixed, or deciding pass/fail from CDP snapshots, screenshots, and assertions.
---

# Daytona Flow Validator

Use this skill to decide whether a Daytona Electron or browser flow actually
works. Launching the sandbox is separate. This skill owns the feedback loop.

## Core Rule

Never report success from a click, script return value, or recording alone.
Every meaningful action must follow this loop:

1. Observe with `browser_snapshot` or `browser_eval`.
2. Act with `browser_click`, `browser_fill`, or `browser_eval`.
3. Observe again with `browser_snapshot` or `browser_eval`.
4. Assert the expected URL, text, state, process, network, or file result.
5. Capture a screenshot checkpoint when the visible state matters.

If any assertion is missing, the flow is not validated yet.

## Minimum Pass Evidence

For a UI flow, collect all of these when feasible:

- CDP target proof: `browser_list` shows the intended target.
- App proof: `navigator.userAgent` contains `Electron/` for desktop flows, or does not for standalone Chrome flows.
- State proof: URL, visible text, selected model/provider, status, or route matches the expected outcome.
- Backend proof: relevant `daytona exec` process/log/health check for sidecars, Den, worker proxy, or mock servers.
- Visual proof: `browser_screenshot` or `.devcontainer/capture-daytona-screenshot.sh` at important checkpoints.
- Human proof: recording URL only when requested or useful for PR evidence.

## Validation Loop Template

Use this structure for each step in the final report:

```text
Step: <what was attempted>
Before: <snapshot/eval showed X>
Action: <tool/selector used>
After: <snapshot/eval showed Y>
Assertion: pass/fail because <observable signal>
Evidence: <screenshot path or artifact URL if captured>
```

## Prefer Accessible Snapshots

Start with `browser_snapshot` for normal UI controls because it gives stable
UIDs for `browser_click` and `browser_fill`. Use `browser_eval` when:

- React dynamic UI makes snapshot UIDs stale.
- Native file pickers must be bypassed.
- Lexical editor input needs a synthetic paste event.
- You need to inspect app state, localStorage, URL, or text quickly.

## Lexical Composer

Prefer synthetic paste for the OpenWork composer:

```js
(function pasteComposer(text) {
  var editor = document.querySelector('[contenteditable="true"][data-lexical-editor="true"]');
  if (!editor) return { ok: false, reason: 'composer not found' };
  editor.focus();
  var data = new DataTransfer();
  data.setData('text/plain', text);
  editor.dispatchEvent(new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData: data }));
  return { ok: true, text: editor.innerText };
})('Reply with exactly: Daytona validation OK')
```

Then assert the Run button is enabled before clicking it.

## Screenshots

Use browser screenshots for renderer state:

```text
browser_screenshot({ browser_url: CDP_URL, target_id: TARGET_ID })
```

Use Daytona display screenshots for noVNC/window state:

```bash
daytona exec "$SANDBOX" -- 'bash .devcontainer/capture-daytona-screenshot.sh'
```

Do not treat screenshots as the only assertion. Inspect text/state with CDP too.

## Failure Handling

When a step fails:

- Capture current `browser_snapshot` or `document.body.innerText`.
- Capture a screenshot.
- Inspect the relevant logs before retrying.
- Retry only after naming the suspected cause.

Common logs:

```bash
daytona exec "$SANDBOX" -- 'tail -120 /tmp/electron.log'
daytona exec "$SANDBOX" -- 'tail -120 /tmp/vite.log'
daytona exec "$SERVER_SANDBOX" -- 'tail -120 /tmp/den-api.log'
```

## Final Verdict

Use one of these verdicts:

- `Passed`: every expected outcome has an observable assertion.
- `Failed`: at least one assertion disproves the expected outcome.
- `Incomplete`: the sandbox/tooling failed, evidence is missing, or only a recording/screenshot was collected.
