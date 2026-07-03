# #11612 fix retest — real device MoonCycles (iPhone 16 Pro Max, A18 Pro, iOS 18.7.8)

Retest of the durable fix (`aa1fb212a63`: llama.cpp submodule `c3b9fa647` recoverable
Metal failure + pullable ggml log sink + jetsam memory budget) on the same physical
device that produced the pre-fix crash-loop evidence in the parent directory.

## Build provenance (build-is-mine)

- Built from `feat/multi-account-login-verification` (renderer stamp commit
  `500ca0edc70`, a descendant of fix commit `aa1fb212a63`), `builtAt
  2026-07-02T23:23:56Z`, `runtimeMode: local`, bundle id `ai.elizaos.app`.
- Both iOS LlamaCpp xcframework slices were REBUILT from the fixed fork —
  mobile-build log: `Rebuilding mtp artifact for ios-arm64-metal — fork revision
  changed (eliza-pin-9588-kokoro-decoder-2-g114eee08e -> c3b9fa647)`.
- Shipped binary greps (App.debug.dylib in the installed staged app):
  `nil Metal compute pipeline` ✓, `ggml/llama logs ->` ✓,
  `GGML_METAL_ABORT_ON_NIL_PIPELINE` ✓.
- Deploy: unsigned build → profile graft → explicit nested signing → devicectl
  install (scripts/ios-device-deploy.mjs recipe). Gotcha hit + fixed on the way:
  in a nested whitelabel checkout the repo-root walk can select the outer app
  shell instead of the elizaOS app — must pass
  `ELIZA_MOBILE_REPO_ROOT=<eliza root>` to build/ship the Eliza app.

## Timeline (2026-07-02, EDT)

- 19:25:24 crash baseline recorded (`crash-baseline-pre-launch.txt`)
- 19:25:33 launch #1 (fixed build) — soak: alive at t+60/150/240/420/600/780 s
  (`fix-run-*.png`), model chip "Loading eliza-1-2B…" (first-boot bun cache
  rebuild makes the pre-load phase slow)
- 19:39:50 relaunch — warm caches; native model load starts
- 19:43:32 `ggml.log` appears in the app container (the fix's log sink) —
  pulled via `devicectl device copy from … appDataContainer …
  "Library/Application Support/Eliza/logs/ggml.log"`
- ~19:43   FIRST DECODE — the exact pre-fix crash point — **fails cleanly**
- 19:44:49 device-wide jetsam storm; App killed (`proc-thrashing`) — residual
  symptom #2, see below

## Verdict

### 1. Metal NULL-pipeline SIGSEGV crash-loop: GONE ✔

Pre-fix (same device, same day, parent dir): 4/4 launches died `EXC_BAD_ACCESS
(SIGSEGV) KERN_INVALID_ADDRESS at 0x0` in `ggml_metal_encoder_set_pipeline` ~32 s
after launch (`prefix-App-2026-07-02-182502.ips`: procLaunch 18:24:30 → crash
18:25:02).

Post-fix: **zero new `App-*.ips`** across ~20 minutes / two launches including a
full model load + the first `llama_decode` (`crash-list-final.txt` vs
`crash-baseline-pre-launch.txt` — the only new entry is a JetsamEvent, not an app
crash report). The decode failure was logged and surfaced instead
(`ggml-device.log` tail):

```
ggml_metal_encoder_set_pipeline: error: Metal compute pipeline is nil - failing this graph instead of dispatching
ggml_metal_op_encode: error: node 17 (op = MUL_MAT, name = 'node_48') requires a Metal pipeline that failed to compile - failing graph
ggml_metal_graph_compute: graph encode failed (nil compute pipeline or encoder error) - returning GGML_STATUS_FAILED
llama_decode: failed to decode, ret = -3
```

### 2. Root cause captured — the exact failing kernel (via the new ggml.log sink)

```
ggml_metal_library_compile_pipeline: failed to compile pipeline: base = 'kernel_mul_mm_bf16_f32', name = 'kernel_mul_mm_bf16_f32_bci=0_bco=1_ne12=1_ne13=1_r2=1_r3=1'
ggml_metal_library_compile_pipeline: Error Domain=MTLLibraryErrorDomain Code=5 "Function kernel_mul_mm_bf16_f32 was not found in the library"
```

**`kernel_mul_mm_bf16_f32` is MISSING from the embedded iOS metallib** while the
A18 Pro (bf16-capable GPU) kernel selection requests the bf16 `mul_mm` variant
for eliza-1-2b's bf16 tensors. Not a GPU-family/threadgroup constraint — the
function was never compiled into the library the iOS build embeds. Fix: compile
the iOS embedded Metal library with the BF16 kernel family (or gate
`has_bf16` off when the library lacks the function so the f16/f32 path is
selected).

### 3. Residual — jetsam storm persists for this model (NOT fixed)

`JetsamEvent-2026-07-02-194449.ips`: `largestProcess: App`, App killed
`proc-thrashing`, ~588 processes killed/exited device-wide ~1 min after the
clean decode failure. The 4.63 GB `eliza-1-2b-128k.gguf` stays mapped after the
failed decode (nothing unloads it) and is simply too large for an 8 GB phone.
Remaining work: per-device model tier/quant selection + unload-on-decode-failure.

### 4. Gen / TTS / vision: N/A on this device+build

On-device text generation cannot succeed until the metallib carries the bf16
kernels (every decode fails cleanly at the same missing kernel), so the
dependent TTS/vision voice-reply legs are unreachable. Deep-link composer
prefill (`elizaos://ask?text=…`) verified working (`deeplink-prefill-composer.png`);
launch-payload text is prefill-only by design (attacker-authorable), and
hands-free voice auto-send did not arm from a programmatic deep link (no user
gesture for audio unlock), so no on-device send was possible without a tap.

## Files

- `ggml-device.log` — full on-device ggml/llama log (1037 lines): model load,
  kernel compiles, the missing-kernel error, the clean decode failure. THE
  root-cause artifact.
- `prefix-App-2026-07-02-182502.ips` — pre-fix SIGSEGV report (contrast).
- `JetsamEvent-2026-07-02-194449.ips` — post-fix residual jetsam storm.
- `crash-baseline-pre-launch.txt` / `crash-list-final.txt` — crash-report ledger
  proving zero new App crash reports.
- `fix-run-*.png` — soak screenshots (app alive through t+13 min).
- `deeplink-prefill-composer.png`, `post-jetsam-springboard.png`.
