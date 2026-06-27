---
name: open-knowledge-bug-report
description: "Use when the user reports a problem with OpenKnowledge, asks for help debugging OK, or wants to file a bug report. This skill guides the agent to capture diagnostic information via the ok bug-report CLI command."
compatibility: "Any MCP host (Claude Code, Cursor, Codex, Windsurf) with OpenKnowledge MCP server registered."
metadata:
  version: "0.6.0"
  author: "Inkeep"
  repository: "https://github.com/inkeep/open-knowledge"
---

# Bug Report — agent guidance

When a user reports a problem with OpenKnowledge or asks for debugging help, use the `ok bug-report` command to capture a structured diagnostic bundle.

## Quick path

```bash
ok bug-report --no-reveal
```

The `--no-reveal` flag suppresses the Finder reveal (use it when running as an agent — you want the file path, not a Finder window).

## What the command does

1. Gathers all structured log files from `~/.ok/logs/` (NDJSON format, pino)
2. When invoked inside an OK project directory, filters logs to that project's records
3. Collects system info: OK version, Node/Bun versions, macOS version, locale, timezone, free disk space
4. Collects lock directory contents (server.lock, spawn-error-log) when a project context exists
5. Extracts recent IPC error records from desktop logs
6. Runs an auto-redaction pass over all content (home paths, API tokens, credentials are scrubbed)
7. Writes `~/.ok/bug-reports/<timestamp>-bugreport.zip`
8. Prints the bundle path to stdout

## What's in the bundle

```
<timestamp>-bugreport.zip
├── MANIFEST.json       — what's inside, redaction audit report
├── sysinfo.json        — versions, locale, disk, build channel
├── README.md           — what's safe to share, discipline version
├── logs/               — NDJSON log files (auto-redacted)
├── lockdir/            — server.lock, spawn-error-log (if project)
└── recent-ipc-errors.json — last 50 structured IPC errors
```

## Agent workflow

1. Run `ok bug-report --no-reveal` in the user's project directory (or home if no project)
2. Read the path from stdout
3. Unzip to a temp directory: `unzip -o <path> -d /tmp/ok-diag-<timestamp>/`
4. Read `MANIFEST.json` — check the `redactions` array (if non-empty, some content was scrubbed)
5. Read `sysinfo.json` — check versions, disk space, build channel
6. Grep the log files for errors: `grep '"level":50' logs/*.log | head -20` (level 50 = error in pino)
7. Read `recent-ipc-errors.json` for IPC-layer failures
8. Report findings to the user with actionable next steps

## If the command is not available

The `ok bug-report` command ships with `@inkeep/open-knowledge` >= 0.7.0. If the user's version is older:

1. Check version: `ok --version`
2. If < 0.7.0: suggest `npm install -g @inkeep/open-knowledge@latest` to update
3. Fallback: manually inspect `~/.ok/logs/` for recent `.log` files (NDJSON format, greppable)

## Privacy

The bundle auto-redacts:
- macOS home paths (`/Users/<name>/` → `~/`)
- GitHub PAT prefixes (`ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`)
- AWS access keys, Anthropic tokens, OpenAI tokens
- Bearer authorization headers

The `MANIFEST.json` `redactions` array lists every file and pattern that was scrubbed. The bundle is safe for the user to attach to a GitHub issue.
