# #11612 bf16 retest — MoonCycles (iPhone 16 Pro Max, A18 Pro, iOS 18.7.8)

Rebuild + redeploy + on-device retest of the bf16 metallib fix chain:

- `d2bd92e5390` fix(local-inference): compile iOS metallib at MSL 3.1 (bf16 kernel family)
- submodule `58c0391eb` fix(metal): gate has_bfloat on the loaded library actually containing bf16 kernels
- `0101e1bcbe8` chore(ios-xcframework): require kernel_mul_mm_bf16_f32 in the packaged slices

## Build provenance (build-is-mine)

- Built with `ELIZA_MOBILE_REPO_ROOT=<eliza root>` (whitelabel-checkout gotcha) via
  `scripts/ios-device-deploy.mjs` (unsigned build → profile graft → explicit
  nested signing → devicectl install). Renderer stamp
  `buildId 4fd4abb18d3d…`, `builtAt 2026-07-03T01:06:17Z`, commit `76039e6e4870…`.
- mtp iOS slice rebuilt from fork revision **`58c0391eb-dirty`**
  (`mtp-slice-capabilities.json`, `builtAt 2026-07-03T00:57:44Z`); packaging
  kernel-symbol audit **PASS**; compiled AIR in `libggml-metal.a` contains
  `kernel_mul_mm_bf16_f32` + `air.simdgroup_matrix_8x8_multiply_accumulate…v64bf16…`
  targeting `air64_v26-apple-ios17.0.0` (the MSL 3.1 floor the fix raises).
- Shipped `App.debug.dylib` greps `kernel_mul_mm_bf16_f32` (4 hits).
- Install hit the devicectl DDI-mount flake (error 12040); cleared by
  `pymobiledevice3 mounter auto-mount` + reinstall.

## Timeline (2026-07-02 EDT, launch 21:09:44)

- 21:09:44 launch (`01-boot-home.png` — home up, model chip "Loading eliza-1-2B…")
- ~21:11–21:12 model load completes; warmup decode runs — **bf16 pipeline
  COMPILES AND LOADS** (`ggml-device-postfix.log` line ~5147):
  `ggml_metal_library_compile_pipeline: loaded kernel_mul_mm_bf16_f32_… th_max = 1024`
- immediately after: decode fails with a **GPU out-of-memory storm** (below);
  `llama_decode: failed to decode, ret = -3`; model chip stays "Loading…"
  (`02-model-loading.png`)
- 21:24:03 device jetsam: App killed `proc-thrashing` while frontmost
  (`JetsamEvent-2026-07-02-212403.ips`) — same residual class as the prior run

## Verdict

### 1. #11612 root cause (missing bf16 kernel) — RESOLVED on device ✔

Prior run (same device, parent `11612-fix-retest/`): every decode failed with
`MTLLibraryErrorDomain Code=5 "Function kernel_mul_mm_bf16_f32 was not found in
the library"`.

This run (log session 5, container `E223551C…`): **zero** missing-kernel
errors; the pipeline compiles and loads. The 4 `not found in the library` hits
in `ggml-device-postfix.log` are all in sessions 1–4 (the old pre-fix installs;
the on-device ggml.log is append-only across sessions).

Also: **zero new App crash reports** (`crash-baseline-pre-launch.txt` vs
`crash-list-post-run1.txt`) — the Metal nil-pipeline SIGSEGV class stays gone.

### 2. Generation — STILL BLOCKED, new (different) root cause: GPU OOM

```
llama_prepare_model_devices: using device MTL0 (Apple A18 Pro GPU) … 5460 MiB free
load_tensors:  MTL0_Mapped model buffer size =  4722.29 MiB   (36/36 layers offloaded)
sched_reserve:       MTL0 compute buffer size =  1037.00 MiB  (n_ubatch = 1024)
llama_kv_cache: … 36 MiB total (n_ctx 2048)
ggml_metal_synchronize: error: command buffer 0 failed with status 5
error: Insufficient Memory (00000008:kIOGPUCommandBufferCallbackErrorOutOfMemory)
llama_decode: failed to decode, ret = -3
```

Demand ≈ 4722 + 1037 + 36 ≈ **5.8 GiB against a 5.46 GiB Metal working-set
budget** — every command-buffer submit is rejected. The adapter hardcodes
`n_gpu_layers: 999` (`plugins/plugin-local-inference/src/adapters/capacitor-llama/index.ts`)
and default `n_ubatch` 1024 for a 4.63 GB fp16-class GGUF on an 8 GB phone: no
GPU-memory admission exists on the iOS path. After the failed decode nothing
unloads the model → memory thrash → jetsam (`proc-thrashing`) ~14 min in.

Fix direction (product work, matches the residual already flagged in the prior
README): device-aware offload/ubatch admission against
`recommendedMaxWorkingSetSize` (the desktop path has `hardware.ts assessFit`;
iOS has nothing), and/or a phone-tier quant, plus unload-on-decode-failure.

### 3. Driven user prompt (XCUITest send leg) — harness shipped; run blocked by a physical unlock

`testComposerSendsPromptAndWaitsForReply` (committed to the BootCaptureUITests
harness, `87761c725e4`) drives a REAL composer send: warm-up wait → type →
send-control tap (iOS Return never reaches the web textarea) → hard-assert the
draft cleared → reply filmstrip. `build-for-testing` for the lane went green
(`** TEST BUILD SUCCEEDED **`).

The on-device run could not execute this session: the first attempt hit the
recurring devicectl DDI-mount flake (error 12040); clearing it with
`pymobiledevice3 mounter auto-mount` raced Xcode into a wedged
"Device is busy (Preparing MoonCycles)" state, and the reboot that clears that
wedge leaves the phone at its passcode screen (`PasswordProtected: true`) —
developer services stay unavailable until a human unlocks it. Once unlocked,
the leg is one command:

```
ELIZA_MOBILE_REPO_ROOT=<eliza root> node scripts/ios-device-capture.mjs \
  --platform device --device 59EBB356-BC44-5AA2-91F1-E6AAE756BB86 \
  --app-path ios/build/device-deploy-stage/App.app --skip-build \
  --only-testing AppUITests/BootCaptureUITests/testComposerSendsPromptAndWaitsForReply
```

Expected outcome on this build (from the warmup decode already captured): the
send lands, generation hits the same GPU OOM, and the filmstrip records the
user-visible failure surface — the model chip stays "Loading eliza-1-2B…"
because the load-path warmup decode fails and nothing flips the status.

### 4. TTS / vision — N/A on this device+build

Text generation cannot complete (every decode OOMs), so the dependent
voice-reply TTS and vision-describe legs remain unreachable on this hardware
until the memory-admission work lands.

## Files

- `ggml-device-postfix.log` — full on-device ggml/llama log (5 sessions;
  session 5 = this build). THE artifact: bf16 kernel loads + OOM storm.
- `mtp-slice-capabilities.json` — built-slice provenance (fork rev, target).
- `01-boot-home.png`, `02-model-loading.png` — live UI on the new build.
- `crash-baseline-pre-launch.txt` / `crash-list-post-run1.txt` — no new App
  crash reports; one new JetsamEvent.
- `JetsamEvent-2026-07-02-212403.ips` — App killed proc-thrashing (residual).
- Send-leg filmstrip: not captured this session (device passcode-locked after
  the DDI-wedge reboot — see section 3 for the one-command replay).
