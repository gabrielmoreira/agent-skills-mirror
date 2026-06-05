# pds-vscode-extension � AI-INSTRUCT

**Authority**: DEEP — Authoritative for all work inside `pds-vscode-extension/`
**Last Updated**: 2026-05-28

> **Consolidation fixes applied 2026-05-28**:
> - `package.json` `@pds/pipeline` path corrected from `file:../PDS-Pipeline` → `file:../pds-pipeline`
> - `extension.js` `findBoardEditorDir()` search string corrected from `PDS-BoardEditor` → `pds-board-editor`

---

## Contents

| � | What's here |
|---|-------------|
| [What This Is](#what-this-is) | Extension identity and activation |
| [Panels / Commands](#panels--commands) | All panels provided by the extension |
| [Build Panel (`build-panel.js`)](#build-panel-build-paneljs) | Firmware build panel |
| [Deploy Panel (`deploy-panel.js`)](#deploy-panel-deploy-paneljs) | Flash and deploy panel |
| [Role Editor (`role-panel.js`)](#role-editor-role-paneljs) | Role editor cascade model and hwrev source of truth |
| [Pipeline Panel (`pipeline-panel.js`)](#pipeline-panel-pipeline-paneljs) | Pipeline push panel |
| [Publish Panel (`publish-panel.js`)](#publish-panel-publish-paneljs) | Marketplace publish panel |
| [File Structure](#file-structure) | Extension source layout |
| [Key Hardcoded Values to Know](#key-hardcoded-values-to-know) | Hardcoded API URLs, ports, and IDs |

## What This Is

A VS Code extension (`PDS Toolbox`, publisher `pds-automation`, v0.2.0) that provides a sidebar with all PDS development panels. Entry point: `extension.js`. Activated via `onView:pdsToolbox`.

---

## Panels / Commands

| Command | File | What it does |
|---|---|---|
| `pds.openPinleafForge` | `extension.js` | Opens PDS-BoardEditor (React) in a webview |
| `pds.openBuild` | `build-panel.js` | Builds firmware via `build_selector.py` inside the dev container |
| `pds.openDeploy` | `deploy-panel.js` | Flashes binaries to a physical device via `esptool` on the host |
| `pds.openRoleEditor` | `role-panel.js` | Visual role editor (pins, pipeline blocks) |
| `pds.openPipelinePanel` | `pipeline-panel.js` | POSTs L1/L2/L3 pipeline blobs to WEB-HMI API for a device |
| `pds.publishRole` | `publish-panel.js` | Scaffolds WEB-HMI device handler from a saved role JSON |
| `pds.refreshSidebar` | `sidebar-provider.js` | Refreshes the sidebar tree |

---

## Build Panel (`build-panel.js`)

Runs `PDS-BuildTools/scripts/build_selector.py --board <P> --hwrev <R> --role <ROLE>` in a VS Code terminal. Uses the workspace `.venv` python if present. Persists last selection to `PDS-BuildTools/cache/last_selection.json`.

---

## Deploy Panel (`deploy-panel.js`)

Flashes firmware to a physical device. **Flash runs on the host** (not inside the container) because Windows COM ports are not accessible inside Docker.

### Flash source

Binaries are read from `PDS-BuildTools/dist/`:
```
bootloader.bin
partition-table.bin
pds-device.bin
ota_data_initial.bin
```
Build must complete before flashing. The build panel copies artifacts here.

### Chip detection

`getChipForBoard()` reads `Device/pds/pds_hal/board/{board}/.board_config` and returns `IDF_TARGET` (falls back to `esp32`).

### Panel layout

The deploy panel has two side-by-side sections:

**?? Target Connection** (left, flex):
- Target serial port dropdown + ?? Scan
- ? Flash Firmware | ??? Flash Defaults | ?? Serial Monitor  ? all three buttons in one row
- Hint text below showing NVS offset read from CSV (e.g. "ready to flash to 0x9000")

**?? SM-ButtonPusher** (right, 230px) � always visible:
- **Use Button Pusher** checkbox � enables/disables the controls below
- **BP Port** dropdown � auto-populated by the same port scan as the target port
- **BOOT ch** dropdown (1�6) + **Press** / **Rel** test buttons
- **EN ch** dropdown (1�6) + **Press** / **Rel** test buttons

Test buttons send a single `push`/`release` command immediately (no confirmation dialog). Button highlights yellow while pending and re-enables after 800ms via `bpTestDone` webview message.

### Flash modes

`useButtonPusher` is driven by the checkbox. When unchecked, `autoReset = true` and `--before default_reset` is used (RTS/DTR auto-reset). When checked, `autoReset = false` and `--before no_reset` is used with the SM-ButtonPusher sequence.

| Checkbox | How it works |
|---|---|
| Unchecked | `--before default_reset` � board auto-resets via RTS/DTR. Works on boards with CP2102/CH340. |
| Checked | `--before no_reset` � SM-ButtonPusher physically presses BOOT+EN to enter bootloader, then EN again to reboot after flash. |

### SM-ButtonPusher integration

When **Use Button Pusher** is checked, `runFlash()` / `runFlashDefaults()` receive `bpPort`, `chBoot`, and `chEn` from the panel and execute this sequence in the terminal:

```
buttonpusher.cli --port <BP_PORT> push <CH_BOOT>    ? hold BOOT
buttonpusher.cli --port <BP_PORT> push <CH_EN>      ? press EN/RST
Sleep 200ms
buttonpusher.cli --port <BP_PORT> release <CH_EN>   ? release EN/RST (enters bootloader)
buttonpusher.cli --port <BP_PORT> release <CH_BOOT> ? release BOOT

esptool ... write-flash ...                          ? flash

Sleep 500ms
buttonpusher.cli --port <BP_PORT> push <CH_EN>      ? press EN/RST (reboot to app)
Sleep 100ms
buttonpusher.cli --port <BP_PORT> release <CH_EN>
```

Before executing, a **modal confirmation dialog** shows the current BP port + channel mapping. Cancel aborts; nothing is sent to the device.

**Nothing is hardcoded** � BP port and channel numbers come from the panel dropdowns. Python always resolves to `workspaceRoot/.venv/Scripts/python.exe`. The `buttonpusher` package is installed there from the workspace-local copy (`SM-ButtonPusher/CLI`).

**SM-ButtonPusher source**: `SM-ButtonPusher/` (workspace-local copy of the project)
**Re-install CLI**: `pip install -e SM-ButtonPusher/CLI` into workspace `.venv`
**Calibrate**: `python SM-ButtonPusher/go.py`

**Verified working channel mapping (Node32S board, h2o-Tower setup)**:
- BOOT button ? ch4 (push=50�, release=59�)
- EN/RST button ? ch3 (push=65�, release=76�)
- ButtonPusher port: COM5 | Target ESP32 port: COM10 (CH340, USB VID 1A86:7523)
- Timing: 300ms EN hold, 2000ms bootloader settle after button release, then esptool

**Calibration file** (servo push/release angles per channel, written by the calibration tool):
- **Windows**: `%APPDATA%\buttonpusher\buttonpusher_config.json`  (e.g. `C:\Users\vctma\AppData\Roaming\buttonpusher\buttonpusher_config.json`)
- **Linux/Mac**: `~/.config/buttonpusher/buttonpusher_config.json`
- Override with env var `BUTTONPUSHER_CONFIG_DIR`

Values are read **dynamically at runtime** � the server's `get-config` action re-loads `ChannelConfig` from disk each time. The extension fetches calibration when the BP panel is enabled and posts `bpConfig` to the webview, which renders `? push: X�  rel: Y�` hints beneath each channel dropdown. Changing the channel dropdown re-reads from the cached config without a new server call.

**Persistent server process** (`buttonpusher.server`): A single `python -m buttonpusher.server --port <PORT>` child process is spawned on first use and held alive for the VS Code session. All push/release/get-config commands go through its JSON stdin/stdout protocol � no terminal is spawned for BP operations. The process is killed on extension deactivate (`stopBpServer()`).

### Flash addresses

`parsePartitionCsv()` reads `Device/main/partitions.csv` (with `PDS-BuildTools/dist/partitions.csv` as a higher-priority override) to resolve all flash addresses at runtime. No addresses are hardcoded:

| Binary | Source | Fallback |
|---|---|---|
| `bootloader.bin` | chip-dependent: 0x0 for C3/S3/H2/C6; 0x1000 for esp32/esp32s2 | `0x1000` |
| `partition-table.bin` | always `0x8000` (ESP-IDF fixed) | � |
| `pds-device.bin` | `ota_0` offset from CSV | `0x10000` |
| `ota_data_initial.bin` | `otadata` offset from CSV | `0x2d0000` |
| `nvs_defaults.bin` | `nvs` offset from CSV | `0x9000` |

### Flash Defaults (`flashDefaults`)

Button lives in the **Target Connection** panel (same row as Flash Firmware and Serial Monitor). Flashes `PDS-BuildTools/dist/defaults/{role}/nvs_defaults.bin` to the NVS partition offset from the CSV. Uses the same `autoReset`/`useButtonPusher` flags as the main flash.

### Monitor

`runMonitor()` calls `build_selector.py --monitor <port>`, which opens `idf.py monitor` via the container or a local IDF install.

---

## Role Editor (`role-panel.js`)

### Cascade Model � Source of Truth

The top bar drives a strict cascade. **Each level resets all levels below it.**

```
Board (dropdown)
  +-? MCU Target (readonly label � derived from board JSON mcuTarget)
        +-? HwRev (dropdown)
              +-? Role ID (dropdown)
                    +-? Role Name (dropdown)
```

### Where Each Dropdown is Populated From

| Control | Source | File |
|---------|--------|------|
| **Board** | `PDS-BoardEditor/boards/*.json` � one entry per commercial MCU module | `role-fs.js` `scanBoardsFromFs()` |
| **MCU Target** | `boardJson.mcuTarget` from the selected board JSON | derived in webview |
| **HwRev** | `saved_roles/*.json` � unique `hwrev` values matching the selected `board` | `role-webview-script.js` `onBoardChange()` |
| **Role ID** | `saved_roles/*.json` � unique `role_id` values matching `board` + `hwrev` | `role-webview-script.js` `onHwrevChange()` |
| **Role Name** | `saved_roles/*.json` � unique `role_name` values matching `board` + `hwrev` + `role_id` | `role-webview-script.js` `populateNameDropdown()` |

> **?? HwRev source of truth: saved role files only.**
> Board JSON files (`PDS-BoardEditor/boards/*.json`) do NOT contain `hwrev`.
> The HAL filesystem (`Device/pds/pds_hal/board/`) is NOT consulted for hwrev population.
> If the HwRev dropdown is empty after selecting a board, it means no saved roles exist for that board yet � use `+ New HwRev...`.

### Saved Role JSON Shape

`listSavedRolesSync()` in `role-fs.js` returns:
```js
{ id, fileName, target, board, hwrev, role_name }
// id       � data.role_id || fileName stem
// fileName � file stem (used as the key to load the file)
// board    � matches boardId in board JSON
// hwrev    � e.g. 'hwrev-002'; set when user types in '+ New HwRev...'
// role_name � human label; displayed in the Name dropdown
```

### Cascade Reset Rules

- `onBoardChange` ? resets HwRev, Role ID, Name
- `onHwrevChange` ? resets Role ID, Name
- `onRoleChange` ? resets Name; if `__new__` shows Role ID text input; otherwise hides it and calls `populateNameDropdown`
- `populateNameDropdown` ? returns `fileName` of auto-selected name (if exactly one match); does NOT call `onNameChange` (loop prevention)
- `onNameChange` ? if `__add_new__` shows Name text input; otherwise posts `loadRole`

---



POSTs pre-built L1/L2/L3 blobs from `PDS-BuildTools/dist/defaults/{role}/` to the WEB-HMI REST API:

```
POST /v1/devices/{deviceId}/pending-pipeline
Authorization: Bearer <jwt>
```

Connection settings (API URL, JWT, Device UUID) are persisted to `PDS-BuildTools/.pds_pipeline_config.json` and are also readable by `PDS-BuildTools/scripts/post_pipeline.ps1`.

---

## Publish Panel (`publish-panel.js`)

Scaffolds a new device handler in `WEB-HMI/api/src/devices/<slug>/` from a saved role JSON in `PDS-Role/saved_roles/`. Generates `index.ts`, `config-schema.ts`, `firmware-versions.ts`, and registers the handler in `devices/index.ts`.

---

## File Structure

```
pds-vscode-extension/
+-- extension.js            ? activate(), command registration, Pinleaf Forge webview
+-- build-panel.js          ? PDS Build panel
+-- deploy-panel.js         ? PDS Deploy panel (flash + monitor + button pusher)
+-- pipeline-panel.js       ? Pipeline Push panel
+-- role-panel.js           ? Role Editor panel
+-- role-webview.js         ? Role editor webview HTML
+-- role-webview-script.js  ? Role editor webview JS
+-- role-webview-styles.js  ? Role editor webview CSS
+-- role-actions.js         ? Role editor message handlers
+-- role-data.js            ? Role data helpers
+-- role-fs.js              ? Role file system helpers
+-- publish-panel.js        ? Publish Role command
+-- sidebar-provider.js     ? Sidebar tree view
+-- utils.js                ? findWorkspaceRoot, discoverTargets, load/saveLastSelection
+-- media/                  ? Icons / assets
+-- package.json            ? Extension manifest (contributes, commands, views)
```

---

## Key Hardcoded Values to Know

| Value | Location | Notes |
|---|---|---|
| Flash addresses | `parsePartitionCsv()` | Read from `Device/main/partitions.csv` at runtime � **not hardcoded** |
| NVS offset | `parsePartitionCsv()` | Read from `nvs` row in partition CSV � **not hardcoded** |
| ButtonPusher COM port | Panel UI | Selected via **BP Port** dropdown; not hardcoded |
| BOOT / EN channel | Panel UI | Selected via **BOOT ch** / **EN ch** dropdowns; not hardcoded |
| dist/ binary paths | `deploy-panel.js` | `PDS-BuildTools/dist/*.bin` |
| NVS defaults path | `deploy-panel.js` | `PDS-BuildTools/dist/defaults/{role}/nvs_defaults.bin` |
| Pipeline config file | `pipeline-panel.js` | `PDS-BuildTools/.pds_pipeline_config.json` |
