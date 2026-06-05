# Credentials — Credential Warehousing & Security Rules

**Scope**: `web-firmware-server/` module reference
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
WEB-FwServer/
├── .env                  ← GITIGNORED — actual values
└── .env.example          ← COMMITTED — template only
```

### `.env.example` Format

```bash
# ── Database ──────────────────────────────────────────────
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# ── Authentication ────────────────────────────────────────
JWT_SECRET=your-secret-key-here-minimum-32-characters

# ── Application ───────────────────────────────────────────
NODE_ENV=development
PORT=3002

# ── Storage ───────────────────────────────────────────────
STORAGE_DIR=/path/to/storage/directory
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

# Firmware binaries - gitignored by default
storage/
!storage/.gitignore