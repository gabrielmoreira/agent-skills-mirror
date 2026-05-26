# Conventions — Naming & File Organization

**Scope**: Project-wide canonical reference
**Last Updated**: 2026-05-25

> This file is the **single source of truth** for naming conventions and file organization rules.
> Reference it from other `.ai/instruct.md` files; never duplicate its content elsewhere.

---

## Contents

| Section | What's here |
|---------|-------------|
| [Directory Naming](#directory-naming) | How to name directories |
| [File Naming](#file-naming) | General file naming rules |
| [Documentation Naming](#documentation-naming) | Numbered kebab-case user-facing guides |
| [AI Instruction File Naming](#ai-instruction-file-naming) | Rules for instruction files |
| [.dev-docs Convention](#dev-docs-convention) | Dev documentation subdirectory structure |
| [TOC Requirement](#toc-requirement) | When a table of contents is required |
| [Cross-Reference Convention](#cross-reference-convention) | How to point to source-of-truth sections |
| [No-Duplication Rule](#no-duplication-rule) | Instructions live in exactly one place |
| [Versioning](#versioning) | Code, instruction, and template versioning rules |
| [Code Organization](#code-organization) | Project-specific structure rules (fill in) |
| [.gitignore Decisions](#gitignore-decisions) | What to commit vs. ignore; personal override pattern |

---

## Directory Naming

- Use `kebab-case` for all directories: `my-module`, `api-server`, `data-pipeline`
- All archived content lives under `.archive/` using path-mirroring or `YYYYMMDD/` date-stamped subdirectories (see [Archive Patterns](maintenance.md#archive-patterns))
- Dev documentation subdirectory is always `.dev-docs/` (dot-prefixed, never renamed)
- AI instruction subdirectory is always `.ai/` (dot-prefixed, never renamed)
- The dot-prefix convention applies to **four** categories of directories: tooling (`.github/`, `.vscode/`, `.cursor/`, `.continue/`, `.clinerules/`), hidden state (`.ai/`, `.dev-docs/`), archives (`.archive/`), and reference scaffolds shipped with the template (`.example-module/`, `.examples/`). Do **not** dot-prefix real source modules.
- Avoid spaces in all directory names

---

## File Naming

- **Source code**: follow the language/framework convention
  - TypeScript/JavaScript: `camelCase.ts`, `PascalCase.tsx` for components
  - Python: `snake_case.py`
  - C/C++: `snake_case.c`, `snake_case.h`
- **Config files**: lowercase with dots or hyphens (`tsconfig.json`, `docker-compose.yml`)
- **Markdown docs**: `kebab-case.md` for general docs; zero-padded numbered kebab-case for user-facing guides (see below)
- **Root-level project meta-files** (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE`, `TEMPLATE-USAGE.md`, `AGENTS.md`, `*.code-workspace`) use `UPPER-KEBAB-CASE.md` or the upstream-mandated form — this is the GitHub/industry standard for repository root meta-documents and is exempt from the general `kebab-case` rule. `.code-workspace` files conventionally carry the project name verbatim (e.g. `PDS-Layered-AI-Instruct-Template-V3.code-workspace`).
- **Tool-mandated names** (filenames whose casing is dictated by an external tool's discovery mechanism) are exempt from the rules above. Currently:
  - `.github/copilot-instructions.md` — fixed name required by GitHub Copilot
  - `.github/skills/<skill>/SKILL.md` — fixed `SKILL.md` casing required by the VS Code Copilot skill discovery system
- **Slash-command prompt files** (`.github/prompts/*.prompt.md`) project-specific to this template must use the `ai-` prefix (e.g. `ai-update-index.prompt.md`) to distinguish them from built-in Copilot commands
- **Never** use spaces in filenames

---

## Documentation Naming

User-facing how-to guides and numbered documentation use **zero-padded numbered kebab-case** naming:

```
01-getting-started.md
02-how-to-add-a-module.md
03-how-to-deploy-to-production.md
04-reference-architecture.md
```

**Rules**:
- Prefix with a zero-padded two-digit number: `01`, `02`, ... `10`, `11` (gap freely, e.g. `01`, `05`, `10`)
- Use `kebab-case` for the name portion — no dots, no CamelCase
- Keep names action-oriented: `how-to-...`, `getting-started`, `reference-...`
- This convention applies to **user-facing guides at directory root only** — not to `.dev-docs/` internal files

---

## AI Instruction File Naming

| File | Purpose |
|------|---------|
| `.ai/instruct.md` | Standard per-directory instruction file (authoritative for its directory) |
| `.ai/conventions.md` | This file — global naming conventions |
| `.ai/maintenance.md` | Global archive and safety rules |
| `.ai/credentials.md` | Global credential warehousing rules |
| `.ai/index.md` | Master section index for the whole project |
| `.github/copilot-instructions.md` | Meta-instruction file (special case — fixed name required by GitHub Copilot) |

Use `instruct.md` in every directory that contains source code, configuration, or documentation the AI reasons about. One file type, one purpose — no variants.

---

## .dev-docs Convention

Every directory that accumulates development notes uses a `.dev-docs/` subdirectory.

### Structure

```
any-directory/
├── .ai/                         ← AI instruction files for this directory
│   └── instruct.md
├── README.md                    ← Primary docs (KEEP at root)
├── [source code / config]       ← KEEP at root
└── .dev-docs/
    ├── index.md                 ← Navigation — lists all files in this .dev-docs/
    ├── [active dev notes]       ← Current session notes, status, guides
    └── .old/                    ← Stale/superseded docs (IGNORE by default)
        └── [archived docs]      ← Moved here when outdated
```

### Rules

1. `.dev-docs/` holds dev notes, session reports, status tracking, architecture reviews — **not** primary deliverables
2. `.dev-docs/.old/` holds stale or superseded docs — move here instead of deleting
3. **Copilot should ignore `.old/`** contents unless explicitly asked
4. Keep at directory root (never move into `.dev-docs/`): `README.md`, source code, essential config, execution scripts
5. When creating a new `.dev-docs/`, also create `index.md` inside it

### index.md Format

```markdown
# .dev-docs Index — [Directory Name]

## Active Files
| File | Description | Last Updated |
|------|-------------|--------------|

## Archived (`.old/`)
| File | Why Archived | Date |
|------|-------------|------|
```

---

## TOC Requirement

Any `.ai/instruct.md` with **5 or more sections** must have a **Contents table** immediately after its file header (before the first `##` section). Format:

```markdown
## Contents

| Section | What's here |
|---------|-------------|
| [Section Name](#section-name) | One-line description |
```

**Rules**:
- The link text must exactly match the `##` heading text in the file (grep-able).
- The anchor (`#section-name`) follows GitHub's auto-anchor rules: lowercase the heading, replace spaces with `-`, strip punctuation and backticks, keep alphanumerics and `-`/`_`.
- Anchors are clickable in any markdown viewer (GitHub, VS Code preview) and Ctrl/Cmd+Click-navigable in the VS Code editor.

---

## Cross-Reference Convention

When a file needs to point to content defined elsewhere, use a **standard clickable markdown anchor link**. This is the single canonical form — no separate "grep" syntax.

**Format**:

```markdown
> **→ [Section Heading](relative/path/to/file.md#section-heading)** — one-line description.
```

**Examples** (paths shown as they appear from a `.ai/instruct.md` at the workspace root):

> **→ [Never Delete Rule](maintenance.md#never-delete-rule)** — archive instead of delete.
> **→ [Never Commit Credentials](credentials.md#never-commit-credentials)** — the hard rule on secrets.
> **→ [Data Schema](../some-module/.ai/instruct.md#data-schema)** — canonical field definitions for that module.

**Rules**:
- Paths are **relative to the file containing the link**. From `.ai/maintenance.md`, link to a sibling as `credentials.md#…`; from `.example-module/.ai/instruct.md`, link to a root global as `../../.ai/credentials.md#…`; from `.github/copilot-instructions.md`, use `../.ai/…`.
- The link **text** must exactly match the target heading (drop punctuation/backticks in the visible label only if it improves readability — the anchor must still match the GitHub auto-anchor).
- The **anchor** is the GitHub auto-anchor of the target heading (see TOC Requirement rules above).
- Place the reference at the point where the topic first becomes relevant.
- **Never copy the content** — only link to it.
- Cross-references in non-markdown source comments use the same path-with-anchor form without the markdown link syntax: `// See .ai/credentials.md#never-commit-credentials — secrets via env vars`. VS Code auto-detects these as clickable in many contexts; if not, they remain grep-able.

---

## No-Duplication Rule

**Instructions must live in exactly one place.**

| Scope | Canonical home |
|-------|----------------|
| Applies project-wide | Root `.ai/instruct.md` or `.ai/` global files |
| Applies to multiple subdirectories | Shallowest common parent `.ai/instruct.md` |
| Applies to one directory only | That directory's `.ai/instruct.md` |

- **Never copy** content from a shallower file into a deeper one — use a cross-reference
- Exception: a one-line summary reminder is acceptable, but full content must live in one place only
- When you find duplicated content across `.ai/instruct.md` files: consolidate to the appropriate level and replace all copies with cross-references

---

## Versioning

### Code Versioning

| Type | Convention | Example |
|------|-----------|--------|
| Libraries / packages / APIs | Semantic versioning: `MAJOR.MINOR.PATCH` | `2.1.0` |
| Deployable applications | Semver or calendar versioning — establish once and document in `README.md` | `2025.05.25` |
| Database migrations | Sequential integer or timestamp prefix | `0042_add_user_table.sql` |
| Breaking API changes | Increment `MAJOR`; a `v1` route must remain functional after `v2` ships | |

### Instruction File Dating

Every `.ai/instruct.md` contains a `**Last Updated**: [DATE]` field.

**Rules**:
- Update `Last Updated` to today’s date (`YYYY-MM-DD`) whenever the file’s content changes
- AI **must** update this field automatically when modifying any `.ai/instruct.md` file — this is a pre-approved auto-action (no confirmation needed)
- Never leave `[DATE]` as a literal placeholder in a **live** instruction file. Fill it immediately when context makes the date unambiguous (session date is known, the user said "today", etc.)
- **Template scaffold exception**: prompt-file templates and inline code-block templates (e.g., the template snippet inside `/ai-new-module`) may keep `YYYY-MM-DD` or `[DATE]` as a literal placeholder because the *user* of the template substitutes the value at instantiation time. As soon as the template is instantiated into a real file, the placeholder must be filled.
- The root `.github/copilot-instructions.md` has a `Template Version` field — increment it only when the template structure itself changes, not on every edit

This principle extends to all `[PLACEHOLDER]` values in any instruction file: if the correct value is self-evident from context, fill it in without waiting for the user to ask.

---

## Code Organization

> **Project-specific — fill this in.** Replace this section with your project’s actual code organization rules: module boundaries, import constraints, layer responsibilities, and any structural invariants the AI must enforce.
>
> Examples of what belongs here:
> - “Controllers must not import from other controllers”
> - “All database access goes through the repository layer”
> - “No circular imports across modules”
> - “Shared utilities live in `shared/` — never inline in feature modules”
> - “Firmware HAL layer must not call application-layer functions”
>
> Generic programming principles (single-responsibility, no monoliths) are not repeated here — only rules specific to this codebase.

> **→ [Stack-Specific Conventions](stack-examples/README.md)** — copy-paste starting points for TypeScript+React, Python+FastAPI, and Embedded C/C++ projects. Reference only; not authoritative.

---

## .gitignore Decisions

> **→ [.gitignore Requirements](credentials.md#gitignore-requirements)** — mandatory credential-safety patterns every module's `.gitignore` must include. This section covers the broader what-to-commit-vs-ignore policy; credentials.md is the canonical list of must-ignore patterns.

When adding a new file or config to the project, apply this rule:

| File type | Action | Notes |
|-----------|--------|-------|
| Secrets, credentials, API keys, tokens | **Always gitignore** | See `.ai/credentials.md` |
| Build output, generated files, dependencies | **Always gitignore** | Not source; regeneratable |
| Team-shared config (`.vscode/settings.json`, `tsconfig.json`) | **Commit** | All contributors benefit from the same baseline |
| Environment templates (`.env.example`) | **Commit** | Safe; contains no real values |
| Actual env files (`.env`) | **Always gitignore** | Contains real secrets |
| Personal machine overrides | **Gitignore using `*.local.*` pattern** | See note below |

**Personal override pattern**: For any committed config file that a developer needs to customize locally without affecting others, create a sibling file named `<original>.local.<ext>` (e.g., `settings.local.json`, `docker-compose.local.yml`). Add the `*.local.*` pattern to `.gitignore` so these files are never committed.

> VS Code does not read `settings.local.json` — for VS Code editor preferences, use VS Code user settings (`Ctrl+Shift+P` → Open User Settings).

**AI Rule**: When creating a new config file, check whether it belongs in `.gitignore`. If the file could contain environment-specific or secret values, default to gitignoring it and creating a committed `.example` or `.local` counterpart.

---

## AI Enforcement

When a user proposes or writes a filename, function name, class name, variable name, or directory name that violates the conventions in this file:

1. **Flag the violation** — briefly state which rule is broken
2. **Suggest a conforming name** — provide a specific replacement using the correct convention for the language and context
3. **Do not silently accept** non-conforming names; always surface the suggestion before proceeding
4. Apply the same standard to AI-generated names — any identifier or path the AI writes must follow these conventions

**Examples**:

| Proposed | Violation | Suggested |
|----------|-----------|----------|
| `MyComponent.md` | Markdown docs use `kebab-case` | `my-component.md` |
| `GetUserData.ts` | TS functions use `camelCase` | `getUserData.ts` |
| `user_service/` | Directories use `kebab-case` | `user-service/` |
| `DataProcessor_v2.py` | Python files use `snake_case` | `data_processor_v2.py` |
| `UserAuthAndProfileManager.ts` | Single responsibility violated — split | `user-auth.ts` + `user-profile.ts` |
