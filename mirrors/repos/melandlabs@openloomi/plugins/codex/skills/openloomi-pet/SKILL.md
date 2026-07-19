---
name: openloomi-pet
description: "OpenLoomi Pet sprite & state helper for Codex. Use when the user wants to change their Loomi Pet state, switch theme, drop in a custom character, override individual sprites, or ask Codex to mirror its lifecycle onto the pet. Triggers: pet state, set pet, loomi pet, pet to happy, pet to working, pet to thinking, fox sprite, capybara sprite, custom pet theme, pet-custom, pet-config, override pet sprite."
allowed-tools: Bash(node ${CODEX_PLUGIN_ROOT}/scripts/loomi-bridge.mjs *)
---

# OpenLoomi Pet Sub-skill (Codex)

> **Codex parity note:** this skill ships only in the Claude plugin today. The
> Codex plugin's `loomi-bridge.mjs` already exposes the same `pet <state>`
> command and lifecycle hooks (see
> [`plugins/codex/README.md` § Codex Pet lifecycle hooks](#)), and the file-based
> theme system is runtime-side, identical across both plugins. The Codex
> plugin does not yet have its own `openloomi-pet` SKILL.md — this stub mirrors
> the Claude one so users on either surface get the same guidance.
>
> When Codex's `pet <state>` behaviour diverges from Claude's, this file is the
> authoritative Codex-side reference.

The Loomi Pet has 9 universal state names. The runtime's `map_state_to_pet`
watcher renders the matching sprite for whichever theme is active (fox,
capybara, or any folder under `~/.openloomi/pet-custom/`). State set:

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

- `node ${CODEX_PLUGIN_ROOT}/scripts/loomi-bridge.mjs pet <state>` — synchronous, returns JSON; use only when the user explicitly asks.
- Hooks call `state <name> --event <event>` automatically (fire-and-forget, 2s timeout).

The Codex bridge mirrors the Claude bridge's `cmdPet`. Invalid state names
are rejected client-side before any HTTP call. The endpoint
`POST /api/pet/state` may not exist in the target runtime; the bridge
falls back to a polite "endpoint pending" notice without raising an error.

```bash
node plugins/codex/scripts/loomi-bridge.mjs pet happy
node plugins/codex/scripts/loomi-bridge.mjs pet working
```

Failure modes (all return structured JSON, never throw):

| Code               | Cause                                                                      |
| ------------------ | -------------------------------------------------------------------------- |
| `MISSING_STATE`    | No positional state argument                                                |
| `INVALID_STATE`    | State not in the 9-state vocabulary; response includes `validStates`        |
| `TOKEN_MISSING`    | `~/.openloomi/token` does not exist or is unreadable — run `setup` first    |
| `ENDPOINT_MISSING` | Runtime answered 404 — non-blocking; bridge retries automatically later     |
| `API_UNREACHABLE`  | No local API responded on 3414 / 3515; `attempts` lists every URL tried     |
| `PET_FAILED`       | Runtime answered but with a non-success status code (e.g. 400 invalid_state for `sleeping` / `sweeping`) |
| `PET_STATE_SET`    | Success — runtime accepted the state                                        |

---

## Help the user customize their pet's appearance

The Codex bridge only drives the **state** — sprite overrides and theme
folders are file-based and live outside the plugin. When the user asks to
"change the pet's look" or "add a custom character", walk them through the
file system. **Do not** try to write `pet-config.json` from the bridge;
the bridge has no such command and the runtime's file watcher does the work.

### Decision tree

1. **"I just want the other built-in"** → right-click Loomi → `Theme → Fox` / `Theme → Capybara`. Persisted in `~/.openloomi/pet-config.json` under `activeTheme`. Long-press (~600 ms) is the fallback if `contextmenu` is swallowed by the host.
2. **"I want my own character"** → drop a folder at `~/.openloomi/pet-custom/<name>/` with PNGs named after the states. The watcher auto-discovers it within ~250 ms and the theme appears in the menu.
3. **"I want to change just one sprite"** → edit `~/.openloomi/pet-config.json`'s `overrides` map. Wins over both built-ins and custom-theme sprites for the matching `(theme, state)` pair.
4. **"I want to make my theme the default"** → set `activeTheme` to the custom theme's folder name.

### What the bridge can and can't do

| User intent                                | Bridge role                                                                |
| ------------------------------------------ | -------------------------------------------------------------------------- |
| Flip to `happy` mid-task                   | `pet happy` — yes                                                          |
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
- **`sleeping` / `sweeping` rejected by `/api/pet/state`** — those are watcher-only vocabulary; the runtime returns `400 invalid_state`. The Codex bridge surfaces this as `PET_FAILED` (not `INVALID_STATE`) — distinguish it from a typo before reporting.

---

## Codex-specific deltas vs the Claude plugin

| Behaviour                              | Claude                                                       | Codex                                                                                          |
| -------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| Slash command surface                  | `/openloomi:pet <state>`                                     | None — users drive `node plugins/codex/scripts/loomi-bridge.mjs pet <state>` directly          |
| Lifecycle hooks                        | Opt-in via `/openloomi:hooks install`                        | Declared in `plugins/codex/hooks/hooks.json`; bundled by default                               |
| Hook state-name source tag             | `source: "claude-plugin"`                                    | `source: "codex-plugin"`                                                                       |
| Failure surfacing on rejected states   | `INVALID_STATE` for typos, `PET_FAILED` for runtime rejects  | Same — `INVALID_STATE` client-side, `PET_FAILED` with status 400 for runtime rejects           |
| Fallback when runtime lacks the API    | Bridge returns "would have set state to X — pending endpoint" | Same polite notice, plus an `ENDPOINT_MISSING` code if the runtime returns 404                |
| Pet theme / override file ownership    | None — runtime watcher                                       | None — runtime watcher (the Codex plugin never writes `pet-config.json` either)                |

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
- Claude-side counterpart: [`plugins/claude/skills/openloomi-pet/SKILL.md`](../../claude/skills/openloomi-pet/SKILL.md)