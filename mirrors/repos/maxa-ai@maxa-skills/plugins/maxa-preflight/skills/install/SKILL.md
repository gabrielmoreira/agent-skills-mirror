---
name: install
description: >
  Install the autopilot-preflight binary from GitHub Releases. Use when the
  user says "install preflight", "set up autopilot-preflight", "get the
  preflight binary", "I need autopilot-preflight", or when another
  maxa-preflight skill fails because the binary is not found on PATH.
---

# Install Autopilot Preflight

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, RECOMMENDED, and MAY in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Installs the `autopilot-preflight` binary from GitHub Releases onto the user's machine. Single native binary, no runtime dependencies.

## Pre-check

Before doing anything, check whether it's already installed:

```
autopilot-preflight --version
```

If that succeeds, tell the user the installed version and stop — nothing to do. Only proceed if the command is not found.

## Constraints

- MUST NOT clone, fork, or build from source. Installation is binary-only from GitHub Releases.
- MUST verify the SHA-256 checksum before installing. Never skip this step.
- MUST NOT ask the user for their OS or architecture — detect it automatically.
- MUST clear macOS quarantine on Darwin (`xattr -d com.apple.quarantine`). MUST NOT run this on Linux.
- If `~/.local/bin` is not on PATH, warn the user and provide the exact export line for their shell.

## Procedure

### 1. Detect platform

Map the local OS and architecture to the release artifact name:

| `uname -s` | `uname -m` | Artifact suffix |
|---|---|---|
| Darwin | arm64 | `darwin-arm64` |
| Darwin | x86_64 | `darwin-amd64` |
| Linux | x86_64 | `linux-amd64` |
| Linux | aarch64 | `linux-arm64` |
| MINGW* / MSYS* / Windows | x86_64 | `windows-amd64.exe` |

If the platform doesn't match any row, tell the user their platform is not supported and stop.

### 2. Discover the latest release and asset names

Release artifact filenames include the version number (e.g., `autopilot-preflight-0.3.0-darwin-arm64`), so the exact filename is not known in advance. MUST list the release assets first, then match the correct one by platform suffix.

**Step 2a — list assets:**

```bash
gh release view --repo maxa-ai/maxa-autopilot-preflight --json tagName,assets --jq '.assets[].name'
```

**Step 2b — identify the two files to download:** From the asset list, find the one whose name ends with the platform suffix from step 1 (e.g., `darwin-arm64`), and its `.sha256` companion. These are the only two files needed.

### 3. Download

```bash
mkdir -p /tmp/preflight-install
gh release download --repo maxa-ai/maxa-autopilot-preflight \
  --pattern "EXACT_BINARY_NAME" \
  --pattern "EXACT_BINARY_NAME.sha256" \
  --dir /tmp/preflight-install
```

Replace `EXACT_BINARY_NAME` with the actual asset name found in step 2b (e.g., `autopilot-preflight-0.3.0-darwin-arm64`).

**If `gh` is not available**, fall back to `curl` against the GitHub Releases API:

```bash
# Fetch latest release tag
LATEST=$(curl -sL https://api.github.com/repos/maxa-ai/maxa-autopilot-preflight/releases/latest | grep '"tag_name"' | head -1 | sed 's/.*"tag_name": *"//;s/".*//')

mkdir -p /tmp/preflight-install

# Download binary (replace EXACT_BINARY_NAME)
curl -fSL "https://github.com/maxa-ai/maxa-autopilot-preflight/releases/download/${LATEST}/EXACT_BINARY_NAME" \
  -o /tmp/preflight-install/EXACT_BINARY_NAME

# Download checksum
curl -fSL "https://github.com/maxa-ai/maxa-autopilot-preflight/releases/download/${LATEST}/EXACT_BINARY_NAME.sha256" \
  -o /tmp/preflight-install/EXACT_BINARY_NAME.sha256
```

If the repository is private and the user is not authenticated with `gh`, tell them to run `gh auth login` first — do not attempt to work around auth.

### 4. Verify checksum

```bash
cd /tmp/preflight-install && shasum -a 256 -c EXACT_BINARY_NAME.sha256
```

If verification fails, abort and tell the user the download may be corrupted.

### 5. Install

```bash
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"
mkdir -p "$INSTALL_DIR"
cp /tmp/preflight-install/EXACT_BINARY_NAME "$INSTALL_DIR/autopilot-preflight"
chmod +x "$INSTALL_DIR/autopilot-preflight"
```

On macOS only, also clear quarantine:

```bash
xattr -d com.apple.quarantine "$INSTALL_DIR/autopilot-preflight" 2>/dev/null || true
```

MUST NOT run `xattr` on Linux — the command does not exist there.

### 6. Verify installation

```bash
autopilot-preflight --version
```

If this fails because `~/.local/bin` is not on PATH, tell the user which line to add to their shell config:

```
export PATH="$HOME/.local/bin:$PATH"
```

Name the correct rc file based on their shell (`~/.zshrc`, `~/.bashrc`, `~/.profile`).

### 7. Clean up

```bash
rm -rf /tmp/preflight-install
```

## After installation

Mention that the user can run `autopilot-preflight --help` to see available commands, and that the `guide` skill in this plugin explains when and how to use each one.
