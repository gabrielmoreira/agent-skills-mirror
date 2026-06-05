# AI-INSTRUCT: PDS-BuildTools

**Purpose**: Firmware compilation and build orchestration for hardware targets

**Location**: `K:\PDS_AutomationSuite\PDS-BuildTools`

**This is the AUTHORITATIVE instruction set for build operations in this directory.**

**Authority Level**: DEEP (Authoritative for this subdirectory; overrides parent guidelines for build-specific concerns)

---

## Contents

| § | What's here |
|---|-------------|
| [Primary Interface: VS Code Extension](#primary-interface-vs-code-extension) | How to invoke builds |
| [Directory Structure](#directory-structure) | Layout of pds-build-tools/ |
| [Discovery System](#discovery-system) | How boards, hwrevs, and roles are discovered |
| [Build Invocation](#build-invocation) | build_selector.py call signature |
| [IDF_TARGET Resolution](#idf_target-resolution) | How the ESP-IDF target chip is determined |
| [CMake Role Variables](#cmake-role-variables) | CMake vars injected per role |
| [Build System Flow](#build-system-flow) | End-to-end build pipeline |
| [Serial Flash vs OTA vs Config Blob Deployment](#serial-flash-vs-ota-vs-config-blob-deployment) | When to use each deployment method |
| [AI Agent Guidelines](#ai-agent-guidelines) | Rules for AI-driven build invocations |
| [Troubleshooting](#troubleshooting) | Common build errors and fixes |
| [Related Documentation](#related-documentation) | Cross-references |
| [NVS Defaults Image](#nvs-defaults-image) | How NVS default blobs are built and flashed |
| [SM-ButtonPusher Integration](#sm-buttonpusher-integration) | Using the button-pusher for automated testing |

## Primary Interface: VS Code Extension

**Primary build interface**: `scripts/build_selector.py --board <board> --hwrev <HWREV> --role <ROLE>` — call it directly from the terminal or via the VS Code extension panel (which spawns it as a subprocess). The Tkinter GUI (`go_gui_tkinter.py`) and old CLI (`go.py`) are legacy — do NOT develop or extend them.

The VS Code extension provides:
- Three-column selector (board ? Hardware Revision ? Role)
- Dynamic discovery from HAL directory structure
- Real-time command preview
- Integrated build output terminal
- Selection persistence

---

## Directory Structure

```
pds-build-tools/
+-- AI-INSTRUCT.md               # This file - AUTHORITATIVE
+-- README.md                    # Quick start for build operations
+-- _legacy/                     # Archived: go.py, go_gui_tkinter.py — DO NOT USE
+-- scripts/
¦   +-- build_selector.py        # Build dispatcher — primary entry point
¦   +-- build_espidf.py          # ESP-IDF toolchain wrapper
¦   +-- build_silabs.py          # Silicon Labs toolchain wrapper
¦   +-- build_in_devcontainer.py # Runs build inside Dev Container (Docker)
¦   +-- cleanup_h2o_dev.py       # Build artifact cleanup
¦   +-- idf_setup_windows.ps1   # One-time ESP-IDF Windows host setup helper
¦   +-- post_pipeline.ps1        # POSTs L1/L2/L3 blobs to WEB-HMI API for a device
¦   +-- gen_nvs_devrig.py        # Generates nvs_devrig.csv + .bin from HMI API device creds
¦   +-- status_check.ps1         # Queries device status + telemetry from WEB-HMI API
+-- tests/                       # Static tests for PDS-BoardEditor board JSON schemas (NOT build system)
¦   +-- test_board_editor.py     # Tests board JSON integrity + pin capability schemas
¦   +-- test_all_boards.py       # Validates named board specs (CPU, GPIO, interfaces)
¦   +-- test_boards_simple.py    # Quick sanity check on board keys + pin_capabilities
+-- config/                      # Legacy — DO NOT USE
+-- docs/                        # Build documentation
+-- cache/                       # Build cache (gitignore)
+-- __pycache__/                 # Python cache (gitignore)
+-- .last_selection.json         # User selection persistence (gitignore)
+-- .dev_creds.json              # Dev-rig WiFi credentials — gitignored, never commit
```

---

## Discovery System

The extension dynamically discovers build targets from the HAL directory structure:

```
Device/pds/pds_hal/board/
+-- esp32c3_sm/
¦   +-- hwrev_001/
¦   ¦   +-- h2o_001/
¦   ¦   +-- sv_001/
¦   +-- hwrev_002/
¦       +-- h2o_001/
+-- esp32s3/
    +-- hwrev_001/
        +-- ...
```

**Discovery Algorithm**:
1. Scan `Device/pds/pds_hal/board/` for board directories
2. For each board, scan for `hwrev_*` subdirectories
3. For each selected hwrev, scan for role directories
4. Populate selectors with discovered items — **roles refresh when hwrev changes**

**No JSON files required** — everything is auto-discovered from directory structure.

---

## Build Invocation

When user clicks COMPILE:

1. **Validation**: Check all three selections (board, hwrev, role)
2. **Command Generation**: Build command string for display
3. **Execution**: Spawn `scripts/build_selector.py` directly (no go.py):
   ```bash
   python scripts/build_selector.py --board <board> --hwrev <HWREV> --role <ROLE>
   ```
4. **Output Streaming**: Capture stdout line-by-line, display in terminal
5. **Status Tracking**: Update UI with build progress/completion

`build_selector.py` detects the toolchain from the board name, reads **IDF_TARGET** from `.board_config` in the board directory, then delegates to `build_in_devcontainer.py`.

---

## IDF_TARGET Resolution

Each board directory contains a `.board_config` file:

```
Device/pds/pds_hal/board/
+-- esp32c3_sm/.board_config     ? IDF_TARGET=esp32c3
+-- esp32_node32s/.board_config  ? IDF_TARGET=esp32
+-- esp32s3/.board_config        ? IDF_TARGET=esp32s3
```

**Never hardcode `esp32c3` in build scripts.** Always read `.board_config`.

---

## CMake Role Variables

The role to compile is communicated to CMakeLists.txt via two CMake cache variables:

| Variable | Format | Example |
|----------|--------|---------|
| `PDS_HWREV` | `hwrev_NNN` | `hwrev_001` |
| `PDS_ROLE` | role directory name | `h2o-106` |

These are appended to `idf.py build` after a double-dash:

```bash
IDF_TARGET=esp32 idf.py -DPDS_HWREV=hwrev_001 -DPDS_ROLE=h2o-106 build
```

**Important**: `-D` flags are **global options** to `idf.py` and must appear **before** the `build` subcommand. Placing them after `build --` causes a Click parsing error in ESP-IDF 5.4.

`build_selector.py` normalises the hwrev value — `"001"` and `"hwrev_001"` are both accepted from callers.

---

## Firmware Version Format

The compiled firmware version string is set by `build_selector.py` as `PROJECT_VER`:

```
firmwareVersion = {hw_code}.{major}.{minor}.{patch}
Example: C02.0.1.018
```

- `hw_code` is the 3-char code for this `board + hwrev` combination, looked up from
  `pds-build-tools/.flash_config.json` ? `hwrev_codes` map.
- Patch auto-increments on every successful build (stored in `.flash_config.json` ? `versions`).
- Major and minor are hand-bumped for breaking changes.
- The firmware reports this string to the cloud via telemetry; the DB `firmwareVersion` column
  is overwritten on every telemetry push.

> **? Root `AI-INSTRUCT.md` § Device Identity Model — Hardware Code Registry** — complete hw_code?board+hwrev table.


## Build System Flow

```
User (VS Code extension panel)
    ? (selects board ? hwrev ? role)
    ? (clicks COMPILE)
    +-? Validate selections
    +-? Update command preview
    +-? Spawn subprocess: scripts/build_selector.py
         +-? Parse --board --hwrev --role [--flash <PORT>]
         +-? Normalise hwrev ("001" ? "hwrev_001")
         +-? Read IDF_TARGET from .board_config
         +-? Start devcontainer, copy /src ? /build
         +-? Run inside container:
         ¦     IDF_TARGET=<target> idf.py -DPDS_HWREV=<hwrev> -DPDS_ROLE=<role> build
         +-? docker cp artifacts ? pds-build-tools/dist/   (always on build success)
         ¦     pds-device.bin, bootloader.bin,
         ¦     partition-table.bin, ota_data_initial.bin
         +-? [if --flash PORT]: esptool flash from Windows host
               sys.executable -m esptool --chip <idf_target> -p <PORT> ...
```

## Serial Flash vs OTA vs Config Blob Deployment

See **`.dev-docs/OTA-PARADIGM.md`** for the complete OTA paradigm (cloud queue, device poll, FW server binary storage, ACK flow).

Three distinct deployment modes — do NOT conflate them:

| Mode | Script | When |
|------|--------|------|
| **Serial flash** (USB/UART) | `build_selector.py --flash COM<N>` | Initial programming, no WiFi yet |
| **OTA upload** (FwServer) | `deploy_firmware.py --ota` | Upload new firmware binary for WiFi OTA delivery |
| **Config blob push** (HTTPS) | `deploy_firmware.py --push-config` | Push L1/L2/L3 to live device at known IP |

### Serial Flash (esptool)

- Flash is **never run inside Docker** — COM ports are Windows-only and invisible to containers.
- `build_selector.py` builds inside the container, copies the 4 binaries to `dist/` via `docker cp`, then flashes from the **Windows host** using `sys.executable -m esptool` (the venv Python that launched the script).
- esptool must be installed in the project venv: `pip install esptool`
- Flash addresses (esp32): `0x1000` bootloader, `0x8000` partition-table, `0x10000` app, `0x2d0000` ota_data

### `headless_flash.py` — Scripted Flash Tool

`scripts/headless_flash.py` is a headless version of the deploy panel's flash logic.
Reads `pds-build-tools/.flash_config.json` for port, chip, role, and ButtonPusher settings.

**Flags:**

| Flag | What it flashes | Address |
|------|-----------------|---------|
| *(none)* | Full firmware (bootloader + partition-table + app + ota_data) | Various |
| `--defaults` | `nvs_defaults.bin` — pipeline + ui_params, **no WiFi creds** | `0x9000` |
| `--nvs <path>` | Any NVS binary at the given path | `0x9000` |
| `--l1l2l3` | L1/L2/L3 pipeline bins + L4 (if present) with 4-byte length frame | Partition table |

**L4 handling in `--l1l2l3`**: If `dist/defaults/<role>/<role>_l4.bin` exists (generated for roles with OLED peripherals), it is automatically included in the flash at the `pds_l4` partition offset. L4 absent = silently skipped.

**?? Dev rig NVS workflow:**

`--defaults` flashes `nvs_defaults.bin` which contains pipeline blobs and `ui_params` but **no WiFi credentials**. On a dev rig device, this **wipes the devrig credentials** (SSID, device_id, device_token).

Correct dev rig NVS flow:
1. Run `gen_nvs_devrig.py` — fetches device credentials from HMI API admin endpoint, writes `nvs_devrig.csv` + `nvs_devrig.bin` to `dist/defaults/<role>/`. Requires `.dev_creds.json` (gitignored) with WiFi credentials.
2. Flash `nvs_devrig.bin` with `--nvs dist/defaults/<role>/nvs_devrig.bin` — restores WiFi + device creds
2. Flash L4 via `--l1l2l3` — L4 goes to the raw `pds_l4` partition
3. On first boot, firmware reads `pds_l4` partition ? seeds NVS `ui_params` automatically ? OLED works

Never use `--defaults` on a dev rig that already has devrig credentials flashed.

### OTA / Config Deploy

Use `deploy_firmware.py` after the device is on WiFi. See that script's docstring for full usage.

---

## AI Agent Guidelines

### When Working in This Directory

1. **VS Code extension is the only UI** — do not develop `go_gui_tkinter.py` or `go.py`
2. **Scripts in `scripts/`** are the build orchestration layer — edit only if changing build logic
3. **Config files** are legacy — dynamic HAL directory discovery is authoritative
4. **Documentation** goes to `docs/` — do not add `.md` files to root

### Adding Features

**UI Changes**: Edit the VS Code extension source
**Build Logic**: Edit `scripts/build_selector.py` and board builders
**New Documentation**: Create in `docs/` only

### Discovery System Rules

To add new boards/hwrevs/roles:
1. Create directories under `Device/pds/pds_hal/board/`
2. They **automatically appear** in the extension selectors
3. No code changes needed

---

## Troubleshooting

### No boards Showing
- Check path: `K:\PDS_AutomationSuite\Device\pds\pds_hal\board\`
- Verify directory structure exists

### Build Fails with No Output
- Check `scripts/build_selector.py` exists
- Verify build tools (ESP-IDF or Silicon Labs SDK) are available via Dev Container
- See `.github/copilot-instructions.md` — ESP-IDF lives in `Device/DEV-Container-ESPIDF/`

### Build Environment
**ESP-IDF is NOT installed locally.** It runs inside the Dev Container at `Device/DEV-Container-ESPIDF/`. Never invoke `idf.py` outside a container context.




---

## Related Documentation

- **PROTOCOL.md** - Device communication protocol
- **AI-INSTRUCT.md** (root) - Project-wide guidelines
- **Device/AI-DEVICE-OVERVIEW.md** - Hardware architecture
- **`.dev-docs/OTA-PARADIGM.md`** - Full OTA update paradigm (FW Server + HMI API + firmware)
- **`.github/debug/_dev_auth.md`** - Dev credentials, rig IDs, token refresh (gitignored)

---

## NVS Defaults Image

When deploying to a fresh device, a pre-populated NVS partition image is flashed alongside the
firmware so the device boots with a working default pipeline configuration.

### Generation

The NVS defaults image is produced by the role tool, **not** this build tool. See
`PDS-Role/AI-INSTRUCT.md §"Blob Generation & NVS Image"` for the full pipeline.

Summary:
```
PDS-Role/tools/blob_packer.py  ?  <role>_l1.bin, _l2.bin, _l3.bin
    + nvs_partition_generator.py  ?  nvs_defaults.bin
```

Output lands in `pds-build-tools/dist/defaults/<role_id>/nvs_defaults.bin`.

### Flash Address

| Artifact | Address |
|---|---|
| `bootloader.bin` | `0x1000` |
| `partition-table.bin` | `0x8000` |
| `pds-device.bin` | `0x10000` |
| `ota_data_initial.bin` | `0x2d0000` |
| `nvs_defaults.bin` | `0x9000` ? NVS partition |

### Deploy Panel Integration

The VS Code deploy panel (in `PDS-vscode-extension/deploy-panel.js`) auto-detects
`dist/defaults/<role_id>/nvs_defaults.bin` when a role is selected and enables a
**"Flash Defaults"** button that adds `0x9000 nvs_defaults.bin` to the esptool command.

### What Is NOT in the NVS Image

WiFi credentials (SSID/password) are **never** included in `nvs_defaults.bin`.
They are always provisioned on first boot via the SoftAP captive portal (`h2o-tower-XXXXXX`).

On dev rigs, use `nvs_devrig.bin` (generated alongside `nvs_defaults.bin`) which contains both pipeline defaults AND devrig-specific credentials. See the `headless_flash.py` section above for the correct NVS flash sequence.

---

---

## SM-ButtonPusher Integration

The **SM-ButtonPusher** (separate device at `K:\SM-ButtonPusher\`) automates the physical BOOT + EN button sequence for boards that **lack auto-reset circuitry**.

### Which boards Need It

| board | `AUTO_RESET` | Notes |
|----------|-------------|-------|
| `esp32c3_sm` | `no` | Super Mini bare PCB has no RC auto-reset circuit — RTS/DTR do not enter download mode |
| `esp32_node32s` | `yes` | CP2104 handles auto-reset via RTS/DTR |
| `esp32s3` | `yes` | DevKitC handles auto-reset via RTS/DTR |

The `AUTO_RESET` key is read from each board's `.board_config`. The deploy panel (`PDS-vscode-extension/deploy-panel.js`) reads this via `discoverBoards()` and **only shows the ButtonPusher checkbox when the selected board has `autoReset: false`**.

### Channel Map

| Channel | Button |
|---------|--------|
| 1 | BOOT |
| 2 | ENABLE (EN/RST) |

### Deploy Panel Behavior

- **`autoReset=true`** (Node32S, esp32s3): uses `--before default_reset` — no ButtonPusher checkbox shown.
- **`autoReset=false`** (esp32c3_sm): uses `--before no_reset` — checkbox **?? Use ButtonPusher (COM5)** appears.
  - **Checked**: deploy panel runs BOOT+EN sequence before esptool, then presses EN to reset after flash.
  - **Unchecked**: user presses BOOT+EN manually before clicking Flash.

### Manual Sequence (if not using ButtonPusher)

```powershell
$bp = "C:\Users\vctma\AppData\Local\Programs\Python\Python312\python.exe"
& $bp -m buttonpusher.cli --port COM5 --json push 1        # hold BOOT
& $bp -m buttonpusher.cli --port COM5 --json push 2        # press EN
Start-Sleep -Milliseconds 200
& $bp -m buttonpusher.cli --port COM5 --json release 2     # release EN
& $bp -m buttonpusher.cli --port COM5 --json release 1     # release BOOT
# device is now in download mode — run esptool.py flash next
```

**Constraint**: COM5 can only be held by one process at a time. Close the ButtonPusher GUI or any serial monitor before running CLI commands.

---

**Last Updated**: 2026-05-27
**Authority Level**: DEEP (Authoritative for pds-build-tools directory)
**Maintainer**: AI Development Team




