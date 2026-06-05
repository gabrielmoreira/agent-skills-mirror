# Conventions — Naming & File Organization

**Scope**: `pds-role/` module reference
**Last Updated**: 2026-05-27

> **? Root [``.ai/conventions.md``](../../.ai/conventions.md)** — This file is authoritative for all directories in this project.

## Contents

| Section | Description |
|---------|-------------|
| [Project-Specific Rules](#project-specific-rules) | Directory naming, file naming, and documentation conventions for pds-role module |
| [Code Organization](#code-organization) | Layer structure including tools/, templates/, and saved_roles/ directories |
| [Credential Management](#credential-management) | Guidelines for handling secrets and credential files |
| [Blob Generation & NVS Image](#blob-generation--nvs-image) | Blob generation process and output file structure |
| [CLI Usage](#cli-usage) | Command-line interface options and usage examples |

## Project-Specific Rules

### Directory Naming

- Dev documentation: ``.dev-docs/`
- AI instructions: ``.ai/`
- All Python modules use `snake_case.py`

### File Naming

| Context | Case | Example |
|---------|------|---------|
| TypeScript files | `camelCase.ts`, `PascalCase.tsx` | `main.tsx`, `client.ts` |
| Python scripts | `snake_case.py` | `role_builder.py` |
| C/C++ headers | `snake_case.h` | `pds_core.h` |

### Documentation

- User-facing guides: numbered `kebab-case.md`
- Root meta-files: `UPPER-KEBAB-CASE.md`

---

## Code Organization

| Layer | Responsibility |
|-------|----------------|
| `tools/` | Python backend (scanning, generation, validation) |
| `templates/` | Jinja2 code-generation templates |
| `saved_roles/` | Persisted role configurations (JSON) |

### Technology Stack

- **Primary**: Python with standard library + Jinja2
- **Integration**: VS Code extension via webview panel

---

## Credential Management

> **? Root [``.ai/credentials.md``](../../.ai/credentials.md)** — Global credential rules apply.

| File | Commit? | Notes |
|------|---------|-------|
| `.env` | ? | Secrets (DATABASE_URL, JWT_SECRET) |
| `.env.example` | ? | Template with placeholder values |

---

## Blob Generation & NVS Image

All generated artifacts for a role are written to:
```
PDS-BuildTools/dist/defaults/<role_id>/
    <role_id>_l1.bin          ? Layer 1 pipeline byte stream
    <role_id>_l2.bin          ? Layer 2 hw_vars blob
    <role_id>_l3.bin          ? Layer 3 settings blob
    <role_id>_l4.bin          ? Layer 4 ui_params blob
    nvs_defaults.bin          ? Combined NVS partition image
```

---

## CLI Usage

```bash
# Interactive mode — prompts for board, hwrev, role name, modules
python go.py

# List available modules and their headers
python go.py --list-modules

# Generate from a saved role config
python go.py --config <role_id>

# Dry run — show what would be generated without writing files
python go.py --dry-run --config <role_id>
```

