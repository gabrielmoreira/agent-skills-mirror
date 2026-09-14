---
description: Build, run, test, and ship OpenHuman from source.
icon: code-branch
---

# Overview

OpenHuman is open source under GPLv3 at [github.com/tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman). This section is for contributors and anyone running OpenHuman from source.

If you just want to use the app, head to [Getting Started](../overview/getting-started.md). If you're here to read the architecture, hack on a feature, or land a PR, you're in the right place.

---

## Where things live

| Path        | What's there                                                                                                      |
| ----------- | ----------------------------------------------------------------------------------------------------------------- |
| `app/`      | pnpm workspace `openhuman-app`. Vite + React frontend (`app/src/`) and the Tauri desktop host (`crates/openhuman-app/`). |
| `crates/`   | Rust crates: `openhuman-core` (lib `openhuman_core` + the `openhuman-core` CLI binary; domains under `src/<domain>/`, JSON-RPC, MCP routing), `openhuman-app` (Tauri host), `openhuman-embed` (library facade), `openhuman-rpc` (shared RPC contracts + HTTP client), `openhuman-tui` (terminal frontend). |
| `gitbooks/` | This site (the public-facing docs).                                                                               |
| `docs/`     | Internal maintainer docs: test-coverage matrix, release smoke checklist, library benchmarking and minimal-recipe notes, translated READMEs, `community/`. |

`AGENTS.md` at the repo root is the source of truth for AI agents working on the codebase (`CLAUDE.md` is a symlink to it). Same rules apply to humans.

---

## Start here

If it's your first time pulling the repo:

1. [**Getting Set Up**](getting-set-up.md). Toolchain, dependencies, the Tauri CLI - everything `pnpm dev` needs to actually start.
2. [**Building the Rust Core**](building-rust-core.md). Fresh-machine setup for the Rust workspace only: pinned toolchain, OS packages, and exact `cargo` commands.
3. [**Architecture**](architecture.md). How the desktop app, the in-process Rust core, the JSON-RPC bridge, and the dual sockets fit together. Read this before you make non-trivial changes.
4. [**Frontend**](architecture/frontend.md) and [**Tauri Shell**](architecture/tauri-shell.md). The React app and the desktop host that wraps it.
5. [**MCP Server**](mcp-server.md). Opt-in stdio MCP mode for exposing read-only OpenHuman memory tools to local clients.

---

## Testing

OpenHuman ships with three test layers. Know which one your change belongs in:

- [**Testing Strategy**](testing-strategy.md). When to write Vitest vs cargo tests vs WDIO.
- [**E2E Testing**](e2e-testing.md). WDIO/Appium specs, dual-platform setup (Linux tauri-driver, macOS Appium Mac2), and how to run a single spec locally.
- [**Agent Observability**](agent-observability.md). The artifact-capture layer that makes E2E and agent runs debuggable after the fact.

PRs must clear the **≥ 80% coverage on changed lines** gate. Add tests for new behavior, not just the happy path.

---

## Shipping

- [**Release Policy**](release-policy.md). Version policy, release cadence, OAuth + installer rules.
- [**Cloud Deploy**](../features/cloud-deploy.md). Backend/cloud-side deployment when a change crosses the desktop boundary.

---

## Going deeper

- [**Agent Harness**](architecture/agent-harness.md). The tinyagents-based turn loop (checkpointing, circuit breakers, sub-agent handback, journals/replay) and how to extend the tool surface.
- [**Workflows**](../features/workflows.md). The tinyflows-backed `flows` domain: triggers, trust origins, approval-gated runs, and the `flows_*` RPC surface.
- [**Hooks**](hooks.md). User-owned scripts that run before a tool executes, after a file edit, or when a turn finishes.
- [**Chromium Embedded Framework**](cef.md). Historical design notes from the CEF era; the shell now runs on stock Tauri (Wry).

For features still being built, the Subconscious Loop page covers the background task evaluation system end-to-end.

---

## Contributing

- Open issues and PRs at [tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman).
- PRs target `main`. Push to your fork, not upstream.
- Follow [`CONTRIBUTING.md`](../../CONTRIBUTING.md) and the issue/PR templates.
- Keep changes focused. A bug fix doesn't need surrounding cleanup; a one-shot operation doesn't need a helper.

Help building toward AGI doesn't have to mean shipping a kernel - bugfixes, docs, integrations, and tests all move the bar.
