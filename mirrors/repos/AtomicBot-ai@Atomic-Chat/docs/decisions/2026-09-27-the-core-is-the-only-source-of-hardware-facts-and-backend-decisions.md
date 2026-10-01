---
date: 2026-09-27
title: "The core is the only source of hardware facts and backend decisions"
---

# 2026-09-27 — The core is the only source of hardware facts and backend decisions

- **Context:** the machine was measured twice and the backend chosen twice.
  `tauri-plugin-hardware` probed with NVML and vulkano and the app pushed those
  facts into the core as `PUT /hardware/override`; since stage 10a the core has
  a probe of its own. Each llama.cpp extension ran the whole "which build fits,
  which is recommended, is there an update" decision through the eight Rust
  commands of its plugin (`get_supported_features`,
  `determine_supported_backends`, `list_supported_backends`,
  `find_latest_version_for_backend`, `prioritize_backends`,
  `check_backend_for_updates`, `should_migrate_backend`,
  `handle_setting_update`), while the core carried a port of the same policy
  that nothing called. Two copies drift: the fork's `detectIdealBackendType`
  still gated Vulkan on an inline `6 * 1024` after ADR 2026-09-14 had moved
  upstream to one 2 GiB constant; the two plugins' Windows CUDA 12 driver
  floors differ (551.61 vs 527.41) and each carried its own copy of the
  compute-capability veto, "kept in sync by hand". A CLI or library host of
  the core, with no app to inject facts, believed it had no GPU and no AVX.
- **Decision:** the core measures and the core answers; the app decides when.
  The extensions read `GET /hardware/info` (`getSystemInfo()` keeps its name)
  and ask `POST /backends/:provider/catalog`,
  `POST /backends/:provider/recommendation` and
  `POST /backends/:provider/updates` for the hardware-gated catalog, the
  recommendation and the update check. The core persists the optimal record
  inside the recommendation; the extension mirrors `{revision, record}` from
  the response and never `PUT`s an optimal record after a detection. The app
  does not relay `atomic-core://backend:better-detected`: the extension shows
  the dialog from the response it asked for. `tauri-plugin-hardware` stays for
  System Monitor usage polling only, and `PUT /hardware/override` is no longer
  sent. The Rust decision commands are deprecated, not deleted: their `#[test]`
  tables are the source of the `backend-select` (upstream) and
  `backend-select-llamacpp` (TurboQuant) fixture sets that pin the core's port,
  emitted by `backend_select_fixture_dump.rs` in each plugin. Install,
  `version_backend` switching, the 24 h startup policy, hot-swap, the dropdown
  and the banner stay in the app.
- **Consequences:** one probe and one selector per provider, exercised by every
  host of the core. On Windows the shell probe can see less than NVML did (a
  MUX-parked dGPU, no `nvidia-smi` on PATH, PowerShell constrained language
  mode), so the CUDA tier can degrade to Vulkan or CPU there; the hardware page
  shows the `source` of the facts and says when usage polling sees more GPUs
  than the probe did, and a refresh re-probes. Vulkan `device_type` is exact
  only with `vulkaninfo` present, otherwise a heuristic or `Unknown`. The
  fixture sets replay green in the core (339 cases across both providers) with
  one recorded shape divergence: the core leaves `order` absent on a merged
  catalog entry where Rust serialised the `serde` default `0`. Follow-up:
  delete the Rust commands and their Tauri registrations once the desktop e2e
  scenario has run against the new core on Windows and Linux, and re-emit the
  fixtures whenever a plugin table changes until then.
- **Owner:** `team`.
- **Links:** `extensions/shared/atomicCoreRuntime.ts`,
  `extensions/llamacpp-upstream-extension/src/{hardware,backend,index}.ts`,
  `extensions/llamacpp-extension/src/{hardware,backend,index}.ts`,
  `web-app/src/services/hardware/tauri.ts`,
  `web-app/src/routes/settings/hardware.tsx`,
  `src-tauri/plugins/tauri-plugin-llamacpp-upstream/src/backend_select_fixture_dump.rs`,
  `src-tauri/plugins/tauri-plugin-llamacpp/src/backend_select_fixture_dump.rs`,
  `tests/fixtures/core-contracts/backend-select/`,
  `tests/fixtures/core-contracts/backend-select-llamacpp/`,
  `../atomic-chat-core/test/contract/backend-select.test.ts`,
  `../atomic-chat-core/docs/decisions/2026-09-27-the-core-probes-hardware-with-shell-tools.md`,
  `../atomic-chat-core/docs/decisions/2026-09-27-the-core-advises-on-backends-the-app-decides.md`,
  [Pin wire contracts with Rust fixtures](2026-09-15-pin-wire-contracts-with-rust-fixtures.md).

Supersedes, in
[One GPU VRAM floor for every OS](2026-09-14-one-gpu-vram-floor-for-every-os.md),
the sentence that applies the floor "at both sites" in the extension: both
sites are now the core's. Supersedes, in
[Bridge core-owned backend work into existing app events](2026-09-16-bridge-core-owned-backend-progress-and-cache.md),
the sentence that "waits for a successful compare-and-set before showing a new
result": the core makes the compare-and-set inside the recommendation and the
app shows what it answers. Supersedes, in
[Cache optimal backends for chat upgrade prompts](2026-07-30-cache-optimal-backends-for-chat-upgrade-prompts.md),
the sentence that keeps "each extension authoritative for mapping hardware to
its own concrete backend artifact": the core's per-provider policy is.
