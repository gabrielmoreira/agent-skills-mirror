# [PROJECT_NAME] — Root AI Instructions (Template Scaffold)

**Scope**: Authoritative for the entire project (workspace root)
**Last Updated**: 2026-05-25

> This is the **root-level** `.ai/instruct.md` template scaffold. In this template repository, placeholders are intentional.
> After adoption, this file becomes authoritative for your project-wide concerns once `/ai-onboard` (or manual setup) fills the fields.
> Module-level `.ai/instruct.md` files are **more authoritative** than this file when working inside those directories.
> See `.github/copilot-instructions.md` for how the hierarchy works.

---

## Contents

| Section | What's here |
|---|-------------|
| [Project Overview](#project-overview) | What this project is and does |
| [Architecture Overview](#architecture-overview) | High-level structure and tech stack |
| [Key Directories](#key-directories) | Directory map with links to module .ai/ instructions |
| [Global Rules Reference](#global-rules-reference) | Links to canonical cross-cutting rules |
| [AI-INSTRUCT Maintenance Rule](#ai-instruct-maintenance-rule) | When and how to update this system |

---

## Project Overview

> **Replace this section with your project description.**

**[PROJECT_NAME]** is a [one-sentence description of what the project does].

**Purpose**: [What problem does it solve? Who uses it?]

**Tech stack**:
- [e.g., TypeScript / Node.js / Express]
- [e.g., React / Vite / Tailwind]
- [e.g., PostgreSQL / TypeORM]
- [e.g., Docker / Railway]

**Primary language(s)**: [LANGUAGES]

**Environments**:
| Name | URL / Access | Notes |
|------|-------------|-------|
| Local dev | `localhost:[PORT]` | — |
| Staging | [URL] | — |
| Production | [URL] | — |

---

## Architecture Overview

> **Replace with your architecture diagram or description.**

```
[PROJECT_NAME]/
├── [module-a]/         ← [what it does — e.g., React frontend]
├── [module-b]/         ← [what it does — e.g., Express API + TypeORM]
├── [module-c]/         ← [what it does — e.g., shared DB entities]
└── [module-d]/         ← [what it does — e.g., firmware/device layer]
```

**Data flow**: [Describe how data moves through the system at a high level.]

**Key external dependencies**: [List critical third-party services: payment processors, email providers, cloud storage, etc.]

---

## Key Directories

| Directory | AI Instructions | Covers |
|-----------|-----------------|--------|
| Root | `.ai/instruct.md` (this file) | Project-wide rules and architecture |
| `.ai/` | (global shared files) | Cross-cutting rules: conventions, maintenance, credentials, index |
| `[module-a]/` | `[module-a]/.ai/instruct.md` | [description] |
| `[module-b]/` | `[module-b]/.ai/instruct.md` | [description] |
| `.example-module/` | `.example-module/.ai/instruct.md` | Bare scaffold for a new module (reference) |
| `.examples/` | `.examples/README.md` | Filled-in module showcases: `auth-api`, `data-layer`, `ui-component` |
| `.github/` | `.github/copilot-instructions.md` | AI tooling meta-instructions |
| `.cursor/` | `.cursor/rules/project.mdc` | Pointer rules so Cursor reads the same `.ai/` hierarchy |

> Add a row for every major directory that has its own `.ai/instruct.md`.

---

## Global Rules Reference

These rules are canonical and live in `.ai/`. **Do not restate them here — only link.**

| Rule | Canonical location |
|------|-------------------|
| Naming & file organization | [`.ai/conventions.md`](conventions.md) |
| Archive / never-delete / never-reset-db | [`.ai/maintenance.md`](maintenance.md) |
| Credential warehousing & .gitignore | [`.ai/credentials.md`](credentials.md) |
| Master index of all instruction sections | [`.ai/index.md`](index.md) |

---

## AI-INSTRUCT Maintenance Rule

> **→ [AI-INSTRUCT Maintenance Rule](../.github/copilot-instructions.md#ai-instruct-maintenance-rule)** — update instruction files as part of every architectural change; run `/ai-update-index` after.
