---
name: himalaya
description: "Operates IMAP/SMTP mailboxes from the terminal with the Himalaya CLI (list, search, compose, reply, flags, attachments, JSON). Use when reading or sending mail non-interactively via himalaya. Not for Resend/React Email app integration (email) and not a Hermes inbound email gateway."
version: 1.1.1
author: community
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Email, IMAP, SMTP, CLI, Communication]
    homepage: https://github.com/pimalaya/himalaya
prerequisites:
  commands: [himalaya]
---

# Himalaya Email CLI

Himalaya is a CLI email client that manages email from the terminal using IMAP, SMTP, Notmuch, or Sendmail backends. This skill is separate from any Hermes Email gateway adapter — it operates a mailbox directly through the external `himalaya` CLI.

## When to Use

- You need to **read, list, search, move, copy, or delete** emails from a terminal session.
- You need to **compose, reply to, or forward** emails non-interactively via piped stdin.
- You need to **download attachments** or **manage message flags** (seen, flagged, etc.).
- You need **structured JSON output** from an email client for programmatic parsing.
- Trigger keywords: email, mail, IMAP, SMTP, inbox, send, reply, forward, attachment, folder, himalaya.

## Prerequisites

1. Himalaya CLI installed — verify with `himalaya --version`.
2. A configuration file at `~/.config/himalaya/config.toml` (Windows: `%USERPROFILE%\.config\himalaya\config.toml`).
3. IMAP/SMTP credentials configured (password stored securely via `pass`, system keyring, or a command that outputs the password).

### Installation

```powershell
# Windows (PowerShell) — via cargo (requires Rust toolchain)
cargo install himalaya --locked

# Or download pre-built binary from GitHub releases
# https://github.com/pimalaya/himalaya/releases
```

```bash
# Linux/macOS — pre-built binary (recommended)
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh

# macOS via Homebrew
brew install himalaya

# Or via cargo (any platform with Rust)
cargo install himalaya --locked
```

## Procedure

### 1. Configuration Setup

Run the interactive wizard (requires PTY mode in agent environments):

```bash
himalaya account configure
```

Or create `~/.config/himalaya/config.toml` manually:

```toml
[accounts.personal]
email = "you@example.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@example.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show email/imap"  # or use keyring

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show email/smtp"

# Folder aliases (himalaya v1.2.0+ syntax). Required whenever the
# server's folder names don't match himalaya's canonical names
# (inbox/sent/drafts/trash). Gmail is the common case — see
# `references/configuration.md` for the `[Gmail]/Sent Mail` mapping.
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "Sent"
folder.aliases.drafts = "Drafts"
folder.aliases.trash = "Trash"
```

> **Load `references/configuration.md`** when setting up a new account, troubleshooting authentication, or configuring folder aliases for non-standard providers (Gmail, Fastmail, etc.).

### 2. List Folders

```bash
himalaya folder list
```

### 3. List Emails

```bash
# List emails in INBOX (default)
himalaya envelope list

# List emails in a specific folder
himalaya envelope list --folder "Sent"

# List with pagination
himalaya envelope list --page 1 --page-size 20
```

### 4. Search Emails

```bash
himalaya envelope list from john@example.com subject meeting
```

### 5. Read an Email

```bash
# Read email by ID (shows plain text)
himalaya message read 42

# Export raw MIME
himalaya message export 42 --full
```

### 6. Compose a New Email (Non-Interactive)

**Always pipe via stdin from agent environments** — this is the reliable path:

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: Test Message

Hello from Himalaya!
EOF
```

Alternative with headers flag:

```bash
himalaya message write -H "To:recipient@example.com" -H "Subject:Test" "Message body here"
```

> **Load `references/message-composition.md`** when composing rich emails with attachments, multipart MIME, or advanced MML syntax.

### 7. Reply to an Email

```bash
# Get the reply template, edit it, and send
himalaya template reply 42 | sed 's/^$/\nYour reply text here\n/' | himalaya template send
```

Or build the reply manually with proper headers:

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: sender@example.com
Subject: Re: Original Subject
In-Reply-To: <original-message-id>

Your reply here.
EOF
```

Reply-all (interactive — needs `$EDITOR`, use template approach above instead for agent use):

```bash
himalaya message reply 42 --all
```

### 8. Forward an Email

```bash
# Get forward template and pipe with modifications
himalaya template forward 42 | sed 's/^To:.*/To: newrecipient@example.com/' | himalaya template send
```

### 9. Move/Copy Emails

```bash
# Move to folder (target folder comes first, then the message ID)
himalaya message move "Archive" 42

# Copy to folder (target folder comes first, then the message ID)
himalaya message copy "Important" 42
```

### 10. Delete an Email

```bash
himalaya message delete 42
```

### 11. Manage Flags

```bash
# Add flag
himalaya flag add 42 --flag seen

# Remove flag
himalaya flag remove 42 --flag seen
```

### 12. Attachments

```bash
# Save attachments from a message
himalaya attachment download 42

# Save to specific directory
himalaya attachment download 42 --downloads-dir ~/Downloads
```

### 13. Multiple Accounts

```bash
# List accounts
himalaya account list

# Use a specific account
himalaya --account work envelope list
```

### 14. Structured Output

Most commands support `--output` for structured output — use `json` for programmatic parsing:

```bash
himalaya envelope list --output json
himalaya envelope list --output plain
```

### 15. Debugging

```bash
# Enable debug logging
RUST_LOG=debug himalaya envelope list

# Full trace with backtrace
RUST_LOG=trace RUST_BACKTRACE=1 himalaya envelope list
```

## Pitfalls

### HARD RULE: Folder Alias Syntax (v1.2.0+)

Pre-v1.2.0 docs used a `[accounts.NAME.folder.alias]` sub-section (singular `alias`). **v1.2.0 silently ignores that form** — TOML parses fine, but the alias resolver never reads it, so every lookup falls through to the canonical name.

On Gmail this means save-to-Sent fails **after** SMTP delivery succeeds, and `himalaya message send` exits non-zero. Any caller (agent, script, user) that retries on that exit code will re-run the entire send — including SMTP — producing **duplicate emails to recipients**.

**Always use `folder.aliases.X`** (plural, dotted keys, directly under `[accounts.NAME]`):

```toml
# CORRECT — v1.2.0+
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "Sent"

# WRONG — silently ignored in v1.2.0+
# [accounts.personal.folder.alias]
# inbox = "INBOX"
```

### Interactive Editor Mode

`himalaya message write` and `himalaya message reply` without piped input open `$EDITOR`. This works with `pty=true` + background + process tool, but **piping via stdin is simpler and more reliable** in agent environments. Always prefer `cat << 'EOF' | himalaya template send` over interactive editor mode.

### Message IDs Are Folder-Relative

Message IDs are relative to the current folder. Always re-list envelopes after folder changes before operating on a message by ID.

### `himalaya account configure` Requires Interactive Input

The wizard requires interactive input — use PTY mode: `terminal(command="himalaya account configure", pty=true)`. In non-interactive agent environments, create `config.toml` manually instead.

### Password Storage

Never hardcode passwords in `config.toml`. Use `pass`, system keyring, or a command that outputs the password via `backend.auth.cmd`.

## Verification

1. **Verify installation:**
   ```bash
   himalaya --version
   ```
   Expected output: `himalaya 1.x.x`

2. **Verify configuration is loaded:**
   ```bash
   himalaya account list
   ```
   Expected: lists configured accounts with the default account marked.

3. **Verify IMAP connectivity:**
   ```bash
   himalaya envelope list --page 1 --page-size 5
   ```
   Expected: shows up to 5 envelopes from INBOX.

4. **Verify SMTP by sending a test to yourself:**
   ```bash
   cat << 'EOF' | himalaya template send
   From: you@example.com
   To: you@example.com
   Subject: Himalaya Test

   This is a test message from Himalaya CLI.
   EOF
   ```
   Expected: command exits 0, message appears in INBOX.

5. **Verify folder aliases (critical for Gmail):**
   ```bash
   himalaya folder list --output json
   ```
   Confirm that aliased folders resolve correctly. Then send a test email and verify it appears in the Sent folder — if `himalaya message send` exits non-zero after successful SMTP delivery, your alias syntax is wrong (see Pitfalls).

## Related Skills

- **Hermes Email Gateway Adapter** — for receiving emails addressed to the agent via Hermes' built-in IMAP/SMTP adapter (separate from this CLI skill).
