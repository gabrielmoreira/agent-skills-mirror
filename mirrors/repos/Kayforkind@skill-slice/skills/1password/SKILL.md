---
name: 1password
description: "Drives 1Password CLI (op) for service-account, desktop-app, or Connect auth, then op read, op inject, and op run so secrets stay out of plaintext env files. Use when installing op, signing in, resolving op:// references, injecting templates, or wrapping commands with secret env vars. Not for inventing vault items or password-reset UX; never print raw secrets unless the user explicitly asks."
version: 1.0.1
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [security, secrets, 1password, op, cli]
    category: security
setup:
  help: "Create a service account at https://my.1password.com → Settings → Service Accounts"
  collect_secrets:
    - env_var: OP_SERVICE_ACCOUNT_TOKEN
      prompt: "1Password Service Account Token"
      provider_url: "https://developer.1password.com/docs/service-accounts/"
      secret: true
---

# 1Password CLI

Use this skill when the user wants secrets managed through 1Password instead of plaintext env vars or files. The primary host platform is Windows (PowerShell); Linux/macOS commands are provided where they differ.

## When to Use

- Install or configure the 1Password CLI (`op`)
- Sign in with `op signin` (desktop app integration)
- Read secret references like `op://Vault/Item/field`
- Inject secrets into config/templates using `op inject`
- Run commands with secret env vars via `op run`
- Set up headless/CI authentication using a service account token

## Prerequisites

- A 1Password account (personal, family, or business)
- 1Password CLI (`op`) installed — see Procedure below
- One of the following authentication methods:
  - **Service Account token** (`OP_SERVICE_ACCOUNT_TOKEN`) — recommended for automation/CI
  - **Desktop App Integration** — interactive, requires the 1Password desktop app unlocked
  - **Connect Server** — self-hosted, for shared/team automation
- `tmux` available for stable authenticated sessions during non-interactive terminal calls (desktop app flow only; not needed for service account token)

## Procedure

### 1. Install the CLI

```powershell
# Windows (winget) — primary
winget install AgileBits.1Password.CLI
```

```bash
# macOS
brew install 1password-cli

# Linux — see references/get-started.md for distro-specific package links
# Load references/get-started.md when the user needs Linux install details or distro-specific URLs.
```

### 2. Verify installation

```powershell
op --version
```

### 3. Choose and configure an authentication method

#### Option A — Service Account (recommended for automation / Hermes)

Set `OP_SERVICE_ACCOUNT_TOKEN` in your environment. On Windows PowerShell:

```powershell
$env:OP_SERVICE_ACCOUNT_TOKEN = "YOUR_TOKEN_HERE"
```

For persistent storage, add it to your shell profile or a `.env` file loaded by your agent framework. The skill will prompt for this token on first load if missing.

No desktop app is needed. Supports `op read`, `op inject`, `op run`.

```powershell
op whoami  # verify — should show Type: SERVICE_ACCOUNT
```

> **Service accounts require CLI v2.18.0 or later.**

#### Option B — Desktop App Integration (interactive)

1. Open the 1Password desktop app.
2. Go to **Settings → Developer → Integrate with 1Password CLI** and enable it.
3. Ensure the app is unlocked.
4. Run `op signin` and approve the biometric/prompt in the desktop app.

```powershell
op signin --account my.1password.com
```

#### Option C — Connect Server (self-hosted)

```powershell
$env:OP_CONNECT_HOST = "http://localhost:8080"
$env:OP_CONNECT_TOKEN = "YOUR_CONNECT_TOKEN"
```

### 4. Running `op` in non-interactive terminal sessions (desktop app flow)

Non-interactive terminal commands can lose auth context between calls. For reliable `op` use with desktop app integration, run sign-in and secret operations inside a dedicated tmux session.

> **This is NOT needed when using `OP_SERVICE_ACCOUNT_TOKEN`** — the token persists across terminal calls automatically.

```bash
SOCKET_DIR="${TMPDIR:-/tmp}/hermes-tmux-sockets"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/hermes-op.sock"
SESSION="op-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell

# Sign in (approve in desktop app when prompted)
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "eval \"\$(op signin --account my.1password.com)\"" Enter

# Verify auth
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op whoami" Enter

# Example read
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op read 'op://Private/Npmjs/one-time password?attribute=otp'" Enter

# Capture output when needed
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200

# Cleanup
tmux -S "$SOCKET" kill-session -t "$SESSION"
```

### 5. Common operations

#### Read a secret

```powershell
op read "op://app-prod/db/password"
```

#### Get an OTP

```powershell
op read "op://app-prod/npm/one-time password?attribute=otp"
```

#### Inject secrets into a template

```powershell
echo "db_password: {{ op://app-prod/db/password }}" | op inject
```

#### Run a command with a secret env var

```powershell
$env:DB_PASSWORD = "op://app-prod/db/password"
op run -- pwsh -c 'if ($env:DB_PASSWORD) { Write-Output "DB_PASSWORD is set" } else { Write-Output "DB_PASSWORD missing" }'
```

```bash
# Bash equivalent
export DB_PASSWORD="op://app-prod/db/password"
op run -- sh -c '[ -n "$DB_PASSWORD" ] && echo "DB_PASSWORD is set" || echo "DB_PASSWORD missing"'
```

> **Load `references/cli-examples.md`** when the user needs more advanced `op` command examples (bulk inject, document operations, item creation, etc.).

## Pitfalls

- **Never print raw secrets back to the user** unless they explicitly request the value. Prefer `op run` / `op inject` so secrets stay in env/process memory only.
- **"account is not signed in" error (desktop app flow):** Run `op signin` again in the same tmux session. Auth context does not persist across separate terminal calls without a persistent session.
- **Desktop app integration unavailable (headless/CI):** Use the service account token flow instead. Interactive `op signin` will hang or fail.
- **Service account CLI version:** Service accounts require CLI v2.18.0+. Run `op --version` to confirm.
- **Secret reference syntax:** Field names with spaces must be included as-is inside the `op://` URI, e.g. `op://Vault/Item/one-time password?attribute=otp`.
- **Writing secrets to files:** Avoid writing secrets into config files. Use `op inject` with a template, or `op run` to pass secrets as env vars to the consuming process.
- **Windows PowerShell quoting:** Use double quotes for `op://` URIs in PowerShell. Single quotes prevent variable expansion but are fine for literal secret references.

## Verification

1. Confirm the CLI is installed and at a supported version:

```powershell
op --version
# Expected: 2.18.0 or higher (required for service accounts)
```

2. Confirm authentication is active:

```powershell
op whoami
# Service account → Type: SERVICE_ACCOUNT
# Desktop app  → Type: INDIVIDUAL / BUSINESS with your account details
# Connect      → Type: CONNECT
```

3. Confirm a secret can be read (replace with a real reference):

```powershell
op read "op://Private/Test/username"
# Expected: the stored value, printed to stdout
```

4. Confirm `op run` injects env vars correctly:

```powershell
$env:TEST_SECRET = "op://Private/Test/username"
op run -- pwsh -c 'Write-Output "Secret length: $($env:TEST_SECRET.Length)"'
# Expected: Secret length: <non-zero number>
```

## References

- `references/get-started.md` — load when the user needs Linux distro-specific install instructions or package manager details.
- `references/cli-examples.md` — load when the user needs advanced `op` command examples beyond read/inject/run.
- https://developer.1password.com/docs/cli/
- https://developer.1password.com/docs/service-accounts/
