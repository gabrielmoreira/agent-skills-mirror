---
name: shell-wsl
description: Shell script bugs, WSL quirks, upgrade scripts, embedded device deployment, and Rust/Cargo
---

When working on projects related to shell scripting and wsl patterns, apply this domain knowledge.

# Shell Scripting & WSL — Domain Knowledge

## Shell Script Bug Patterns

### exit vs return
- `return` only works in **sourced** scripts or functions.
- When a script is **executed** (`./script.sh` or `bash script.sh`), `return` is invalid.
- Use `exit 1` for executable scripts, `return 1` inside functions.
- `return -1` is technically undefined behavior — use `exit 1` or `return 1`.

### Variable Quoting (CRITICAL)
- Always quote variables: `"$var"`, `"$@"`, `"$file"`.
- Unquoted variables cause word splitting on spaces/newlines.
- `$@` → `"$@"` — preserves argument boundaries.
- `rm /path/$var/*` → `rm "/path/$var/"*` — prevents glob expansion of empty var.

### Directory Safety
- Always `mkdir -p` before writing to directories that may not exist.
- `rm dir/*` fails if directory is empty — use `rm -f dir/* 2>/dev/null || true`
  or check first: `[ -d dir ] && find dir -type f -delete`.

### Error Handling
- `set -euo pipefail` at the top of scripts:
  - `-e`: exit on error
  - `-u`: treat unset variables as errors
  - `-o pipefail`: pipe fails if any command fails (not just the last)
- Chain with `&&` when you want dependent commands to stop on failure.

## Upgrade / Update Script Patterns

### git_pull_and_build Helper
```bash
git_pull_and_build() {
    local repo_dir="$1"; shift
    local old_head new_head
    cd "$repo_dir"
    old_head=$(git rev-parse HEAD)
    git pull --ff-only
    new_head=$(git rev-parse HEAD)
    if [ "$old_head" = "$new_head" ]; then
        echo "No changes, skipping rebuild"
        return 0
    fi
    "$@"  # Run build commands passed as remaining args
}
```
- Only rebuilds when `git pull` brings new commits.
- Build commands passed as trailing arguments for flexibility.

### Dependency Ordering
- Build in dependency order: e.g., ncurses → tmux, nano (both depend on ncurses).
- Each section is independent — failures propagate via `set -e`.

### Package Manager Detection
```bash
# Only run if the command exists
command -v snap >/dev/null 2>&1 && snap refresh
command -v npm  >/dev/null 2>&1 && sudo npm update -g
command -v pip3 >/dev/null 2>&1 && pip3 install --user --upgrade <packages>
command -v rustup >/dev/null 2>&1 && rustup update
command -v cargo >/dev/null 2>&1 && cargo install-update --all
```
- Guard each section with `command -v` — silently skipped if not installed.
- `npm update -g` needs `sudo` when global prefix is root-owned (`/usr/local`).

### Quieting Verbose Output (keep errors + status lines)
- Prefer **`apt-get -qq`** over `apt` in scripts — `apt-get` is the stable scripting
  interface and avoids the `WARNING: apt does not have a stable CLI` message; `-qq` silences
  progress while still printing errors to stderr.
- `snap refresh >/dev/null` (and similar) to drop chatty stdout; **don't** redirect stderr —
  you want failures to surface.
- Keep the script's *own* headers/status `echo`s; only suppress the noisy stdout of the tools
  it calls, so a run still reads as a clear progress log.

### Systemd Detection
```bash
# Check for systemd (important for WSL where it may not be PID 1)
if [ -d /run/systemd/system ]; then
    sudo fwupdmgr refresh && sudo fwupdmgr update
fi
```
- `fwupdmgr` needs `sudo` to bypass polkit (unavailable without systemd).
- Snap requires systemd — won't function in WSL without it.

## WSL-Specific Quirks

### Systemd in WSL
- By default, WSL2 does NOT run systemd as PID 1.
- To enable: add to `/etc/wsl.conf`:
  ```ini
  [boot]
  systemd=true
  ```
- Then restart: `wsl --shutdown` from PowerShell.
- Without systemd: snap, polkit, fwupd, and other systemd-dependent tools fail.

### Terminal / Progress Indicators
- `TERM=xterm-color` is too limited — causes Copilot CLI to skip progress indicators.
- Fix: set `TERM=xterm-256color` in tmux config:
  ```
  set -g default-terminal "xterm-256color"
  ```
- Then restart tmux (`tmux kill-server`).

### APT Troubleshooting
- **Broken repo files**: Check `/etc/apt/sources.list.d/` for wrong URLs
  (e.g., Edge repo pointing at Chrome URL).
- **Legacy keyrings**: `/etc/apt/trusted.gpg` is deprecated — migrate keys to
  `/etc/apt/trusted.gpg.d/` as individual `.gpg` files.
- **Stale local repos**: Check `/var/cuda-repo-*` and similar — can waste gigabytes.
  Remove the `.list` file and the local repo directory.
- `apt-key` is deprecated — use `signed-by=` in repo definitions.

### Cross-Compilation from WSL
- Rsync sources to WSL native filesystem for better build performance
  (avoid Windows filesystem overhead via `/mnt/c/`).
- Visual Studio remote development presets work with WSL via CMake vendor settings.

## Embedded Device Shell Patterns (mFi/OpenWrt)

### Symlink-Based Config
- DRY principle: shared files (profile, rc.poststart, mqtt.ini) aren't duplicated.
- Device directories contain only symlinks to shared files + device-specific configs.
- `add.sh` bootstraps a new device directory with appropriate symlinks.

### Deployment Pipeline
```bash
# 1. Archive device config
tar czf /tmp/config.tar.gz -C device_dir .
# 2. SCP to device
scp /tmp/config.tar.gz ubnt@device.local:/tmp/
# 3. SSH: stop, deploy, commit, restart
ssh ubnt@device.local 'cd /var/etc/persistent && \\
    /usr/bin/mfi-mqtt-client stop && \\
    tar xzf /tmp/config.tar.gz -C bin/ && \\
    cfgmtd -w -p /etc/ && \\
    /var/etc/persistent/rc.poststart'
```

### One-Connection Deploy (stream tar over SSH)
Collapse the separate `scp` + `ssh` into a **single** SSH connection by piping tar through it —
fewer auth round-trips, no temp file on the device:
```bash
tar -chf - -C "./$host/" ./ | ssh "ubnt@$host.local" \
    'tar -xf - -C /var/etc/persistent/ && \
     pkill -9 mfi-mqtt-client; \
     cfgmtd -w -p /etc/ && /var/etc/persistent/rc.poststart'
```
- `-c` = create, `-h` = **follow symlinks** (dereference the symlinked config into real files),
  `-f -` = write archive to stdout; the remote `tar -xf -` reads it from stdin.
- Everything after the extract runs in the *same* remote shell, so stop/clean/commit/restart
  need no extra connection.

### Version-Aware Updater (compare against GitHub, no marker file)
- Rather than tracking installed version in a marker file, ask the installed tool
  (`mytool --version` → `mytool 1.2.0`) and compare against the latest GitHub release tag.
- Only download when the remote tag is newer. Handle the `<tool> <version>` output and a
  `v`-prefixed tag with the same portable semver parse/compare.
- A portable shell semver comparator (no `sort -V` dependency assumed):
  ```bash
  ver_lt() { # returns 0 if $1 < $2
      [ "$1" = "$2" ] && return 1
      [ "$(printf '%s\n%s\n' "$1" "$2" | sort -t. -k1,1n -k2,2n -k3,3n | head -1)" = "$1" ]
  }
  ```

### Startup System
- `rc.poststart` runs all executable scripts in `rc.poststart.d/` in parallel (`&`).
- Modular: add new services by dropping scripts into the directory.
- Non-executable files are skipped.

## Rust/Cargo Patterns (from WSL-Hello-sudo)
- `clippy -- -D warnings` treats all warnings as errors (strict linting).
- `Cow<str>` → `Cow<'_, str>` — always make elided lifetimes explicit.
- `#[allow(dead_code)]` on enum variant fields that are matched structurally
  but never read directly.
- `Some(code) if code == 0` → `Some(0)` — simplify redundant guards.
- `bindgen` for C FFI bindings generation.

### Cargo.lock Reproducibility (CRITICAL for binaries)
- **Commit `Cargo.lock` for binaries/applications** (not for libraries). An unpinned
  lockfile means every build re-resolves dependencies and picks the newest patch versions,
  causing builds that "used to work" to break when a transitive dependency publishes an
  incompatible patch.
- Example failure: `actix-web 4.13 → cookie 0.16.2` breaks when `time >= 0.3.50` is resolved
  (`Parsable::parse` signature changed), while `simple_logger` requires `time >= 0.3.49` —
  only `time = 0.3.49` satisfied both. A fresh resolve picked 0.3.52 and broke the build.
- **Fixes** (in order of preference):
  1. Commit `Cargo.lock` pinned to a working set (`cargo generate-lockfile` +
     `cargo update -p <crate> --precise <version>`). Remove it from `.gitignore`.
  2. Constrain in `Cargo.toml`: `time = "=0.3.49"` (works without a committed lock).
  3. Drop unused features pulling the problematic crate:
     `actix-web = { default-features = false, features = [...] }` to exclude `cookies`.
- **Docker gotcha**: ensure the Dockerfile `COPY`s the real `Cargo.lock` before
  `cargo build`, otherwise the pin doesn't apply in-image.
- Diagnose transitive deps with `cargo tree -i <crate>`.
