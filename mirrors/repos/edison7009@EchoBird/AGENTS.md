# AGENTS.md — EchoBird

Instructions for agents (ZCode / Claude Code / Codex) working in this repo.
Read this before modifying code.

## Project shape

Tauri desktop app: React + TypeScript + Vite frontend in `src/`, Rust backend
in `src-tauri/`. Two-tier tool/feature registries often ship in **both** a
bundled copy and a remote copy (e.g. `src/data/<x>.json` vs
`docs/api/<...>/index.json`) — when adding or editing an entry, update **both**
files unless told otherwise; they share one schema and the remote wins at
runtime. Prettier governs the frontend JSON/TS; rustfmt governs `src-tauri/`.

## Desktop interaction rules

- EchoBird is a desktop application, not a website. Do not add custom hover
  tips, custom tooltips, or other web-style hover-only guidance.
- Keep the mouse cursor as the system default everywhere. Do not use
  `cursor: pointer` or any other cursor-changing style for buttons, links,
  draggable areas, disabled controls, or other interactive elements.

## CI gates (must pass locally before pushing)

CI runs two jobs in parallel, each with this order — **format runs first and
fails the whole job before clippy/test even start**, so a format slip hides
whether the code is actually sound. Match the order locally:

**Frontend** (`src/`, repo root):
```bash
npm run typecheck        # tsc --noEmit
npm run format:check     # prettier --check  (or `npm run format` to auto-fix)
npm run lint             # eslint  (or `npm run lint:fix`)
npm test                 # vitest
```

**Rust** (`src-tauri/`, or pass `--manifest-path src-tauri/Cargo.toml`):
```bash
cargo fmt --check        # FORMAT FIRST. `cargo fmt` to auto-fix.
cargo clippy --all-targets --all-features -- -D warnings   # CI denies warnings
cargo test
```

Run **all of them**, every push. A green `cargo check`/`cargo test` does NOT
imply a green CI — `cargo fmt --check` is a separate gate and the one most
often skipped. Same for the frontend: `npm run format:check` is not implied by
`typecheck` or `lint`.

### Lesson (learned the hard way)

Commit `4774b1d5` passed `cargo check` + `cargo clippy` + `cargo test` locally
but failed CI because `cargo fmt` hadn't been run (a braced-import reorder and
a wrapped method chain). CI's `cargo fmt --check` failed in the first step,
so clippy/test never executed — the failure said nothing about correctness,
only about formatting. Don't repeat it: treat the format gate as equal to
clippy/test, not optional.

## Verification habits

- After writing Rust: `cargo fmt`, then `cargo clippy --all-targets --all-features -- -D warnings`, then `cargo test`.
- After writing TS/TSX/JSON: `npm run format` (or `format:check`), `npm run typecheck`, `npm run lint`.
- The `winreg` crate's `FromRegValue for String` does **not** auto-expand
  `REG_EXPAND_SZ` — values like `%USERPROFILE%\...` come back literal. Expand
  them via `services::tool_manager::expand_path` (or `expand_path`-equivalent)
  rather than assuming the registry hands back resolved paths.
- Don't add `#![cfg(...)]` inside a module file when the `mod` declaration in
  `services/mod.rs` already gates it with `#[cfg(...)]` — rustfmt flags it as
  a duplicated attribute.

## Account login UI conventions

- Use `src/pages/AppManager/AccountSectionPrimitives.tsx` for account login
  buttons and rows. ChatGPT is the structural reference; do not copy a new
  provider-specific button/row implementation.
- Keep provider colors via `colorClassName` and provider quota content via
  `secondary`. Claude, DeepSeek and WorkBuddy retain their designed colors;
  Grok uses the same black/white treatment as ChatGPT.
- Buttons are 48px tall, pill-shaped, with a 24px product icon and the existing
  add-account / waiting-for-browser translations. Login timeout is 60 seconds.
- Rows are 48px tall: 16px selection marker on the left, identity above quota
  in the center, plan above refresh/delete actions on the right. Display the
  plan once. Missing quota is unknown (`—`), never fabricated as zero.
- Use Lucide refresh/delete icons. Only show refresh when a real refresh
  action exists; disable it while pending. Clicks and keyboard actions on
  nested controls must not change account selection. Rows support Enter/Space.
- Selecting an account clears the API-model selection and vice versa. Adding
  an account saves it in EchoBird; applying a selection switches the client.
  Keep the existing delete confirmation. Cancel and clean up login on timeout
  or leaving the tool, and ignore late responses from earlier attempts.
- No extra explanatory copy, hover tips, or cursor changes. New integrations
  must test selection/action isolation, pending state and their quota display.

## Commit policy

Commit only when asked. Push only when asked. Keep history linear (rebase onto
`origin/main` when the remote has moved).
