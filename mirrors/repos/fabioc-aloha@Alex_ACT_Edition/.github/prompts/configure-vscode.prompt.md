---
description: "Apply baseline VS Code user-scope settings for fleet policy compliance"
mode: agent
lastReviewed: 2026-05-25
---

# Configure VS Code

Use this on first session setup (or when moving to a new machine) to apply a stable user-level VS Code policy.

For a first-session **orientation tour** (identity, what's loaded, where to start), use `/welcome` instead.

## Objective

Produce and apply a portable settings payload at user scope so workspace settings do not override fleet behavior.

## Source of truth

The baseline payload lives in `.github/config/welcome-baseline.json` (`settings` object). Both `/configure-vscode` (apply) and `/configure-vscode-verify` (audit) load from the same file — update once.

## Apply Steps

1. Load the baseline from `.github/config/welcome-baseline.json` (`settings` object).

2. Detect user settings path:
   - Windows: `%APPDATA%\Code\User\settings.json`
   - macOS: `~/Library/Application Support/Code/User/settings.json`
   - Linux: `~/.config/Code/User/settings.json`

3. Merge each baseline key/value into existing user settings (do not overwrite unrelated keys).

4. Verify applied keys by reading back values.

5. Report exactly which keys changed and which were already compliant.

## Windows Reference Command

```powershell
$baseline = Get-Content '.github\config\welcome-baseline.json' -Raw | ConvertFrom-Json -AsHashtable
$userSettings = Join-Path $env:APPDATA 'Code\User\settings.json'
if (-not (Test-Path $userSettings)) { '{}' | Set-Content -Path $userSettings -Encoding UTF8 }
$current = Get-Content -Path $userSettings -Raw | ConvertFrom-Json -AsHashtable
foreach ($k in $baseline.settings.Keys) { $current[$k] = $baseline.settings[$k] }
$current | ConvertTo-Json -Depth 30 | Set-Content -Path $userSettings -Encoding UTF8
```

## Guardrails

- User-scope only. Do not write these keys to workspace `.vscode/settings.json`.
- Stable settings only — the baseline file is the source of truth; do not inline payload here.
- Preserve all unrelated existing user settings.
