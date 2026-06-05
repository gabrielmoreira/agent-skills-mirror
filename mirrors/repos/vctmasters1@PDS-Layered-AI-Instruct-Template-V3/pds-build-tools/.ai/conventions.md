# Conventions — Naming & File Organization

**Scope**: `pds-build-tools/` module reference
**Last Updated**: 2026-05-27

> **? Root [``.ai/conventions.md``](../../.ai/conventions.md)** — This file is authoritative for all directories in this project.

## Contents

| Section | Description |
|---------|-------------|
| [Project-Specific Rules](#project-specific-rules) | Directory naming, file naming, and documentation conventions for pds-build-tools module |
| [Code Organization](#code-organization) | Layer structure including config/, scripts/, and tests/ directories |
| [Credential Management](#credential-management) | Guidelines for handling secrets and credential files |
| [Build Pipeline](#build-pipeline) | Build input/output processes and dist directory structure |
| [Dev Container](#dev-container) | Container-based build environment for reproducibility |

## Project-Specific Rules

### Directory Naming

- Dev documentation: ``.dev-docs/`
- AI instructions: ``.ai/`

### File Naming

| Context | Case | Example |
|---------|------|---------|
| Python scripts | `snake_case.py` | `build_selector.py` |
| PowerShell scripts | `PascalCase.ps1` | `BuildSelector.ps1` |

### Documentation

- User-facing guides: numbered `kebab-case.md`
- Root meta-files: `UPPER-KEBAB-CASE.md`

---

## Code Organization

| Layer | Responsibility |
|-------|----------------|
| `config/` | Build configuration files |
| `scripts/` | Python build scripts |
| `tests/` | Unit and integration tests |

### Technology Stack

- **Primary**: Python 3.10+ for build automation
- **Secondary**: PowerShell for Windows tooling
- **Target**: ESP-IDF builds via Docker container

---

## Credential Management

> **? Root [``.ai/credentials.md``](../../.ai/credentials.md)** — Global credential rules apply.

| File | Commit? | Notes |
|------|---------|-------|
| `.env` | ? | Secrets (DATABASE_URL, JWT_SECRET) |
| `.env.example` | ? | Template with placeholder values |

---

## Build Pipeline

### Input
- Board JSON (`PDS-BoardEditor/boards/<board>.json`)
- Hardware revision
- Role configuration (`pds-role/saved_roles/<role>.json`)

### Output
```
dist/
+-- bootloader.bin
+-- partition-table.bin
+-- pds-device.bin
+-- ota_data_initial.bin
+-- defaults/
    +-- <role>/
        +-- <role>_l1.bin
        +-- <role>_l2.bin
        +-- <role>_l3.bin
        +-- <role>_l4.bin
        +-- nvs_defaults.bin
```

---

## Dev Container

Build runs inside the dev container to ensure reproducibility:
- ESP-IDF version pinned via ``.devcontainer/Dockerfile`
- Python venv with required packages
- Esptool installed on host for flashing

