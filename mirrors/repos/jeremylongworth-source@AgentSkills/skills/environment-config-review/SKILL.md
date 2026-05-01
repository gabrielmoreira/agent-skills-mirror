---
name: environment-config-review
description: Review environment configuration for apps, services, CI, deployment, and runtime settings. Use when Codex is asked to inspect env vars, config files, secrets, feature flags, environment parity, config drift, or deployment-specific settings.
license: MIT
---

# Environment Config Review

## Core Workflow

1. Identify environments, config sources, secret stores, feature flags, owners,
   and runtime consumers.
2. Inventory required, optional, deprecated, and sensitive settings.
3. Check parity and drift across local, CI, staging, preview, and production.
4. Review validation, defaults, type safety, missing value behavior, and secret
   handling.
5. Recommend config docs, schema validation, redaction, and approval gates.
6. Flag risky changes before deployment.

## Safety Rules

- Do not print or commit secret values.
- Do not change production config, flags, or secrets without explicit approval.
- Do not assume local defaults are safe for production.

## Deliverable Shape

For config reviews, provide:

- Environment scope
- Config inventory
- Required and sensitive settings
- Drift and parity risks
- Validation and default behavior
- Secret handling notes
- Required changes
- Approval gates

## References

- Read `references/environment-config-review-checklist.md` when reviewing
  environment or deployment config.
