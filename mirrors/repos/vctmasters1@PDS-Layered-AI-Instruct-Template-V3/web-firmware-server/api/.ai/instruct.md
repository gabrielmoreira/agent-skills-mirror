# AI-INSTRUCT: web-firmware-server/api

**Package**: `web-fwserver-api`
**Role**: Firmware binary storage and OTA delivery service
**Dev Port**: 3002
**Prod**: Railway (separate service from HMI API)
**Last Updated**: 2026-05-29

> **Consolidation fixes applied 2026-05-29**:
> - `tsconfig.json` `@db-central/*` path corrected from `../../DB-Central/src/*` → `../../db-central/src/*` (lowercase). References path also lowercased.
> - `node_modules/` was missing — `npm install` had never been run. Run `npm install` in `web-firmware-server/api/` after any fresh clone.

---

## Contents

| § | What's here |
|---|-------------|
| [Purpose](#purpose) | Service role: firmware binary storage and OTA delivery |
| [Auth](#auth) | JWT auth, admin-only upload, device token download |
| [Routes](#routes) | API endpoint listing |
| [Binary Storage](#binary-storage) | File naming, path conventions, storage rules |
| [Database](#database) | Firmware entity schema |
| [Architecture Position](#architecture-position) | Where this service sits in the system |
| [Source Structure](#source-structure) | Directory layout |
| [Dev Commands](#dev-commands) | Build and run scripts |
| [Railway Deployment](#railway-deployment) | Production deployment config |

## Purpose

This service stores compiled firmware binaries and serves them to devices for OTA updates. It is **not** a general-purpose file server — it only handles PDS device firmware.

The OTA paradigm end-to-end is documented in **`.dev-docs/OTA-PARADIGM.md`**.

---

## Auth

Uses the **same `JWT_SECRET`** as `WEB-HMI/api` and `WEB-Marketplace/api`. A user JWT issued by any service is valid here. The shared secret must match across all three services.

Two auth levels:
- **Staff JWT** (`isStaff: true`): upload firmware, list all, set active
- **Device JWT** (`X-Device-Token` header): download firmware for OTA

For dev credentials (token, user account): **`.github/debug/_dev_auth.md`** (gitignored).

**IMPORTANT for AI**: Do NOT attempt to log in via Marketplace API (port 3000) — its email validator rejects `.local` TLDs. Do NOT try `admin@local.dev` or `vctmasters@gmail.com`. The dev account is `dev@pds.local` / `PdsLocal!Dev1`, login via **HMI API port 3001** (`/v1/auth/login`). A long-lived token lives in `_dev_auth.md` — use it directly instead of logging in. Do NOT start the Marketplace API just to get a token.

---

## Routes

| Route | Method | Auth | Purpose |
|-------|--------|------|---------|
| `/health` | GET | None | Health check |
| `/v1/firmware` | GET | Staff JWT | List all firmware (filterable by platform/hwrev/deviceType) |
| `/v1/firmware/:platform/:hwrev/:deviceType` | GET | Staff JWT | List versions for a target |
| `/v1/firmware/:platform/:hwrev/:deviceType/:version` | GET | Staff JWT | Get metadata for a specific version |
| `/v1/firmware/upload` | POST | Staff JWT | Upload new binary (multipart/form-data) |
| `/v1/firmware/:platform/:hwrev/:deviceType/:version/device-download` | GET | Device JWT | Binary download for device OTA |

---

## Binary Storage

Files live at: `storage/{platform}/{hwrev}/{deviceType}/{version}/{filename}`

Example: `storage/esp32_node32s/hwrev_001/aeroponic-controller/0.1.007/pds-device.bin`

The `STORAGE_DIR` env var overrides the default path. In Railway production, set this to a persistent volume mount.

Upload field names (multipart):
- `file` — the binary (`.bin`)
- `platform` — e.g. `esp32_node32s`
- `hwrev` — e.g. `hwrev_001`
- `deviceType` — e.g. `aeroponic-controller`
- `version` — e.g. `0.1.007`

SHA-256 checksum is computed server-side at upload time and stored in the DB. The download endpoint streams directly from disk.

---

## Database

> **→ `DB-Central/.ai/instruct.md`** — DB-Central is the single source of truth for all TypeORM entities and migrations. Do not edit entity files in this service's `src/entities/` — those are legacy copies pending removal.

Shares the same PostgreSQL instance (`pds_marketplace` DB) as HMI API and Marketplace. `synchronize` must be `false` once DB-Central migration is applied — schema is managed by DB-Central migrations only.

Authoritative entity: `DB-Central/src/entities/firmware.ts`  
Legacy stub (pending removal): `src/entities/firmware.ts`

Key fields: `id`, `platform`, `hwrev`, `deviceType`, `version`, `binaryPath`, `binarySize`, `sha256`, `active`, `releasedAt`

**Unique key**: `(platform, hwrev, deviceType, version)` — this is the safety mechanism that prevents deploying the wrong firmware to the wrong hardware. Do not relax or remove this constraint. A firmware record is only valid for one exact target combination.

**`synchronize: true` cannot add NOT NULL columns to existing tables** if there are already rows — Postgres rejects it because existing rows would violate the NOT NULL constraint. When the `Firmware` entity gains new non-nullable columns (as happened with `platform` and `hwrev`), you must manually migrate the DB:

```powershell
# Write the SQL to a temp file and docker cp it in — avoids PowerShell quoting issues
@"
ALTER TABLE firmwares ADD COLUMN IF NOT EXISTS platform VARCHAR NOT NULL DEFAULT '';
ALTER TABLE firmwares ADD COLUMN IF NOT EXISTS hwrev VARCHAR NOT NULL DEFAULT '';
UPDATE firmwares SET platform = 'esp32c3_sm', hwrev = 'hwrev-002' WHERE platform = '';
ALTER TABLE firmwares ALTER COLUMN platform DROP DEFAULT;
ALTER TABLE firmwares ALTER COLUMN hwrev DROP DEFAULT;
"@ | Out-File -FilePath "$env:TEMP\fw_migrate.sql" -Encoding utf8
docker cp "$env:TEMP\fw_migrate.sql" pds-marketplace-db:/tmp/fw_migrate.sql
docker exec pds-marketplace-db psql -U pds -d pds_marketplace -f /tmp/fw_migrate.sql
```

After migration, restart FwServer — TypeORM synchronize will then reconcile the indexes (old unique index on `(deviceType, version)` → new unique index on `(platform, hwrev, deviceType, version)`). The old narrow index must be dropped manually if TypeORM doesn't clean it up:

```powershell
docker exec pds-marketplace-db psql -U pds -d pds_marketplace -c 'DROP INDEX IF EXISTS "IDX_798768ca1ff859e9c3c5356326";'
```

**The `active` flag matters**: FwServer's download route queries `WHERE ... active = true`. A firmware record with `active = false` returns 404 to the device, which causes `ESP_FAIL` OTA ACK. Verify with: `GET /v1/firmware/:platform/:hwrev/:deviceType/:version`.

---

## Architecture Position

```
PDS-BuildTools/scripts/deploy_firmware.py --ota
    └─→ POST /v1/firmware/upload  (multipart)  → stores binary on disk + DB record

WEB-HMI/api  POST /v1/devices/:id/ota
    └─→ builds pendingOtaUrl = {BASE_URL}/v1/firmware/{platform}/{hwrev}/{deviceType}/{version}/device-download
    └─→ stores in device.pendingOtaUrl

Device firmware (ESP32)
    └─→ polls WEB-HMI/api GET /pending-sync → receives otaUrl
    └─→ GET {otaUrl} with X-Device-Token → downloads from THIS service
    └─→ applies OTA, reboots, ACKs via WEB-HMI/api POST /ota/ack
```

---

## Source Structure

```
src/
├── index.ts              ← Express app + CORS + startup
├── database.ts           ← TypeORM datasource
├── config/
│   └── jwt.ts            ← JWT secret (must match HMI API)
├── entities/
│   ├── firmware.ts       ← Firmware DB entity
│   ├── user.ts           ← User entity (read-only, owned by Marketplace)
│   └── index.ts
├── middleware/
│   ├── auth.ts           ← verifyToken (user JWT)
│   ├── adminOnly.ts      ← isStaff check
│   └── security.ts       ← Helmet + rate limiting
└── routes/
    └── firmware.ts       ← All routes
```

---

## Dev Commands

```powershell
Set-Location "k:\PDS_AutomationSuite\WEB-FwServer\api"
npm run dev    # builds + runs on port 3002
```

---

## Railway Deployment

`railway.toml`:
```toml
buildCommand = "npm ci && npm run build"
startCommand = "node dist/index.js"
```

Env vars required in production:
- `DATABASE_URL` — shared PostgreSQL connection string
- `JWT_SECRET` — must match HMI API and Marketplace API
- `STORAGE_DIR` — path to persistent volume for binary storage
- `CORS_ORIGINS` — comma-separated allowed origins (e.g. `https://pipedreamsystems.com`)
- `NODE_ENV=production`


