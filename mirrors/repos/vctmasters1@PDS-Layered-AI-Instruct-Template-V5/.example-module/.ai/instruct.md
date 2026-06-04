# .example-module — Module AI Instructions

**Scope**: Authoritative for everything inside `.example-module/`
**Last Updated**: 2026-05-25

> Deeper than root `.ai/instruct.md` — this file is authoritative when working in this directory.
> The root `.ai/instruct.md` provides project-wide context only.

---

## Contents

| Section | What's here |
|---|-------------|
| [Module Overview](#module-overview) | What this module does |
| [Directory Structure](#directory-structure) | Internal layout |
| [Module-Specific Rules](#module-specific-rules) | Rules that apply only here |
| [Subdirectory Contexts](#subdirectory-contexts) | Deeper `.ai/instruct.md` files if any |
| [Global Rules Reference](#global-rules-reference) | Links to cross-cutting rules (do not restate) |

---

## Module Overview

> **Replace with your module description.**

`.example-module` is a [DESCRIPTION]. It is responsible for [RESPONSIBILITY].

**Entry point**: `src/index.ts` *(replace with real path)*
**Exposed interface**: [API endpoints / exports / events / etc.]
**Dependencies on other modules**: [List any]
**External dependencies**: [Third-party services, libraries]

---

## Directory Structure

```
.example-module/
├── .ai/
│   └── instruct.md         ← This file (authoritative for this module)
├── src/
│   ├── index.ts            ← Entry point
│   ├── [layer-a]/          ← [what it does]
│   └── [layer-b]/          ← [what it does]
├── .env.example            ← Environment variable template for this module (committed)
├── .env                    ← Real values (gitignored)
└── .dev-docs/
    ├── index.md            ← Dev notes navigation
    └── .old/               ← Stale docs (ignore by default)
```

---

## Module-Specific Rules

> **Replace with rules that apply only to this module.**

- [Rule 1: e.g., all database queries must go through the repository layer]
- [Rule 2: e.g., never call external APIs directly from route handlers — use the service layer]
- [Rule 3: e.g., all responses must use the standard `{ data, error, meta }` envelope]

### Naming Within This Module

> If this module has its own naming conventions that differ from the global ones, document them here.
> Otherwise, remove this section and reference `.ai/conventions.md`.

---

## Subdirectory Contexts

> If subdirectories within this module have their own `.ai/instruct.md` files, list them here.

| Subdirectory | File | Notes |
|-------------|------|-------|
| *(none yet)* | — | — |

---

## Global Rules Reference

> Do not restate global rules here. Reference them.

> **→ [No-Duplication Rule](../../.ai/conventions.md#no-duplication-rule)** — instructions live in one place.
> **→ [Never Delete Rule](../../.ai/maintenance.md#never-delete-rule)** — archive instead of deleting files.
> **→ [Never Reset Databases](../../.ai/maintenance.md#never-reset-databases)** — what requires confirmation.
> **→ [Never Commit Credentials](../../.ai/credentials.md#never-commit-credentials)** — all secrets via environment variables.
