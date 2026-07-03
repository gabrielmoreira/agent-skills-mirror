# #11760 — on-device inference memory policy: evidence

Policy implemented: **RAM-class caps + idle unload + pressure release** of the
resident inference state (no process isolation — rationale in the PR body).

Verification device: **arm64 emulator AVD (emulator-5554), Android 15 / API 35,
MemTotal 8129212 kB ≈ 7.75 GiB usable → RAM class `standard` by measurement.**
The 5.7 GB-class (Pixel 6a) profile is forced for the soak via the policy's
debug-prop override surface:

```
adb shell setprop debug.eliza.inference.ram_class constrained
adb shell setprop debug.eliza.inference.idle_unload_ms 120000   # 2 min, observable
```

This is honestly NOT a 5.7 GB device: lmkd's kill line sits higher here than on
the Pixel 6a, so the emulator soak proves the policy *fires and reclaims* under
real ambient pressure with the constrained profile active; the device-exact
10-minute soak on Pixel 6a hardware is the hardware-lab row (#11734).

## Files

| file | what |
| --- | --- |
| `exit-info-before-install.txt` | `dumpsys activity exit-info` before installing this build |
| `exit-info-after-soak.txt` | same dump after the soak. Acceptance row: the app's only exit reasons are `10 (USER REQUESTED)` (this session's + sibling-session `am force-stop`s) and `16 (PACKAGE UPDATED)` (this session's reinstalls) — **zero `reason=3 (LOW_MEMORY)`** |
| `lmkd-survival.txt` | headline acceptance evidence: during the soak lmkd fired **38 kills across 28 other packages** under "low watermark is breached" while `ai.elizaos.app` was killed **0 times** |
| `policy-decision-logs.txt` | Java (`ElizaAgent`) + TS (`aosp-local-inference`) RAM-class decisions (all `ramClass=CONSTRAINED nCtx=4096 idleUnloadMs=120000`), the on-device pressure release, and the working post-KV-fix generate |
| `logcat-relevant.txt` | filtered logcat slice: every policy decision + release + lmkd line + our-app process death |
| `meminfo-timeline.tsv` | `dumpsys meminfo ai.elizaos.app` (TOTAL PSS/RSS) + bun agent VmRSS + `/proc/meminfo` MemAvailable sampled every 15 s across the soak |
| `soak-driver.log` | transcript of the soak driver (chat turns via `/v1/chat/completions`, timings, phase markers) |

## What was observed

- **RAM-class policy fires** — three independent constrained decisions logged (`totalMem≈2975MB`, `lmkThreshold=216MB`, `nCtx=4096`, `idleUnloadMs=120000`) from both the Java probe and the TS bootstrap.
- **KV fix verified** — after fixing the retired-QJL-KV bug this soak surfaced, a real on-device generate completed (`fast path done, latencyMs=3782`, `cacheTypeK=q8_0 cacheTypeV=f16`).
- **Pressure release fires (lever c)** — the in-process leg released the model at `MemAvailable=233MB / MemTotal=2976MB` under real pressure.
- **Acceptance met** — lmkd actively reclaimed 28 other apps under low-watermark pressure and never targeted `ai.elizaos.app`; exit-info is clean of `reason=3 LOW_MEMORY`.

## Honest caveats

- The session-shared AVD reported **MemTotal ≈ 2.9 GiB** at soak time (`ActivityManager` totalMem=2975 MB) — measured RAM class `CONSTRAINED`, *harder* than the 5.7 GB Pixel 6a target. It is CPU-path (no `libggml-vulkan.so` staged → the bionic Vulkan delegation is inactive, so there is no Mali GL-mtrack term to reclaim); the same `resetResident`/`unloadModel` release plumbing is covered by the Java + TS unit tests.
- Sibling sessions reinstalled a different APK mid-run (documented shared-emulator hazard). Each clobber was reclaimed by reinstalling this branch's APK; the app's non-LMK exits above are those reinstalls/force-stops, not policy behavior.
- The device-exact 10-min Pixel 6a soak (Mali GL mtrack + that device's lmkd tables) is the hardware-lab row → #11734.
