# AGENTS.md — RuView (WiFi-DensePose)

Project rules for Codex (and any agent) working in the `ruvnet/RuView` / `wifi-densepose` repo. Mirrors the Claude Code `ruview` plugin.

## What this repo is

WiFi-based human sensing from Channel State Information (CSI). Dual codebase: Rust port in `v2/` (15 crates), Python v1 in `archive/v1/`. ESP32-S3 / ESP32-C6 firmware in `firmware/esp32-csi-node/`. 96 ADRs in `docs/adr/`.

## Hard rules

- Do exactly what's asked — nothing more, nothing less.
- Never create files (especially `*.md`/README) unless required for the task. Prefer editing an existing file.
- Never save working files/tests/notes to the repo root — use `v2/crates/`, `tests/`, `docs/`, `scripts/`, `examples/`.
- Read a file before editing it.
- Never commit secrets, credentials, or `.env`.
- Validate user input at system boundaries; sanitize file paths.
- ESP32-C3 and the original ESP32 are **not supported** (single-core). Use ESP32-S3 (8MB/4MB) or ESP32-C6.

## Build & test

```bash
# Rust workspace (1,400+ tests, ~2 min)
cd v2 && cargo test --workspace --no-default-features
# Single crate, no GPU
cargo check -p wifi-densepose-train --no-default-features
# Deterministic Python pipeline proof (SHA-256 Trust Kill Switch)
python archive/v1/data/proof/verify.py     # must print VERDICT: PASS
# Python v1 tests
cd archive/v1 && python -m pytest tests/ -x -q
```

## ESP32 firmware (Windows)

ESP-IDF v5.4 does **not** work under Git Bash/MSYS2 and `cmd.exe /C` hangs when called from bash. Build/flash via the **Espressif Python venv as a subprocess with `MSYSTEM*` env vars stripped** — the exact command is in `CLAUDE.local.md`. Default ESP32 serial port: **COM8** (confirm with `mode` / Device Manager — older docs say COM7 or COM9). Provision WiFi: `python firmware/esp32-csi-node/provision.py --port COM8 --ssid ... --password ... --target-ip ... [--channel N] [--filter-mac MAC]`. Serial monitor via pyserial, not `idf.py monitor`. Always test with real WiFi CSI, never mock mode.

## Witness verification (ADR-028)

After significant changes: run the Rust tests + Python proof, then `bash scripts/generate-witness-bundle.sh`, then `cd dist/witness-bundle-ADR028-*/ && bash VERIFY.sh` (7/7 PASS). Pre-merge checklist lives in `CLAUDE.md`.

## Prompt files in `codex/prompts/`

| Prompt | Purpose |
|--------|---------|
| `ruview-start` | Onboarding — Docker demo / repo build / live ESP32 |
| `ruview-flash` | Build + flash ESP32 firmware (8MB / 4MB) |
| `ruview-provision` | Provision WiFi creds + sink IP + channel/MAC overrides |
| `ruview-app` | Run a sensing application (presence / vitals / pose / sleep / MAT / point cloud) |
| `ruview-train` | Train / evaluate / publish a model (incl. GPU on GCloud) |
| `ruview-verify` | Run the trust pipeline + pre-merge checklist |

Install: copy `codex/prompts/*.md` into `~/.codex/prompts/`, or run Codex with this directory on its prompt path.

## Reference

`README.md`, `docs/user-guide.md`, `docs/wifi-mat-user-guide.md`, `docs/build-guide.md`, `docs/TROUBLESHOOTING.md`, `docs/adr/`, `docs/tutorials/`, `examples/`, `CLAUDE.md`, `CLAUDE.local.md`.
