# #11339 — CUDA embedding hardware-probe validation (RTX 5080 Laptop, driver 595.71.05)

Host: `BEAST` — Linux x86_64, 24 cores, 30.7 GB RAM, NVIDIA GeForce RTX 5080
Laptop GPU 16 GB (PCI `0000:02:00.0`), driver/GSP firmware **595.71.05**,
RTD3 fine-grained runtime PM enabled.

## What happened on this host (root cause, `logs/00-kernel-gpu-wedge.log`)

During this validation campaign the GPU **really failed** — not simulated:

1. Under host RAM pressure (~4.6 GB free), the driver's runtime-suspend loop
   repeatedly failed with `NVRM ... Out of memory [NV_ERR_NO_MEMORY]` while
   cycling D3cold wake/suspend (`Enabling HDA controller` every ~30 s).
2. At `15:08:21` the GSP unload timed out
   (`kflcnWaitForHaltRiscv_GA102: Timeout waiting for RISC-V to halt`,
   `gpuPowerManagementEnter: GSP unload failed at suspend`,
   `can't suspend (nv_pmops_runtime_suspend returned -5)`).
3. The device's kernel runtime-PM state is now `error`
   (`/sys/bus/pci/devices/0000:02:00.0/power/runtime_status` → `error`);
   every `nvidia-smi` fails **fast** with exit 6:
   `Unable to determine the device handle for GPU0: ... Unknown Error`.
   Recovery requires a driver rebind or reboot (root); it does not self-heal.

This turned the lane into a live fire drill for exactly the property #11339
demands: **graceful CPU degradation when CUDA is present but unusable.**

## Captures

| Log | What it proves |
| --- | --- |
| `logs/00-kernel-gpu-wedge.log` | Kernel NVRM trace of the real GPU failure + `nvidia-smi` exit 6 + PM `error` state. |
| `logs/01-probe-hardware.log` | `probeHardware()` (the exact probe `configureLocalEmbeddingPlugin()` awaits at boot) on the wedged host: `gpu: null` → `selectEmbeddingTierFromHardware()` → `fallback` → CPU preset (`gpuLayers: 0`). No crash — the selection degrades. Captured while free RAM was 4.6 GB (the pressure that triggered the wedge). |
| `logs/02-embed-throughput-cpu-lib.log` | REAL gte-small load + embeddings through the fused `libelizainference` (CPU-only staged lib), `harness/embed-throughput.ts`. Positive per-layer proof: `load_tensors: layer N assigned to device CPU` for all layers. 64 embeds → **21.3 embeddings/sec, 46.9 ms/embed, dim 384, norm 1.0** (first run, cold page cache: 4.3/sec). |
| `logs/03-embed-cuda-lib-broken-driver.log` | REAL detected-but-unusable degradation: the **CUDA-built** fused lib (linked against `libggml-cuda` / `libcudart` / `libcuda`) loading gte-small with the default full-offload request (`n_gpu_layers=99`) on the wedged driver. `ggml_cuda_init: failed to initialize CUDA: no CUDA-capable device is detected` → **every layer falls back to `assigned to device CPU`** → embeddings still produced (7.6 embeddings/sec), exit 0, **no crash**. |

Harnesses (run from repo root, see file headers):

```
bun --conditions=eliza-source .github/issue-evidence/11339-cuda-embedding-probe/harness/probe-hardware.ts
ELIZA_INFERENCE_LIBRARY=<lib> bun --conditions=eliza-source .github/issue-evidence/11339-cuda-embedding-probe/harness/embed-throughput.ts
```

`embed-throughput.ts` drives the same modules the desktop TEXT_EMBEDDING
handler (`makeFusedEmbeddingHandler`) uses: `resolveFusedLibraryPath` →
`loadElizaInferenceFfi` → `ffi.create(<embed bundle>)` →
`eliza_inference_embed` (MEAN pooling), with the gte-small GGUF staged the way
`resolveFusedEmbedBundleRoot` stages it.

## Probe fix shipped with this evidence

`plugins/plugin-local-inference/src/services/gpu-detect.ts` — the boot probe
runs `nvidia-smi` with a 3 s timeout and caches the result for the process
lifetime. On RTD3 laptops the first `nvidia-smi` after GPU sleep must
cold-wake the card, which can exceed 3 s — a timeout-killed first call would
cache `gpu: null` and wrongly demote embeddings to the CPU tier permanently.
The probe now retries **once** with a 15 s deadline when (and only when) the
first call was killed by its timeout (`error.code === "ETIMEDOUT"`, verified
identical on Node 25.2 and Bun 1.4). Fast nonzero exits (this host's PM-error
state) and ENOENT are *not* retried — they are real "no usable GPU" answers.
Contract pinned in `src/services/gpu-detect.test.ts` (7 tests, including the
exact exit-6 shape this host produced).

## Validation finding (out of scope to fix here)

The preset/env `gpuLayers` is **not threaded into the fused desktop embed
load**: `resolveDesktopEmbeddingConfig()` computes `gpuLayers` (from
`LOCAL_EMBEDDING_GPU_LAYERS` / the tier preset) but `getFusedEmbeddingHandle()`
never passes it — the native `eliza_inference_embed`
(`native/llama.cpp/tools/omnivoice/src/eliza-inference-ffi.cpp`) hard-codes
`eliza_load_llm_model_locked(ctx, /* n_gpu_layers= */ -1, ...)`, which resolves
via `ELIZA_LLM_USE_GPU` (default **true** → 99 layers). Consequences:

- the CPU-tier selection (`gpuLayers: 0`) does not actually pin the fused
  desktop embed load to CPU — degradation currently relies on ggml's own
  device fallback (which log 03 proves works when CUDA init fails), and
- an operator's `LOCAL_EMBEDDING_GPU_LAYERS=0` is silently ignored on this
  path (`ELIZA_LLM_USE_GPU=0` is the knob that actually reaches the load).

Fixing this needs an additive fused-lib ABI change (per-ctx embed gpu-layers
setter) + rebuild of shipped libs — tracked as a follow-up on the issue.

## Blocked residual (requires reboot of this host)

The **accelerated** capture — gte-small layers assigned to CUDA + CPU-vs-CUDA
embeddings/sec — cannot be produced while the driver is in PM `error` state.
Re-capture after reboot with:

```
ELIZA_INFERENCE_LIBRARY=plugins/plugin-local-inference/native/llama.cpp/build-desktop-cuda/bin/libelizainference.so \
  bun --conditions=eliza-source .github/issue-evidence/11339-cuda-embedding-probe/harness/embed-throughput.ts
```

Expected: `load_tensors: layer N assigned to device CUDA0` lines and a large
throughput multiple over the 21.3 embeddings/sec CPU baseline.
