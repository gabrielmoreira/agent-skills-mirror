---
name: sharepoint-backup-sharepoint-agents
description: Read-only backup of named .agent files from a SharePoint site to a local directory.
---

# backup-sharepoint-agents

## Purpose

Downloads named `.agent` files to a local directory as a precaution before any tenant cleanup is
considered. Makes no changes to the tenant. Idempotent — always writes to the same fixed output
directory and overwrites in place on every run.

## Input boundaries

- `-ConfigFile` — connection/authentication context only.
- `-SitePath` (required) — site-relative path to the folder containing the `.agent` files.
- `-AgentFileNames` (required) — explicit list. No hardcoded default — generalized from the
  original Phase 5 `backup-existing-agents.ps1`, which hardcoded specific agent
  filenames; those 5 values now live only in that Phase 5 script's own thin-wrapper defaults.
- `-OutputDir` — local destination directory.
- **Read-only** — no tenant write of any kind.

## Scripts

- `../../scripts/backup-sharepoint-agents.ps1`

## Related

- `restore-sharepoint-agents` — the corresponding restore skill.

