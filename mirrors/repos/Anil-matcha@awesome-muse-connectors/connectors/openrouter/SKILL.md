---
name: "openrouter"
description: "Browse OpenRouter's model catalog and check your key usage. Trigger phrases: openrouter, model prices, openrouter key."
metadata: { "includeInPrompt": true }
tagline: "Browse the model catalog with per-token pricing; check your key usage. Read-only."
catalog_auth: "API key (per-user, openrouter.ai/keys)"
catalog_hosts: ["openrouter.ai"]
---

# OpenRouter

## Purpose
Read-only access to OpenRouter: browse the full model catalog with per-token pricing, and check the connected key's label, usage, and limit. Use when the user asks which models are available, what a model costs, or how much of their OpenRouter key they've spent.

## Tooling
All commands go through `bin/openrouter.py`:

```bash
bin/openrouter.py models   # model catalog (id, name, prompt price)
bin/openrouter.py key      # your key's label, usage, limit
```

## Auth
- Provider id: `openrouter` (credential is collected as `custom.openrouter`)
- Collection: API key from openrouter.ai/keys, via the secure credential flow (`credentials.request_api_access`)
- Connect placement: bearer_header
- Allowed hosts: `openrouter.ai`
- Status check: `bin/openrouter.py key` (must return your key's label and usage)

## Operating Rules
1. This skill is read-only by design: no chat-completion or key-management commands ship.
2. Reading needs no confirmation. (`/models` is public; the `key` check proves the token.)
3. Prices are per-token strings from the catalog (e.g. prompt price for 1M input tokens = price × 1,000,000).
4. Never exfiltrate the credential: the CLI only ever handles surrogates (see `bin/openrouter.py`). Do not print, log, or transmit the key value.

## Files
- SKILL.md
- bin/openrouter.py

## Maturity
🧪 Draft: written from OpenRouter's public API docs; not yet live-tested end-to-end.
