# PDS-Pipeline: Shared Pipeline Package

**Authority**: DEEP � Authoritative for all work inside `pds-pipeline/`
**Last Updated**: 2026-05-27 (encoder blocks added; control_point concept; setpoint_src removed from PID)  
**Status**: Active — Single source of truth for pipeline block definitions

---

## Contents

| § | What's here |
|---|-------------|
| [Purpose](#purpose) | What @pds/pipeline provides |
| [Portability Requirement](#portability-requirement) | Why this package must remain framework-agnostic |
| [Railway Deployment — Repo Root Architecture](#railway-deployment--repo-root-architecture) | How the package is deployed via Railway |
| [The Core Rule: No Duplicate Block Definitions](#the-core-rule-no-duplicate-block-definitions) | Single source of truth mandate |
| [FieldMeta.level — Four-Tier Access System](#fieldmetalevel--four-tier-access-system) | Access level field definitions |
| [encoder_mapped — Backend Driver Block](#encoder_mapped--backend-driver-block) | How encoder_mapped works; control_point concept; no HMI settings |
| [Directory Structure](#directory-structure) | Package source layout |
| [Visual Design System](#visual-design-system) | Color, icon, and layout conventions |
| [Access Level System (Four-Tier)](#access-level-system-four-tier) | Full access level spec |
| [How to Add a New Block Type](#how-to-add-a-new-block-type) | Step-by-step checklist |
| [Consumer Integration](#consumer-integration) | How HMI API and frontend consume this package |
| [What Does NOT Live Here](#what-does-not-live-here) | Scope boundary |

## Purpose for everything related to the **pipeline data model**:

- **Block registry** — struct layouts, field names, and UI metadata for every `pds_fb` block type
- **Decoded output types** — `DecodedField`, `DecodedBlock`, `DecodedPipeline`, `DecodedPipelineSettings` — the shared contract between the API codec and the frontend renderer
- **Design tokens** — the CSS variable system that all pipeline UI consumers must use

All pipeline UI surfaces must import from this package, not define their own copies:

| Consumer | What it uses |
|----------|--------------|
| `WEB-HMI/api` (Express/TypeORM) | `block-registry` + decoded types — codec imports `FieldMeta`, `FmtChar`, and the `Decoded*` shapes |
| `WEB-HMI/src` (React frontend) | decoded types + `FieldMeta`, `AccessLevel` — `PipelineBlockPanel.tsx` imports directly |
| `PDS-vscode-extension` (webview) | `block-registry` — bundled into webview JS by esbuild |

> **`pipeline-codec.ts` is NOT in this package.** The L1/L2/L3 binary encoder/decoder lives
> in `WEB-HMI/api/src/pipeline/pipeline-codec.ts` — it is an API-layer concern and uses
> `Buffer` (Node.js only).  It imports block-registry types via the `@pds/pipeline` re-export
> shim and re-exports the `Decoded*` types for any API code that imports from the codec.

### Full public API (`src/index.ts`)

```typescript
// Block registry
export { fmtCharSize, BLOCK_REGISTRY, TYPE_ID_TO_NAME } from './block-registry';
export type { FmtChar, FieldMeta, BlockRegEntry, AccessLevel } from './block-registry';

// Decoded output types — produced by the API codec, consumed by the frontend
export type { DecodedField, DecodedBlock, DecodedPipeline, DecodedPipelineSettings };
```

---

## Portability Requirement

**All code in this package must run in two environments without modification:**

| Environment | Runtime | Notes |
|-------------|---------|-------|
| **VS Code extension webview** | Chromium (VS Code embedded browser) — bundled, no `require()` | JS/TS is bundled by esbuild; CSS uses `--vscode-*` tokens provided by the runtime |
| **Railway server** (WEB-HMI/api) | Node.js on Railway's containerized infrastructure | TypeScript compiled via `tsc`; served as CommonJS via `dist/` |

### Rules that follow from this:

1. **No Node.js built-ins in business logic** — `fs`, `path`, `os`, `crypto`, `Buffer` etc. must never be used inside `src/block-registry.ts`, `src/pipeline-codec.ts`, or any future logic file. Those files are consumed by the webview too. Node-specific code belongs in the API layer, not here.

2. **No DOM APIs** — `document`, `window`, `localStorage` etc. must not appear in this package. UI rendering happens in the consumers, not here.

3. **No runtime dependencies** — this package has zero `dependencies` in `package.json`. Everything is pure TypeScript logic. Consumers bundle or compile it themselves.

4. **CSS uses `--vscode-*` token names** — In the VS Code webview these are provided by the runtime. In the WEB-HMI React app, `design-tokens.css` provides the `.pds-vscode-compat` alias block that maps `--vscode-*` names to `--pds-*` values. Same CSS works in both environments without branching.

---

## Railway Deployment — Repo Root Architecture

**Architecture**: The `WEB-HMI/api` Railway service has **Root Directory cleared** in the Railway dashboard. Railway clones the full monorepo, giving the build environment access to `pds-pipeline/`. This enables `file:` npm linking and is the single-source-of-truth approach.

### How sharing works

```
pds-pipeline/src/block-registry.ts        ← CANONICAL SOURCE (edit only here)
         ↓  npm file: link
WEB-HMI/api/node_modules/@pds/pipeline/  ← Symlink → pds-pipeline/
WEB-HMI/api/src/pipeline/block-registry.ts  ← Re-export shim (imports from @pds/pipeline)
         ↓  (future) bundled by esbuild
PDS-vscode-extension webview              ← Imports pds-pipeline/src/ directly
```

### Railway build sequence

`WEB-HMI/api/railway.toml`:
```toml
buildCommand = "cd PDS-Pipeline && npm ci && npm run build && cd ../WEB-HMI/api && npm ci && npm run build"
startCommand = "node WEB-HMI/api/dist/index.js"
```

Steps:
1. Build PDS-Pipeline → generates `dist/` with compiled JS + `.d.ts` types
2. Install API deps (`npm ci`) — creates the `file:../PDS-Pipeline` symlink in `node_modules/@pds/pipeline`
3. Compile API (`tsc`) — resolves types from `@pds/pipeline/dist/index.d.ts`

### Dashboard requirement (one-time setup)
- Railway dashboard → `WEB-HMI/api` service → Settings → Root Directory → **clear this field**
- After clearing, `startCommand` must be `node WEB-HMI/api/dist/index.js` (not `node dist/index.js`)

### Local development
```sh
cd PDS-Pipeline && npm ci && npm run build
cd ../WEB-HMI/api && npm install && npm run build
```

### VS Code extension
esbuild bundles directly from `pds-pipeline/src/` — no npm linking needed for the extension.

---

## The Core Rule: No Duplicate Block Definitions

`role-data.js` in the VS Code extension and `block-registry.ts` in WEB-HMI previously defined block metadata separately. **This package eliminates that duplication.**

- `BLOCK_REGISTRY` in `src/block-registry.ts` is the **only** place to add or modify block field metadata
- `role-data.js` in the extension is **legacy** — migrate entries here, do not add new ones there
- `blob_packer.py` in `pds-role/tools/` is the **Python mirror** — keep in sync manually (it's the ground truth for firmware packing)

> **→ `pds-role/.ai/instruct.md` § Blob Generation & NVS Image** — authoritative documentation for layer binary formats, the blob packer tool, and NVS image generation

---

## FieldMeta.level — Four-Tier Access System

Every field in `fieldMeta` carries a required `level` property that controls which UI roles can see and edit it:

| Level | Audience | Examples |
|-------|----------|----------|
| `'hw'` | Board designer | `adc_channel`, `pin_power`, PWM frequency — physical hw config |
| `'tuner'` | Commissioning technician | PID gains, calibration voltages, fan enabled, stepper params |
| `'user'` | Plant operator | Setpoint, enabled on most blocks, cycle durations, thresholds |
| `'role'` | Role editor only — **never shown in HMI** | `control_point` picker on encoder_mapped; wiring-only config |

### UI filter rules

| Mode | Shows |
|------|-------|
| `'user'` | `user` fields only |
| `'tuner'` | `user` + `tuner` fields |
| `'full'` | All fields including `hw` |

Fields with `level: 'role'` are **never shown in any HMI mode** — they are wiring config set exclusively in the role editor. Blocks with `hideInSettings: true` have no settings panel at all.

### Key invariant

Blocks whose **every field** is `'hw'` or `'tuner'` are entirely **invisible in `user` mode** and should not appear in the operator's pipeline view. Example: `fan_float` and `fan_bool` blocks — their only field (`enabled`) is `level: 'tuner'`, so they are hidden from operators.

When adding a new block, every `fieldMeta` entry **must** include an explicit `level` — there is no default.

---

## encoder_mapped — Backend Driver Block

`encoder_mapped` (type `0xA3`) is a **backend driver block** — it runs in the firmware tick loop but has **no HMI settings panel**. The entire block is hidden from the HMI operator interface.

### Why it exists

An encoder is a physical dial. Its value needs to flow into a settable float field in another pipeline block (e.g. a PID's setpoint). The `encoder_mapped` block performs this wiring at firmware load time.

### control_point concept

A **control_point** is a 3-tuple `(target_pipeline_idx, target_block_idx, target_field_idx)` stored at the end of the encoder_mapped L3 struct (bytes 36–38, with pad at 39). It tells the pipeline engine: "after all pipelines are built, wire my output float to field `target_field_idx` of block `target_block_idx` in pipeline `target_pipeline_idx`".

| Field | Size | Meaning | Unassigned value |
|-------|------|---------|------------------|
| `target_pipeline_idx` | uint8 | Pipeline index (0-based load order) | `0xFF` |
| `target_block_idx` | uint8 | Block index within that pipeline | — |
| `target_field_idx` | uint8 | Settable field index within the block | — |

The post-build wiring pass in `pds_pipeline.c` calls `pds_fb_encoder_mapped_set_target(handle, float *target_ptr)` which stores a pointer to the live target float in the encoder context. Every tick, `encoder_mapped_run()` writes `mapped_value` to that pointer.

### Supported targets (field_idx)

| Block type | type_id | field_idx | Field |
|------------|---------|-----------|-------|
| pid | `0x21` | `0` | `setpoint` |

Adding support for a new target type requires a new `if` branch in the post-build pass in `pds_pipeline.c`.

### Role JSON format

```json
{
  "blockType": "encoder_mapped",
  "settings": {
    "peripheral_id": "periph_abc",
    "enabled": true,
    "control_point": "<pipeline_id>:<block_idx>:<field_name>"
  }
}
```

The blob packer resolves `"pipeline_id:block_idx:field_name"` at pack time:
- `pipeline_id` → `target_pipeline_idx` via `_pipeline_index_map`
- `block_idx` → `target_block_idx` (literal integer)
- `field_name` → `target_field_idx` by looking up the field's position in the target block's `l3_fields`

If `control_point` is absent from the role JSON, all three target bytes are packed as `0xFF, 0, 0` (unassigned).

### encoder_mapped struct layout (40 bytes)

```
bytes  0– 2  int8   pin_a, pin_b, pin_index
byte   3     uint8  pin_bitmask
byte   4– 7  float  map_min
bytes  8– 9  uint16 sample_interval_ms
bytes 10–13  bool×4 enabled, active_low, invert_direction, reset_on_index
byte  14     int8   [field, usage varies]
byte  15     pad
bytes 16–19  float  map_max
bytes 20–23  float  map_clamp_low
bytes 24–27  float  map_clamp_high
byte  28     bool   clamp_output
bytes 29–31  pad×3
byte  32     uint8  target_pipeline_idx   ← 0xFF = not assigned
byte  33     uint8  target_block_idx
byte  34     uint8  target_field_idx
byte  35     uint8  _pad3
```

### setpoint_src removed from PID

Previously, `pid` (0x21) had a `setpoint_src_idx` uint8 in its L3 struct (byte 32) and `pds_fb_pid_set_setpoint_source()` that wired a sensor slot pointer into the PID at load time.

**This was removed.** The encoder_mapped control_point mechanism replaces it:
- No `setpoint_src` field in role JSON for pid blocks
- No `setpoint_src_idx` in the pid struct (byte 32 is now `_pad1`)
- No post-build setpoint wiring pass for pid in `pds_pipeline.c`
- The encoder_mapped control_point post-build pass handles the wiring

### What encoder blocks are visible where

| Block | `hideInSettings` | HMI settings panel | Role editor |
|-------|------------------|-------------------|-------------|
| `encoder_position` (0xA1) | `true` | Hidden | Not user-configurable |
| `encoder_velocity` (0xA2) | `true` | Hidden | Not user-configurable |
| `encoder_mapped` (0xA3) | `true` | Hidden | Configurable (control_point picker) |

---

## Directory Structure

```
pds-pipeline/
├── .ai/instruct.md              ← You are here
├── package.json                ← npm package: @pds/pipeline
├── tsconfig.json               ← Compiles to dist/
├── src/
│   ├── index.ts                ← Public exports — import everything from here
│   ├── block-registry.ts       ← BLOCK_REGISTRY: struct layout + UI metadata + FieldMeta.level
│   └── design-tokens.css       ← CSS variables — the visual system
└── dist/                       ← Build output (gitignored)
    ├── index.js
    ├── index.d.ts
    └── ...
```

> `pipeline-codec.ts` is **not** here — it lives at `WEB-HMI/api/src/pipeline/pipeline-codec.ts`.

---

## Visual Design System

### The Role Editor Look and Feel is Authoritative

The **VS Code extension Role Editor** defines the visual language. All pipeline UI surfaces — whether the extension webview, WEB-HMI settings screen, or any future consumer — must use this visual system.

Key visual patterns from the Role Editor:

| Pattern | CSS Class | Purpose |
|---------|-----------|---------|
| Function card | `.func-card` | Top-level collapsible block container |
| Card header | `.func-card-header` | Click-to-collapse; checkbox + title + chevron |
| Card body | `.func-card-body` | Expanded content area |
| Instance group | `.instance-group` | One instantiation of a block within a card |
| Instance header | `.instance-header` | Alias name + remove button |
| Sub-component group | `.subcomp-group` | Nested feature block (e.g. dosing pump inside pH) |
| Block row | `.block-row` | Compact row in pipeline list view |
| Block type badge | `.block-type-badge` | Color-coded by category |
| Pipeline card | `.pipeline-card` | Top-level pipeline container |
| Add-block row | `.add-block-row` | Inline block type selector + add button |
| Setting row | `.instance-var` | Label + input + type badge per field |

### Design Token CSS Variables

All UI components **must** use the CSS variables defined in `src/design-tokens.css`. These map to:
- VS Code's `--vscode-*` tokens in the extension webview (provided by the webview runtime)
- Custom fallback values in the WEB-HMI React app (`--pds-*` fallbacks for dark/light themes)

**Never hard-code colors.** Use the token variables. This is what makes both the extension webview and the web app look consistent.

### Category Color Coding

Block types are grouped by category. These accent colors are authoritative:

| Category | Accent | Usage |
|----------|--------|-------|
| `input` (sensors, timers) | `#58a6ff` (blue) | Badge color, border tint |
| `output` (PWM, GPIO write) | `#3fb950` (green) | Badge color, border tint |
| `logic` (comparators, math) | `#d29922` (amber) | Badge color, border tint |
| `utility` (fan/distribute) | `#a78bfa` (purple) | Badge color, border tint |
| Action/add controls | `#38bdf8` (sky) | Add buttons, Settings buttons |
| Danger / remove | `#f85149` (red) | Remove buttons, conflict highlights |

---

## Access Level System (Four-Tier)

**Status**: Implemented — `level` is a required field on `FieldMeta`.

```typescript
export interface FieldMeta {
  label: string;
  units?: string;
  min?: number;
  max?: number;
  step?: number;
  level: 'hw' | 'tuner' | 'user' | 'role';  // 'role' = role-editor only, never in HMI
  description?: string;
}
```

| Level | Who sees it | Examples |
|-------|-------------|---------|
| `'hw'` | Board designer only — set at design time, never by operator | `adc_channel`, `pin_pwm`, `pwm_frequency_hz`, `oversample_count`, `pin_power`, `pin_output`, `pin_input` |
| `'tuner'` | Commissioning technician | `kp`, `ki`, `kd`, `Vmin`, `Vmax`, `scale_min`, `scale_max`, `output_min`, `output_max`, `deadband`, `reverse_acting`, `debounce_ms` |
| `'user'` | Plant operator — everyday runtime control | `setpoint`, `enabled`, `on_duration_ms`, `off_duration_ms`, `sample_interval_ms` (sensor) |
| `'role'` | Role editor only — **never in HMI** | `target_pipeline_idx` (encoder_mapped control_point picker) |

UI filter rules:
- `mode='operator'` → show only `level: 'user'` fields
- `mode='tuner'` → show `level: 'user'` AND `level: 'tuner'` fields
- `mode='hw'` → show `'user'`, `'tuner'`, and `'hw'` fields
- `level: 'role'` → **never shown in any HMI mode**

---

## How to Add a New Block Type

1. **Add to `src/block-registry.ts`** — add a new entry to `BLOCK_REGISTRY` with:
   - `typeId`: must match `pds_block_registry.h` in the firmware
   - `l3Fmt`: struct format string (Python struct notation, LE, no leading `<`)
   - `l3Fields`: field names in order, one per non-padding char
   - `fieldMeta`: label, units, level, step, min/max, description for each field

2. **Mirror in `pds-role/tools/blob_packer.py`** — add the same entry to `BLOCK_DEFS`

3. **Mirror in firmware** — `Device/pds/pds_pipeline/pds_fb/` headers and .c files

4. **Do NOT add to `role-data.js`** in the VS Code extension — that file is legacy

---

## Consumer Integration

### WEB-HMI/api (Node.js)
```typescript
// tsconfig path alias or npm link
import { BLOCK_REGISTRY, decodePipeline, reEncodePipeline } from '@pds/pipeline';
```

### WEB-HMI/src (React)
```typescript
import { BLOCK_REGISTRY, type FieldMeta, type BlockRegEntry } from '@pds/pipeline';
```

### PDS-vscode-extension (webview bundle — future)
```javascript
// After webview is migrated to React + esbuild:
const { BLOCK_REGISTRY } = require('@pds/pipeline');
```

### Current wiring (before full migration)
- `WEB-HMI/api/src/pipeline/block-registry.ts` re-exports from this package
- `role-data.js` in the extension is NOT yet migrated — still the legacy source for the extension

---

## What Does NOT Live Here

| Artifact | Where it lives |
|----------|---------------|
| React component (`PipelineBlockPanel`) | `WEB-HMI/src/components/` — will move here once extension webview is React |
| API routes | `WEB-HMI/api/src/routes/` |
| VS Code extension host code | `PDS-vscode-extension/` |
| Firmware structs | `Device/pds/pds_pipeline/pds_fb/` |
| Python packer | `pds-role/tools/blob_packer.py` |
