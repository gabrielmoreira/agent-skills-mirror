---
type: skill
lifecycle: stable
inheritance: inheritable
name: vscode-environment
description: Optimal workspace setup for productivity.
tier: standard
applyTo: '**/*vscode*,**/*environment*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# VS Code Environment Skill


> Optimal workspace setup for productivity.

## Essential Extensions

| Category | Extensions |
| -------- | ---------- |
| AI | GitHub Copilot, Copilot Chat |
| Git | GitLens, Git Graph |
| Markdown | Markdown All in One, markdownlint |
| Format | Prettier, EditorConfig |
| Diagrams | Mermaid Preview, Draw.io |

## Workspace Settings

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.rulers": [80, 120],
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": true
}
```

## extensions.json

```json
{
  "recommendations": [
    "github.copilot",
    "github.copilot-chat",
    "eamodio.gitlens",
    "esbenp.prettier-vscode",
    "davidanson.vscode-markdownlint"
  ]
}
```

## launch.json Patterns

| Type | Use |
| ---- | --- |
| Node.js | `"type": "node"` |
| TypeScript | `"type": "node", "preLaunchTask": "tsc"` |
| Extension | `"type": "extensionHost"` |
| Python | `"type": "debugpy"` |

## tasks.json Patterns

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "build",
      "type": "npm",
      "script": "compile",
      "problemMatcher": "$tsc"
    }
  ]
}
```

## Workspace Structure

```text
.vscode/
├── settings.json      # Workspace settings
├── extensions.json    # Recommended extensions
├── launch.json        # Debug configs
├── tasks.json         # Build tasks
└── *.code-snippets    # Custom snippets
```

## Multi-Root Workspaces

```json
{
  "folders": [
    { "path": "frontend" },
    { "path": "backend" }
  ],
  "settings": {}
}
```

## Per-Language Settings

```json
{
  "[markdown]": {
    "editor.wordWrap": "on",
    "editor.quickSuggestions": false
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```
