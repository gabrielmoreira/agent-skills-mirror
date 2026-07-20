---
name: openloomi-pet
description: "OpenLoomi Pet sprite and state helper for Codex. Use for pet state, themes, custom characters, and sprite overrides."
allowed-tools: Bash(node $SKILL_DIR/../../scripts/loomi-bridge.mjs *)
---

# OpenLoomi Pet Sub-skill

The Loomi Pet has 9 universal state names. The plugin ships the fox
(`loomi-*`) sprite set for branding; the OpenLoomi runtime's
`map_state_to_pet` watcher renders the matching sprite for whichever
theme you have active (fox or capybara, or any folder under
`~/.openloomi/pet-custom/`). State set:

| State | When to use |
|---|---|
| `happy` | A task just completed successfully |
| `idle` | Loomi is waiting for the next loop tick (watcher-only — do not set from Codex) |
| `juggling` | Multiple sub-agents are running |
| `needsinput` | Permission prompt / elicitation dialog visible |
| `presenting` | Fresh decision requires the user's review (watcher-only — do not set from Codex) |
| `sleeping` | Local hour outside 6–22 with no pending work (watcher-only — do not set from Codex) |
| `sweeping` | User dismissed a card just now (watcher-only) |
| `thinking` | Between steps, awaiting LLM response |
| `working` | A tool call is in progress (`PreToolUse` hook fires this) |

## Available commands

- `node $SKILL_DIR/../../scripts/loomi-bridge.mjs pet <state>` — synchronous, returns JSON; use only when the user explicitly asks.
- Hooks call `state <name>` automatically (fire-and-forget, 2s timeout).

Sprite set is hardcoded in the bridge — invalid state names are rejected
before any HTTP call. The endpoint `POST /api/pet/state` may not yet exist
in the target OpenLoomi runtime; the bridge falls back to "would have set
state to X — pending OpenLoomi endpoint" without raising an error.

---

## Help the user customize their pet's appearance

The bridge only drives the **state** — sprite overrides and theme folders
are file-based and live outside the plugin. When the user asks to "change
the pet's look" or "add a custom character", walk them through the file
system. **Do not** try to write `pet-config.json` from the bridge; the
bridge has no such command and the runtime's file watcher does the work.

### Decision tree

1. **"I just want the other built-in"** → right-click Loomi → `Theme → Fox` / `Theme → Capybara`. Persisted in `~/.openloomi/pet-config.json` under `activeTheme`. Long-press (~600 ms) is the fallback if `contextmenu` is swallowed by the host.
2. **"I want my own character"** → drop a folder at `~/.openloomi/pet-custom/<name>/` with PNGs named after the states. The watcher auto-discovers it within ~250 ms and the theme appears in the menu.
3. **"I want to change just one sprite"** → edit `~/.openloomi/pet-config.json`'s `overrides` map. Wins over both built-ins and custom-theme sprites for the matching `(theme, state)` pair.
4. **"I want to make my theme the default"** → set `activeTheme` to the custom theme's folder name.

### What the bridge can and can't do

| User intent                                | Bridge role                                                                |
| ------------------------------------------ | -------------------------------------------------------------------------- |
| Flip to `happy` mid-task                   | ``pet happy`` — yes                                               |
| Switch fox ↔ capybara                      | **No** — that's a menu action or `pet-config.json` edit; do not try the bridge |
| Add a custom character                     | **No** — direct them to `~/.openloomi/pet-custom/<name>/` and the file watcher |
| Override a single sprite                   | **No** — direct them to `~/.openloomi/pet-config.json`'s `overrides` map    |
| Diagnose "the pet isn't switching themes"  | Direct them to the troubleshooting section in [pet docs](https://github.com/melandlabs/openloomi/blob/main/apps/marketing/content/pet.mdx) |
| Drive the pet from their own tool          | Direct them to `POST /api/pet/state` — see [Pet API](https://github.com/melandlabs/openloomi/blob/main/apps/marketing/content/pet-api.mdx) |

### Filename conventions to communicate

When guiding the user through a custom theme, surface these conventions up-front:

- **PNG only.** `.gif`, `.webp`, `.apng`, `.lottie` are silently ignored.
- **Bare or prefixed names both work.** `idle.png`, `loomi-idle.png`, `capybara-thinking.png`, `my-pack-sweeping.png` all normalize correctly (case-insensitive).
- **One recognizable state PNG is enough.** The folder is registered as a theme as soon as it has ≥1 normalized state stem; missing states fall through to the active theme's `idle` sprite.
- **Hidden / dot-prefixed folders are ignored.** `.git`, `.DS_Store` etc.

### Override JSON shape to communicate

The `overrides` map is camelCase on the wire — `activeTheme`, `customThemesDir`. Snake_case keys silently no-op the assignment (the unit test at `apps/web/src-tauri/src/pet/theme.rs:499` pins the contract). Use the exact shape:

```json
{
  "version": 1,
  "activeTheme": "fox",
  "customThemesDir": "~/.openloomi/pet-custom",
  "overrides": {
    "fox": {
      "idle": "/absolute/path/to/my-fox-idle.png"
    }
  }
}
```

Absolute paths only — the runtime routes them through `tauri::convertFileSrc`, so relative paths and `~/` prefixes will not resolve.

### Common pitfalls to surface

- **The folder doesn't show up** — usually a missing or mis-named state PNG. Run them through the [filename convention table](https://github.com/melandlabs/openloomi/blob/main/apps/marketing/content/pet.mdx#filename-conventions).
- **Override doesn't apply** — host log line `[loomi-pet/theme] failed to parse ~/.openloomi/pet-config.json` means the JSON itself is malformed and defaults loaded. Host log line `[loomi-pet/theme] failed to read <path>: <io error>` means the path doesn't resolve.
- **Theme menu tick is wrong / stuck** — almost always a camelCase vs snake_case wire-format mismatch. The widget reads `activeTheme`, not `active_theme`.
- **`sleeping` / `sweeping` rejected by `/api/pet/state`** — those are watcher-only vocabulary; the runtime returns `400 invalid_state`. Do not POST them from your tool.

---

## What NOT to do from Codex

- **Do not** try to call `POST /api/pet/state` with `sleeping` or `sweeping`. The API rejects them; the watcher owns them.
- **Do not** try to write `pet-config.json` from the bridge. The bridge has no command for it; the file watcher owns updates.
- **Do not** invent new state names. `CAPYBARA_STATES` rejects them before any HTTP call.
- **Do not** claim support for non-PNG sprite formats. The asset pipeline is static PNG only.
- **Do not** say "I'll set up your custom theme for you" if you can only walk them through the file system. The watcher does the work; you guide.

---

## See also

- [Customize your Loomi Pet (user docs)](https://github.com/melandlabs/openloomi/blob/main/apps/marketing/content/pet.mdx) — full guide to themes, custom folders, overrides, troubleshooting
- [Pet API](https://github.com/melandlabs/openloomi/blob/main/apps/marketing/content/pet-api.mdx) — `POST /api/pet/state` for external tools
- [Attention Agent](https://github.com/melandlabs/openloomi/blob/main/apps/marketing/content/attention-agent.mdx) — the desktop pet as a whole
- The runtime source: `apps/web/src-tauri/src/pet/theme.rs` (custom themes + overrides), `apps/web/src-tauri/src/pet/watcher.rs::map_state_to_pet` (state resolution)

---

## Sandbox and network

If `node ... loomi-bridge.mjs pet <state>` or `POST /api/pet/state` fails
with a network error (`ECONNREFUSED`, `ETIMEDOUT`, "unreachable"), check
whether Codex is running inside a sandbox before concluding the OpenLoomi
desktop API is stopped. Codex network sandboxing can block loopback access
to the host's `localhost` (e.g. `http://localhost:3414`). The bridge's
"would have set state to X — pending OpenLoomi endpoint" fallback hides
this in many cases, but a genuine `ECONNREFUSED` still surfaces.

Request approval and retry the same command outside the sandbox. If the
outside-sandbox retry succeeds, treat the in-sandbox failure as a sandbox
artifact. Do not tell the user the pet API is broken until the
outside-sandbox retry also fails. See `openloomi` for the canonical
`loopbackAccess.verification.commands` probe.
