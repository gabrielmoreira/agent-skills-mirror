---
name: localvideo
description: >-
  Local LongCat-Video on Windows (high-VRAM NVIDIA) with identity-first
  flow (hero still → I2V → lengthen → upscale). Use for /localvideo;
  never text-only T2V for celebrity/character likeness finals.
---

# localvideo

## Stack

Resolve install roots from the environment (do not invent a publisher path):

| Piece | Path |
|-------|------|
| Code + venv | `$env:LONGCAT_ROOT` (LongCat-Video checkout) |
| Weights | `$env:LONGCAT_WEIGHTS` |
| Short T2V | `run_sample_windows.py` |
| Long T2V+VC | `run_long_windows.py` |
| Windows I2V | `run_i2v_windows.py` (**prefer `--no-distill`**) |
| Official I2V demo | `run_demo_image_to_video.py` |
| Python | `$env:LONGCAT_ROOT\.venv\Scripts\python.exe` |
| Stills | `/localimage` → style-routed ComfyUI (default Flux photoreal) |
| Docs | `WINDOWS_SETUP.md`, `windows_vram.py` (`--gpu-heavy`) |

After gen → **`local-media-router`**. Before gen → run `local-media-router/discover.ps1` and match motion-prompt style to the still’s model/style (no Pixar words on a Flux photo hero).

### I2V note

Distill LoRA + accelerate CPU offload / gpu-heavy can crash with `Tensor on device meta`. Until fixed: **`run_i2v_windows.py --no-distill`** (e.g. `--steps 20`).

## Canonical quality flow (mandatory mindset)

```
Hero still (Flux / ref) → still QA
  → I2V @ 3s → frame identity QA
  → only then 6s/10s (continuation)
  → upscale → NVENC final
  → stranger-test QA (identity FAIL = BLOCKER)
```

### When pure T2V is OK
Landscapes, products, vehicles, abstract, non-likeness stylized scenes.

### When pure T2V is NOT OK for finals
Named people, celebrities, recurring characters, “must look like X”. Use **ref + I2V**. Lesson learned: MJ stage text-only distill → wrong face.

## Preconditions

```powershell
Test-Path "$env:LONGCAT_ROOT\run_sample_windows.py"
Test-Path "$env:LONGCAT_ROOT\run_long_windows.py"
Test-Path "$env:LONGCAT_WEIGHTS\dit"
ffmpeg -hide_banner -encoders 2>&1 | Select-String "h264_nvenc"
nvidia-smi --query-gpu=memory.free,memory.total --format=csv,noheader
```

If free VRAM &lt; 6GB: warn — do **not** start ComfyUI in parallel with LongCat.

## Arg grammar

```
/localvideo [3s|6s|10s] [best|gpu-heavy] [ref <image>] <prompt>
/localvideo edit <path> [extend|restyle|trim|upscale] [prompt...]
```

Also accept: `3 sec`, `~10s`, `--gpu-heavy`, `--best`, `--ref`.

## Decision tree — identity (before duration)

1. Prompt names a **person / character / celebrity** OR user cares about likeness?  
   - **Yes** → need `ref <image>` or produce still via `/localimage` and **stop for approval**.  
   - User says “text only anyway” → warn, then T2V only if they confirm.  
2. Else → T2V allowed.

## Decision tree — duration

1. `edit` → EDIT mode (below).  
2. Duration token present → use table.  
3. Else → **ASK**: 3s / 6s / 10s.  
4. If user asks **10s** but no approved 3s keeper for likeness jobs → **recommend 3s first**; only skip if they explicitly say so.

| Token | Runner | Notes |
|-------|--------|-------|
| `3s` | sample · 49 frames | **Default iterate** |
| `6s` | long · 93f · cont=0 | After 3s OK |
| `10s` | long · cont=1 · trim 10s | After 3s OK for likeness |

## Decision tree — quality flags

| Token | Maps to |
|-------|---------|
| `gpu-heavy` | `--gpu-heavy --gpu-gib 20` |
| `best` | `--gpu-heavy --gpu-gib 20 --no-distill --steps 40` (or 50 if user accepts time) + plan upscale after |
| *(default)* | distill + cpu_offload (fast / draft) |

Draft vs final: draft may use distill; **likeness finals should use `best` or at least gpu-heavy + more steps**.

## I2V vs T2V

| Mode | When | How (this PC) |
|------|------|----------------|
| **I2V** | `ref` present or approved still in pack `refs/` / `raw/hero.png` | Prefer LongCat image-to-video path; if Windows I2V runner not yet wrapped, say so and either wrap from `run_demo_image_to_video.py` or use Comfy I2V — **do not silently fall back to T2V for likeness** |
| **T2V** | No likeness requirement | `run_sample_windows.py` / `run_long_windows.py` |

Pack should store: `refs/hero.png` (approved still), `raw/`, `keep/`, `final/`.

## Edit modes

| Mode | Behavior |
|------|----------|
| `extend` | Lengthen (seeded VC when CLI exists; else new segment + optional concat) |
| `restyle` | New gen with prompt; keep source |
| `trim` | ffmpeg cut |
| `upscale` | lanczos+NVENC default; SeedVR2/ESRGAN if installed and user asks |

## Invocation examples

```powershell
$py = "$env:LONGCAT_ROOT\.venv\Scripts\python.exe"
# Draft 3s T2V (non-likeness)
& $py run_sample_windows.py --output_dir $out --output_name clip.mp4 --prompt '...' --num_frames 49 --steps 16 --distill
# Best-ish 3s
& $py run_sample_windows.py ... --num_frames 49 --no-distill --steps 40 --gpu-heavy --gpu-gib 20
# 10s after approval
& $py run_long_windows.py ... --continuations 1 --gpu-heavy
ffmpeg -y -i raw\clip.mp4 -t 10 -c:v h264_nvenc -preset p5 -cq 19 -an final\clip_10s.mp4
```

## Post + QA

1. Promote to `keep/` + NVENC `final/` via **local-media-router**  
2. Extract start/mid/end (or 6 frames) → **Read** each  
3. **Identity stranger test** for people/characters — FAIL = BLOCKER  
4. `manifest.json` includes `ref`, `mode: t2v|i2v`, `quality: draft|best`  
5. Report paths + elapsed; never claim ship on identity FAIL  

## Constraints

- Local only from this skill  
- Never delete keepers/finals  
- One GPU heavy job at a time  
- Honest ceiling: local likeness &lt; Flow/Veo; still→I2V is the way to close the gap  
