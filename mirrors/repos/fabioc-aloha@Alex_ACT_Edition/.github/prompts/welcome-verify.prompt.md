---
description: "Read-only audit of user-level VS Code/Copilot settings compliance"
mode: agent
lastReviewed: 2026-05-13
---

# Welcome Verify

Use this to verify fleet policy compliance on a machine without changing any settings.

## Objective

Audit user-scope VS Code settings against the central baseline and report drift.

## Baseline Keys

Expected values:

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

## Read-Only Steps

1. Resolve the user settings path for the current OS.
2. Read `settings.json` as-is.
3. Compare each baseline key/value pair.
4. Classify each key:
   - `compliant` (value matches)
   - `drift` (key exists but value differs)
   - `missing` (key absent)
5. Report compliance summary and drift table.
6. Recommend running `/welcome` only if drift or missing keys are found.

## Output Format

```text
Compliance: <X>/<N> keys
Drift: <count>
Missing: <count>

Drifted keys:
- key: expected=<...>, actual=<...>

Missing keys:
- key: expected=<...>

Recommendation:
- No action required | Run /welcome to apply baseline
```

## Guardrails

- Do not modify files.
- User-scope only (never evaluate workspace `.vscode/settings.json` for policy compliance).
- Treat unknown extra keys as informational only, not non-compliance.
