# Agent Cheat Sheet

This repository contains `sidekick.nvim`, a Neovim plugin that integrates GitHub Copilot "Next Edit Suggestions" (NES) into Neovim. The plugin relies on Copilot's LSP and ships with an automated test + docs workflow.

## Project Overview

- Core modules live under `lua/sidekick/` (`config.lua`, `nes/`, `status.lua`, etc.).
- Tests are written with `mini.test` and live in `tests/`. Specs are table-driven whenever possible.
- Docs are generated automatically via `./scripts/docs`, which extracts Lua annotations to update `README.md` sections.
- Code style is Lua with `stylua` / `selene` configs already included.

## Everyday Commands

- `./scripts/test` – runs the `mini.test` suite using the Lazy.nvim harness; automatically installs test dependencies. Set `LAZY_OFFLINE=1` when you need to skip the bootstrap download (for fully offline CI).
- `./scripts/docs` – regenerates docs in `README.md` using the snippets in `tests/readme.lua`.
- `stylua lua tests` – format Lua source and tests when needed.
- `selene` – lint Lua files (if selene is installed in the environment).
- Inspect Neovim help topics from the CLI:

  ```bash
  # show all doc paths then grep for a topic
  nvim --headless '+lua print(table.concat(vim.api.nvim_get_runtime_file("doc/*.txt", true), " "))' +qall \
    | xargs rg "vim.text.diff" -C4

  # jump straight to a help entry and print the next 50 lines
  nvim --headless \
    '+lua vim.cmd.help("nvim_buf_set_extmark"); print(table.concat(vim.api.nvim_buf_get_lines(0, vim.fn.line(".") - 1, vim.fn.line(".") + 50, false), "\n"))' +qa
  ```

  Swap in the topic/API you need to research.

## Adding Features

- Respect the `Config.nes.enabled` callback so that users can disable NES globally (`vim.g.sidekick_nes = false`) or per-buffer (`vim.b[buf].sidekick_nes = false`).
- Keep new configuration options documented in `lua/sidekick/config.lua`; docs are generated from this file.
- When touching the diffing logic (`lua/sidekick/nes/diff.lua`), update or add table-driven tests in `tests/diff_spec.lua`.
- If a change affects status reporting, extend `tests/status_spec.lua` so notifications stay covered.

## Writing Tests

- Use `mini.test` assertions (`assert.are.same`, `assert.is_true`, etc.).
- Prefer table-driven specs for combinatorial cases (`tests/diff_spec.lua`, `tests/nes_spec.lua` demonstrate the style).
- Stub Neovim APIs carefully: reassign functions and restore them in `after_each` hooks. For upvalue-based helpers (e.g., health reporters), use `debug.setupvalue`.

## Things to Watch

- The repo may run in headless CI where network calls are blocked; stubs or fixtures should avoid third-party fetches.
- Avoid touching generated docs directly—run `./scripts/docs` instead.
- Maintain ASCII unless the surrounding context already uses Unicode (sign glyphs in configs are fine).
- Do not rely on `vim.lsp._set_clients`; tests should stub `Config.get_client` or `vim.lsp` methods directly.

## Useful Paths

- Core diff logic: `lua/sidekick/nes/diff.lua`
- NES orchestration: `lua/sidekick/nes/init.lua`
- Treesitter helpers: `lua/sidekick/treesitter.lua`
- Status integration: `lua/sidekick/status.lua`
- Tests entry point: `tests/minit.lua`

Keep this sheet handy when automating changes or onboarding new agents.
