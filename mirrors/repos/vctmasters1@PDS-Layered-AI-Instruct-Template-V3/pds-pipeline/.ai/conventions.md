# Conventions -- Naming and File Organization for pds-pipeline

**Scope**: Authoritative for pds-pipeline/ directory
**Last Updated**: 2026-05-27

> This file extends the root .ai/conventions.md with pds-pipeline-specific rules.
> **Always reference root conventions rather than duplicating them here.**

---

## Directory Structure Conventions

| Directory | Purpose |
|-----------|---------|
| src/ | TypeScript source code (compiled to JS via tsc) |
| dist/ | Compiled output (gitignored, generated on build) |
| .ai/ | AI instruction files for this directory |

---

## File Naming Conventions

| File Type | Convention | Example |
|-----------|-----------|---------|
| TypeScript source | camelCase.ts or PascalCase.tsx | block-registry.ts, design-tokens.css |
| Documentation (user-facing) | Zero-padded numbered kebab-case | 01-getting-started.md |
| Config files | lowercase with dots/hyphens | tsconfig.json, package.json |

> **File Naming Rules**: general naming conventions apply.

---

## Code Organization

### Source File Locations

```
src/
|-- index.ts              Public API exports (re-exports)
|-- block-registry.ts     BLOCK_REGISTRY: struct layout + UI metadata
|-- design-tokens.css     CSS variable definitions (--vscode-* tokens)
```

### Export Rules

- Never export raw Buffer APIs
- Import from @pds/pipeline only; do not import directly from src/
- All public API must be re-exported via index.ts

### Module Boundaries

| Consumer | What it imports |
|----------|-----------------|
| WEB-HMI/api | @pds/pipeline decoded types + block registry |
| PDS-vscode-extension | Direct import from src/ (bundled by esbuild) |

---

## TypeScript Rules

1. No Node.js built-ins in src/ files
2. No DOM APIs
3. Zero dependencies pure TypeScript logic only
4. Use ES module syntax throughout

---

## CSS Variable System

All pipeline UI must use the --vscode-* token names defined in src/design-tokens.css:

| Token | VS Code Runtime | WEB-HMI Fallback |
|-------|-----------------|------------------|
| --vscode-button-background | Provided by runtime | Mapped to --pds-button-bg |

> Visual Design System: color coding and category-specific accents.

---

## Block Registry Format

When adding a new block type:

1. Add entry to BLOCK_REGISTRY in src/block-registry.ts
2. Mirror entry in pds-role/tools/blob_packer.py
3. Mirror struct in firmware headers (.h) and implementations (.c)
4. Do NOT add to legacy role-data.js in VS Code extension

---

## Portability Requirements

This package must compile/run in two environments without modification:

| Environment | Runtime | Notes |
|-------------|---------|-------|
| VS Code webview | Chromium | Bundled by esbuild; no require() |
| Railway server | Node.js | Compiled via tsc; served as CommonJS |

> Portability Requirement: full rules in instruct.md.

---

## AI Enforcement

When a user proposes code that violates these conventions:

1. Flag the violation with the specific rule broken
2. Suggest a conforming alternative
3. Do not silently accept non-conforming names or structures
4. Ensure any AI-generated code follows these rules exactly
