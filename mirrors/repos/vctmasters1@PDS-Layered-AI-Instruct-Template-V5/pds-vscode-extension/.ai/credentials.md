# Credentials — Credential Warehousing & Security Rules

**Scope**: `pds-vscode-extension/` module reference
**Last Updated**: 2026-05-27

> **→ Root [`.ai/credentials.md`](../../.ai/credentials.md)** — This file is authoritative for all directories in this project.

## Never Commit Credentials

**Never commit credentials, secrets, API keys, passwords, tokens, or connection strings to git.**

This includes:
- Database passwords and full connection strings
- API keys (third-party services, internal services)
- JWT secrets and signing keys

## .env File Convention

```
pds-vscode-extension/
├── .env                  ← GITIGNORED — actual values
└── .env.example          ← COMMITTED — template only
```

### `.env.example` Format

```bash
# ── Extension Configuration ───────────────────────────────
EXTENSION_ID=pds.pds-toolbox
PUBLISHER_ID=pds-automation
VERSION=0.2.0

# ── External Services ─────────────────────────────────────
JWT_SECRET=your-secret-key-here-minimum-32-characters
```

## .gitignore Requirements

```gitignore
# Credentials & secrets — NEVER COMMIT
.env
.env.local
.env.*.local
*.pem
*.key
credentials/
secrets/

# VS Code extension artifacts
node_modules/
dist/
*.vsix