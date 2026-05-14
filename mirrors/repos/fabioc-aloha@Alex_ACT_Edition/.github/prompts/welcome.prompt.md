---
description: "First-session orientation and cross-machine user settings bootstrap"
mode: agent
lastReviewed: 2026-05-13
---

# Welcome

Use this on first session setup (or when moving to a new machine) to apply a stable user-level VS Code policy.

## Objective

Produce and apply a portable settings payload at user scope so workspace settings do not override fleet behavior.

## User Settings Payload (Stable Only)

Use this JSON payload:

```json
{
  "update.mode": "default",
  "extensions.autoUpdate": true,
  "extensions.autoCheckUpdates": true,
  "extensions.autoUpdateOnlyEnabledExtensions": false,

  "chat.agent.enabled": true,
  "chat.useAgentSkills": true,
  "chat.includeReferencedInstructions": true,
  "chat.commandCenter.enabled": true,
  "chat.todoListTool.enabled": true,
  "chat.planWidget.inlineEditor.enabled": true,

  "github.copilot.chat.copilotMemory.enabled": true,
  "github.copilot.chat.tools.memory.enabled": true,
  "github.copilot.chat.codesearch.enabled": true,
  "github.copilot.chat.responsesApi.toolSearchTool.enabled": true,
  "github.copilot.chat.agent.modelDetails.enabled": true,
  "mermaid-chat.enabled": true,

  "chat.tools.terminal.backgroundNotifications": true,
  "chat.tools.terminal.detachBackgroundProcesses": true,
  "terminal.integrated.tabs.allowAgentCliTitle": true,

  "chat.experimental.implicitContext.enabled": false,
  "chat.experimental.symbolTools.cacheStable": false
}
```

## Apply Steps

1. Detect user settings path:
   - Windows: `%APPDATA%\\Code\\User\\settings.json`
   - macOS: `~/Library/Application Support/Code/User/settings.json`
   - Linux: `~/.config/Code/User/settings.json`

2. Merge payload into existing user settings (do not overwrite unrelated keys).

3. Verify applied keys by reading back values.

4. Report exactly which keys changed and which were already compliant.

## Windows Reference Command

Use this PowerShell merge pattern:

```powershell
$userSettings = Join-Path $env:APPDATA 'Code\\User\\settings.json'
if (-not (Test-Path $userSettings)) { '{}' | Set-Content -Path $userSettings -Encoding UTF8 }
$current = Get-Content -Path $userSettings -Raw | ConvertFrom-Json -AsHashtable
$payload = @{
  "update.mode" = "default"
  "extensions.autoUpdate" = $true
  "extensions.autoCheckUpdates" = $true
  "extensions.autoUpdateOnlyEnabledExtensions" = $false
  "chat.agent.enabled" = $true
  "chat.useAgentSkills" = $true
  "chat.includeReferencedInstructions" = $true
  "chat.commandCenter.enabled" = $true
  "chat.todoListTool.enabled" = $true
  "chat.planWidget.inlineEditor.enabled" = $true
  "github.copilot.chat.copilotMemory.enabled" = $true
  "github.copilot.chat.tools.memory.enabled" = $true
  "github.copilot.chat.codesearch.enabled" = $true
  "github.copilot.chat.responsesApi.toolSearchTool.enabled" = $true
  "github.copilot.chat.agent.modelDetails.enabled" = $true
  "mermaid-chat.enabled" = $true
  "chat.tools.terminal.backgroundNotifications" = $true
  "chat.tools.terminal.detachBackgroundProcesses" = $true
  "terminal.integrated.tabs.allowAgentCliTitle" = $true
  "chat.experimental.implicitContext.enabled" = $false
  "chat.experimental.symbolTools.cacheStable" = $false
}
foreach ($k in $payload.Keys) { $current[$k] = $payload[$k] }
$current | ConvertTo-Json -Depth 30 | Set-Content -Path $userSettings -Encoding UTF8
```

## Guardrails

- User-scope only. Do not write these keys to workspace `.vscode/settings.json`.
- Stable settings only. Keep preview/experimental toggles off unless explicitly requested.
- Preserve all unrelated existing user settings.
