---
name: localimage-stills
description: >-
  Implements the /localimage backend: ComfyUI checkpoint discovery, style-token
  routing to Flux-fp8 or Krea, hero stills for LongCat I2V, then pack handoff.
  Use for style maps, refs/hero.png, or Flux versus Krea still batches. Do not
  use as the ComfyUI install/node chair (comfyui) or as NVENC pack layout
  (local-media-router). Not a user-facing slash command.
---

# localimage-stills (backend for `/localimage`)

**User entry:** only `/localimage`. This skill is implementation.

## Model learning / style routing

Before every gen:

```powershell
powershell -File "..\local-media-router\discover.ps1"
# then read ..\local-media-router\models_discovered.json
```

| Style tokens | Model | Workflow |
|--------------|-------|----------|
| realistic, photoreal, photo, cinematic, *(default)* | `flux1-dev-fp8.safetensors` | `workflows/flux_fp8_t2i.json` |
| krea, fast, stylized | `krea2_turbo_fp8_scaled.safetensors` | Krea API JSON (export if missing) |
| pixar, disney, 3d cartoon | **none installed** | **ASK** — offer Flux photoreal or Krea; never silent Pixar |
| anime, illustration | Krea (closest) or ask | |

**Lesson (MJ pack):** A prompt *file* said Pixar while the actual still+video used Flux photoreal. Always record `style` + `model` in the pack manifest and keep prompt files aligned with the routed model.

## Role with `/localvideo`

- `hero` / likeness → `refs/hero.png` after face QA
- `4x` → Read all; pick best; user can override
- Do not hand a weak face to I2V

## Stack

| Piece | Path |
|-------|------|
| ComfyUI | `$env:COMFYUI_ROOT` |
| venv | `$env:COMFYUI_ROOT\venv\Scripts\python.exe` |
| Models | `$env:COMFYUI_ROOT\models`, `$env:COMFYUI_MODELS` |
| Default | Flux fp8 |
| API | `http://127.0.0.1:8188` |
| Workflow | `workflows/flux_fp8_t2i.json` |

After gen → **local-media-router**. Details → **comfyui** skill.

## Preconditions

```powershell
Test-Path "$env:COMFYUI_ROOT\main.py"
try { Invoke-RestMethod http://127.0.0.1:8188/system_stats -TimeoutSec 3 | Out-Null; "UP" } catch { "DOWN" }
nvidia-smi --query-gpu=memory.free --format=csv,noheader
```

If LongCat is using the GPU → wait/ask.

## Execute

1. Route style → model/workflow  
2. Inject prompt/seed/batch into workflow JSON  
3. The sibling comfyui skill's workflow runner (`run_workflow` / `run_batch` helpers there)  
4. Copy → pack `raw/` → `keep/` / `final/` / `refs/hero.png` if hero  
5. **Read** every image; write `style`+`model` into manifest  

## Constraints

- Local only  
- Never delete keepers/finals  
- One `/localimage` command only — never create a duplicate slash entry  
