#!/usr/bin/env bash
set -euo pipefail

workspace="${1:-$PWD}"
if [[ ! -d "$workspace" ]]; then
  echo "[apply] workspace not found: $workspace" >&2
  exit 2
fi

skill_root="$HOME/.copilot/skills/playwright-vision-low-resource"
mkdir -p "$workspace/.vscode"

mcp_target="$workspace/.vscode/mcp.json"
mcp_template="$skill_root/templates/mcp.low-resource.jsonc"

if [[ -f "$mcp_target" ]]; then
  cp "$mcp_target" "$mcp_target.bak.$(date +%Y%m%d-%H%M%S)"
  cp "$mcp_template" "$workspace/.vscode/mcp.low-resource.recommended.json"
  echo "[apply] existing .vscode/mcp.json preserved"
  echo "[apply] wrote recommendation: .vscode/mcp.low-resource.recommended.json"
else
  cp "$mcp_template" "$mcp_target"
  echo "[apply] created .vscode/mcp.json from low-resource template"
fi

pw_cfg="$workspace/playwright.low-resource.config.ts"
if [[ ! -f "$pw_cfg" ]]; then
  cp "$skill_root/templates/playwright.low-resource.config.ts" "$pw_cfg"
  echo "[apply] created playwright.low-resource.config.ts"
else
  echo "[apply] kept existing playwright.low-resource.config.ts"
fi

echo "[apply] done"
