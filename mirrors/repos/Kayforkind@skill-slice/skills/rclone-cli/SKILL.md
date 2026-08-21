---
name: rclone-cli
description: "Runs rclone for cloud file ops across 70+ remotes: copy/sync/move, mount, bisync, encrypted backups, server-side copy, and S3-compatible config. Use when the user mentions rclone or terminal cloud transfer, mount, or remote management. Not for vendor web consoles or treating rclone.conf as shareable; never log rclone config show with redaction disabled."
version: 1.0.1
risk: unknown
source: https://github.com/chaunsin/agent-skills/tree/master/skills/rclone-cli
source_repo: chaunsin/agent-skills
source_type: community
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/chaunsin/agent-skills/blob/master/LICENSE
---

# rclone — The Swiss Army Knife of Cloud Storage

Rclone is a command-line program to manage files on cloud storage. It is a feature-rich alternative to cloud vendors' web storage interfaces. Over 70 cloud storage products support rclone including S3 object stores, business & consumer file storage services, and standard transfer protocols.

Rclone has powerful cloud equivalents to the unix commands rsync, cp, mv, mount, ls, ncdu, tree, rm, and cat. It preserves timestamps and verifies checksums at all times. Transfers can be restarted from the last good file.

**Official resources:** [rclone.org](https://rclone.org/) | [Docs](https://rclone.org/docs/) | [Commands](https://rclone.org/commands/) | [Install](https://rclone.org/install/) | [Forum](https://forum.rclone.org/) | [GitHub](https://github.com/rclone/rclone)

## When to Use

Use this skill when the user mentions rclone or any task involving terminal-based cloud file operations:

- Upload, download, sync, copy, move, or delete files on cloud storage
- Mount cloud storage as a local filesystem
- Configure or manage cloud storage remotes (S3, Google Drive, Dropbox, OneDrive, Azure Blob, B2, GCS, SFTP, WebDAV, etc.)
- Set up encrypted cloud backups
- Cloud-to-cloud migration or server-side copy
- Bandwidth-limited or scheduled transfers
- Remote control API usage
- Bidirectional sync (bisync)
- Filtering files by pattern, size, or age for transfer operations

**Trigger keywords:** rclone, cloud storage, S3, sync, mount, remote, backup to cloud, cloud-to-cloud, encrypted backup, rclone config, rclone serve, bisync.

## Prerequisites

1. Verify rclone is installed:

```bash
rclone --version
```

2. If not found, install using the bundled script at `scripts/install.sh` in this skill's directory, or install directly:

```bash
# Stable release
sudo -v ; curl https://rclone.org/install.sh | sudo bash

# Beta release
sudo -v ; curl https://rclone.org/install.sh | sudo bash -s beta
```

3. On Windows (PowerShell), download the zip from [rclone.org/install/](https://rclone.org/install/) or use `winget install Rclone.Rclone` / `scoop install rclone`. Ensure `rclone.exe` is on your `PATH`.

4. For detailed installation troubleshooting, read `references/install.md`.

## Procedure

### Step 1: Configure a Remote

```bash
# Interactive configuration (recommended)
rclone config

# Show current config (redacts secrets by default)
rclone config show

# List configured remotes
rclone listremotes

# Create a remote non-interactively
rclone config create myremote s3 provider=AWS env_auth=true region=us-east-1

# Update existing remote
rclone config update myremote region=us-west-2
```

**HARD RULE:** Never expose credentials in plain text on the command line. Use `rclone config` to store credentials securely, or use environment variables. The config file `~/.config/rclone/rclone.conf` contains sensitive data — protect it with `chmod 600`.

**HARD RULE:** `rclone config show --redacted=false` outputs full secrets. NEVER share, log, or commit this output.

### Step 2: Understand Basic Syntax

```
rclone subcommand [options] source:path dest:path
```

Source and destination paths use `remote:path` syntax. For local paths, just use `/path/to/dir`.

### Step 3: List and Inspect

```bash
rclone ls remote:path                    # list all objects with size
rclone lsd remote:path                   # list directories
rclone lsl remote:path                   # list with size, modtime, path
rclone lsf remote:path                   # list in flexible format
rclone size remote:path                  # total size and object count
rclone tree remote:path                  # tree view
rclone about remote:                     # get quota information
```

### Step 4: Copy Files

```bash
# Local to remote
rclone copy /local/path remote:path

# Remote to local
rclone copy remote:path /local/path

# Remote to remote (server-side if possible)
rclone copy remote1:path remote2:path
```

`copy` does NOT delete files at destination — it is safe for additive transfers.

### Step 5: Sync Files (DESTRUCTIVE — Always Dry-Run First)

```bash
# ALWAYS dry-run first!
rclone sync --dry-run /local/path remote:path

# Review output carefully, then run for real
rclone sync -P /local/path remote:path

# Interactive mode (asks before each operation)
rclone sync -i /local/path remote:path
```

**HARD RULE:** `rclone sync` makes dest identical to source — files in dest that are not in source will be DELETED. Always verify with `--dry-run` first.

### Step 6: Move Files

```bash
# Copies then deletes source
rclone move /local/path remote:path
```

### Step 7: Delete Operations (DESTRUCTIVE)

```bash
# Delete contents of path (respects filters)
rclone delete remote:path

# Delete path AND all contents (IGNORES all filters!)
rclone purge remote:path
```

**HARD RULE:** `rclone purge` ignores all filters — it deletes everything under the specified path. Use with extreme caution.

### Step 8: Verify Integrity

```bash
rclone check /local/path remote:path     # compare source and dest
rclone checksum remote:path              # verify checksums
rclone cryptcheck crypt:path              # verify encrypted remote
```

### Step 9: Directory Operations

```bash
rclone mkdir remote:path                 # create directory
rclone rmdir remote:path                 # remove empty directory
rclone rmdirs remote:path                # remove empty directories recursively
```

### Step 10: Filtering

```bash
# Include only specific patterns
rclone copy /src /dst --include "*.jpg"
rclone copy /src /dst --include-from filter-file.txt

# Exclude specific patterns
rclone copy /src /dst --exclude "*.tmp"
rclone copy /src /dst --exclude-from exclude-file.txt

# Use filter rules (preferred when mixing include/exclude)
rclone sync /src /dst --filter "+ *.jpg" --filter "- *"
rclone sync /src /dst --filter-from rules.txt

# Size-based filtering
rclone copy /src /dst --min-size 1M --max-size 10G

# Age-based filtering
rclone copy /src /dst --min-age 7d --max-age 30d
```

**HARD RULE:** Do NOT mix `--include`, `--exclude`, and `--filter` flags. Use `--filter` exclusively when combining rules.

Filter pattern syntax:
- `*` matches any sequence of non-separator characters
- `**` matches any sequence including separators
- `?` matches any single non-separator character
- `{a,b}` matches pattern alternatives
- `{{regexp}}` matches using Go regexp

For complex filter rules, read `references/filtering.md`.

### Step 11: Mount as Local Filesystem

```bash
# Basic mount
rclone mount remote:path /mnt/remote

# Recommended mount with caching (safer writes)
rclone mount remote:path /mnt/remote \
  --vfs-cache-mode full \
  --vfs-cache-max-size 10G \
  --vfs-read-chunk-size 128M

# Unmount
fusermount -u /mnt/remote                # Linux
umount /mnt/remote                        # macOS
```

**HARD RULE:** Mount operations can cause data loss if the mount is interrupted during writes. Use `--vfs-cache-mode full` for safer writes.

For detailed mount documentation, read `references/commands/rclone_mount.md`.

### Step 12: Serve Protocols

```bash
rclone serve http remote:path             # HTTP file server
rclone serve webdav remote:path           # WebDAV server
rclone serve sftp remote:path             # SFTP server
rclone serve ftp remote:path              # FTP server
rclone serve s3 remote:path               # S3-compatible server
rclone serve dlna remote:path             # DLNA media server
rclone serve restic remote:path           # Restic backup backend
rclone serve docker remote:path           # Docker registry
```

**HARD RULE:** Remote control API (`--rc`) should bind to localhost only by default. Exposing it without authentication (`--rc-htpasswd`) allows anyone to control your rclone instance.

For API details, read `references/rc.md`.

### Step 13: Encrypted Backup (Crypt Remote)

```bash
# Configure encrypted remote wrapping another remote
rclone config
# Choose "crypt" type, point to an existing remote (e.g., "drive:private")

# Use crypt remote — files are encrypted/decrypted transparently
rclone copy /local/files crypt:path
rclone ls crypt:path

# Check integrity of encrypted files
rclone cryptcheck crypt:path
```

For crypt configuration details, read `references/crypt.md`.

### Step 14: Global Flags (Most Common)

```bash
# Verbosity
-v                                        # info level
-vv                                       # debug level (shows filter matches)
--log-level LEVEL                         # DEBUG|INFO|NOTICE|ERROR

# Safety
--dry-run                                 # preview without doing anything
-i, --interactive                         # ask before each operation
--ignore-existing                         # skip files that exist at dest
-I, --ignore-times                         # transfer all, ignore modtime/size

# Transfer control
--transfers N                             # parallel transfers (default 4)
--checkers N                              # parallel checks (default 8)
--bwlimit RATE                            # bandwidth limit (e.g. 10M)
--max-transfer SIZE                        # stop after transferring this much
-c, --checksum                            # use checksum instead of modtime
--size-only                               # compare by size only

# Performance
--multi-thread-streams N                  # multi-thread downloads (default 4)
-P, --progress                            # show real-time progress

# Config
--config STRING                           # config file path
-C, --no-check-dest                       # skip dest check on copy
```

For the complete flags reference, read `references/flags.md`.

## Common Workflows

### Initial Setup

```bash
rclone config          # interactive setup wizard
rclone lsd remote:     # verify connection works
```

### Backup Local to Cloud

```bash
rclone sync --dry-run -P /home/user/documents remote:backup/documents
# Review dry-run output carefully, then:
rclone sync -P /home/user/documents remote:backup/documents
```

### Cloud-to-Cloud Migration

```bash
rclone copy --dry-run -P source_remote:path dest_remote:path
rclone copy -P --transfers 8 source_remote:path dest_remote:path
```

### Restore from Cloud

```bash
rclone copy --dry-run remote:backup/documents /home/user/restored
rclone copy -P remote:backup/documents /home/user/restored
```

### Bandwidth-Limited Transfer

```bash
rclone copy --bwlimit 10M -P /data remote:backup
```

### Encrypted Backup

```bash
# First configure a crypt remote wrapping your storage remote
rclone config
# Then use the crypt remote for all operations
rclone sync -P /sensitive-data crypt:backup
```

### Scheduled Backup (cron)

```bash
# Add to crontab (daily at 2am):
0 2 * * * rclone sync -P /data remote:backup >> /var/log/rclone.log 2>&1
```

## Detailed Reference Files

For in-depth information, consult these reference files in this skill's directory. These files are converted from the official Hugo-based rclone documentation under `testdata/rclone/docs/`. Treat any remaining Hugo shortcode or template syntax as a conversion bug: replace it with normal Markdown, a static table, or an official URL before relying on it in an answer.

| File | Content | When to read | Official link |
|------|---------|-------------|---------------|
| `references/usage.md` | Full usage guide: syntax, config, remote paths, options | Understanding advanced rclone behavior | [Docs](https://rclone.org/docs/) |
| `references/flags.md` | Complete global flags reference | Looking up specific flag options | [Flags](https://rclone.org/flags/) |
| `references/filtering.md` | Filtering, includes/excludes, patterns | Building complex filter rules | [Filtering](https://rclone.org/filtering/) |
| `references/rc.md` | Remote control / HTTP API | Using rclone's API for programmatic control | [RC API](https://rclone.org/rc/) |
| `references/bisync.md` | Bidirectional sync between two paths | Setting up two-way sync | [Bisync](https://rclone.org/bisync/) |
| `references/crypt.md` | Encrypted remote configuration | Setting up encrypted cloud storage | [Crypt](https://rclone.org/crypt/) |
| `references/cache.md` | Cache backend and directory caching | Optimizing performance with caching | [Cache](https://rclone.org/cache/) |
| `references/chunker.md` | Transparent file chunking | Handling large files on limited remotes | [Chunker](https://rclone.org/chunker/) |
| `references/union.md` | Union backend (merge multiple remotes) | Combining multiple storage backends | [Union](https://rclone.org/union/) |
| `references/combine.md` | Combine backend (unified namespace) | Unified view of multiple remotes | [Combine](https://rclone.org/combine/) |
| `references/hasher.md` | Hasher backend for checksum handling | Adding hash support to remotes | [Hasher](https://rclone.org/hasher/) |
| `references/overview.md` | Cloud storage system feature comparison | Comparing provider capabilities | [Overview](https://rclone.org/overview/) |
| `references/install.md` | Detailed installation instructions | Troubleshooting installation | [Install](https://rclone.org/install/) |
| `references/docker.md` | Docker usage guide | Running rclone in Docker | [Docker](https://rclone.org/docker/) |
| `references/faq.md` | Frequently asked questions | Troubleshooting common issues | [FAQ](https://rclone.org/faq/) |
| `references/commands/` | Individual command documentation | Detailed command usage | [Commands](https://rclone.org/commands/) |

### Popular Provider References

For configuring specific cloud storage providers, read the corresponding file in `references/providers/` when present. Some virtual/backing providers, such as `crypt`, `cache`, `chunker`, `union`, `combine`, and `hasher`, live as top-level files in `references/` because they are cross-provider backends rather than single cloud services.

- `s3.md` — Amazon S3 / compatible ([Official](https://rclone.org/s3/))
- `drive.md` — Google Drive ([Official](https://rclone.org/drive/))
- `dropbox.md` — Dropbox ([Official](https://rclone.org/dropbox/))
- `onedrive.md` — Microsoft OneDrive ([Official](https://rclone.org/onedrive/))
- `azureblob.md` — Azure Blob Storage ([Official](https://rclone.org/azureblob/))
- `b2.md` — Backblaze B2 ([Official](https://rclone.org/b2/))
- `googlecloudstorage.md` — Google Cloud Storage ([Official](https://rclone.org/googlecloudstorage/))
- `sftp.md` — SFTP ([Official](https://rclone.org/sftp/))
- `webdav.md` — WebDAV ([Official](https://rclone.org/webdav/))
- `swift.md` — OpenStack Swift ([Official](https://rclone.org/swift/))
- `ftp.md` — FTP ([Official](https://rclone.org/ftp/))
- And 60+ more providers — each has a page at `https://rclone.org/<name>/`

### Command References

For detailed command documentation, read the corresponding file in `references/commands/`:
- `rclone_copy.md`, `rclone_sync.md`, `rclone_move.md` — transfer commands
- `rclone_mount.md` — FUSE mount
- `rclone_serve_*.md` — various serve modes
- `rclone_config*.md` — configuration management
- `rclone_bisync.md` — bidirectional sync
- And 80+ more commands — each has a page at `https://rclone.org/commands/<command>/`

## Pitfalls

1. **`rclone sync` deletes files at destination that don't exist at source.** Always run with `--dry-run` first and review the output carefully before committing.

2. **`rclone purge` ignores all filters.** It deletes everything under the specified path regardless of any `--include`, `--exclude`, or `--filter` rules. Use `rclone delete` instead if you need filter support.

3. **Mixing `--include`, `--exclude`, and `--filter` flags produces unexpected results.** Use `--filter` exclusively when combining include and exclude rules.

4. **Mount interrupted during writes causes data loss.** Always use `--vfs-cache-mode full` for safer write operations.

5. **`rclone config show --redacted=false` outputs full secrets.** Never share, log, or commit this output. It exposes S3 secret keys, OAuth tokens, and service account JSON.

6. **Remote control API exposed without authentication.** Binding `--rc` to anything other than localhost without `--rc-htpasswd` allows anyone to control your rclone instance.

7. **Private keys and tokens committed to version control.** The config file `~/.config/rclone/rclone.conf` contains sensitive data — protect it with `chmod 600` and never commit it.

8. **Assuming examples work without environment-specific testing.** Verify commands, dependencies, credentials, and external service behavior before applying changes. Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.

9. **Hugo shortcode/template syntax in reference files.** These are conversion bugs from the original documentation. Replace with normal Markdown, a static table, or an official URL before relying on the content.

## Verification

1. **Verify rclone is installed and working:**

```bash
rclone version
# Expected: rclone v1.xx.x with build date and OS/arch info
```

2. **Verify a remote is configured and accessible:**

```bash
rclone listremotes
# Expected: lists all configured remote names, one per line

rclone lsd remote:
# Expected: lists top-level directories on the remote
```

3. **Verify a sync operation before running it:**

```bash
rclone sync --dry-run -v /local/path remote:path
# Expected: lists files that would be transferred and deleted
# Review carefully — especially any "Deleted" entries
```

4. **Verify integrity after transfer:**

```bash
rclone check /local/path remote:path
# Expected: "0 differences found" or lists of differing files
```

5. **Verify config file permissions:**

```bash
ls -la ~/.config/rclone/rclone.conf
# Expected: -rw------- (600) — only owner can read/write
```

## Related skills

- `s3-cli` — Direct AWS CLI S3 operations when rclone is not available
- `restic` — Encrypted, deduplicated backups (can use rclone as a backend via `rclone serve restic`)
