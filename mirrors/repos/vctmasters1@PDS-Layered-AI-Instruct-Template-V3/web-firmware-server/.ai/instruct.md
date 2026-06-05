# web-firmware-server: Firmware Storage and OTA Delivery

**Project**: PDS-AutomationSuite-02012026  
**Last Updated**: 2026-05-27  
**Service**: Internal microservice (not directly user-facing)

---

## Contents

| Section | Description |
|---------|-------------|
| [What This Is](#what-this-is) | Overview of the web-firmware-server service and its role as the single source of truth for firmware binaries and version metadata. |
| [Directory Structure](#directory-structure) | File layout of the service including storage for firmware binaries and API implementation. |
| [Service Rules](#service-rules) | Core operational rules including table ownership, user table access, authentication, file storage, and consumer restrictions. |
| [Adding a New Device Type](#adding-a-new-device-type) | Instructions for adding support for new device types through firmware uploads without code changes. |
| [Firmware URL Path Segments](#firmware-url-path-segments) | Details on the four-path-segment download URLs derived from database columns. |
| [Development](#development) | Local development setup and running instructions. |
| [Database](#database) | PostgreSQL configuration, migrations for firmwares table, and connection pool settings. |
| [Deployment](#deployment) | Railway deployment configuration, internal access rules, and required environment variables. |
| [Authority](#authority) | Clarification that this file is authoritative for all work inside web-firmware-server/. |

---

## What This Is

\`web-firmware-server\` is a small internal Express microservice. It is the **single source of truth** for firmware binaries and version metadata. It handles upload, versioning, and OTA delivery of firmware to PDS devices.

---

## Directory Structure

```
web-firmware-server/
├── AI-INSTRUCT.md              ← This file
├── storage/                    ← Firmware binaries (gitignored; Railway volume in production)
│   └── .gitignore
└── api/                        ← Express + TypeORM backend
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── index.ts            ← Entry — mounts /v1/firmware, port 3002
        ├── database.ts         ← TypeORM DataSource (User stub + Firmware)
        ├── config/
        │   └── jwt.ts          ← JWT_SECRET shared with WEB-Marketplace and WEB-HMI
        ├── entities/
        │   ├── user.ts         ← STUB — maps to users table (id, isStaff only)
        │   └── firmware.ts     ← Firmware entity — THIS SERVICE OWNS THIS TABLE
        ├── middleware/
        │   ├── auth.ts
        │   ├── adminOnly.ts    ← Requires isStaff = true
        │   └── security.ts
        └── routes/
            └── firmware.ts     ← All /v1/firmware/* endpoints
```

---

## Service Rules

| Concern | Rule |
|---------|------|
| Table ownership | \`web-firmware-server\` owns \`firmwares\`. No other service migrates or synchronizes it. |
| User table | Read-only stub. Never write to \`users\` from this service. |
| Auth | All routes require \`verifyToken\`. Upload/delete/patch require \`adminOnly\`. |
| File storage | Binaries in \`storage/\` — always gitignored. Use \`STORAGE_DIR\` env var in production. |
| Consumers | Only \`WEB-HMI/api\` should call this service. It is not directly public-facing. |

---

## Adding a New Device Type

No code changes needed — firmware routes accept any \`deviceType\` string. Upload a binary via \`POST /v1/firmware\` with the correct \`deviceType\` matching the slug registered in \`WEB-HMI/api/src/devices/\`.

---

## Firmware URL Path Segments

All four path segments in the download URL come from the DB device row:

```
/v1/firmware/{board}/{hwrev}/{deviceType}/{version}/device-download
```

| Segment | DB column | Provisioned by | Example |
|---------|-----------|----------------|---------|
| \`board\` | \`device.board\` | Admin at provision | \`esp32c3_sm\` |
| \`hwrev\` | \`device.hwrev\` | Admin at provision | \`hwrev-002\` |
| \`deviceType\` | \`device.deviceType\` | Admin at provision | \`aeroponic-controller\` |
| \`version\` | \`device.pendingOtaVersion\` | Set when OTA is queued | \`C02.0.1.018\` |

> **→ Root \`AI-INSTRUCT.md\` § Device Identity Model — End-to-End Identity Flow** — full map of how these fields are set at build time, provision time, and consumed at OTA time.

---

## Development

```powershell
Set-Location "k:\PDS_AutomationSuite\web-firmware-server\api"
npm install
npm run dev
```

Service starts on port \`3002\`. Requires the same PostgreSQL instance as \`WEB-Marketplace\` and \`WEB-HMI\`.

---

## Database

- Shared PostgreSQL instance (same as \`WEB-Marketplace\` and \`WEB-HMI\`).
- \`synchronize: true\` in dev; \`synchronize: false\` + explicit migrations in production.
- **Owns migrations for**: \`firmwares\` table only.
  - \`1741200000000-AddFirmwaresTable\` — creates the \`firmwares\` table
  - \`1741400000000-AddFirmwareBoardHwrev\` — adds \`board\` and \`hwrev\` columns; replaces old 2-tuple unique constraint with 4-tuple (board, hwrev, deviceType, version)
- Migrations run automatically via \`AppDataSource.runMigrations()\` at startup when \`NODE_ENV=production\`.
- Connection pool: \extra: { max: 5 }\ — combined with Marketplace and HMI = 15 total ≤ Railway's ~25 cap.
- \`user.ts\` entity here is a **read-only stub** — maps to \`users\` table owned by \`WEB-Marketplace\`. Do not add migrations for it here.

### Dev startup SQL note

In \`src/index.ts\`, a \`pg\` raw-SQL block runs **only in dev** (\`NODE_ENV !== "production"\`) to add nullable \`board\`/\`hwrev\` columns if they are missing (pre-4-tuple era schema upgrade) and to delete rows with NULL key columns before TypeORM synchronize runs. This block does not run in production. In production, only the TypeORM migrations apply.

---

## Deployment

- **Railway**: separate service (\`fwserver-service\`) from Marketplace and HMI.
- **Internal only**: FwServer is NOT directly public-facing. It has no gateway route. Only \`WEB-HMI/api\` talks to it server-to-server (via \`FW_SERVER_URL\` env var — Railway private networking in production).
- **Path prefix**: none (no gateway route). FwServer is reachable only from within the Railway private network.
- \`storage/\` maps to a Railway volume in production (\`STORAGE_DIR\` env var).
- CORS: \`CORS_ORIGINS\` env var should be set to \`https://pipedreamsystems.com\` (only HMI origin).

**Env vars required at runtime** (Railway dashboard):

| Var | Value |
|-----|-------|
| \`DATABASE_URL\` | Shared PostgreSQL connection string |
| \`JWT_SECRET\` | Must match \`WEB-Marketplace\` and \`WEB-HMI\` |
| \`NODE_ENV\` | \`production\` |
| \`PORT\` | Set automatically by Railway |
| \`STORAGE_DIR\` | Path to Railway volume mount for firmware binaries |
| \`CORS_ORIGINS\` | \`https://pipedreamsystems.com\` |

---

## Authority

This file is authoritative for all work inside web-firmware-server/. For broader conventions, see the root .ai/conventions.md.
