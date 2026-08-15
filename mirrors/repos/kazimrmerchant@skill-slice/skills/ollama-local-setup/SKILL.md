---
name: ollama-local-setup
description: "Stands up and repairs a Windows local Ollama server so models on a custom disk appear on localhost:11434 (/api/tags and /v1/models) and GPU KV-cache is not starved. Use when ollama list is empty, models vanish after reboot, port 11434 conflicts, or throughput collapses. Not for Ollama Cloud GLM planning (ollama). Never treat the tray app as honoring OLLAMA_MODELS without a junction."
version: 1.0.1
category: mlops
---

# ollama-local-setup

Production guide for standing up and fixing a local Ollama server on **Windows**, where models live on a non-default disk and must be visible to clients connecting via `http://localhost:11434` (both the native `/api/tags` and the OpenAI-compatible `/v1/models`). Also covers performance tuning — diagnosing and fixing GPU starvation caused by oversized context windows (KV cache spilling to CPU RAM).

## When to Use

Trigger this skill when any of the following are true:

- `ollama list` is empty, `/api/tags` returns `{}`, or `/v1/models` returns `{"object":"list","data":null}`.
- User wants local-only inference (Hermes `provider=ollama`, `base_url=http://localhost:11434/v1`, `api_key=ollama`).
- Models were moved to another drive and the server no longer sees them.
- After a reboot or relaunch the local models "vanished."
- You are about to start an `ollama serve` / `ollama app` and port 11434 may already be in use.
- Local inference is very slow (single-digit tok/s) or GPU utilization sits near ~5% even on a powerful GPU (e.g. RTX 3090 Ti). Classic KV-cache spill from an oversized `context_length`.

## Prerequisites

- **Windows host** (PowerShell primary). Linux/macOS notes provided where relevant.
- Ollama installed (app or CLI). Default install path: `$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe`.
- A target models directory on a non-default drive, e.g. `YOUR_MODELS_DIR`, containing `blobs/` (multi-GB files) and `manifests/` (model tags). Set `$env:OLLAMA_MODELS` to that path.
- For performance tuning: an NVIDIA GPU with `nvidia-smi` available.
- For Hermes integration: Hermes config must set `provider=ollama`, `base_url=http://localhost:11434/v1`, `api_key=ollama`, and `context_length>=64000` (Hermes refuses to init below 64K).

## Procedure

### Phase 1 — Fix "empty models" on Windows (three gotchas)

There are three silent failure modes on Windows that cause `ollama list` to return empty:

1. **`OLLAMA_MODELS` must use BACKSLASHES** on Windows (e.g. `YOUR_MODELS_DIR` via `$env:OLLAMA_MODELS`). Forward slashes are silently rejected — Ollama falls back to the empty default `C:\Users\<user>\.ollama\models`, and `/api/tags` returns `{}`. This is silent: no error, just empty.
2. **The Windows Ollama app (`ollama app.exe`, the tray app) IGNORES `OLLAMA_MODELS` entirely.** It always serves from its default path. Fix by redirecting the default path itself with a directory junction (see below), not by setting the env var alone.
3. **Only ONE server per port.** Two `ollama serve`/app processes on 11434 → `/v1/models` returns `null` and clients get 404s. Kill all Ollama processes, then start exactly one.

#### Step 1 — Set the env var correctly (backslashes)

```powershell
# Point at YOUR_MODELS_DIR (backslashes on Windows)
$env:OLLAMA_MODELS = "YOUR_MODELS_DIR"
# User scope (re-logon to apply; new shells only)
setx OLLAMA_MODELS $env:OLLAMA_MODELS

# Machine scope (requires admin)
setx OLLAMA_MODELS $env:OLLAMA_MODELS /M
```

> **HARD RULE:** Always use backslashes on Windows. Forward slashes are the #1 silent failure.

#### Step 2 — Redirect the default path with a directory junction

The app ignores the env var, so redirect the default path `C:\Users\<user>\.ollama\models` to your custom directory:

```powershell
# Only if the default dir is empty or you've moved its contents
cmd /c rmdir "C:\Users\<user>\.ollama\models"

# Create the junction (reboot-safe, filesystem-level)
cmd /c mklink /J "C:\Users\<user>\.ollama\models" $env:OLLAMA_MODELS
```

A junction is filesystem-level and **reboot-safe** — it survives restarts and does not depend on an env var being set.

> **HARD RULE:** Do not trust the app to honor `OLLAMA_MODELS`. Use the junction. Setting the env var alone will not move the app's models.

#### Step 3 — Kill stale processes, then start exactly ONE server

```powershell
# Kill all Ollama processes
taskkill /F /IM "ollama app.exe" /T
taskkill /F /IM ollama.exe /T

# Launch the normal app (tray + supervised server)
start "" "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
```

> **HARD RULE:** Do not run both `ollama app.exe` and a manual `ollama serve`. Pick one. Two listeners on 11434 break `/v1/models`.

> **Linux/macOS note:** `OLLAMA_MODELS` works normally there and forward slashes are fine. The junction trick is Windows-specific. On Linux a symlink (`ln -s`) achieves the same redirect.

#### Step 4 — Verify

See [Verification](#verification) below. If still empty, re-read `OLLAMA_MODELS` with backslashes and confirm the junction target exists and contains `blobs/` + `manifests/`.

> **Load `references/windows-troubleshooting.md`** when you need copy-paste command recipes (env set, junction, kill+relaunch, verify) with placeholders for a specific user/machine.

### Phase 2 — Performance tuning (GPU starvation from oversized context)

**Symptom:** a large model (e.g. `qwen3.6:27b`, 27B) generates ~3 tok/s and `nvidia-smi` shows ~5% GPU compute util during generation, even on a strong GPU (RTX 3090 Ti, 24 GB). VRAM shows the model loaded but the KV cache is elsewhere.

**Root cause:** Ollama sizes the KV cache from the effective context length at load = `min(client context_length request, OLLAMA_CONTEXT_LENGTH env var)`. A 27B model at 256K context needs a ~40 GB KV cache. When that exceeds free VRAM, Ollama **silently allocates it in CPU RAM** and shuffles KV data per token → GPU idle, throughput collapses. The binding cap is the server env var `OLLAMA_CONTEXT_LENGTH`; lowering the Hermes/client `context_length` alone does NOT free VRAM unless the env var is also reduced.

#### Step 1 — Persist tuning in Windows User env

```powershell
setx OLLAMA_CONTEXT_LENGTH 65536
setx OLLAMA_KV_CACHE_TYPE q4_0
setx OLLAMA_FLASH_ATTENTION true
```

- **`OLLAMA_CONTEXT_LENGTH=65536`** — 64K satisfies Hermes's `context_length>=64000` requirement and is small enough for the KV cache to fit on GPU for most chat.
- **`OLLAMA_KV_CACHE_TYPE=q4_0`** — 4-bit KV cache. `qwen3.6:27b` ≈ 17.8 GB + q4 KV ≈ 2.6 GB ≈ 20.4 GB of 24 GB, leaving headroom.
- **`OLLAMA_FLASH_ATTENTION=true`** — faster attention kernels.

#### Step 2 — Restart the server

```powershell
taskkill /F /IM "ollama app.exe" /T
taskkill /F /IM ollama.exe /T
# Then launch one server (app or ollama serve, not both)
start "" "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
```

#### Step 3 — Verify performance improvement

In one shell, monitor GPU:

```powershell
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv -l 1
```

In another shell, run a 200-token generation. Use `think:false` for Qwen3 (it defaults to thinking mode, which inflates latency).

> **Load `references/performance-tuning.md`** when diagnosing GPU starvation or when you need the exact generation-speed probe and before/after numbers (~3→~33 tok/s, ~5%→~90% GPU util on a 3090 Ti).

## Pitfalls

- **Forward-slash env var is the #1 silent failure.** Always set backslashes on Windows. A forward-slash `YOUR_MODELS_DIR` is silently rejected; Ollama falls back to the empty default with no error.
- **Don't trust the app to honor `OLLAMA_MODELS`.** Use the junction. Setting the env var alone will not move the app's models.
- **Don't run both `ollama app.exe` and a manual `ollama serve`.** Pick one. Two listeners on 11434 break `/v1/models` (returns `null`, clients get 404s).
- **Oversized `context_length` starves the GPU (performance, not visibility).** A 27B model at 256K context allocates a ~40 GB KV cache that won't fit VRAM, so Ollama spills it to CPU RAM → ~5% GPU util, ~3 tok/s. Fix: cap `OLLAMA_CONTEXT_LENGTH` (e.g. 65536) and set `OLLAMA_KV_CACHE_TYPE=q4_0`. Reducing the *client* `context_length` alone does not help — the server env var is the binding cap.
- **Verify with `ollama list` and raw `curl`, not fragile JSON-parsing one-liners.** Prefer the official CLI and a direct `curl http://localhost:11434/api/tags`. A mis-parsed probe can report "empty" when the server is actually healthy (false alarm). See `scripts/verify-ollama.ps1`.
- **Confirm models are actually on disk** at the junction target before blaming the server: `blobs/` should contain multi-GB files and `manifests/` should contain model tags.
- **Qwen3 defaults to thinking mode**, which inflates latency during speed probes. Always pass `think:false` when measuring generation throughput.

## Verification

Run `scripts/verify-ollama.ps1` (PowerShell, no external deps) for a deterministic probe that checks `/api/tags`, `/v1/models`, `OLLAMA_MODELS`, and the default-vs-custom path; reports a clear PASS/FAIL.

Or manually:

```powershell
# CLI check
ollama list

# Native API
curl -s http://localhost:11434/api/tags

# OpenAI-compatible API
curl -s http://localhost:11434/v1/models
```

**Expected:** all configured models appear under both endpoints, including the one the client needs (e.g. `qwen3.6:27b` for Hermes).

**For Hermes integration,** ensure config sets:
- `provider=ollama`
- `base_url=http://localhost:11434/v1`
- `api_key=ollama`
- `context_length>=64000` (Hermes refuses to init below 64K)

**For performance verification,** watch `nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv -l 1` in one shell while running a 200-token generation in another. Expect GPU util to jump from ~5% to ~90% and throughput from ~3 tok/s to ~33 tok/s on a 3090 Ti with the tuning recipe applied.

## Support Files

- **`references/windows-troubleshooting.md`** — Load when you need copy-paste command recipes (env set, junction, kill+relaunch, verify) with placeholders for a specific user/machine.
- **`references/performance-tuning.md`** — Load when diagnosing GPU starvation or when you need the exact generation-speed probe and before/after numbers.
- **`scripts/verify-ollama.ps1`** — Load and run for a deterministic end-to-end probe (checks `/api/tags`, `/v1/models`, `OLLAMA_MODELS`, and default-vs-custom path; reports PASS/FAIL).
