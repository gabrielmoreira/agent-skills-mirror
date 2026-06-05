# Device — Multi-Container Firmware Architecture

**Authority**: DEEP — Authoritative for all work inside `device/`
**Last Updated**: 2026-05-27

---

## Contents

| Section | What's here |
|---------|-------------|
| [Purpose](#purpose) | What the device/ directory contains |
| [Structure](#structure) | Directory layout: firmware source and containers |
| [Container Naming Convention](#container-naming-convention) | How DEV-Container-* directories are named |
| [Mount Architecture](#mount-architecture) | How source is mounted into containers |
| [Build Flow](#build-flow) | Build pipeline from source to binary |
| [For Developers (Editing)](#for-developers-editing) | How to edit firmware source outside containers |
| [For AI Agents / Build System](#for-ai-agents--build-system) | How AI and build scripts invoke the container |
| [Key Files Updated](#key-files-updated) | Files that change with each board/hwrev/role |
| [Verification](#verification) | How to confirm a build is correct |
| [Troubleshooting](#troubleshooting) | Common issues and fixes |
| [Build Structure Change (April 2026)](#build-structure-change-april-2026) | April 2026 architectural change notes |
| [Partition Table (April 2026)](#partition-table-april-2026) | Partition layout and NVS zones |
| [sdkconfig — Optimization and Size](#sdkconfig--optimization-and-size) | Build optimization flags and flash size constraints |

---

## Purpose

This directory (`device/`) contains **device firmware source code** and **containerized development environments** for building it.

**Key Principle**: Device firmware is **truly generic** (CoreBinary). Platform-specific initialization is provided by `pds_platform_main.c` in the selected target's `common/` directory. Board pin-cap specs live in `pds-board-editor/boards/<boardId>.json` (flat — no subdirs).

---

## Structure

```
device/
├── main/                              # Main application entry point
│   ├── CMakeLists.txt
│   ├── main.c
│   └── ...
│
├── pds/                               # PDS hardware abstraction layer
│
├── DEV-Container-esp32c3_sm/             # Container: esp32c3_sm builds
│   ├── .devcontainer/
│   │   ├── devcontainer.json
│   │   └── Dockerfile
│   ├── AI-INSTRUCT.md
│   └── README.md
│
├── DEV-Container-esp32_node32s/          # Container: esp32_node32s builds
│   ├── .devcontainer/
│   │   ├── devcontainer.json
│   │   └── Dockerfile
│   └── ...
│
├── DEV-Container-SILABS/              # Container: Silicon Labs builds  
│   ├── .devcontainer/
│   │   ├── devcontainer.json
│   │   └── Dockerfile
│   ├── AI-INSTRUCT.md
│   └── README.md
│
└── .ai/instruct.md                     # This file
```

---

## Container Naming Convention

**Rule**: Each board has its own container — containers are NEVER shared across boards.

Container directory names follow: `DEV-Container-<board_name>`

| Board dir (`pds_hal/board/`) | Container dir (`device/`) |
|---|---|
| `esp32c3_sm` | `DEV-Container-esp32c3_sm` |
| `esp32_node32s` | `DEV-Container-esp32_node32s` |
| `efr32mg24` *(future)* | `DEV-Container-efr32mg24` |

`build_selector.py` derives the container name automatically as `DEV-Container-{board}` — no configuration key needed.

---

## Mount Architecture

**Key Principle**: Source code is editable on host, all compiler/toolchain artifacts stay container-local.

### Read-Only Source Mounts
Both containers mount source code **read-only** from the host:

```
Host k:\PDS-Master-001\device\main  →  Container /src/main  (read-only)
Host k:\PDS-Master-001\device\pds   →  Container /src/pds   (read-only)
```

### Container-Local Build Directory
- On each build, source is copied from `/src/*` to container-local `/build/*`
- All compiler output stays in container: `/build/main/build/`, `/build/main/sdkconfig`, etc.
- Build artifacts are **never synced back to host**

### Mount Configuration (devcontainer.json)

**ESP-IDF Container**:
```json
"mounts": [
  "source=${localEnv:HOME}${localEnv:USERPROFILE}/.espressif,target=/root/.espressif,type=bind,consistency=cached",
  "source=k:/PDS-Master-001/device/main,target=/src/main,type=bind,readonly",
  "source=k:/PDS-Master-001/device/pds,target=/src/pds,type=bind,readonly"
]
```

**Silabs Container**: Same as ESP-IDF (minus .espressif mount if not needed)

---

## Build Flow

```
build_selector.py detects board
  │
  ├─ ESP32?
  │   └─ devcontainer exec (start container)
  │       └─ Copy /src/* → /build/*  (container-local)
  │           └─ cd /build/main && idf.py build
  │               └─ Output stays in /build/main/build/ (container only)
  │
  └─ Silabs?
      └─ devcontainer exec (start container)
          └─ Copy /src/* → /build/*  (container-local)
              └─ cd /build/main && make
                  └─ Output stays in /build/main/ (container only)
```

---

## For Developers (Editing)

Edit source files directly on host:
```
k:\PDS-Master-001\device\main\*.*    ← Edit here
k:\PDS-Master-001\device\pds\*\*.*   ← Edit here
```

These appear in container at `/src/main` and `/src/pds` (read-only). On next build, they are copied to `/build/main` and `/build/pds` for compilation.

---

## For AI Agents / Build System

> **→ `device/DEV-Container-esp32c3_sm/.ai/instruct.md`** — platform-specific build commands and mount paths for ESP32-C3
> **→ `device/DEV-Container-SILABS/.ai/instruct.md`** — platform-specific build commands for Silicon Labs

General pattern (see container files for authoritative per-board steps):

1. Derive container path: `DEV-Container-{board}` (from `build_selector.py`)
2. Start container: `devcontainer up --workspace-folder "{container_path}"`
3. Copy source: `mkdir -p /build && cp -r /src/main /build/ && cp -r /src/pds /build/`
4. Execute build inside container (ESP32: `idf.py build`, Silabs: `make`)
5. Build output stays in container at `/build/main/build/`

---

## Key Files Updated

### [main/CMakeLists.txt](main/CMakeLists.txt)
- **Before**: `set(EXTRA_COMPONENT_DIRS pds)` - looked for pds in same directory
- **After**: `set(EXTRA_COMPONENT_DIRS ../pds)` - looks for pds at device level
- This allows the source to be copied into `/build/` and still find `/build/pds/`

### [main/idf_component.yml](main/idf_component.yml)
- Removed external `espressif/mdns` dependency (not available in ESP-IDF v5.4.1)
- Uses built-in lwip mdns support instead

### [pds/pds_network/CMakeLists.txt](pds/pds_network/CMakeLists.txt)
- Removed `mdns` from REQUIRES (since it's built-in to lwip)

### [DEV-Container-esp32c3_sm/.devcontainer/devcontainer.json](DEV-Container-esp32c3_sm/.devcontainer/devcontainer.json)
- Updated to mount source read-only at `/src/main` and `/src/pds`
- Fixed Python venv paths for ESP-IDF v5.4.1

---

## Verification

> **→ `device/DEV-Container-esp32c3_sm/.ai/instruct.md`** — exact verification commands for ESP32-C3 container

General check: confirm `/src/main` is read-only and `/build` is writable after starting the container.

---

## Troubleshooting

**Build artifacts syncing back to host**
- This is by design—only source syncs, not build output
- To extract binaries, use: `devcontainer exec ... bash -c 'cat /build/main/build/H2o-Tower.bin' > output.bin`

**Source changes not appearing in build**
- Source is mounted read-only, which is correct
- Changes on host automatically appear in `/src/` in container
- They get copied to `/build/` on next build

**Container using old source**
- `docker system prune -a -f --volumes` clears all containers

---

## Build Structure Change (April 2026)

`device/main/` is the ESP-IDF project root (`CMakeLists.txt` + `main.c`).  
ESP-IDF requires a `main/` **component subdirectory** within the project.

The component lives at `device/main/main/CMakeLists.txt` and references `../main.c`:

```cmake
idf_component_register(
    SRCS "../main.c"
    INCLUDE_DIRS "."
    REQUIRES freertos pds_hal
)
```

`main.c` itself is platform-agnostic — it calls `pds_platform_init()` and
`pds_platform_loop()`, which are implemented in `pds_hal/board/<target>/common/pds_platform_main.c`.

---

## Partition Table (April 2026)

All builds use a **custom `partitions.csv`**, NOT the ESP-IDF default single-app table.
The correct layout for a 4 MB flash (role editor flash size is authoritative):

```
# Name       Type  SubType  Offset    Size
nvs          data  nvs      0x9000    24K     WiFi creds / usrset
phy_init     data  phy      0xF000    4K      RF calibration
ota_0        app   ota_0    0x10000   <app>   Active firmware slot
ota_1        app   ota_1    <calc>    <app>   OTA update slot
otadata      data  ota      <calc>    8K      Boot slot selector
pds_l1       data  0x40     <calc>    64K     L1 pipeline byte stream
pds_l2       data  0x41     <calc>    64K     L2 hw_vars blobs
pds_l3       data  0x42     <calc>    64K     L3 settings blobs
pds_log      data  0x43     <calc>    128K    Diagnostic log ring buffer
```

- **App slot size** is set in the Role Editor (Flash Partitions section) — must be a multiple of 64 KB
- Both OTA slots are identical size — `pds_build_tools` generates `partitions.csv` from role config
- `pds_l1 / pds_l2 / pds_l3` are read/written via `esp_partition_read/write`, NOT NVS
- `pds_log` is a circular ring buffer for field diagnostics

---

## sdkconfig — Optimization and Size

`device/main/sdkconfig` is shared across all boards and hwrevs. Key settings that affect binary size:

### Compiler optimization — MUST be SIZE for all builds
```
CONFIG_COMPILER_OPTIMIZATION_SIZE=y   ← correct (-Os)
CONFIG_COMPILER_OPTIMIZATION_DEBUG=y  ← WRONG — produces -Og (debug), bloats binary 15-25%
```
Do not leave `DEBUG` set. It is not appropriate for any production or OTA build.

### mbedTLS certificate bundle — must be CMN in all builds

PDS devices are commercial-grade products. In production they connect to the HMI API over **HTTPS** (Railway terminates TLS). The CMN bundle is required so the device can validate the server's certificate chain at runtime.

```
CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_CMN=y   ← required — contains the common CAs Railway uses (~30KB)
CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL=y  ← WRONG — full Mozilla bundle (~80KB), wasted flash
CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_NONE=y  ← WRONG — cert validation impossible in production
```

`CONFIG_ESP_HTTPS_OTA_ALLOW_HTTP=y` is kept in sdkconfig so the dev-rig can use a plain `http://` `api_url`. It does **not** disable HTTPS for production — a production NVS image sets `api_url` to an `https://` URL and the firmware uses TLS automatically.

### TLS cert validation — dev vs production

`pds_cloud_push.c` gates cert validation with `CLOUD_SKIP_CERT`:

```c
#ifdef CONFIG_PDS_DEV_MODE
#  define CLOUD_SKIP_CERT  true    /* http:// on local dev rig — skip cert check */
#else
#  define CLOUD_SKIP_CERT  false   /* https:// in production — validate against CMN bundle */
#endif
```

Every `esp_http_client_config_t` in cloud push also sets `.crt_bundle_attach = esp_crt_bundle_attach` so the CMN CA bundle is available for validation when `CLOUD_SKIP_CERT` is `false`.

**Never** set `CONFIG_PDS_DEV_MODE=y` in a production firmware build. Production NVS images must use an `https://` `api_url`.

### After sdkconfig changes
A full rebuild inside the devcontainer is required — sdkconfig changes are not incremental:
```bash
cd /build/main && idf.py fullclean && idf.py build