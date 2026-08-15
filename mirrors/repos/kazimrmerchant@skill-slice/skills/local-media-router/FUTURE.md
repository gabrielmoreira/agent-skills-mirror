# Future improvements (`/localvideo` · `/localimage`)

Prioritized backlog from Ollama Cloud GLM-5.2 design pass (2026-08-06) + workstation realities.

## P1 — soon
1. **Seeded video continuation CLI** — `run_long_windows.py --seed_video <mp4>` / I2V Windows wrapper so ref→3s→10s is one path.
2. **Export Flux fp8 API workflows** into `localimage/workflows/` (unblocks reliable `/localimage hero`).
3. **Windows `run_i2v_windows.py`** mirroring low-VRAM / gpu-heavy (critical for likeness flow).
4. **Helper `--duration 3|6|10`** + `--ref` flags on one entry script.
5. Auto `/reviewresults` + identity stranger test after likeness jobs.

## P2
4. `seed:N` / `--neg` parsing in both commands.
5. SeedVR2 / Real-ESRGAN upscale path when models present under `$env:UPSCALE_MODELS`.
6. Multi-GPU / queue lock file so LongCat and ComfyUI never collide.
7. Wall-clock + peak VRAM appended automatically to `run.log`.

## P3
8. `_localmedia` catalog JSONL indexer.
9. `/localvideo batch Nx` multi-seed packs.
10. Optional local music bed attach (only if a local TTS/music tool is installed).
11. Quote-series / YT pack auto-slug from director skill when cwd is YT Videos.

## P4
12. Live preview frames during LongCat denoise (needs runner hooks — not present).
13. Auto `/reviewresults` after every `/localvideo 10s` ship.

## Advice for future calls (operators)

- Always pass **duration** on video (`3s|6s|10s`) to skip the ask gate.
- Prefer **`/localvideo 3s`** for prompt iteration; only spend **10s** on keepers.
- Use **`/localvideo edit … upscale`** after a good 480p plate instead of forcing native long HD.
- Keep Flow for scarce-credit hero shots; these commands are the daily driver.
- After changing runners, update flag tables in `localvideo/SKILL.md` (do not guess).
- First `/localimage` on a new machine: export Comfy API workflow once, then never again.
