---
date: 2026-09-29
title: "Fetch large files over several connections, and give up on quiet ones"
---

# 2026-09-29 — Fetch large files over several connections, and give up on quiet ones

- **Context:** Field feedback on 2026-09-29: "2 GB shows an hour, then no
  progress; only a restart helps." Both halves were real. The Rust
  downloader (`src-tauri/src/core/downloads/`) read each body with no read
  timeout and no TCP keepalive (reqwest 0.11 has neither by default), so a
  connection that died without a FIN — a Wi-Fi switch, a laptop that slept,
  a VPN reconnect — waited forever; the five-step retry ladder only runs on
  an error or an early end, and neither ever came. And every file came over
  one connection: on the same Mac and the same 2 GB GGUF from Hugging Face's
  CDN, one stream ran at 1.2–2.1 MB/s, four at 2.9 MB/s together, eight at
  5.6 MB/s. Meanwhile the panel quoted the last smoothed speed and a frozen
  ETA through a stall, and progress went out only every 10 MB per file —
  one update every 20 s at 0.5 MB/s. PostHog (`model_download`, 30 days,
  per user × model): 75% of attempts ended with the model, 12% only in a
  cancel, 9.5% with no terminal event at all, 3% in failures — and only 105
  `network` failures, because a stall never became an error. Every terminal
  event read `size_bucket: 'unknown'`: those handlers read a size the
  extensions' events never carry.
- **Decision:** Four changes, all in the app's downloader (models still
  download here, not through the core; the core's TypeScript port gets the
  same treatment when downloads move there).
  1. **Watchdog.** A body read that yields nothing for 30 s fails the
     connection and reconnects from the durable offset through the existing
     ladder; response headers must arrive within 30 s of a request; TCP
     keepalive is on. After 10 s of silence the task emits a new `stalled`
     stage, and the in-stream reconnect ladder now reports `retrying`.
  2. **Honest panel.** A `stalled` or `retrying` stage drops the speed
     estimate, hides the ETA and shows the stage next to the percentage
     (`42% · Stalled, reconnecting… · 4.20 / 12.40 GB`); bytes arriving clear
     it. Progress events are time-based (every 500 ms per task) instead of
     every 10 MB per file.
  3. **Several connections** (`segmented.rs`). A file of at least 64 MB whose
     server answers a ranged probe with a matching 206 is split into up to
     eight ranges (none under 16 MB), each fetched over its own HTTP/1.1
     connection and written in place into a `.tmp` created at full size; a
     connection that finishes takes over the far half of the largest range
     still running. Resume state is `<save_path>.parts` — per range, start,
     bytes on disk, end — replaced atomically, recording only bytes whose
     write returned. It exists exactly as long as the full-size `.tmp`: it is
     written before the `.tmp` grows and removed only after the `.tmp` became
     the final file or was truncated, so a `.tmp` without a `.parts` is always
     a single-stream partial, safe to append to. A server that ignores ranges,
     or stops honouring them, gets the single-stream download from byte 0. A
     single-stream partial left by an older build becomes a finished first
     range, so its bytes are not fetched again.
  4. **Telemetry.** The terminal `model_download` event reads size from the
     download store's row and adds `avg_bytes_per_second`, `stall_count` and
     `retry_count`.
- **Consequences:** A dead connection now costs 30 s instead of a restart,
  and the user sees why the bar is not moving. Measured with this code on the
  same Mac, a 386 MB GGUF from Hugging Face took 325 s over one connection
  (1.13 MB/s) and 101–135 s over eight (2.7–3.7 MB/s), the file's sha256
  matching the Hub's. Large downloads open up to
  eight connections per file (sixteen for a model with its mmproj); a split
  closes the donor's connection mid-body, which can waste what was in flight
  on it. On Windows, the first write far into a freshly extended `.tmp` makes
  NTFS zero-fill the gap once — the cost of writing the file once more, paid
  by that connection's write. The free-space preflight counts a resumed
  download's bytes from its `.parts`, not from the full-size `.tmp`; the
  Windows path-length check now budgets for `.parts.new`, the longest sidecar.
  The extensions' failed-download cleanup removes `.parts` with the rest.
  Everything that calls `download_files` — backends, diffusion files, MLX —
  gets the same behaviour. The timing and sizing knobs live in one
  `TransferTuning` so tests can shrink them.
- **Owner:** team.
- **Links:** [`src-tauri/src/core/downloads/segmented.rs`](../../src-tauri/src/core/downloads/segmented.rs),
  [`src-tauri/src/core/downloads/helpers.rs`](../../src-tauri/src/core/downloads/helpers.rs),
  [`web-app/src/lib/downloadFormat.ts`](../../web-app/src/lib/downloadFormat.ts),
  [`web-app/src/hooks/useDownloadStore.ts`](../../web-app/src/hooks/useDownloadStore.ts),
  [`web-app/src/containers/DownloadManegement.tsx`](../../web-app/src/containers/DownloadManegement.tsx);
  builds on [resuming from verified persisted offsets](2026-07-14-resume-interrupted-model-downloads-from-verified-persisted.md)
  and the #290 download stages.
