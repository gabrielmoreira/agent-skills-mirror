# AI-INSTRUCT: PhoneApps — Cross-Platform Mobile

**Last Updated**: 2026-05-27  
**Authority**: DEEP � Authoritative for all work inside `phone-apps/`

---

## Contents

| § | What's here |
|---|-------------|
| [Purpose](#purpose) | What phone-apps/ contains |
| [The Cross-Platform Mandate](#the-cross-platform-mandate) | Both apps must stay feature-identical |
| [Shared Contract (What Both Apps Agree On)](#shared-contract-what-both-apps-agree-on) | API, BLE UUIDs, auth model shared across apps |
| [Required Architecture Layers (Both Platforms)](#required-architecture-layers-both-platforms) | Mandatory layers for each app |
| [Screen Inventory (Both Apps Must Have These)](#screen-inventory-both-apps-must-have-these) | Required screens list |
| [Generic Decoder / Assembler Pattern](#generic-decoder--assembler-pattern) | Telemetry binary decode pattern |
| [Authentication](#authentication) | JWT auth and credential storage |
| [OTA Flow (Cloud-Dispatched)](#ota-flow-cloud-dispatched) | OTA update flow |
| [What Belongs Here vs Elsewhere](#what-belongs-here-vs-elsewhere) | Scope boundary |
| [Directory Reference](#directory-reference) | Subdirectory cross-references |

## Purpose of the PDS ecosystem.

```
phone-apps/
├── Android/          ← Kotlin + Jetpack Compose (active)
└── Ios/              ← Swift + SwiftUI (scaffold — not yet implemented)
```

Both apps are **cloud-first** clients: they talk to the same WEB-HMI REST API (`WEB-HMI/api`) and use the same BLE provisioning protocol (defined in `PROTOCOL.md`). They are independent native codebases — no shared code files, no cross-compilation framework (no Flutter, no React Native). Sharing is **architectural**, not file-level.

---

## The Cross-Platform Mandate

> **Every feature must be designed generically, then implemented per-platform.**

When you add a new capability to either app:

1. Define the **intent** in generic terms (layer name, data model name, API contract).
2. Implement it in one platform first using that generic design.
3. The other platform implementation follows the same design, not the other platform's code.

If a design requires a platform-specific workaround, isolate it in the platform layer. The rest of the stack stays generic.

---

## Shared Contract (What Both Apps Agree On)

Neither app owns any protocol definition. All shared contracts are defined externally:

| Shared Thing | Defined By | Where |
|---|---|---|
| BLE provisioning UUIDs | PROTOCOL.md | `PROTOCOL.md` + `phone-apps/android/…/ble/BleConstants.kt` |
| Cloud REST API shape | WEB-HMI API routes | `WEB-HMI/api/src/routes/devices.ts` |
| Device telemetry binary format | Device firmware structs | `PDS_TELDATA_*` structs in `Device/pds/` |
| Pipeline binary format (L1/L2/L3) | Pipeline packer | `PDS-Pipeline/` |
| OTA flow | HMI API OTA routes | `WEB-HMI/api/src/routes/devices.ts` |

**Rule**: If the contract changes in any of those places, both apps must update in the same operation.

---

## Required Architecture Layers (Both Platforms)

Both apps must implement these conceptual layers, named consistently:

### 1. `Network` — Cloud API client
- Authenticates with JWT (Bearer token from `POST /v1/auth/login`)
- Calls all HMI REST endpoints (`GET /v1/devices`, `GET /v1/devices/:id`, telemetry, OTA, pipeline-settings, etc.)
- Supports a **local relay mode**: connects to device IP directly using `X-Device-Token` header (for local network fallback)
- Supports **mock mode** for development without a live server

**Android**: `NetworkManager.kt`  
**iOS**: `NetworkManager.swift` (to be created, mirroring the same modes)

### 2. `Ble` — BLE provisioning
- Scans for devices advertising `PROVISIONING_SERVICE_UUID` (`0000181c-…`)
- Writes WiFi SSID to `SSID_CHARACTERISTIC_UUID` (`00002a3d-…`)
- Writes WiFi password to `PASSWORD_CHARACTERISTIC_UUID` (`00002a3e-…`)
- Writes connect trigger to `CONNECT_CHARACTERISTIC_UUID` (`00002a3f-…`)
- Reports scan/connection state via observable state (Flow / Publisher)

**Android**: `BluetoothManager.kt` + `BleConstants.kt`  
**iOS**: `BleManager.swift` + `BleConstants.swift` (to be created)

### 3. `DevicePlatform` — Per-platform capabilities and OTA
- **Abstract layer** (`abstract/`): `OtaProvider`, `PlatformInterface`, `DevicePinMap`, `PlatformPinCapabilities`
- **Platform implementations** (`<targetId>/`): one subdirectory per MCU target, matching HAL target names
- OTA is now **cloud-dispatched** — the app calls `POST /v1/devices/:id/ota { version }` instead of pushing a binary directly. The `OtaProvider` on each platform is still used for legacy direct-BLE OTA if needed.

**Android**: `dev_platforms/abstract/` + `dev_platforms/<targetId>/`  
**iOS**: mirror the same structure under `DevicePlatforms/Abstract/` + `DevicePlatforms/<TargetId>/`

### 4. `Models` — Shared data model types
Data classes/structs that mirror the device protocol. These must be kept in sync with the binary format defined in `Device/pds/`:

| Model | Mirrors |
|---|---|
| `TeldataHeader` | `PDS_TELDATA_header_t` |
| `TeldataPacket` | `PDS_TELDATA_packet_t` |
| `AdcReading`, `PwmState`, `GpioState`, `LedState` | Per-pin substructs |
| `PinFunction` (enum) | `pds_pin_function_t` enum values |
| `DeviceStatus` | HMI API `GET /v1/devices/:id` response |

**Android**: `models/DataTypes.kt`, `models/Serialization.kt`  
**iOS**: `Models/DataTypes.swift`, `Models/Serialization.swift`

### 5. `Automation` — Pipeline models and UI
- Generic data models for conditions, actions, timers, and pipelines
- Does **not** contain platform-specific serialization logic — that belongs in `DevicePlatform/PlatformInterface`
- Serialization to L1/L2/L3 binary blobs is done via `PlatformInterface.serializePipeline()`

**Android**: `automation/datamodels/`, `automation/PlatformInterface.kt`, `automation/PipelineBuilders.kt`  
**iOS**: mirror under `Automation/`

### 6. `UI` — Screens and ViewModels
- MVVM throughout: each screen has a ViewModel; ViewModel holds state and calls Network/Ble
- Screens are platform-native (Compose / SwiftUI) — but the navigation structure and screen inventory must be the same on both platforms
- No business logic in UI files

**Android**: `ui/`, `viewmodel/`  
**iOS**: `UI/`, `ViewModel/`

---

## Screen Inventory (Both Apps Must Have These)

| Screen | Purpose |
|---|---|
| Login / Onboarding | JWT auth against HMI API |
| Device List | Lists all devices for this user (`GET /v1/devices`) |
| Device Home | Live telemetry dashboard for selected device |
| Automation / Pipeline | View/edit automation pipeline |
| Settings | App settings, account management |
| Associate Device | BLE provisioning wizard (scan → credential entry → connect) |
| Version / OTA | Firmware version info, update trigger, auto-update toggle |
| Sysconf | System configuration (pin assignments, peripheral settings) |

---

## Generic Decoder / Assembler Pattern

Telemetry decoding and pipeline packing must be written as **generic decoders/assemblers** — not hardcoded for any specific role or device type.

- The decoder reads the `TeldataHeader` to know how many ADC/PWM/GPIO/LED entries to parse.
- It does not hard-code "pin 3 is pH sensor". It reads `pinNumber` and `label` from the binary and presents them generically.
- The UI consumes a list of decoded `AdcReading`, `PwmState`, etc. — it does not address pins by constant.
- Pipeline packing calls `PlatformInterface.serializePipeline()` — the platform impl knows the struct layout.

**This is the same philosophy as the server-side pipeline packer (`PDS-Pipeline/`).** The phone is just another decoder.

---

## Authentication

- **JWT**: Obtained via `POST /v1/auth/login { email, password }` → `{ token }`. Stored in secure storage (Keychain / EncryptedSharedPreferences). Sent as `Authorization: Bearer <token>` on every cloud request.
- **Local relay**: `X-Device-Token` header (the device's NVS token) for direct device communication. Never stored long-term; entered manually or scanned via QR.
- **No plaintext credential storage.** Tokens must be stored in the platform secure store.

---

## OTA Flow (Cloud-Dispatched)

The cloud OTA flow is:
1. App calls `GET /v1/devices/:id/available-firmware` → gets list of versions
2. App calls `POST /v1/devices/:id/ota { version }` → cloud queues OTA
3. Device polls `GET /pending-sync` → finds `otaUrl` + `otaVersion` → calls `esp_https_ota()` → ACKs → reboots
4. App shows pending OTA status by reading `device.pendingOtaVersion` from `GET /v1/devices/:id`

The app does **not** push a binary to the device. It only instructs the cloud to queue it.

---

## What Belongs Here vs Elsewhere

| Thing | Belongs In |
|---|---|
| BLE provisioning UUIDs | `phone-apps/android/…/BleConstants.kt` (authoritative) / mirrored in iOS |
| Cloud API data shape | `WEB-HMI/api/src/routes/` |
| Binary telemetry format | `Device/pds/` firmware headers |
| Pipeline packing rules | `PDS-Pipeline/` |
| Phone app network code | `phone-apps/android/` or `phone-apps/ios/` |
| Phone app UI | `phone-apps/android/` or `phone-apps/ios/` |

---

## Directory Reference

| Directory | AI-INSTRUCT | Status |
|---|---|---|
| `phone-apps/android/` | `AI-INSTRUCT.md` | Active — Kotlin + Jetpack Compose |
| `phone-apps/ios/` | `AI-INSTRUCT.md` | Scaffold — Swift + SwiftUI |


