# Conventions — Naming & File Organization

**Scope**: `device/` module reference
**Last Updated**: 2026-05-27

> **? Root [``.ai/conventions.md``](../../.ai/conventions.md)** — This file is authoritative for all directories in this project.

## Contents

| Section | Description |
|---------|-------------|
| [Project-Specific Rules](#project-specific-rules) | Directory naming, file naming, and documentation conventions for device module |
| [Code Organization](#code-organization) | Layer structure including main/ and pds/ directories |
| [Credential Management](#credential-management) | Guidelines for handling secrets and credential files |
| [Firmware Development Rules](#firmware-development-rules) | Key practices for embedded C/C++ development with ESP-IDF |
| [Build & Deployment](#build--deployment) | Development and production build processes |

## Project-Specific Rules

### Directory Naming

- Dev documentation: ``.dev-docs/`
- AI instructions: ``.ai/`

### File Naming

| Context | Case | Example |
|---------|------|---------|
| C files | `snake_case.c` | `pds_core.c` |
| Header files | `snake_case.h` | `pds_core.h` |
| Assembly | `snake_case.S` | `startup.S` |

### Documentation

- User-facing guides: numbered `kebab-case.md`
- Root meta-files: `UPPER-KEBAB-CASE.md`

---

## Code Organization

| Layer | Responsibility |
|-------|----------------|
| `main/` | Application entry point and main loop |
| `pds/` | PDS modules (HAL, core, validation, etc.) |

### Technology Stack

- **Primary**: Embedded C/C++ for ESP32
- **Build System**: ESP-IDF
- **Microcontrollers**: ESP32 variants (C3, S3, H2, C6)

---

## Credential Management

> **? Root [``.ai/credentials.md``](../../.ai/credentials.md)** — Global credential rules apply.

| File | Commit? | Notes |
|------|---------|-------|
| `.env` | ? | Secrets (DATABASE_URL, JWT_SECRET) |
| `.env.example` | ? | Template with placeholder values |

---

## Firmware Development Rules

1. **Never commit credentials** to flash - use NVS partition for runtime config
2. **Always use const** for string literals and lookup tables
3. **Check return codes** from all ESP-IDF API calls
4. **Use FreeRTOS patterns**: xTaskCreate, queues, semaphores appropriately

---

## Build & Deployment

### Development

```bash
# From the pds-build-tools directory
python scripts/build_selector.py --board <board_id> --hwrev <rev>
```

### Production

Firmware is flashed via `esptool` with the NVS partition containing role defaults.

