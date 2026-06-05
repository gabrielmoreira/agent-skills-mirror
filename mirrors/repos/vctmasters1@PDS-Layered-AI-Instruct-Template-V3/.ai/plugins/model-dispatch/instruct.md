# Model Dispatch — Plugin Instructions

**Scope**: `.ai/plugins/model-dispatch/`
**Last Updated**: 2026-06-04

> Depth-priority leaf. Authoritative for work performed inside this plugin
> directory only. Outside this directory the framework's normal rules apply.

---

## Contents

| Section | What's here |
|---------|-------------|
| [Purpose](#purpose) | Why this plugin exists |
| [Authority](#authority) | What this file governs and what it does not |
| [Tier Naming](#tier-naming) | How tier names are formed |
| [The `model:` Frontmatter Field](#the-model-frontmatter-field) | Contract for agents and prompts |
| [Privacy Pinning](#privacy-pinning) | When a task MUST stay local |
| [Adding a New Tier](#adding-a-new-tier) | Step-by-step |
| [Adding a New Adapter](#adding-a-new-adapter) | Step-by-step |
| [Discovery Scripts](#discovery-scripts) | Conventions for `scripts/detect-*.ps1` |

---

## Purpose

Express **policy** for which class of model handles which class of task, without baking provider choices into the core framework. Concrete dispatch is left to the runtime that reads the policy.

## Authority

This file is authoritative for:

- The schema of `tiers.yaml`.
- The meaning of `model:` frontmatter values.
- Naming and shape of files inside this plugin directory.

This file is **not** authoritative for:

- Whether any specific agent uses a model — that lives in the agent's own frontmatter.
- How the runtime actually dispatches a call — that is the runtime's concern.
- Provider-specific behaviour — that lives in `adapters/*.md`.

## Tier Naming

- Use kebab-case.
- Encode the **constraint** the tier guarantees, not a vendor name. Good: `local-fast`, `local-strong`, `cloud-frontier`, `local-vision`, `local-embed`. Bad: `gpt-5`, `qwen-27b`.
- Names are stable identifiers — renaming a tier requires updating every `model:` frontmatter reference. Consult the naming agent before renaming.

## The `model:` Frontmatter Field

When this plugin is `experimental` or `stable`, an agent or prompt MAY add:

```yaml
---
description: ...
tools: [...]
model: local-strong       # MUST exist as a key under `tiers:` in tiers.yaml
---
```

Rules:

- `model:` is **optional**. Absent = "no preference; runtime decides."
- The value MUST resolve to a tier in the active `tiers.yaml`.
- The validator check `model-tier-resolves` enforces this when the plugin is active.

## Privacy Pinning

If `tiers.yaml` marks a tier with `privacy: local-only: true`, the runtime MUST NOT fall back to a cloud tier when the local tier is unavailable. It must surface an error and wait. This protects:

- Tasks touching credentials, customer data, or proprietary source.
- Adopters operating in regulated environments.

The `pds-man-environment` agent should refuse to silently downgrade.

## Adding a New Tier

1. Open `tiers.yaml` (or `tiers.example.yaml` if still in template form).
2. Add the tier under `tiers:`. Include `description:`, `provider:`, `endpoint:`, `model_id:`, and `privacy:` keys per the example.
3. Update [README.md](README.md) if the new tier introduces a new privacy class or constraint.
4. Run the validator.

## Adding a New Adapter

1. Create `adapters/<provider>.md`.
2. Document: endpoint URL pattern, authentication mechanism, request/response shape, known limitations, how to detect availability.
3. Reference the adapter from any tier that uses it (`provider: <provider>` in `tiers.yaml`).
4. Do NOT add adapter code here — adapter files are contracts, not implementations.

## Discovery Scripts

Scripts under `scripts/` MUST:

- Be **read-only**. No installs, no config writes, no API calls that mutate state.
- Print human-readable output (not JSON) — they target adopters running them interactively.
- Fail soft. If a probe target is offline, report "not detected" and continue.
- Honour [.ai/environment.md](../../environment.md) — never mutate the host.
