---
name: setup-ai-operations
description: "Configure optional Microsoft Foundry, Hugging Face, and ElevenLabs provider access for AI Operations. Use after installing the plugin, when a provider is unavailable, when auditing authentication, or when previewing and provisioning the exact ElevenLabs private runtime."
lastReviewed: 2026-08-11
---

# Setup AI Operations

Configure only the providers the user chooses. Plugin installation is not
authorization to authenticate providers, install Python packages, or spend
credits.

## Onboarding Boundary

Onboarding ends after plugin installation and component verification. During
onboarding, do not ask for API keys, tokens, or other credentials, do not
initiate provider login, and do not provision a provider runtime. Report that
planning is available without credentials. Defer provider login and
authentication until an approved execution plan selects a provider and
execution requires access.

## Procedure

1. Determine whether this is onboarding or just-in-time preparation for a
   selected execution.
2. During onboarding, inspect the MCP definitions, report all three providers
   as unverified, state that planning is ready, and stop without authentication
   or provisioning.
3. After an approved plan selects a provider and execution requires access,
   configure only that provider.
4. For Foundry, start `aiops-foundry` at `https://mcp.ai.azure.com` and
   complete Microsoft Entra ID login. Confirm an Azure subscription, Foundry
   project, and Contributor-or-higher access before execution.
5. For Hugging Face, start `aiops-huggingface` and complete the first-party
   login flow. Provider settings control enabled Hub and Space tools.
6. Keep all provider credentials optional during installation and planning.
   Do not request or validate an API key until the user has selected a model and
   operation that needs it.
7. After model selection, route hosted providers through provider-native login
   and local providers through the exact host environment variable or approved
   secret storage. Never write, print, or request the secret value in chat.
8. For ElevenLabs runtime setup, identify `ELEVENLABS_API_KEY` as the selected
   execution secret when the chosen model requires it.
9. Run `scripts/provision-runtime.mjs` without flags. Show its preview: Python,
   exact `elevenlabs-mcp==0.12.2` package, private runtime target, and package
   index policy.
10. Ask for explicit consent before `--apply`.
11. On approval, rerun the provisioner with `--apply`.
12. Reload the host, then run `npm run verify` from the plugin source or its
   equivalent installed-path verifier.
13. Report each provider independently. One unavailable provider does not make
   the optional plugin unusable for the others.

## Runtime Boundary

- Hugging Face uses a publisher-hosted HTTP MCP server.
- ElevenLabs uses a plugin-private Python virtual environment.
- Provisioning never installs globally and never supplies `--index-url` or an
  alternate package source.
- `ELEVENLABS_MCP_OUTPUT_MODE=resources` avoids implicit Desktop writes.
- Provider credentials stay in provider OAuth, environment variables, or host
  secret storage.
- Host environment variables and approved secret storage remain outside
   generated plans, logs, manifests, and commits.

## Failure Handling

| Signal | Action |
| --- | --- |
| Hosted provider needs login | Complete the provider-native flow; do not invent headers. |
| Python is below 3.11 | Stop and select a supported interpreter before provisioning. |
| Package install fails | Report pip's error without adding an index override. |
| Runtime is missing | Re-run preview and consented apply. Do not replace it with `uvx` or unpinned pip. |
| Selected model needs a missing API key | Stop execution, name the exact host environment variable or approved secret-storage route, and keep other providers usable. |

## Anti-Patterns

| Anti-pattern | Correction |
| --- | --- |
| Configure every provider automatically | Ask which providers the user wants. |
| Paste tokens into MCP JSON | Use OAuth, environment, or secret storage. |
| Run `pip install` globally | Provision the plugin-private environment. |
| Apply without preview | Show the exact package and target first. |
| Treat setup as spending consent | Execution requires a separate approved plan. |

## Would Revise If

Revise by **2026-11-11** if provider authentication cannot be completed on a
supported host, if the exact ElevenLabs runtime fails after successful setup,
or if two users confuse provider setup with consent to execute paid work.
