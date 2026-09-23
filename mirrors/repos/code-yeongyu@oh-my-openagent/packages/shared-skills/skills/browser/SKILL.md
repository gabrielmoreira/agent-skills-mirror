---
name: browser
description: "Drives a real browser: sites the user is already signed into, forms and clicks, JS-rendered pages, screenshots, web QA, extension popups, and a human handoff for login, CAPTCHA or OTP. Works through the BrowserSkill extension and its bsk CLI, inside the user's own browser, in a separate Agent Window. Use for any interactive browser task; not for a plain search or an unblocked static fetch."
---

# Browser

Two engines live behind this skill. Choose before you act:

| You need | Engine | Where |
|---|---|---|
| A site the user is signed into, a form, a click-through, a screenshot, web QA, an extension popup | **attached** — the user's own browser | this file |
| A throwaway profile, bot-scoring evasion, a CAPTCHA, network interception, a QA flight trace, coordinate control | **owned** — a browser your code launches | [references/owned-engine/README.md](references/owned-engine/README.md) |
| Text out of a URL, a 403 bypass, a platform that blocks fetchers | neither | the `ultimate-browsing` skill |

**Attached is the default,** because it is the only engine carrying the user's logins and the only
one where a human is a single command away. The owned engine is an opt-in local install, not part
of this package.

## Step 0 — prove the stack before you drive it

```bash
node "<skill-root>/scripts/browser-doctor.mjs"
```

It reports one of four states and what to do next:

| State | Meaning | Next |
|---|---|---|
| `ready` | CLI, daemon and a connected browser | start a session |
| `no-extension` | CLI works, no browser is connected | give the user the store link the doctor printed, wait, re-run |
| `no-cli` | `bsk` is not installed | `node "<skill-root>/scripts/browser-install.mjs"`, then re-run |
| `no-browser-support` | the platform has no supported browser | say so and stop |

**Never substitute another browser for a missing one.** A headless browser you launch yourself has
none of the user's sessions, so every login turns into a ladder you should not be climbing. If the
attached engine is unavailable, say which state you hit and ask the user.

## The loop

```bash
bsk session start --json --no-focus --name "<task>"     # keep session_id
bsk navigate https://example.com --session <id> --json
bsk observe --session <id>                              # @eN refs live here
bsk click @e1 --session <id> --json
bsk screenshot --session <id> --out ./shot.png --json
bsk session stop <id> --json                            # success AND failure
```

1. **Observe before every action.** `observe` returns a semantic tree whose `@eN` refs are reissued
   on each call. Read a ref and use it in the same cycle; a ref from two calls ago points somewhere
   else now.
2. **Navigation and large DOM changes stale every ref.** Observe again rather than reusing.
3. **Two identical failures mean change approach, not retry.** A third identical attempt is a defect.
4. **Borrow a user tab explicitly** (`tab list --scope user`, `tab borrow <id>`, `tab return <id>`).
   Borrowing prompts the user; never invent tab ids and never repeat a denied borrow.
5. **Always stop the session,** on success and on failure. Stopping also returns borrowed tabs.

Command semantics, the flags that behave differently than they read, and the failure table are in
[references/commands.md](references/commands.md).

## When a human is the only way through

Login, CAPTCHA, OTP, a payment confirmation, a consent dialog:

```bash
bsk request-help --session <id> --prompt "<what you need done>" [--target @eN]
```

Then observe again. Respect a `cancelled` or `timed_out` answer; do not work around it by changing
the extension's automation settings.

## Rules

- **Never read credentials through the page.** No `evaluate` that extracts a password, token, cookie
  or recovery code. The value of this engine is that the browser is already signed in.
- **Never clear cookies, cache or site data.** It is the user's real profile; clearing it logs them
  out everywhere. No flow here needs it.
- **`--no-focus` by default.** The browser belongs to someone who is probably using it.
- **One short, named session per task,** always stopped.
- Do not toggle the extension's automation settings, and do not restart the browser to fix a state.

## More

- [references/install.md](references/install.md) — installing the CLI and the extension, per OS
- [references/commands.md](references/commands.md) — command semantics, refs, failure table
- [references/remote.md](references/remote.md) — agent on one machine, browser on another
- [references/recipes/1password.md](references/recipes/1password.md) — reading a vault the user has unlocked
- [references/owned-engine/README.md](references/owned-engine/README.md) — the code-driven engine
