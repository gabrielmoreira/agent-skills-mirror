---
description: How to build OpenHuman from source - toolchain, submodules, Tauri CLI, and local desktop builds.
icon: wrench
---

# Building & Installing OpenHuman

This guide covers the full desktop/source install path and release installers.

If you only need the Rust workspace under `crates/` on a fresh machine, use [Building the Rust Core](building-rust-core.md). That page documents the pinned Rust toolchain, OS package prerequisites, and the exact `cargo` commands for `openhuman-core`.

This guide covers two paths:

1. Build and compile OpenHuman from source
2. Install the latest stable release binaries

## Prerequisites

- `git`
- Node.js 24 or newer (see `app/package.json`)
- `pnpm@10.10.0` (see the root `package.json` `packageManager` field)
- Rust 1.96.1 through `rustup` with `rustfmt` and `clippy` (see `rust-toolchain.toml`)
- CMake, required by native Rust dependencies
- Git submodules under `vendor/` (`git submodule update --init --recursive`), required by both the core and the desktop shell
- Platform desktop build tools: Xcode Command Line Tools on macOS, or the Tauri GTK/WebKit/AppIndicator package set on Linux

macOS Homebrew quick start:

```bash
brew install node@24 pnpm rustup-init cmake
rustup toolchain install 1.96.1 --profile minimal
rustup component add rustfmt clippy --toolchain 1.96.1
```

Arch Linux quick start:

```bash
sudo pacman -S --needed nodejs npm rustup cmake base-devel clang openssl \
  alsa-lib xdotool libxtst libxi libevdev gtk3 webkit2gtk-4.1 \
  libayatana-appindicator librsvg patchelf nss nspr at-spi2-core \
  libcups libdrm libxkbcommon libxcomposite libxdamage libxfixes \
  libxrandr mesa pango cairo libxshmfence
npm install -g pnpm@10.10.0
rustup toolchain install 1.96.1 --profile minimal
rustup component add rustfmt clippy --toolchain 1.96.1
```

## Build from source (local compile)

Run from the repository root:

```bash
# 1) Clone and enter the repo
git clone https://github.com/tinyhumansai/openhuman.git
cd openhuman

# 2) Fetch the vendored tiny* crate submodules
git submodule update --init --recursive

# 3) Install JS deps (workspace)
pnpm install

# 4) Build desktop app artifacts
pnpm build
```

For local development instead of production build:

```bash
# Web-only UI development
pnpm dev

# Desktop app development: runs scripts/run-dev-macos.sh (`cargo tauri dev` with a dev config override)
pnpm dev:app

# Other Tauri CLI commands (from app/node_modules) run against crates/openhuman-app/
pnpm tauri build
```

## Install latest stable release (macOS/Linux x64)

Primary install command:

```bash
curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash
```

Installer behavior:

- Resolves latest stable OpenHuman release for your platform
- Validates artifact digest when available
- Installs locally (no sudo by default)
- macOS: installs `OpenHuman.app` into `~/Applications`
- Linux x64: installs AppImage as `~/.local/bin/openhuman` and writes a desktop entry

### Arch Linux package recipe

The repository includes an `openhuman-bin` AUR recipe at
[`packages/arch/openhuman-bin`](../../packages/arch/openhuman-bin/). It uses the
official x86_64 AppImage as the binary source, extracts the bundled application
tree during `makepkg`, installs a desktop entry, and exposes `/usr/bin/openhuman`.

Until the package is published on AUR, build it locally on Arch:

```bash
cd packages/arch/openhuman-bin
makepkg --syncdeps --install
```

After publication, Arch users can install it with:

```bash
yay -S openhuman-bin
```

Useful flags:

```bash
# Preview actions without writing files
curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash -s -- --dry-run
```

## Windows (latest stable)

Use PowerShell:

```powershell
irm https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.ps1 | iex
```

Windows installer behavior:

- Resolves latest stable release
- Downloads MSI/EXE for x64
- Verifies digest when available
- Runs per-user install where supported by installer package

## ARM Linux Build (aarch64)

CI builds the `aarch64-unknown-linux-gnu` target on an `ubuntu-24.04-arm` runner
with the same Tauri command as x64 (see
[`.github/workflows/build-desktop.yml`](../../.github/workflows/build-desktop.yml)).
Locally, with the Linux desktop package set installed:

```bash
pnpm tauri build --target aarch64-unknown-linux-gnu --bundles deb appimage
```

The shell is stock Tauri on Wry, so the resulting binary needs no extra
library path. Install the `.deb` bundle with `dpkg -i`.

Manual download links (all platforms):

- Website: https://tinyhuman.ai/openhuman
- Latest release: https://github.com/tinyhumansai/openhuman/releases/latest

## Troubleshooting

### Stale `openhuman` RPC process on the core port

**Symptom**

A previous Tauri build or `openhuman-core run` harness left a process listening on `OPENHUMAN_CORE_PORT` (default `7788`). Until issue #1130 the new Tauri build would silently attach to that listener, leading to version drift and 401s when the new build's `OPENHUMAN_CORE_TOKEN` didn't match.

**Current behavior (issue #1130)**

`core_process::ensure_running` now probes the port at startup:

- If `GET /` identifies the listener as an OpenHuman core (JSON body with `"name": "openhuman"`), it is treated as a stale process from a previous run and proactively terminated (`SIGTERM`, then `SIGKILL` after 750ms on Unix; `taskkill /F /T /PID` on Windows). The Tauri host then spawns its own fresh embedded core.
- If the listener is something else (or doesn't speak HTTP), startup fails loudly with the conflict surfaced in the log instead of silently attaching.
- Set `OPENHUMAN_CORE_REUSE_EXISTING=1` to opt back into the legacy attach-to-anything behavior, useful when running `openhuman-core run` as a manual debugging harness.

**Manual cleanup (still works)**

```bash
pkill -f "OpenHuman.app/Contents"
pkill -f "openhuman-core"
```
