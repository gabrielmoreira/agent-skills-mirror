# GEMINI.md - peon-ping

## Project Overview
`peon-ping` is a cross-platform (macOS, Linux, WSL, Windows) notification system that brings game character voice lines and visual overlay banners to AI coding agents. It helps developers maintain flow by providing audible and visual feedback when an agent completes a task, requires input, or encounters an error.

The project implements the [Coding Event Sound Pack Specification (CESP)](https://github.com/PeonPing/openpeon), an open standard for coding event sounds.

### Main Technologies
- **Shell Scripting:** Core logic in `peon.sh`, `relay.sh`, and various `install.sh`/`uninstall.sh` scripts.
- **Python:** Embedded within shell scripts for robust JSON parsing and complex logic.
- **TypeScript:** Used for the OpenCode adapter, MCP server, and the documentation site.
- **Next.js:** Powers the project's website and documentation in `docs/`.
- **PowerShell:** Provides native Windows and WSL support.
- **Swift:** Optimized audio playback on macOS (`peon-play.swift`).
- **BATS (Bash Automated Testing System):** Primary testing framework for shell scripts.

---

## Architecture

- **Core (`peon.sh`):** The primary entry point for hooks. It handles event mapping, sound selection, and triggers playback/notifications.
- **Adapters (`adapters/`):** Translation layers for various IDEs/Agents (Claude Code, Gemini CLI, GitHub Copilot, Cursor, Windsurf, etc.) to map their specific events to CESP categories.
- **MCP Server (`mcp/`):** A Model Context Protocol server that allows AI agents to trigger sounds directly via tool calls.
- **Relay (`relay.sh`):** An HTTP server that allows remote environments (SSH, Devcontainers, Codespaces) to route audio and notifications back to a local machine.
- **Trainer (`trainer/`):** A built-in exercise reminder system that piggybacks on coding sessions.
- **Packs:** Sound packs are stored in `packs/` (or `~/.openpeon/packs/`) and defined by `openpeon.json` manifests.

---

## Building and Running

### Installation
- **macOS/Linux:** `curl -fsSL https://peonping.com/install | bash`
- **Windows:** `Invoke-WebRequest -Uri "https://peonping.com/install.ps1" | Invoke-Expression`
- **Homebrew:** `brew install PeonPing/tap/peon-ping`

### CLI Commands
The `peon` command (alias for `peon.sh`) is the main management interface:
- `peon status`: Check current configuration and active pack.
- `peon toggle`: Mute/unmute sounds and notifications.
- `peon volume 0.5`: Set playback volume (0.0 - 1.0).
- `peon packs list`: List installed sound packs.
- `peon packs use <name>`: Switch to a specific pack.
- `peon relay --daemon`: Start the audio relay for remote sessions.
- `peon trainer on`: Enable exercise reminder mode.

### Testing
- **Shell Tests:** Run `bats tests/` (requires [BATS](https://github.com/bats-core/bats-core)).
- **TypeScript Tests:**
  - Adapters: `cd adapters/opencode && npm test`
  - MCP: `cd mcp && npm test` (if applicable, uses Vitest).
- **Web Development:** `cd docs && npm run dev` to start the documentation site.

---

## Development Conventions

### Coding Style
- **Portability:** Scripts should aim for compatibility across macOS, Linux (various distros), and WSL.
- **JSON Processing:** Use the embedded Python pattern (`python3 -c "..."`) for parsing JSON instead of external tools like `jq` to minimize dependencies.
- **Async Execution:** Playback and notifications should be backgrounded (`&`) to avoid blocking the AI agent's flow.
- **Mocking:** Tests use a comprehensive mocking environment in `tests/setup.bash` to intercept system calls like `afplay`, `osascript`, and `curl`.

### Sound Pack Specification (CESP)
All sound packs must follow the CESP standard. Standard categories include:
- `session.start`: Greeting when a session begins.
- `task.acknowledge`: Agent acknowledges a task.
- `task.complete`: Task finished successfully.
- `task.error`: Task failed or encountered an error.
- `input.required`: Agent is waiting for user input.
- `resource.limit`: Rate or token limit reached.
- `user.spam`: Rapid prompt detection (Easter egg).

### Adding Adapters
New adapters should be placed in `adapters/` and should map IDE-specific hooks to the standard `peon.sh` categories or trigger sounds directly using the logic in `peon.sh`.
