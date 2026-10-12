#!/usr/bin/env bash
set -euo pipefail

# Disable Serena's anonymous usage ping (OS/version/backend) for MCP-launched instances.
export SERENA_USAGE_REPORTING=false

# --project-from-cwd: auto-activate the project so agents never need activate_project.
# --enable-web-dashboard=false: parallel agent sessions would each spawn an idle
# dashboard HTTP server (ports 24282+); logs remain available under ~/.serena/logs.
set -- --project-from-cwd --enable-web-dashboard=false "$@"

# Default to the claude-code context when the client passes none: Serena's own
# default (desktop-app) re-enables shell/file/search tools that CLI agents already
# have natively. Codex passes --context=codex via ~/.codex/config.toml; Claude Code
# passes --context=claude-code via ~/.claude.json, but that file is app-managed
# state, so keep a durable fallback here.
case " $* " in
*" --context "* | *" --context="*) ;;
*) set -- "$@" --context=claude-code ;;
esac

exec "$HOME/.local/bin/serena" start-mcp-server "$@"
