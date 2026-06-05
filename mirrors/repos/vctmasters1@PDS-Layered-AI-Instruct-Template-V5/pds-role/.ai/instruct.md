# AI-INSTRUCT: pds-role

**Purpose**: Role creation and module composition tool for device firmware

**Authority**: DEEP — Authoritative for all work inside pds-role/

**Last Updated**: 2026-05-27





---

## Contents

| �# | What's here |
|---|-------------|
| [What Is a Role?](#what-is-a-role) | Role definition and purpose |
| [Architecture](#architecture) | Role system architecture |
| [Technology](#technology) | Tools and frameworks used |
| [Migration Guide — Old Pattern → 3-Layer Binary Pipeline](#migration-guide--old-pattern--3-layer-binary-pipeline) | How to migrate from old role format |
| [Blob Generation & NVS Image](#blob-generation--nvs-image) | How L1/L2/L3/L4 blobs are packed |
| [GUI Design](#gui-design) | Role editor UI design rules |
| [Core Concepts](#core-concepts) | Blocks, fields, layers explained |
| [Output: What Gets Generated](#output-what-gets-generated) | Files produced by go.py |
| [CLI Usage](#cli-usage) | Command-line interface |
| [Role Configuration Schema](#role-configuration-schema) | JSON schema for role config files |
| [Naming Conventions](#naming-conventions) | Role, block, and file naming rules |
| [Integration Points](#integration-points) | How PDS-Role connects to other tools |
| [What Belongs Here](#what-belongs-here) | Scope boundary |
| [Development Rules](#development-rules) | Constraints for role development |

## What Is a Role?

A **role** defines what a device *does* on a given hardware revision. The same PCB (hwrev) can serve completely different purposes depending on its role:

| Role | Purpose | Example |
|------|---------|---------|
| `h2o_001` | Aeroponics tower controller | Pumps, misting, pH sensors |
| `sv_001` | Server room monitor | Temperature, humidity, alerts |
| `wh_001` | Weather station | Wind, rain, barometric pressure |

A role determines:
- Which **PDS modules** are compiled into the firmware
- Which **headers** are included
- The **process action loop** (`pds_process_action.c`) — usrset defaults + telemetry provider registration
- Default **user settings** (`usrset_defaults.h`) — compiled-in defaults, overridden by NVS at runtime

> **Pin assignments are NOT part of a role file.** Pins are Layer 2 `hw_vars` blobs in the
> binary pipeline — sent over-the-air from the Role Editor. `pds_pins.c` does not exist.

---

## Architecture

```
pds-role/
├── AI-INSTRUCT.md               # This file - AUTHORITATIVE
├── go.py                        # CLI entry point
│
├── tools/                       # Python backend
│   ├── __init__.py
│   ├── role_builder.py          # CLI command handler — scan, validate, generate
│   ├── role_config.py           # Role configuration model & serialization
│   ├── module_scanner.py        # Discovers PDS modules, headers, capabilities
│   ├── pin_assigner.py          # Auto-assigns pins based on feature requirements
│   └── variable_registry.py     # Groups variables by function for remote access
│
│   NOTE: The VS Code webview panel for the role editor lives in:
│         PDS-vscode-extension/  (NOT here)
│         See root AI-INSTRUCT.md �#"VS Code Extension" for the full file map.
│
├── templates/                   # Jinja2 code-generation templates
│   ├── pds_process_action.c.j2 # Role init: usrset_init + telemetry provider registration
│   └── usrset_defaults.h.j2    # Compiled-in usrset defaults header
│
├── saved_roles/                 # Persisted role configurations (JSON)
│
└── .dev-docs/                     # Development documentation
```

---

## Technology

**Language**: Python (primary)

- All scanning, generation, and validation logic is Python
- Uses only standard library + Jinja2 for templating
- Runs in the workspace `.venv` virtual environment
- Invoked by the PDS Toolbox VS Code extension via a webview panel

**Integration with PDS Toolbox Extension** (`PDS-vscode-extension/`):

| Layer | Language | File | Responsibility |
|-------|----------|------|----------------|
| **Backend** | Python | `pds-role/tools/role_builder.py` | Scan modules, validate selections, generate role files |
| **Command / wiring** | JS | `PDS-vscode-extension/role-panel.js` | Registers VS Code command, loads data, routes webview messages |
| **Filesystem** | JS | `PDS-vscode-extension/role-fs.js` | Scans targets, boards, modules, pin caps, saved roles from disk |
| **Actions** | JS | `PDS-vscode-extension/role-actions.js` | Saves/loads role JSON; spawns Python `go.py` in a terminal |
| **Static data** | JS | `PDS-vscode-extension/role-data.js` | `PDS_FB_BLOCKS`, `COMPONENTS`, `PREFABS`, `DEFAULT_VARS` |
| **HTML assembler** | JS | `PDS-vscode-extension/role-webview.js` | Serialises data, assembles final HTML string |
| **UI styles** | CSS (as JS string) | `PDS-vscode-extension/role-webview-styles.js` | All CSS for the webview panel |
| **UI logic** | JS (webview) | `PDS-vscode-extension/role-webview-script.js` | State, cascade, rendering, drag/drop — runs in the webview iframe |

> **⚠️ CRITICAL — `role-webview-script.js` must be loaded with `fs.readFileSync`, NOT `require()`**
> See root `AI-INSTRUCT.md` �#"Role Editor file responsibilities" for full explanation.
> Symptom if broken: UI renders but has zero interactivity (no cascade, no buttons, no clicks).

---

## Migration Guide — Old Pattern → 3-Layer Binary Pipeline

> **Context**: The role editor previously generated `default_ladder.st` (IEC 61131-3 Structured Text) for
> automation logic, `default_usrset.json` for user settings, and `pds_pins.c` for pin assignments.
> This approach required parsing on the device and Ladder Logic editor tooling.
> It has been replaced by a **3-layer binary pipeline architecture** with no on-device JSON/text parsing.

### What Changed

| Old (deprecated) | New (3-layer binary) |
|---|---|
| `default_ladder.st` — Structured Text automation program | Layer 1 `pipeline` blob — flat byte stream of block type IDs + sentinel bytes |
| `pds_pins.c` — compiled pin assignments | Layer 2 `hw_vars` blob — packed `pins_t` structs, positionally indexed by Layer 1 |
| `default_usrset.json` — user settings as JSON | Layer 3 `settings` blob — packed `settings_t` structs + global header (`update_rate_ms`, `ble_enabled`, `wifi_enabled`) |
| `pds_process_action.c` — hand-written process loop | Pipeline engine (`pds_pipeline.c`) — walks Layer 1 sentinel stream, builds and ticks block chain |
| `pds_comp_*` bundled components | `pds_fb_*` function block primitives composed in the pipeline |

### Layer 1 Byte Stream Format

```
Byte 0:       version (0x01)
Byte 1..end:  pipelines packed as: 0x00 [type_id ...] 0xFE  repeated; 0xFF = empty flash
```

Block type IDs (current — `PDS-vscode-extension/role-data.js` is the authoritative source):

| ID | Block | Category |
|----|-------|----------|
| `0x01` | `sensor_analog` | input |
| `0x02` | `sensor_dht22_temp` | input |
| `0x03` | `sensor_dht22_humid` | input |
| `0x04` | `hmi_toggle` | input |
| `0x05` | `hmi_momentary` | input |
| `0x06` | `abortable_sub_pipeline` | system |
| `0x07` | `pipeline_suspend` | system |
| `0x08` | `pipeline_resume` | system |
| `0x09` | `logic_or` | logic |
| `0x0A` | `hmi_initiate` | input |
| `0x10` | `timer_countdown` | timer |
| `0x11` | `timer_countup` | timer |
| `0x12` | `timer_cycle` | timer |
| `0x13` | `timer_elapsed` | timer |
| `0x20` | `pid_pwm` | output |
| `0x21` | `pid` | logic |
| `0x22` | `pwm_output` | output |
| `0x30` | `gpio_input` | input |
| `0x31` | `gpio_output` | output |
| `0x40` | `limit_high` | logic |
| `0x41` | `limit_low` | logic |
| `0x50` | `ref` | utility |
| `0x51` | `sensor_value` | input |
| `0x70` | `fan_float` | utility |

### Role Editor Responsibilities (New)

The role editor should:
1. Let the user compose blocks into named **pipelines** of three kinds:
   - **`pipeline`** — continuously-ticking data-flow channel (sensor→logic→output). Runs every loop tick.
   - **`routine`** — sequential, once-per-trigger procedure. Starts when `hmi_initiate` fires; executes blocks top-to-bottom once, then returns. No input wiring — order determines execution.
   - **`sensor`** — sensor data source pipeline. Blocks produce named sensor values read by `sensor_value` blocks in other pipelines.
2. Let the user manage **peripherals** (I²C/SPI devices e.g. ADS1115, DS18B20, DHT22). Adding a peripheral auto-creates a sensor pipeline pre-populated with its channel blocks, tagged with `peripheral_id`. Removing a peripheral cascades to delete its sensor pipelines.
3. Serialize the pipeline topology as the Layer 1 byte stream (one byte per block type_id).
4. Collect `pins_t` values for each block → pack Layer 2 blob.
5. Collect `settings_t` values for each block → pack Layer 3 blob.
6. Write the global Layer 3 header: `update_rate_ms`, `ble_enabled`, `wifi_enabled`.
7. Upload all three layers in a single request:
   ```
   POST /v1/devices/:id/pipeline
   { l1: "<base64>", l2: "<base64>", l3: "<base64>", meta: { pipelines: [...] } }
   ```
   `meta` carries the pipeline names and block aliases that the WEB-HMI overlays onto
   the decoded settings view. The device fetches the framed blob on its next poll.

### Routine Execution Model

Routines are **sequential, not data-flow**. On each tick, the pipeline engine checks if the leading `hmi_initiate` block has fired (rising edge). If yes, the routine executes all blocks in order (one pass), then returns. Blocks in a routine do **not** pass signals between each other — there is no port-based wiring. The `abortable_sub_pipeline` block is the exception: it has its own inner block list that loops every tick until an exit condition fires.

### abortable_sub_pipeline Inner Blocks

The `abortable_sub_pipeline` block contains an **inner pipeline** (a `blocks[]` array). On entry, all inner blocks get a rising-edge signal. On subsequent ticks, they evaluate normally. Exit conditions (`exit_conditions[]`) reference inner block indices and port 0 — when any condition output ≥ 0.5, the loop aborts and the outer routine continues.

**No input wiring** — neither outer routine blocks nor inner blocks have an `inputs` map. All connections are implicit chain order or explicit exit conditions.

### Cross-Layer Version Coupling

Layers 2 and 3 are positionally indexed to Layer 1. If Layer 1 changes (topology update)
but Layers 2/3 are stale, the device will misindex silently.

**Rule**: When the role editor uploads a new Layer 1, it **must** also upload fresh Layers 2 and 3
at the same time. Uploading Layer 3 alone (settings tweak) is safe only if the pipeline
topology has not changed.

### `pds_comp_*` Archive Status

All `pds_comp_*` components have been moved to `Device/pds/pds_components/__archived_comp/`.
They are **not compiled** and serve as reference implementations only. New pipeline blocks
follow the `pds_fb_*` pattern. See `Device/pds/pds_components/include/pds_component_base.h`
for the chaining convention.

This follows the same pattern as `build-panel.js` → `PDS-BuildTools/scripts/build_selector.py`.

---

## Blob Generation & NVS Image

### Purpose

The role config (saved as `pds-role/saved_roles/<role_id>.json`) contains all the information
needed to produce the four binary layers the firmware expects:

| Layer | NVS key | Content |
|-------|---------|----------|
| L1 | `"pipeline"` | Flat byte stream: version byte + `0x00 [type_ids…] 0xFE` per pipeline + `0xFF` terminator |
| L2 | `"hw_vars"` | Packed `pins_t` structs in Layer 1 positional order |
| L3 | `"settings"` | Global header (`update_rate_ms` etc.) + packed `settings_t` structs in Layer 1 order |
| L4 | `"ui_params"` | Per-device UI layout parameters (OLED screens, elements, telemetry sources) |

### Parse-and-Pack Utility

A **blob packer** utility (`pds-role/tools/blob_packer.py`) is responsible for:

1. Reading the role JSON (`saved_roles/<role_id>.json`)
2. Walking the pipeline block sequence → emitting the Layer 1 byte stream
3. Collecting per-block `pins_t` values → packing Layer 2 blob
4. Collecting per-block `settings_t` values + global header → packing Layer 3 blob
5. Iterating `peripherals[]` with `ui_params: true` → packing Layer 4 blob
6. Writing `<role_id>_l1.bin`, `<role_id>_l2.bin`, `<role_id>_l3.bin`, `<role_id>_l4.bin` to an output directory

L4 format is documented in `Device/pds/pds_ui/AI-INSTRUCT.md`.

**This utility is intentionally multi-path** — the same `blob_packer.py` is called by:
- The **role editor "Generate"** button (via `go.py`) to produce local blobs for deploy
- The future **web service** (a separate host process that accepts role JSON and returns blobs)
- Potentially the **build pipeline** to embed defaults at compile time

### NVS Image Path (Preferred for Production Deploy)

Once the three blobs are generated, they are packed into an NVS partition image that can be
flashed directly to the device at address `0x9000` (the `nvs` partition):

```
pds-role/tools/blob_packer.py  →  _l1.bin, _l2.bin, _l3.bin
                                       ↓
              nvs_partition_generator.py (ESP-IDF tool)
                  CSV input:
                    pds, namespace, , ,
                    pds, blob, pipeline, <l1.bin contents>
                    pds, blob, hw_vars,  <l2.bin contents>
                    pds, blob, settings, <l3.bin contents>
                       ↓
              nvs_defaults.bin  →  esptool flash at 0x9000
```

This approach pre-populates a fresh device with a working default configuration without
requiring any post-flash app interaction. WiFi credentials (SSID/password) are NOT
included in the NVS image — they are always provisioned on first boot via SoftAP.

### Output Location Convention

Generated artifacts for a role are written to:
```
PDS-BuildTools/dist/defaults/<role_id>/
    <role_id>_l1.bin          ← Layer 1 pipeline byte stream
    <role_id>_l2.bin          ← Layer 2 hw_vars blob
    <role_id>_l3.bin          ← Layer 3 settings blob
    <role_id>_l4.bin          ← Layer 4 ui_params blob
    nvs_defaults.bin          ← Combined NVS partition image (flash at 0x9000)
```

The deploy panel in the VS Code extension discovers this folder and adds a
**"Flash Defaults"** option when `nvs_defaults.bin` is present.

---

## GUI Design

The role editor is a **three-panel graphical webview panel** inside VS Code.

```
┌──────────────┬──────────────────────────────────┬──────────────┐
│  LEFT        │  MAIN PANEL                      │  RIGHT       │
│  SIDEBAR     │                                  │  SIDEBAR     │
│              │  [Top Bar — identity + actions]  │              │
│  GPIO Pin    │                                  │  pds_fb      │
│  Map         │  pds_storage module card         │  Block       │
│              │                                  │  Palette     │
│  ──────────  │  ──── PIPELINES ────             │              │
│              │  Pipeline 1  [blocks...]         │  ──────────  │
│  Variable    │  Pipeline 2  [blocks...]         │              │
│  Registry    │  + Add Pipeline                  │  Prefabs     │
└──────────────┴──────────────────────────────────┴──────────────┘
```

### 1. Role Identity (Top Bar)

The **Board** dropdown is the sole cascade driver. All other identity fields derive from it.

| Control | Type | Behavior |
|---------|------|----------|
| Board | **Dropdown** | Scanned from `PDS-BoardEditor/boards/` — commercial MCU module (e.g. `esp32-sm`). Selecting a board drives the entire cascade. |
| MCU Target | **Readonly label** | Derived from `boardJson.mcuTarget` — NOT a dropdown. Displays next to the Board selector. |
| HwRev | **Dropdown** | Populated exclusively from `hwrev` values in **saved role files** (`pds-role/saved_roles/*.json`) filtered by the selected board. Board JSON files have no `hwrev` field — they are commercial MCU module specs. Always includes `+ New HwRev...`. |
| Role | **Dropdown** | Populated from HAL dir roles for the selected target+hwrev, plus saved roles filtered by board+hwrev. Includes `+ New Role...`. |
| Role ID | **Text input** | Editable identifier (e.g. `h2o_002`). Auto-filled when loading a saved role. |
| Role Name | **Text input** | Human-readable label (e.g. `aeroponics_adv`). |
| Save | **Button** | Saves config to `pds-role/saved_roles/{role_id}.json`. |
| Generate | **Button** | Calls `go.py --config {role_id}` in a VS Code terminal. |
| Dry Run | **Button** | Calls `go.py --config {role_id} --dry-run` — preview without writing files. |

**Cascade rule**: Saved roles are filtered by `board` field — **never by `target`** — because `target` values in saved files may be stale.

### 2. Left Sidebar — GPIO Pin Map

Sortable table showing all GPIO pins for the selected board (from `PDS-BoardEditor/boards/{boardId}.json`).

| Column | Description |
|--------|-------------|
| Pin | GPIO number |
| J# | Header position (`jpin`) if defined in the board spec |
| Caps | Capability badges: `GPIO`, `ADC`, `PWM`, `SPI`, `I2C`, `UART` |
| Assigned | What pipeline block or component has claimed this pin |

- **Sort**: Click any column header to sort ascending/descending.
- **Drag-to-reassign**: Assigned pins are draggable. Drop onto a compatible row to reassign. Capability mismatch shows a red highlight; valid targets show green.
- **Conflict detection**: Row background turns red if two assignments share the same GPIO.
- **Reserved pins** shown in muted italic (power, GND, strapping pins).

### 3. Left Sidebar — Variable Registry

Shows configurable variables for enabled modules. Currently scoped to `pds_storage`.

Each variable row has:
- **Checkbox** — toggles `remote: true/false` (whether the variable is accessible via BLE/WiFi)
- **Name** (monospace) + **Type** label
- **BLE/WiFi** badge (green) if remote, **CONST** badge (grey) if not

### 4. Main Panel — pds_storage Module Card

`pds_storage` is the only module with a visible configuration card. All other PDS modules (`pds_core`, `pds_hal`, `pds_validation`, `pds_components`, `pds_control`, `pds_network`, `pds_telemetry`) are force-enabled and included automatically — they do not appear as cards in the UI.

The `pds_storage` card shows:
- Enable/disable checkbox
- Its configurable variables (NVS namespace, partition sizes, OTA, etc.) with default value inputs
- Remote-access toggles per variable

### 5. Main Panel — Pipeline Builder

The primary composition surface. Each **pipeline** is a named, ordered list of function blocks representing one processing channel on the device. Pipelines have a `kind`: `pipeline` (continuously ticking), `routine` (sequential, once per trigger), or `sensor` (sensor data source). See the **Pipeline Kinds** section for details.

**Pipeline card controls:**
- Drag handle (⠿) — reorder pipelines by dragging
- Name input — editable pipeline label
- Enable checkbox — marks pipeline active/inactive
- Collapse chevron (click anywhere on header)
- ✕ remove button

**Block row controls (inside a pipeline):**
- Type badge (coloured by category: input/output/logic/utility)
- Alias input — user-friendly name for this block instance
- Settings button — toggles the block detail panel
- ✕ remove button

**Block detail panel** (when Settings is expanded):
- Per-setting fields: number, text, bool checkbox, enum select, or **pin select** dropdown
- Pin select dropdowns are filtered by the setting's `pin_cap` (e.g. only ADC-capable GPIOs for an ADC input block)
- Pin selections are reflected immediately in the Pin Map sidebar

**Fan output blocks** — blocks with `fan: true` show a nested `↳ Outputs` sub-panel for adding child output blocks (e.g. a distribute block fanning to multiple GPIO outputs).

**Add-block row** — each pipeline has a dropdown + "Add" button at the bottom for adding a new block by type.

### 6. Right Sidebar — Block Palette

Grid of all available blocks, grouped by category:

| Category | Colour | Examples |
|----------|--------|----------|
| Input | Blue | `sensor_analog`, `gpio_input`, `hmi_initiate`, `sensor_value` |
| Output | Green | `gpio_output`, `pid_pwm`, `pwm_output` |
| Logic | Yellow | `pid`, `limit_high`, `limit_low`, `logic_or` |
| Timer | Orange | `timer_countdown`, `timer_countup`, `timer_cycle`, `timer_elapsed` |
| System | Grey | `pipeline_suspend`, `pipeline_resume`, `abortable_sub_pipeline` |
| Utility | Purple | `ref`, `fan_float` |

Clicking a tile appends that block type to the currently selected pipeline. Tiles are greyed and non-clickable when no pipeline is selected.

### 7. Right Sidebar — Prefabs

Pre-composed pipeline templates. Clicking a prefab creates a new pipeline pre-populated with a sensible block sequence. Each tile shows the prefab label, description, and a chip list of its blocks.

---

## Core Concepts

### Module Inclusion

The role editor scans `Device/pds/` for all available PDS modules. Module visibility in the UI is split into two tiers:

| Module | UI Visibility | Behaviour |
|--------|---------------|-----------|
| `pds_core` | Hidden | Always included; force-enabled |
| `pds_hal` | Hidden | Always included; force-enabled |
| `pds_validation` | Hidden | Always included; force-enabled |
| `pds_components` | Hidden | Always included; force-enabled |
| `pds_control` | Hidden | Always included; force-enabled |
| `pds_network` | Hidden | Always included; force-enabled |
| `pds_telemetry` | Hidden | Always included; force-enabled |
| `pds_odbii` | Hidden | Always included; force-enabled |
| `pds_storage` | **Visible card** | Configurable — user can enable/disable and set storage variables |

All modules are present in `state.modules` internally; only `pds_storage` is rendered as a card in the UI (`visibleModules = ['pds_storage']`).

### pds_storage Variables

The `pds_storage` card exposes these configurable variables:

| Variable | Type | Default | Remote |
|----------|------|---------|--------|
| `nvs_namespace` | `string[16]` | `"pds"` | No |
| `config_version` | `uint16` | `1` | No |
| `storage_type` | `enum:fat,spiffs` | `"fat"` | No |
| `storage_pct` | `uint8` | `25` | No |
| `ota_enabled` | `bool` | `true` | No |
| `storage_enabled` | `bool` | `true` | No |
| `nvs_size_kb` | `uint16` | `20` | No |

---

## Output: What Gets Generated

When the user finalizes a role configuration, the tool generates files in **one location**:

**Path**: `Device/pds/pds_hal/board/{target}/hwrev_{rev}/{role_id}/`

| File | Template | Purpose |
|------|----------|---------|
| `pds_pins.c` | `templates/pds_pins.c.j2` | Pin assignment table — generated from selected pin assignments |
| `pds_process_action.c` | `templates/pds_process_action.c.j2` | Role init: loads usrset defaults + registers telemetry provider; `pds_process_action()` stub (not called by loop) |
| `usrset_defaults.h` | `templates/usrset_defaults.h.j2` | Compile-time user-setting defaults; consumed by `pds_usrset_init()` in `pds_role_init()` |

### usrset_defaults.h

The role builder collects user-settable defaults from two sources in the role config:

1. **`variables`** — module-level vars with `remote: true` flag
2. **`components[type][i].settings`** — component instance settings, prefixed `{type_short}[{i}]_` (multi-instance) or `{type_short}_` (single)

Variable names are truncated to 31 chars to fit the NVS key limit. The generated array is named `pds_usrset_defaults[]` with companion macro `PDS_USRSET_DEFAULTS_COUNT`.

`pds_role_init()` (in `pds_process_action.c`) calls `pds_usrset_init(pds_usrset_defaults, PDS_USRSET_DEFAULTS_COUNT)` then `pds_usrset_load_nvs()` to layer saved user values on top.

### Template Conventions — `pds_process_action.c.j2`

**Critical rules enforced by the template**:

1. **Standard includes are hardcoded** — `pds_usrset.h`, `pds_telemetry.h`, `usrset_defaults.h`
   are always emitted unconditionally. The `selected_headers` loop **must filter them out**
   to avoid duplicate `#include` directives:
   ```jinja
   {%- set _hardcoded = ['pds_usrset.h', 'pds_telemetry.h', 'usrset_defaults.h'] -%}
   {% for header in selected_headers %}{% if header not in _hardcoded %}
   #include "{{ header }}"
   {% endif %}{% endfor %}
   ```

2. **`nvs.h` must always be included** — `pds_usrset_load_nvs()` returns `ESP_ERR_NVS_NOT_FOUND`
   which is defined in `nvs.h` (part of the `nvs_flash` IDF component). `esp_err.h` alone
   does not provide NVS error codes.

3. **`pds_storage` headers emit their own ESP-IDF includes via `pds_nvs.h` / `pds_usrset.h`** —
   do not add raw `nvs_flash.h` or `nvs.h` from selected_headers; the template standard includes
   already handle it.

---

### Build Integration

For the generated files to be **compiled into the firmware**, the CMake build must receive the role's hwrev and role_id. `pds_hal/CMakeLists.txt` picks up role files when these cmake variables are set:

```
-DPDS_HWREV=hwrev_001 -DPDS_ROLE=h2o_001
```

The build tools (`PDS-BuildTools/`) pass these via the idf.py invocation. Without them the project will still configure (the CMakeLists guards with `if(DEFINED PDS_HWREV ...)`), but a warning is emitted and role files are excluded.

The call chain at runtime:
1. `pds_platform_init()` → `pds_role_init()` (from `pds_process_action.c`)
2. `pds_role_init()` → `pds_usrset_init(pds_usrset_defaults, ...)` → `pds_usrset_load_nvs()`
3. `pds_platform_loop()` → `pds_pipeline_engine_tick()` (all automation logic runs here; NOT in `pds_process_action()`)

---

## CLI Usage

```bash
# Interactive mode — prompts for board, hwrev, role name, modules
python role_builder.py

# List available modules and their headers
python role_builder.py --list-modules

# Generate from a saved role config
python role_builder.py --config role_config.json

# Dry run — show what would be generated without writing files
python role_builder.py --dry-run --config role_config.json
```

---

## Role Configuration Schema

Role configs are saved to `pds-role/saved_roles/{role_id}.json`. The schema includes a `pipelines` array holding the full pipeline + block topology.

```json
{
  "role_id": "AERO-001",
  "role_name": "Aero-001",
  "target": "esp32",
  "board": "esp32-nodemcu-32s-30pin",
  "hwrev": "hwrev_001",
  "modules": { ... },
  "variables": { ... },
  "pin_assignments": {
    "pl_0_bl_1_fo_0_pin_output": { "gpio": 13, "label": "Fogger - gpio_output" }
  },
  "peripherals": [
    { "id": "periph_abc123", "type": "dht22", "alias": "DHT22-Room",
      "config": { "sample_interval_ms": 30000, "enabled": true },
      "pins": { "pin_data": 17 } }
  ],
  "pipelines": [
    {
      "id": "y688rbhn92hrmg72",
      "name": "Fogger",
      "kind": "pipeline",
      "enabled": true,
      "blocks": [
        { "blockType": "timer_cycle", "alias": "Fogging Cycle",
          "settings": { "on_ms": 5000, "off_ms": 55000, "enabled": true } },
        { "blockType": "pwm_output", "alias": "Fogger Pump",
          "settings": { "pin_pwm": 14, "pwm_frequency_hz": 1000, "ratio": 100, "enabled": true } }
      ]
    },
    {
      "id": "sensors_main_01",
      "name": "Sensors",
      "kind": "sensor",
      "enabled": true,
      "peripheral_id": null,
      "blocks": [
        { "blockType": "sensor_analog", "alias": "Water Temp",
          "settings": { "adc_channel": 1, "pin_power": 15, "sample_interval_ms": 1000,
                        "oversample_count": 8, "raw_low": 0, "raw_high": 4095,
                        "scale_min": 0, "scale_max": 100, "enabled": true } }
      ]
    },
    {
      "id": "6htgs2x6stmmyhj2",
      "name": "Water-Change",
      "kind": "routine",
      "enabled": true,
      "blocks": [
        { "blockType": "hmi_initiate", "alias": "Start Water Change",
          "settings": { "confirm": false, "enabled": true } },
        { "blockType": "pipeline_suspend", "alias": "Suspend: Fogger",
          "settings": { "pipeline_index": 0, "pipeline_id": "y688rbhn92hrmg72", "enabled": true } },
        { "blockType": "abortable_sub_pipeline", "alias": "Change Water",
          "settings": { "enabled": true },
          "exit_conditions": [
            { "id": "ec_timer", "label": "MaxRunTime", "src_block": 0, "src_port": 0 }
          ],
          "blocks": [
            { "blockType": "timer_countdown", "alias": "MaxRunTime",
              "settings": { "duration_ms": 1800000, "enabled": true } },
            { "blockType": "pwm_output", "alias": "EvacPump",
              "settings": { "pin_pwm": 33, "enabled": true } }
          ]
        },
        { "blockType": "pipeline_resume", "alias": "Resume: Fogger",
          "settings": { "pipeline_index": 0, "pipeline_id": "y688rbhn92hrmg72", "enabled": true } }
      ]
    }
  ]
}
```

**Pin assignment keys** use the pattern `pl_{pipelineIdx}_bl_{blockIdx}_{settingName}` for pipeline blocks, and `pl_{pipelineIdx}_bl_{blockIdx}_fo_{outputIdx}_{settingName}` for fan output child blocks. These are rebuilt from `state.pipelines` on load via `rebuildPipelinePinAssignments()`.

### Pipeline Kinds

Each pipeline has a `kind` field:

| kind | Execution | Typical blocks |
|------|-----------|----------------|
| `pipeline` | Continuously ticking every loop tick | `sensor_value`, `pid`, `pwm_output`, `timer_cycle` |
| `routine` | Sequential, once per `hmi_initiate` trigger | `hmi_initiate`, `pipeline_suspend`, `abortable_sub_pipeline`, `pipeline_resume` |
| `sensor` | Sensor data source (produces named sensor values) | `sensor_analog`, `sensor_dht22_temp`, `sensor_dht22_humid` |

### Peripheral System

Peripherals (`state.peripherals[]`) represent physical I²C/SPI devices (e.g. ADS1115, DS18B20, DHT22). Adding a peripheral auto-creates a sensor pipeline tagged with `peripheral_id`. Removing a peripheral deletes its linked sensor pipeline.

Current peripheral types (defined in `PERIPHERAL_TYPES` in `role-data.js`):
- `ads1115` — 4-channel 16-bit ADC (auto-creates 4 `sensor_analog` blocks)
- `ds18b20` — 1-wire temperature (auto-creates 1 temperature block)
- `dht22` — temperature + humidity (auto-creates `sensor_dht22_temp` + `sensor_dht22_humid` blocks)

### No Input Wiring

Blocks do **not** have an `inputs` map. Wiring between blocks is implicit (linear chain order). The firmware `pds_pipeline.c` always wires `block[i]` to `block[i-1]` (except `sensor_value` which gets its source from the `sensor_ref` setting). The JSON schema does not include an `inputs` field.

---

## Naming Conventions

### Role IDs
- Format: `{prefix}_{nnn}` (lowercase prefix + 3-digit number)
- Prefixes follow application domain:
  - `h2o_` — Aeroponics / hydroponics / water systems
  - `sv_` — Server / infrastructure monitoring
  - `wh_` — Weather / environmental
  - `ve_` — Vehicle / OBD-II
  - `gn_` — Generic / testing
- Examples: `h2o_001`, `sv_001`, `wh_001`, `ve_001`, `gn_001`

### Generated Files
- Follow PDS naming: `pds_{module}_{name}.{c,h}` (lowercase)
- Templates use Jinja2: `{name}.j2` extension

### Python Code
- Snake_case for files, functions, variables
- No classes unless needed for clear state management
- Prefer functions and modules over OOP
- Type hints on public function signatures

---

## Integration Points

| System | How PDS-Role Connects |
|--------|----------------------|
| `Device/pds/` | **Reads** module structure; **writes** generated role files into HAL board dirs |
| `PDS-BoardEditor/boards/` | **Reads** board spec JSONs to populate the Board dropdown and pin capabilities |
| `PDS-vscode-extension/` | Role Editor UI lives here; **called by** `role-panel.js` webview panel |
| `PDS-BuildTools/` | Generated roles are immediately buildable via `build_selector.py` |
| `WEB-HMI/api` | At provision time, admin sets `role` field = this role's `role_id` (informational only) |

> **→ Root `AI-INSTRUCT.md` �# Device Identity Model — End-to-End Identity Flow** — shows exactly where `role_id`, `board`, `hwrev`, and `target` from the role JSON map to DB fields and the OTA URL.

**Identity note**: `role_id` (the filename stem of `saved_roles/<role_id>.json`) is the blob generation key and an informational DB field. It is NOT a serial number. Device serial numbers follow the `{PREFIX}-{NNN}` convention documented in root `AI-INSTRUCT.md �# Device Identity Model — Serial Number Convention`.

---

## What Belongs Here

✅ **DO include**:
- Python scripts for module scanning, role generation, and validation
- Jinja2 templates for generated C files and documentation
- Role configuration schema and serialization
- CLI interface for role building

❌ **DO NOT include**:
- Device firmware source code (→ `Device/pds/`, `Device/main/`)
- Hardware board specs (→ `PDS-BoardEditor/`)
- Build system logic (→ `PDS-BuildTools/`)
- VS Code extension JS code (→ `PDS-BoardEditor/vscode-extension/`)
- Android or HMI code

---

## Development Rules

1. **Python is the implementation language** — all logic in Python, no Node.js for backend
2. **Scan, don't hardcode** — module discovery reads `Device/pds/` dynamically
3. **Dependencies from CMakeLists.txt** — parse actual CMake files for REQUIRES, don't duplicate
4. **Templates, not string concatenation** — use Jinja2 for all code generation
5. **Dry-run by default** — show the user what will be generated before writing
6. **Never overwrite without confirmation** — if role files already exist, warn and require explicit override
7. **Validate before generate** — check board/hwrev exists, modules resolve, no circular deps
8. **Auto-assign pins intelligently** — use board pin capabilities (ADC-capable, PWM-capable, etc.) to make sensible defaults; user can always override
9. **Variables drive remote access** — the variable registry determines what's exposed over BLE/WiFi; grouping by function keeps the config/telemetry protocol organized
10. **Saved roles are portable** — JSON configs in `saved_roles/` can be shared, versioned, and re-loaded


