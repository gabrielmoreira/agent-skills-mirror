---
name: agents-md
description: "Creates and audits lean AGENTS.md / CLAUDE.md agent instruction files (target under 60 lines, hard max 100) from the real toolchain, with a CLAUDE.md symlink. Use when the user asks to create, update, or audit AGENTS.md or CLAUDE.md, or to keep agent docs from duplicating linters. Not for authoring SKILL.md skills (create-skill), Claude Code plugin skill packs (skill-development), or README/CONTRIBUTING prose."
version: 1.0.1
risk: unknown
source: community
---

# Maintaining AGENTS.md

AGENTS.md is the canonical agent-facing documentation file. Keep it minimal—agents are capable and don't need hand-holding. Target under 60 lines; never exceed 100. Instruction-following quality degrades as document length increases.

## When to Use

- The user asks to create, update, or audit `AGENTS.md` or `CLAUDE.md`.
- The project needs concise, high-signal agent instructions derived from the actual toolchain and repo layout.
- Existing agent documentation is too long, duplicated, or drifting away from real project conventions.

## Prerequisites

- Project root must be accessible (this is where `AGENTS.md` lives).
- On Windows hosts (primary), use PowerShell for symlink creation and file operations.

## Procedure

### 1. File Setup

1. Create `AGENTS.md` at project root.
2. Create a symlink so `CLAUDE.md` resolves to the same content.

**Windows (PowerShell):**
```powershell
New-Item -ItemType SymbolicLink -Path CLAUDE.md -Target AGENTS.md
```

**Linux / macOS:**
```bash
ln -s AGENTS.md CLAUDE.md
```

> On Windows, creating symlinks may require Developer Mode enabled or an elevated PowerShell session.

### 2. Analyze the Project Before Writing

Before writing anything, inspect the repository to understand what belongs in the file:

1. **Package manager** — Check for lock files: `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, `uv.lock`, `poetry.lock`.
2. **Linter/formatter configs** — Look for `.eslintrc`, `biome.json`, `ruff.toml`, `.prettierrc`, etc. Do **not** duplicate these rules in AGENTS.md.
3. **CI/build commands** — Check `Makefile`, `package.json` scripts, CI configs for canonical commands.
4. **Monorepo indicators** — Check for `pnpm-workspace.yaml`, `nx.json`, Cargo workspace, or subdirectory `package.json` files.
5. **Existing conventions** — Check for `CONTRIBUTING.md`, `docs/`, or `README` patterns.

### 3. Writing Rules

- **Headers + bullets** — No paragraphs.
- **Code blocks** — For commands and templates.
- **Reference, don't embed** — Point to existing docs: "See `CONTRIBUTING.md` for setup" or "Follow patterns in `src/api/routes/`".
- **No filler** — No intros, conclusions, or pleasantries.
- **Trust capabilities** — Omit obvious context.
- **Prefer file-scoped commands** — Per-file test/lint/typecheck commands over project-wide builds.
- **Don't duplicate linters** — Code style lives in linter configs, not AGENTS.md.

### 4. Required Sections

#### Package Manager
Which tool and key commands only:
```markdown
## Package Manager
Use **pnpm**: `pnpm install`, `pnpm dev`, `pnpm test`
```

#### File-Scoped Commands
Per-file commands are faster and cheaper than full project builds. Always include when available:
```markdown
## File-Scoped Commands
| Task | Command |
|------|---------|
| Typecheck | `pnpm tsc --noEmit path/to/file.ts` |
| Lint | `pnpm eslint path/to/file.ts` |
| Test | `pnpm jest path/to/file.test.ts` |
```

#### Commit Attribution
Always include this section. Agents should use their own identity:
```markdown
## Commit Attribution
AI commits MUST include:
```
Co-Authored-By: (the agent model's name and attribution byline)
```
Example: `Co-Authored-By: Claude Sonnet 4 <noreply@example.com>`
```

#### Key Conventions
Project-specific patterns agents must follow. Keep brief.

### 5. Optional Sections

Add only if truly needed:
- API route patterns (show template, not explanation)
- CLI commands (table format)
- File naming conventions
- Project structure hints (point to critical files, flag legacy code to avoid)
- Monorepo overrides (subdirectory `AGENTS.md` files override root)

## Pitfalls

- **Length creep** — Instruction-following quality degrades as document length increases. Target under 60 lines; never exceed 100.
- **Duplicating linter rules** — Never copy `.eslintrc`, `biome.json`, or `ruff.toml` rules into AGENTS.md. Reference the config instead.
- **Embedding instead of referencing** — Don't paste full docs; point to them ("See `CONTRIBUTING.md`").
- **Project-wide builds over file-scoped commands** — Always prefer per-file test/lint/typecheck commands when available.
- **Listing installed skills or plugins** — Agents discover these automatically; don't list them.
- **Windows symlink failures** — On Windows, symlink creation may fail without Developer Mode or elevation. If it fails, create `CLAUDE.md` as a copy or use `Copy-Item` as a fallback.
- **Anti-patterns to omit:**
  - "Welcome to..." or "This document explains..."
  - "You should..." or "Remember to..."
  - Full project-wide build commands when file-scoped alternatives exist
  - Obvious instructions ("run tests", "write clean code")
  - Explanations of why (just say what)
  - Long prose paragraphs

## Verification

1. **Line count check** — Ensure the file is under 60 lines (hard max 100):
   ```powershell
   (Get-Content AGENTS.md).Count
   ```
   ```bash
   wc -l AGENTS.md
   ```

2. **Symlink check** — Confirm `CLAUDE.md` resolves to `AGENTS.md`:
   ```powershell
   Get-Item CLAUDE.md | Select-Object Target
   ```
   ```bash
   ls -l CLAUDE.md
   ```

3. **No linter duplication** — Grep for common linter rule keywords that should not appear:
   ```powershell
   Select-String -Path AGENTS.md -Pattern "semi","no-unused","max-len","indent" | Select-Object LineNumber,Line
   ```
   If matches are found (outside of legitimate command examples), remove them.

4. **Required sections present** — Confirm all four required sections exist:
   ```powershell
   Select-String -Path AGENTS.md -Pattern "Package Manager","File-Scoped Commands","Commit Attribution","Key Conventions"
   ```

## Example Structure

```markdown
# Agent Instructions

## Package Manager
Use **pnpm**: `pnpm install`, `pnpm dev`

## Commit Attribution
AI commits MUST include:
```
Co-Authored-By: (the agent model's name and attribution byline)
```

## File-Scoped Commands
| Task | Command |
|------|---------|
| Typecheck | `pnpm tsc --noEmit path/to/file.ts` |
| Lint | `pnpm eslint path/to/file.ts` |
| Test | `pnpm jest path/to/file.test.ts` |

## API Routes
[Template code block]

## CLI
| Command | Description |
|---------|-------------|
| `pnpm cli sync` | Sync data |
```

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
