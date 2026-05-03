# azure-deployment-preflight

Performs comprehensive preflight validation of Bicep deployments to Azure, including template syntax validation, what-if analysis, and permission checks. Use this skill before any deployment to Azure to preview changes, identify potential issues, and ensure the deployment will succeed. Activate when users mention deploying to Azure, validating Bicep files, checking deployment permissions, previewing infrastructure changes, running what-if, or preparing for azd provision.

## Quick Facts

| Field | Value |
| --- | --- |
| **Category** | cloud-infrastructure |
| **Shape** | `.S..` |
| **Tier** | standard |
| **Token cost** | ~2292 tokens |
| **Engines** | copilot |
| **Requires Edition** | >=1.0.0 |
| **Keywords** | azure, deployment, preflight, performs, comprehensive, validation, bicep, deployments |

## Installation

From ACT Edition:

```text
/mall install azure-deployment-preflight
```

Or manually copy the plugin contents to `.github/skills/local/azure-deployment-preflight/`.

## Artifacts

- **skill**: `SKILL.md`

## Shape: `.S..`

Skill only -- domain knowledge loaded when pattern matches.
