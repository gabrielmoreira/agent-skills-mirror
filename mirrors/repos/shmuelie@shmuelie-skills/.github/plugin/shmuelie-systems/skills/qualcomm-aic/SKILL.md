---
name: qualcomm-aic
description: Qualcomm Cloud AI 100 (AIC100) NPU development — SDK management, model compilation, SD pipeline, LoRA caching, and debugging patterns
---

When working on Qualcomm AIC100 projects, Stable Diffusion inference servers, or NPU-accelerated AI workloads, apply this domain knowledge.

# Qualcomm Cloud AI 100 (AIC100) — Domain Knowledge

## SDK Management

### Installation
- SDK is distributed as zip files: `aic_platform`, `aic_apps`, `aic_factorytools`, `aic_containers`.
- Extract to home directory, then run install script that installs platform debs (firmware, kernel module, runtime).
- Installed to `/opt/qti-aic/` — includes `exec/qaic-exec`, `dev/python/`, `dev/lib/`.

### Version Upgrades (e.g., 1.20.4 → 1.21.2)
1. Stop the server
2. Back up current install script
3. Extract new SDK zips
4. Update install script paths and deb filenames
5. Run `sudo bash scripts/install_runtime.sh`
6. Verify device: `qaic-util -q`
7. Verify exec: `/opt/qti-aic/exec/qaic-exec --help`
8. Verify Python: `python3 -c "import sys; sys.path.insert(0, '/opt/qti-aic/dev/python'); import qaicrt"`
9. Clean up old SDK versions (~4.4GB savings)

### GLIBCXX Conflict (CRITICAL)
- `qaic-exec` has `RUNPATH` pointing to `/opt/qti-aic/dev/lib/x86_64/apps/` which bundles an old
  `libstdc++.so.6` (max GLIBCXX 3.4.14).
- When `LD_LIBRARY_PATH` is empty, the RUNPATH wins, causing `GLIBCXX_3.4.30 not found` errors.
- Fix: set `LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu` in the subprocess environment to override RUNPATH.

## Model Compilation Pipeline

### ONNX → QPC Workflow
1. Export model to ONNX format
2. Compile ONNX to QPC (Qualcomm Program Container) using `qaic-exec`
3. QPC binaries are loaded into DDR, then activated on NPU

### Resource Constraints
- 14 NSPs (Neural Signal Processors) required per model activation
- ~15 GB DDR available — can hold ~4-6 models simultaneously in DDR
- Only one model can hold NSPs at a time (active inference)
- SD pipeline requires 4 QPCs (text encoder, UNet, VAE decoder, safety checker) — ~3.6 GB DDR total

### Model Registry Architecture
```
models/
  registry.yaml          # master index of all models
  <model-name>/
    config.yaml           # metadata, export settings, compile flags, IO spec
    export.py             # model-specific ONNX export
    qpc/                  # compiled QPC binaries (generated)
    onnx/                 # intermediate ONNX files (generated)
```

## Stable Diffusion on AIC100

### Model Type Detection
- **WRONG**: File-size heuristic (>5GB = SDXL) — fails for large SD1.5 checkpoints.
- **RIGHT**: Inspect safetensors header keys:
  - `conditioner` key → SDXL model
  - `cond_stage_model` key → SD 1.5 model
- Reject unsupported architectures (e.g., FLUX) early after key-based detection.

### LoRA Support
- Auto-LoRA trigger-word matching can activate unwanted LoRAs, causing garbled output.
- Parameters to control:
  - `auto_lora` (bool, default `true`) — master switch
  - `auto_lora_filter` (list[str]) — whitelist of LoRA names to allow
- Logic: `auto_lora=false` → skip matching; `auto_lora=true` + empty filter → keep all;
  `auto_lora=true` + filter → keep only matching names.

### LoRA + Model Combo Caching
- Track cache status for each LoRA + model combination on a dashboard.
- Compiled LoRA-fused QPC is specific to the exact model + LoRA + strength combo.

### Job Queue and Progress
- ETA computation: `eta_sec = elapsed * (1 - progress) / progress` (linear extrapolation).
- Report `eta_sec` in WebSocket progress messages and job tracking updates.

## Server Architecture (Python/FastAPI)

### SD WebUI Compatible API
- `POST /sdapi/v1/txt2img` — text to image generation
- `POST /sdapi/v1/img2img` — image to image generation
- `GET /sdapi/v1/sd-models` — list available models
- `GET /sdapi/v1/samplers` — list samplers
- `GET /sdapi/v1/loras` — list LoRAs
- `GET /sdapi/v1/progress` — generation progress
- `POST /sdapi/v1/interrupt` — cancel generation

### Generic Model Inference
- `POST /api/v1/run/{model_name}` — run inference on any registered model
- `GET/POST/DELETE /api/v1/registry` — manage model registry

### WebSocket Support
- `/ws/jobs/{job_id}` — real-time progress updates with ETA
- Generation progress messages include step count, percentage, and preview images

## Debugging

### RAM Usage
- Large model files loaded into DDR can consume significant RAM.
- Monitor with standard Linux tools — models may appear as memory-mapped files.

### Blurry/Garbled Output
- Usually caused by unwanted LoRA activation via trigger-word matching.
- Diagnosis: check which LoRAs were auto-activated in the generation log.
- Fix: use `auto_lora=false` or `auto_lora_filter` to restrict.

### Compilation Failures
- Check for GLIBCXX version conflicts (see SDK section above).
- Verify model architecture detection (SD1.5 vs SDXL vs unsupported).
- Check that `qaic-exec` path and SDK version match.
