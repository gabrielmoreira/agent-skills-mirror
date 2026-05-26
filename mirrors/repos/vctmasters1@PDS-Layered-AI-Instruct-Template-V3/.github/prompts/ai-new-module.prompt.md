---
mode: agent
description: Scaffold a new module with its own .ai/instruct.md and .dev-docs/index.md, register it in the root key-directories table, then rebuild the master index.
---

# New Module

Scaffold a new module that participates in the AI-INSTRUCT hierarchy.

> **→ [Directory Naming](../../.ai/conventions.md#directory-naming)** — directories use `kebab-case`.
> **→ [AI Instruction File Naming](../../.ai/conventions.md#ai-instruction-file-naming)** — instruction file is always `.ai/instruct.md`.
> **→ [`.dev-docs` Convention](../../.ai/conventions.md#dev-docs-convention)** — every module gets a `.dev-docs/index.md`.

## Steps

1. **Ask the user** for:
   - Module name (must be `kebab-case`; reject otherwise per [AI Enforcement](../../.ai/conventions.md#ai-enforcement))
   - One-sentence description of what the module does
   - Whether the module needs its own `.env.example` (i.e., has its own runtime config)

2. **Create the module directory and files**:
   ```
   [module-name]/
   ├── .ai/
   │   └── instruct.md           ← scaffold from the template below
   └── .dev-docs/
       └── index.md              ← scaffold from .ai/conventions.md#dev-docs-convention
   ```

   If the user said the module needs its own env config, also create:
   ```
   [module-name]/.env.example    ← per .ai/credentials.md#env-file-convention
   ```

3. **`[module-name]/.ai/instruct.md` template**:

   ```markdown
   # [module-name] — Module AI Instructions

   **Scope**: Authoritative for everything inside `[module-name]/`
   **Last Updated**: YYYY-MM-DD

   > Deeper than root `.ai/instruct.md` — authoritative when working in this directory.

   ## Module Overview
   [One-sentence description]

   **Entry point**: [path/to/entry]
   **Dependencies on other modules**: [list or "none"]

   ## Module-Specific Rules
   - [Rule 1]
   - [Rule 2]

   ## Global Rules Reference
   > **→ [No-Duplication Rule](../../.ai/conventions.md#no-duplication-rule)** — instructions live in one place.
   > **→ [Never Delete Rule](../../.ai/maintenance.md#never-delete-rule)** — archive instead of delete.
   > **→ [Never Commit Credentials](../../.ai/credentials.md#never-commit-credentials)** — secrets via env vars.
   ```

   Fill `Last Updated` with today's date (no `[DATE]` placeholder — per [Versioning](../../.ai/conventions.md#versioning)).

4. **`[module-name]/.dev-docs/index.md` template**:

   ```markdown
   # .dev-docs Index — [module-name]

   ## Active Files
   | File | Description | Last Updated |
   |------|-------------|--------------|
   | *(none yet)* | — | — |

   ## Archived (`.old/`)
   | File | Why Archived | Date |
   |------|--------------|------|
   | *(none yet)* | — | — |
   ```

5. **Register the module in the root `.ai/instruct.md`**:
   - Open `.ai/instruct.md`
   - Add a row to the `## Key Directories` table:
     `| `[module-name]/` | `[module-name]/.ai/instruct.md` | [one-line description] |`
   - Update its `Last Updated` field to today

6. **Rebuild the master index** by invoking `/ai-update-index` (or follow `.github/prompts/ai-update-index.prompt.md` directly).

7. **Report** what was created and what still needs the user's input (e.g., filling rules in the module's `instruct.md`).

## Guardrails

- Never overwrite an existing module — if `[module-name]/.ai/instruct.md` already exists, stop and ask
- Reject any module name that contains spaces, underscores, or uppercase letters
- Never delete or modify files outside the new module and the root `.ai/instruct.md` key-directories table
