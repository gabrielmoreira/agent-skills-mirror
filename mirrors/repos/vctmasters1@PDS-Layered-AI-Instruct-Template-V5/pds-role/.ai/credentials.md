# Credentials — Credential Warehousing & Security Rules

**Scope**: `pds-role/` module reference
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
pds-role/
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