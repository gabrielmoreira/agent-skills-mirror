# GitHub Copilot CLI Provider Configuration

This file contains Copilot-specific instructions for Claude Octopus workflows.

## Provider Information

- **Provider**: GitHub Copilot CLI (optional)
- **Emoji**: 🟢
- **API Key**: None required — uses GitHub Copilot subscription
- **CLI Command**: `copilot -p` (programmatic mode)
- **Agent Types**: `copilot`, `copilot-research`
- **Cost**: Zero additional — included in GitHub Copilot subscription (Pro, Pro+, Business, Enterprise). Each prompt = 1 premium request from monthly quota.

## Detection

- CLI: `command -v copilot`
- Auth check (precedence order):
  1. `COPILOT_GITHUB_TOKEN` env var (fine-grained PAT with "Copilot Requests" permission)
  2. `GH_TOKEN` env var
  3. `GITHUB_TOKEN` env var
  4. OAuth token from `~/.copilot/config.json` (keychain)
  5. `gh` CLI auth fallback (`gh auth status`)

If the CLI is not installed or not authenticated, silently skip — no errors, no warnings.

## Authentication Setup

### Option 1: Interactive Login (recommended for local dev)
```bash
copilot login
```

### Option 2: Fine-Grained PAT (recommended for CI/automation)
1. Create at https://github.com/settings/personal-access-tokens/new
2. Enable "Copilot Requests" permission
3. Set env var:
```bash
export COPILOT_GITHUB_TOKEN="github_pat_..."
```

### Option 3: Reuse gh CLI Auth
If `gh auth login` is already configured, Copilot CLI uses it automatically.

**Note:** Classic PATs (`ghp_*`) are NOT supported. Use fine-grained PATs (`github_pat_*`).

## Dispatch Pattern

```bash
copilot -p "<prompt>" --no-ask-user
```

## Model Selection

Copilot CLI selects models internally. Default: Claude Sonnet 4.5. Users can configure via `/model` command in the CLI. Available models depend on subscription tier.

## Role Assignment

Copilot serves as:
- **Research assistant** — exploration and analysis via `copilot-research` agent type
- **General perspective** — additional viewpoint via `copilot` agent type

## Limitations

- Each prompt counts as 1 premium request against monthly subscription quota
- No direct model selection from orchestrate.sh (Copilot CLI manages internally)
- Output is plain text (no structured JSON)
- Requires GitHub Copilot subscription (not available on free tier)

## Timeout Configuration

Default timeout: 90 seconds. Configurable via `OCTOPUS_COPILOT_TIMEOUT` env var.

## Error Handling

Common errors:
- `unauthorized`: Not authenticated — run `copilot login`
- `Timeout`: Copilot response took too long — increase timeout
- `command not found`: CLI not installed — `brew install copilot-cli`
