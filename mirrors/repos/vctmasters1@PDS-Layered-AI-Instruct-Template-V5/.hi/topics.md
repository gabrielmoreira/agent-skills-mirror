# Suggested GitHub Repository Topics

When publishing this template (or a fork of it) to GitHub, add the following topics to maximize discoverability. Topics live under the repo **About** sidebar (gear icon → Topics).

## Core topics

- `copilot-template`
- `github-copilot`
- `ai-first-development`
- `copilot-agents`
- `copilot-skills`
- `layered-instructions`
- `ai-instruct`
- `agents-md`

## Supporting topics

- `developer-tools`
- `project-template`
- `monorepo-friendly`
- `vscode-template`
- `cursor-compatible`
- `mcp`

## Recommended repo description (About sidebar)

> A Copilot-ready project template using Depth-Priority Hierarchical-Instruct V1 — per-directory `.hi/instruct.md` rules, slash commands, custom agents, skills, hooks, and a drift validator.

## How to apply

```bash
# Using GitHub CLI — set description + homepage + topics in one shot:
gh repo edit \
  --description "A Copilot-ready project template using Depth-Priority Hierarchical-Instruct V1 — per-directory .hi/instruct.md rules, slash commands, custom agents, skills, hooks, and a drift validator." \
  --add-topic copilot-template,github-copilot,ai-first-development,copilot-agents,copilot-skills,layered-instructions,ai-instruct,agents-md
```

Or, in the GitHub UI: click the gear next to **About** on the repo page, paste the description, and paste the comma-separated topic list.
