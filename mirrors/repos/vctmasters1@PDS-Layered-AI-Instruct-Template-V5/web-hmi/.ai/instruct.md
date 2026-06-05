# WEB-HMI — Full-Stack Device HMI

**Scope**: Authoritative for `web-hmi/` directory  
**Authority**: DEEP — Authoritative for all work inside `web-hmi/`
**Last Updated**: 2026-05-29

> **Consolidation fixes applied 2026-05-28/29**:
> - `package.json` (root and `api/`) `@pds/pipeline` path corrected from `PDS-Pipeline` → `pds-pipeline` (lowercase). Run `npm install` in both `web-hmi/` and `web-hmi/api/` after any fresh clone.
> - `api/tsconfig.json`: `@db-central/*` path corrected from `../../DB-Central/dist/*` → `../../db-central/src/*`. References path also lowercased.
> - `vite.config.ts` `commonjsOptions.include`: regex `/PDS-Pipeline/` → `/pds-pipeline/` (was preventing Rollup from doing CJS interop on `@pds/pipeline` in the production bundle).
> - `api/src/__tests__/setup.ts`: removed mistaken `@testing-library/react` import (frontend library in backend test setup — caused TS2724 build error).

> **Deployment**: Runs on Railway. Gateway (`web-gateway`) routes `/hmi/` → React SPA and `/hmi/api/` → Express API over Railway private network. FwServer is reached internally (not via gateway). Shares a single Railway PostgreSQL instance with WEB-Marketplace and WEB-FwServer via `db-central` entities (tsconfig path alias `@db-central/*`, not a package dependency).

---

## Contents

| § | What's here |
|---|-------------|
| [⚠️ Architecture: Cloud-Only — No Physical Connection](#️-architecture-cloud-only--no-physical-connection) | Service topology; no direct device contact |
| [Frontend Routing (React Router v6)](#frontend-routing-react-router-v6) | Route definitions, lazy loading, auth guards |
| [Cloud Subscription ($1/month)](#cloud-subscription-1month) | User billing model via Stripe |
| [On-Demand Log Sync](#on-demand-log-sync) | How device logs are pulled from cloud |
| [What This Is](#what-this-is) | HMI identity and scope |
| [Directory Structure](#directory-structure) | Frontend and API source layout |
| [Auth](#auth) | Cookie-based JWT, login/session flow |
| [Database](#database) | TypeORM entities and DB connection |
| [Deployment](#deployment) | Production Railway deploy and env vars |
| [Development](#development) | Local dev setup and scripts |
| [Rules](#rules) | Code and architecture constraints |
| [Pipeline Settings — Shared Visual Language with PDS-RoleEditor](#pipeline-settings--shared-visual-language-with-pds-roleeditor) | Visual language contract between HMI and role editor |
| [EC / TDS Display Unit System](#ec--tds-display-unit-system) | Unit selection, display logic, calibration |
| [Device Auth (Firmware → Cloud)](#device-auth-firmware--cloud) | Device token auth from firmware to API |
| [Local Dev Testing with a Physical Device](#local-dev-testing-with-a-physical-device) | Dev-rig setup, creds, port forwarding |
| [Settings Panel: Visual Design Reference](#settings-panel-visual-design-reference) | UI component patterns for settings panels |
| [OTA Firmware Updates](#ota-firmware-updates) | OTA flow from FwServer through HMI API to device |

## ⚠️ Architecture: Cloud-Only — No Physical Connection

**WEB-HMI is a cloud tier only.** There is no direct physical connection (WiFi, BLE, mDNS, or any TCP socket) from this web application to any device. All device↔cloud communication is:

1. **Device → Cloud (telemetry push)**: Device firmware pushes telemetry to `POST /v1/devices/:id/telemetry` on a schedule.
2. **Cloud → Device (commands)**: Config/automation is stored in the cloud. Device polls `GET /v1/devices/:id/pending-sync` and fetches pending config.
3. **Phone-as-relay** (Android App, no cloud plan): Device connects to the phone's hotspot. The native Android app bridges device↔cloud while it has both local WiFi to the device and internet (cellular or other WiFi) to the cloud.

### Cloud Plan vs. No Cloud Plan

| | No Cloud Plan | Cloud Plan ($1/mo) |
|---|---|---|
| **Access from** | Phone on same hotspot as device | Any browser, any network, anywhere |
| **Requires** | PDS Android App + phone hotspot | Just internet on the viewer's device |
| **Device connectivity** | Local WiFi only | Internet (any path) |
| **Fallback** | Phone must stay connected | Works independently |

The only scenario where cloud-enabled access fails is **no internet on the viewer's device** (e.g. airplane mode). The Android app / hotspot path works even without cellular if the phone is on the same local network as the device.

```
── No cloud plan ────────────────────────────────────────────────────────────
WEB HMI (browser) ←HTTPS→ web-hmi/api (cloud) ←HTTPS→ Android App ←WiFi/hotspot→ Device
(Phone must be on device's hotspot; cellular required to reach cloud)

── Cloud plan ($1/mo) ───────────────────────────────────────────────────────
WEB HMI (any browser, anywhere) ←HTTPS→ web-hmi/api (cloud) ←HTTPS→ Device
(Device pushes directly; no phone relay needed)
```

**Never** add WiFi, mDNS, BLE, IP scan, or gateway-proxy logic to WEB-HMI.

### Online/Offline Detection

A device is considered **online** if `lastSeenAt` is within the last 5 minutes. The device firmware updates this field on every telemetry push.

```typescript
const isOnline = device.lastSeenAt
  ? Date.now() - new Date(device.lastSeenAt).getTime() < 5 * 60 * 1000
  : false;
```

---

## Frontend Routing (React Router v6)

The frontend uses `BrowserRouter` with the following URL structure.
Vite serves `index.html` for all paths in dev; Express does the same in production.

```
/                          → redirect → /devices
/login                     → LoginScreen
/devices                   → DeviceListScreen  ("My Devices" landing page)
/devices/:id               → DeviceHMIScreen  (per-device layout + sub-nav)
/devices/:id/settings      → SettingsScreen   (friendly name, cloud sub, pipeline config)
/devices/:id/logs          → LogsScreen       (cloud telemetry + config history)
/devices/:id/versions      → VersionScreen    (firmware info + OTA trigger)
/devices/:id/preferences   → PreferencesScreen (app-level prefs: theme, notifications)
/devices/:id/about         → AboutScreen      (device info panel)
/devices/:id/dashboard     → DashboardScreen  (live — only shown when device online)
/devices/:id/control       → ControlPanel     (live — only shown when device online)
/devices/:id/automation    → AutomationBuilder(live — only shown when device online)
```

### Live Tab Gating

Live tabs (Dashboard / Control / Automation) are shown in `DeviceHMIScreen` only when `isOnline === true`. Do **not** gate on `isConnected` — that field no longer exists.

### Device Card Convention

Cloud device cards always show:
- **Type badge** (short code): `AERO` (aero-ctrl), `CHIL` (h20-chiller), `FEED` (portioning-feeder)
- **Title**: `friendlyName` if set, otherwise `serialNumber`
- **Online / Offline pill**: derived from `lastSeenAt`

Add new device type codes in the `DEVICE_TYPE_CODE` map in
`src/screens/DeviceListScreen.tsx` and `src/screens/DeviceHMIScreen.tsx`.

### Screen Authorship Rules

| Screen | File | Notes |
|--------|------|-------|
| My Devices | `DeviceListScreen.tsx` | Cloud list, Claim Device modal, Download App banner |
| Device HMI layout | `DeviceHMIScreen.tsx` | Breadcrumb + sub-nav + `<Outlet>` |
| Settings | `SettingsScreen.tsx` | Friendly name, cloud subscription ($1/mo), pipeline JSON |
| Logs | `LogsScreen.tsx` | `useParams().id` for device ID, Sync from Device button |
| Versions | `VersionScreen.tsx` | Reads outlet context for device info |
| Preferences | `PreferencesScreen.tsx` | Theme, notifications — no connection state |
| About | `AboutScreen.tsx` | Device info panel |

### Outlet Context

`DeviceHMIScreen` exposes `DeviceHMIContext` via `<Outlet context={...}>`.
Child screens that need the device record use:
```typescript
import { useOutletContext } from 'react-router-dom';
import type { DeviceHMIContext } from './DeviceHMIScreen';
const { device, deviceId } = useOutletContext<DeviceHMIContext>();
```

---

## Cloud Subscription ($1/month)

Device cloud features (log archive, pushed alarms, remote config history) are gated on `device.cloudEnabled`. A Stripe subscription manages billing.

- `POST /v1/cloud/subscribe  { deviceId }` — creates Stripe subscription, sets `cloudEnabled: true`
- `POST /v1/cloud/cancel     { deviceId }` — cancels at period end
- `GET  /v1/cloud/status`                  — returns subscription status for all user devices
- Webhook: `POST /v1/cloud/webhook`        — handles `subscription.deleted`, `subscription.updated`, `invoice.payment_failed`

**Env vars required:**
```
STRIPE_SECRET_KEY        — Stripe secret key
STRIPE_WEBHOOK_SECRET    — Stripe webhook signing secret
CLOUD_PLAN_PRICE_ID      — Stripe Price ID for the $1/month plan
```
In dev without `STRIPE_SECRET_KEY`, subscribe/cancel return mock responses so UI works without Stripe.

Billing uses the user's existing `stripeCustomerId` from the shared `users` table (created during Marketplace registration).

---

## On-Demand Log Sync

Users can request the device push its locally buffered logs to the cloud:
- UI: "↻ Sync from Device" button in LogsScreen
- API: `POST /v1/devices/:id/sync-request` — sets a `pendingSyncRequest` flag on the device
- Firmware polls: `GET /v1/devices/:id/pending-sync` → `{ pending: true/false }`
- Firmware responds by batch-uploading any locally buffered telemetry

---

## What This Is

`WEB-HMI` is the full-stack device Human-Machine Interface. It is two things in one directory:

| Sublayer | Path | Responsibility |
|----------|------|----------------|
| **React Frontend** | `web-hmi/` (root) | Cloud-only SPA — device registry, cloud telemetry, automation pipeline builder, OTA |
| **Express Backend** | `web-hmi/api/` | Cloud device registry, user ownership, config persistence, OTA metadata, cloud billing, auth |

The frontend runs on Vite (dev: port 5173). The backend API runs on Express + TypeORM (dev: port 3001). In production, the Vite build outputs to `web-hmi/dist/` and the Express server serves it.

---

## Directory Structure

```
web-hmi/
├── AI-INSTRUCT.md              ← This file
├── package.json                ← Vite React frontend
├── vite.config.ts              ← Vite config (dev proxy: /v1/* → localhost:3001)
├── tsconfig.json
├── index.html                  ← SPA entry point
├── src/                        ← React + TypeScript source
│   ├── App.tsx
│   ├── screens/
│   │   ├── DeviceListScreen.tsx    ← Cloud list + claim modal + download app banner
│   │   ├── DeviceHMIScreen.tsx     ← Per-device layout + lastSeen-based online gating
│   │   ├── SettingsScreen.tsx      ← Device config + cloud subscription CTA
│   │   ├── LogsScreen.tsx          ← Telemetry archive + config history + sync button
│   │   ├── VersionScreen.tsx       ← Firmware info + OTA trigger
│   │   ├── PreferencesScreen.tsx   ← App-level prefs (theme, notifications)
│   │   ├── AboutScreen.tsx         ← Device info panel
│   │   ├── DashboardScreen.tsx     ← Live dashboard (online devices only)
│   │   ├── ControlPanel.tsx        ← Live control (online devices only)
│   │   └── AutomationBuilder.tsx   ← Automation (online devices only)
│   ├── components/
│   ├── context/
│   │   ├── AppContext.tsx           ← Pipeline/automation state (cloud-ready)
│   │   └── AuthContext.tsx          ← JWT auth
│   ├── hooks/
│   ├── automation/
│   └── types/
│
└── api/                        ← Express + TypeORM backend
    └── src/
        ├── index.ts
        ├── entities/
        │   ├── device.ts           ← cloudEnabled, cloudSubscriptionId, cloudPeriodEnd, lastSeenAt
        │   └── ...
        └── routes/
            ├── devices.ts          ← /v1/devices/* + sync-request + pending-sync
            └── cloud.ts            ← /v1/cloud/* (subscribe, cancel, status, webhook)
```

---

## Auth

- JWT shared with `WEB-Marketplace`. A marketplace-issued token is valid here.
- `JWT_SECRET` env var must match across all three services.

---

## Database

- Shared PostgreSQL instance (same as `WEB-Marketplace` and `WEB-FwServer`).
- `synchronize: false` in all environments — schema is managed by DB-Central migrations only (run `/db-migrate`).
- **All TypeORM entities are defined in `DB-Central/src/entities/`**. The `web-hmi/api/src/entities/` files are re-export shims only — do not add entity definitions there.
- **All migrations run through DB-Central**. The two legacy HMI migration files in `api/src/migrations/` are historical records; they have already been applied and will not re-run.
- Connection pool: `extra: { max: 5 }` on all three services — combined max 15 connections (within Railway's ~25 cap).

> **→ Root `AI-INSTRUCT.md` § Device Identity Model — Field Source of Truth** — defines all DB fields including the `board` and `hwrev` columns (formerly `platform`) used in OTA URL construction and firmware lookups.

---

## Deployment

- **Railway**: one monolithic service (`web-hmi/api`). The Railway build compiles PDS-Pipeline, builds the React frontend (`web-hmi/`), then builds the TypeScript API (`web-hmi/api/`). Express serves `../../dist` (the Vite output) as static files.
- **Path prefix**: `/hmi` for frontend; `/hmi/api` for API calls — set via `VITE_BASE_PATH=/hmi/` and `VITE_API_PREFIX=/hmi/api` in Railway build env.
- **URL shape**: `pipedreamsystems.com/hmi/` (frontend) and `pipedreamsystems.com/hmi/api/v1/...` (API).
- **Gateway**: `WEB-Gateway/` Nginx service has two location rules: `/hmi/api/` strips the API prefix before forwarding (Express sees `/v1/...`), and `/hmi/` strips the frontend prefix for assets/SPA.
- **Railway build command** (in `railway.toml`):
  ```
  cd PDS-Pipeline && npm ci && npm run build && cd ../WEB-HMI && npm ci && npm run build && cd api && npm ci && npm run build
  ```
- **Env vars required at build time** (Railway dashboard):
  - `VITE_BASE_PATH=/hmi/`
  - `VITE_API_PREFIX=/hmi/api`
- **Env vars required at runtime**:
  - `DATABASE_URL`, `JWT_SECRET`, `NODE_ENV=production`, `PORT`, `BASE_URL=https://pipedreamsystems.com/hmi`
  - Stripe keys for cloud subscription, `FW_SERVER_URL` for firmware proxy

### Split Seam

To split this monolith into a standalone API + standalone frontend service (no code changes once the seam is wired):

1. In `web-hmi/api/src/index.ts`, wrap the static-serving block with `if (process.env.SERVE_FRONTEND !== 'false')`. Set `SERVE_FRONTEND=false` on Railway → pure API mode.
2. Deploy `web-hmi/` as a new Railway static service; it builds `dist/` and serves it with `serve -s dist`.
3. Extend `apiClient.ts`: check `import.meta.env.VITE_API_ORIGIN` as a fallback before `VITE_API_PREFIX` (for cross-domain splits; same-domain gateway split needs no change here).
4. In `WEB-Gateway/nginx.conf`, point `location /hmi/` to the new frontend service and `location /hmi/api/` to the API service.

See `## Future: Splitting Frontend and API` in `.github/TODO/ToDo-05162026-PathRouting.md` for full cost estimate and step details.

---

## Development

```powershell
# Frontend (Vite dev server, port 5173)
Set-Location "k:\PDS_AutomationSuite\WEB-HMI"
npm run dev

# Backend API (port 3001)
Set-Location "k:\PDS_AutomationSuite\WEB-HMI\api"
npm run dev
```

Vite proxies `/v1/*` → `http://localhost:3001` in dev. No gateway, no path prefix. Dev `.env` sets `VITE_BASE_PATH=/` and `VITE_API_PREFIX=` (empty).

---

## Rules

- **Never** add WiFi, BLE, mDNS, or IP-scan logic to WEB-HMI frontend.
- **Never** reference `isConnected`, `connectDirect`, `deviceIp`, or `PDS_web_NetworkManager` in any new screen.
- **Never** add marketplace business logic (orders, bids, payments) here.
- **Never** run DB migrations from this service (production).
- **Never** write to the `firmwares` table — that is `WEB-FwServer`'s concern.
- **Always** derive online/offline from `lastSeenAt` (5-minute window).
- **Always** check `web-hmi/api/src/devices/` when adding a new device type.
- **Never** return `deviceToken` from any GET endpoint — it is a write-once credential returned only at claim time and token rotation.

---

## Pipeline Settings — Shared Visual Language with PDS-RoleEditor

`PipelineBlockPanel.tsx` (`src/components/`) is the web equivalent of the VS Code extension's
centre panel (`PDS-vscode-extension/role-webview.js`). They share the **same visual language**
by design — collapsible func-cards, hue-tinted left border (8-hue cycle), instance-var rows
with monospace label / input / unit-badge.  **Do not redesign this component** to match generic
Bootstrap or MUI patterns — it must match the VS Code extension visually.

### How pipeline data flows to this component

```
Device flash (L1/L2/L3 bins)
  └─ post_pipeline.ps1 → POST /v1/devices/:id/pipeline
       └─ server stores framed binary as currentPipeline (base64)
            └─ GET /v1/devices/:id/pipeline-settings
                 └─ pipeline-codec.ts decodes binary → DecodedPipelineSettings JSON
                      └─ PipelineBlockPanel renders it
```

The React frontend **never** decodes L1/L2/L3 binaries — all decoding is server-side in
`web-hmi/api/src/pipeline/pipeline-codec.ts`.  The frontend receives pre-decoded JSON.

### Shared block registry and types

`PDS-Pipeline/` (`@pds/pipeline`) is the single source of truth for:
- Block type definitions — struct layouts, field metadata, display names
- `AccessLevel` type (`'hw' | 'tuner' | 'user'`)
- Decoded output types — `DecodedField`, `DecodedBlock`, `DecodedPipeline`, `DecodedPipelineSettings`

These types flow from `@pds/pipeline` → API codec (produces them) → frontend component (consumes them).
**Do not redefine these types** anywhere in `web-hmi/src` or `web-hmi/api/src`.

| Consumer | Import path |
|----------|-------------|
| Frontend component | `import type { ... } from '@pds/pipeline'` (via `web-hmi/node_modules`) |
| API codec | `import type { ... } from './block-registry.js'` (re-export shim → `@pds/pipeline`) |
| VS Code extension | bundled by esbuild from `PDS-Pipeline/dist/` |

The `WEB-HMI` frontend package has `"@pds/pipeline": "file:../PDS-Pipeline"` in its `package.json`,
resolved to `node_modules/@pds/pipeline` after `npm install`.  Railway picks this up because the
monorepo root is checked out in full (Root Directory is cleared in Railway dashboard).

### If `currentPipeline` is null on the server

The Settings page will show "no L3 binary". This happens when bins were flashed directly
with esptool (`--l1l2l3`) but never pushed through the server.  Fix: run `/pds-push-pipeline`
(`post_pipeline.ps1 -Role <role>`) to register the bins with the server.

---

## EC / TDS Display Unit System

### The mS/cm Contract

The firmware **always outputs EC readings in mS/cm** (electrical conductivity). This is an architectural contract — no PPM conversion happens in firmware.

Calibration constants in role JSON (`Vmin`, `Vmax`, `scale_min`, `scale_max`) are in mS/cm:
- `scale_min = 0` mS/cm (zero conductivity)
- `scale_max = 2.0` mS/cm (= 1000 PPM500 = 1400 PPM700)

The firmware computes:
```
ec_ms_cm = lerp(Vmin → Vmax, scale_min → scale_max, V_adc)
```

For calibration: at probe voltage `V_ref` in a solution of known EC `X mS/cm`:
```
Vmax = (V_ref / X) × scale_max
```

The telemetry field name for the EC sensor is `"ec"` (not `"ppm"`).

`alarm_low` and `alarm_high` in role JSON are in mS/cm. The CalibrationScreen shows and saves these values in mS/cm directly.

### Display Conversion (HMI-side only)

`src/hooks/useEcUnits.ts` converts the firmware's mS/cm telemetry value for display only:

| User preference | Factor | Example (1.0 mS/cm) |
|---|---|---|
| PPM500 (default) | ×500 | 500 PPM |
| PPM700 | ×700 | 700 PPM |
| EC (mS/cm) | ×1 | 1.00 mS/cm |
| CF | ×10 | 10.0 CF |

This conversion is applied in `DashboardScreen.tsx` (`PeriphCard`, `field === 'ec'`) and `LogsScreen.tsx` (`PeriphReadingCell`). Both import `convertEcValue` and `EC_UNIT_LABELS` / `EC_UNIT_DECIMALS` from `useEcUnits.ts`.

The user sets their preference in `PreferencesScreen.tsx`. It is persisted to `localStorage` under key `pds_ec_unit` and propagated via a `CustomEvent('pds-ec-unit-changed')`.

**Do not** add PPM conversion to the firmware or pipeline. **Do not** store PPM values anywhere in the device layer. **Do not** change the `FROM_EC` factors in `useEcUnits.ts` without updating this section.

---

## Device Auth (Firmware → Cloud)

The physical device authenticates using a **device token** — a 64-char hex secret stored in NVS.

### How it works

1. **Provisioning**: Admin provisions device via `POST /v1/devices/admin/provision` → gets `serialNumber` + `claimCode`.
2. **Claim**: User claims device via `POST /v1/devices/register` → response includes `deviceToken` (only time it is returned).
3. **NVS flash**: Owner writes three NVS keys to the device:
   - `api_url` — base URL of WEB-HMI API (e.g. `http://192.168.1.80:3001/v1`)
   - `device_id` — UUID from the claim response
   - `device_token` — 64-char hex secret from the claim response
4. **Firmware push**: On each check-in cycle, device sends:
   ```
   POST /v1/devices/{device_id}/telemetry
   X-Device-Token: {device_token}
   Content-Type: application/json
   { "snapshot": {...}, "deviceTimestampUnix": ..., "deviceUptimeMs": ..., "packetId": ..., "statusFlags": ... }
   ```
5. **Pending sync poll**: Device polls for log sync requests:
   ```
   GET /v1/devices/{device_id}/pending-sync
   X-Device-Token: {device_token}
   ```

### Token rotation

If a token is compromised:
```
POST /v1/devices/:id/refresh-token
Authorization: Bearer <user_jwt>
```
Returns a new `deviceToken`. The old token is immediately invalidated. Re-flash NVS on the device.

### Auth middleware reference

| Middleware | Used by | Accepts |
|---|---|---|
| `verifyToken` | User-facing endpoints | JWT (Bearer header or httpOnly cookie) |
| `verifyDeviceToken` | Device-only endpoints (`pending-sync`) | `X-Device-Token` header |
| `verifyTokenOrDeviceToken` | Mixed endpoints (`POST telemetry`) | Either of the above |

---

## Local Dev Testing with a Physical Device

The ESP32 **cannot reach `localhost`** — it needs a real IP address. Three options:

### Option 1: LAN IP (recommended for bench testing)
Your dev machine is already on your LAN. Check its IP (e.g. `192.168.1.80` — shown in `npm run dev` Vite output).

Put the ESP32 on the same WiFi network and configure NVS:
```
api_url    = http://192.168.1.80:3001/v1
device_id  = <UUID from claim>
device_token = <64-char hex from claim>
```
No Railway deployment needed. Both device and dev server must be on the same LAN.

### Option 2: ngrok (off-network testing without Railway)
```powershell
ngrok http 3001
# → gives e.g. https://abc123.ngrok-free.app
```
Flash `api_url = https://abc123.ngrok-free.app/v1` to NVS. Device can now reach dev API from anywhere.

### Option 3: Railway (production / staging)
Deploy `web-hmi/api` to Railway. Set `DATABASE_URL`, `JWT_SECRET` env vars. Flash the Railway URL.

### NVS key names
These match the firmware's `nvs_read_string` calls (keys defined in `Device/pds/pds_hal/`):

| NVS Key | Value | Notes |
|---|---|---|
| `api_url` | `http://192.168.1.80:3001/v1` | No trailing slash |
| `device_id` | UUID | From claim response |
| `device_token` | 64-char hex | From claim response — treat as secret |

NVS is written via `PDS-BuildTools/dist/defaults/{ROLE}/nvs_defaults.bin` at flash time.

---

## Settings Panel: Visual Design Reference

**File**: `src/screens/SettingsScreen.tsx` + `src/components/PipelineBlockPanel.tsx`

The Pipeline Settings section of the Settings tab was designed to match the visual
language of the **PDS-Role VS Code extension centre panel** — NOT the generic HMI components.

### Where to look when changing this UI

| Reference file | What it contains |
|---|---|
| `PDS-vscode-extension/role-webview-styles.js` | CSS source: `.func-card`, `.func-card-header`, `.instance-var`, `.instance-group`, `.var-type-badge`, `.pipelines-heading`, hue tinting via `[data-hue]` |
| `PDS-vscode-extension/role-webview-script.js` | JS rendering: `renderPipelineCards()`, `instance-var` rows (lines ~694, 778, 828, 956, 1002), settings loop with `var-type-badge` |

### How PipelineBlockPanel.tsx adapts the role editor

| Role editor pattern | PipelineBlockPanel equivalent |
|---|---|
| `.func-card` + `[data-hue]` left-border tint | `BlockCard`: `border-l-4` + 8-colour `HUE_BORDERS[]` cycle |
| `.func-card-header` collapsible | `<button>` header with chevron rotate |
| `.instance-var` row: `label \| input \| type-badge` | `FieldRow`: `min-w-[130px] font-mono label \| input/toggle \| units badge` |
| `.pipelines-heading` divider | `Pipeline N` label + `flex-1 border-t` horizontal rule |
| Module-level variables section | Omitted — the role editor's module vars are design-time; L3 fields serve the same purpose at runtime |

### mode prop

- `mode='settings'` — hides `readOnly: true` fields (pin assignments). Use on Settings tab.
- `mode='full'` — shows all fields including pins. Intended for a future pipeline editor tab.

### Data flow

```
Device currentPipeline (framed L1+L2+L3 stored as base64)
  ↓  GET /v1/devices/:id/pipeline-settings
  web-hmi/api/src/pipeline/pipeline-codec.ts  →  decodeSettings(l1, l3)
  web-hmi/api/src/pipeline/block-registry.ts  →  struct layout + fieldMeta
  ↓  JSON: { updateRateMs, pipelines[…] }
PipelineBlockPanel renders dynamic form
  ↓  PATCH /v1/devices/:id/pipeline-settings  { pipelines: edits }
  encodeSettings(l1, existingL3, edits)  →  new L3
  framePipeline(l1, l2, newL3)  →  stored as pendingPipeline + currentPipeline
  ↓  device picks up on next GET /pending-pipeline poll
```

### Block-registry reference

`api/src/pipeline/block-registry.ts` is a TypeScript port of
`PDS-Role/tools/blob_packer.py` `BLOCK_DEFS`. When `blob_packer.py` BLOCK_DEFS
change (new block type, changed struct), **update both files in sync**.

---

> **→ Root `AI-INSTRUCT.md` § Device Identity Model — Field Source of Truth** — complete field-flow map: how `board`, `hwrev`, `role`, `serialNumber`, `deviceType`, `displayName`, and `firmwareVersion` are defined, where they are set, how they flow through provisioning into the DB, and how the `GET /v1/devices/:id` response and `AboutScreen.tsx` consume them. Includes OTA URL formula and About page field map.

---

## OTA Firmware Updates

The `VersionScreen.tsx` is the user-facing trigger for OTA updates. The full paradigm is documented in **`.dev-docs/OTA-PARADIGM.md`** (covers FW Server, HMI API, firmware polling, ACK, version source of truth, and E2E deploy sequence).

For local dev credentials (Bearer token, rig IDs, status check scripts): **`.github/debug/_dev_auth.md`** (gitignored).

